from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from states.status_info import BestdealStatus
from information_API import hotels
from loguru import logger
from loader import dp, bot
from keyboards.inline import answer, calendar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date

rus = {'year': 'год',
       'month': 'месяц',
       'day': 'день'}

# @dp.message_handler(commands=["bestdeal"])
def register_handlers_bestdeal(dp: Dispatcher):
    dp.register_message_handler(command_handler, commands=['lowprice', 'hightprice', 'bestdeal'], state='*')
    dp.register_message_handler(city_name_handler, state=BestdealStatus.city)
    dp.register_callback_query_handler(keyboard_handler, lambda inline_query: True, state='*')
    # dp.register_message_handler(check_in_out_handler, state=[BestdealStatus.check_in, BestdealStatus.check_out])
    dp.register_callback_query_handler(callback_calendar, lambda DetailedTelegramCalendar: True,
                                       state=BestdealStatus.check_in)
    dp.register_callback_query_handler(callback_check_out, lambda DetailedTelegramCalendar: True,
                                       state=BestdealStatus.check_out)
    dp.register_message_handler(min_price_handler, state=BestdealStatus.min_price)
    dp.register_message_handler(max_price_handler, state=BestdealStatus.max_price)
    dp.register_message_handler(min_distance_handler, state=BestdealStatus.min_distance_center)
    dp.register_message_handler(max_distance_handler, state=BestdealStatus.max_distance_center)
    dp.register_message_handler(hotels_count_handler, state=BestdealStatus.hotels_count)
    # dp.register_message_handler(check_in_input_handler, state=BestdealStatus.check_in)
    # dp.register_message_handler(check_out_handler, state=BestdealStatus.check_out)
    dp.register_message_handler(get_photo_handler, state=BestdealStatus.get_photo)
    dp.register_message_handler(photo_count_handler, state=BestdealStatus.photo_count)
    dp.register_message_handler(get_requests, state=BestdealStatus.executing_request)


@logger.catch()
@dp.callback_query_handler(lambda DetailedTelegramCalendar: True)
async def callback_calendar(call: CallbackQuery, state: BestdealStatus.check_in) -> None:
    """
    Вызывается в случае получения запроса обратного вызова от
    кнопок календаря telegram_bot_calendar
    :param call: полученный результат от нажатия на календарь - дата выезда
    """
    logger.debug(f'Метод callback_calendar вызван с аргументами: {call}')
    result, key, step = DetailedTelegramCalendar().process(call.data)
    logger.debug(result, key, step)
    if not result and key:
        step = rus[LSTEP[step]]
        await bot.edit_message_text(
            'Выберите {step}'.format(step=step),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key
        )
    elif result:
        logger.debug(result)
        await bot.edit_message_text('Вы выбрали {result}'.format(result=result),
                              call.message.chat.id,
                              call.message.message_id)

        BestdealStatus.check_in = str(result)
        logger.debug(f'Записано состояние {BestdealStatus.check_in}')
        # logger.info(f'Установлено состояние {BestdealStatus.check_in} : {str(result)}')
        min_data = result
        calendar, step = DetailedTelegramCalendar(min_date=min_data).build()
        step = rus[LSTEP[step]]
        logger.debug(result)
        logger.debug(calendar)
        await bot.send_message(call.from_user.id, 'Выезд:')
        BestdealStatus.check_out.set()
        await bot.send_message(call.from_user.id,
                             "Выберите {step}".format(step=step),
                             reply_markup=calendar())


@logger.catch()
@dp.callback_query_handler(lambda DetailedTelegramCalendar: True)
async def callback_check_out(call: CallbackQuery, state: BestdealStatus.check_out) -> None:
    """Обработка установки даты отъезда
    :param call: передается ответ от наждатия на клавиатуру пользователем- дата выезда"""
    logger.info('Запущена функция проверки даты выезда check_out')
    BestdealStatus.check_out = str(call.message.text)
    logger.debug(f'Записано состояние {BestdealStatus.check_out}')
    chat_id = call.message.chat.id
    BestdealStatus.min_price.set()
    await bot.send_message(chat_id, 'Минимальная цена за отель: ')


@logger.catch()
@dp.callback_query_handler(lambda inline_query: True)  # декоратор-хендлер для реализации обработки объекта запроса
async def keyboard_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Вызов клавиатуры
    :param call: CallbackQuery
    """
    logger.info(f'Метод  keyboard_handler вызван с аргументами: {callback_query}')
    info = dict(callback_query)
    chat_id = callback_query.message.chat.id
    city_id = str(callback_query['data'])

    logger.info(f'сейчас в callbacks_handler, city_id ={city_id}')
    logger.info(f'{callback_query}, а теперь инфо в словаре создано {info}')
    # В callback_query.data code+id города, a callback_query весь словарь

    if city_id.startswith('code'):
        loc_name = await hotels.exact_location(info, city_id)
        logger.info(f"Город: {loc_name} выбран")
        logger.info('Был осуществлен переход из callbacks_handler в set_city_id')
        await set_city_id(city_id, callback_query.message, state=BestdealStatus.city)
        # await set_city_id(city_id, callback_query.message, state=BestdealStatus.min_price)
        await bot.send_message(chat_id, f'Локация выбрана {loc_name}')
        await bot.delete_message(chat_id, message_id=callback_query.message.message_id)

    elif city_id == 'cancel':
        logger.info(f'Закрыто пользователем')
        reply_text = "Пользователь отменил выбор. Можете повторить выбранную команду /bestdeal или выбрать другую."
        await bot.send_message(chat_id, text=reply_text)
        await bot.delete_message(chat_id, message_id=callback_query.message.message_id)


@logger.catch()
async def command_handler(message: Message, state: FSMContext):
    """Начальный метод обработчик состояний - устанавливает city
    :param message: передано сообщение пользователя-команда
    """
    logger.info('Первичная команда для обработки bestdeal / lowprice/ hightprice.')
    await message.answer('В каком городе будем искать отель?')
    logger.info('Осуществлен переход из command_handler1 в city_name_input_handler')
    await BestdealStatus.city.set()


@logger.catch()
async def city_name_handler(message: Message, state: FSMContext) -> None:
    """Обработка (city_id) ввода названия города - если похожих несколько, то уточняется город
    :param message: передано введенное сообщение пользователя"""
    if any(ext in message.text for ext in ['1234567890!#$%&*()+=/"`[]<>@№:;']):
        await message.answer('Имя города не должно содержать цифры или символы. Введите корректное имя города:')
        await command_handler(message, state=BestdealStatus.city)
    else:
        logger.info('Осуществлен переход из city_name_input_handler в hotels.get_locations')
        await hotels.get_locations(message)


@logger.catch()
async def set_city_id(city_id: str, message: Message, state: FSMContext) -> None:
    """Обработка установки city_id для выбранного пользователем города
    :param: city_id: айди города в формате code+номер id
    :param: message: сообщение
    """
    logger.info(f'Запущен set_city_id, проверка айди города {city_id[4:]}')
    BestdealStatus.city = str(city_id[4:])
    logger.debug(f'Записано состояние {BestdealStatus.city}')
    await message.answer('Дата заезда:')
    BestdealStatus.check_in.set()
    await message.answer("Выберите {step}".format(step=calendar.step), reply_markup=calendar.calendar)
    # state = dp.current_state(chat=message.chat.id, city_id=city_id[4:])
    # # state = dp.current_state(chat=message.chat.id, city_id=city_id[4:])
    # async with state.proxy() as state_data:
    #     state_data['city_id'] = city_id[4:]
    # logger.info(f'Добавлен city_id:{city_id}: {state_data["city_id"]}')
    # await message.reply('Установлено: ', BestdealStatus.city)
    # await BestdealStatus.next()


@logger.catch()
async def parametrs(parameters_name: str, message: Message, state: FSMContext) -> None:
    """Обработка ввода цены запроса поиска отеля (для минимальной и максимальной)
    :param parameters_name:переданные параметры для проверки пользователем
    :message: сообщение переданое на обработку (мин/макс цена Б мин/макс расстояние до центра)
    """
    logger.info('Запущен parametrs')
    parameter_str = message.text.strip()
    try:
        parameter = int(parameter_str)
        if parameter >= 0:
            if isinstance(parameter, int):
                if parameters_name == 'min_price':
                    BestdealStatus.min_price = parameter
                    logger.debug(f'Записано состояние {BestdealStatus.min_price}')
                elif parameters_name == 'max_price':
                    BestdealStatus.max_price = parameter
                    logger.debug(f'Записано состояние {BestdealStatus.max_price}')
                elif parameters_name == 'min_distance':
                    BestdealStatus.min_distance_center = parameter
                    logger.debug(f'Записано состояние {BestdealStatus.min_distance_center}')
                elif parameters_name == 'max_distance':
                    BestdealStatus.max_distance_center = parameter
                    logger.debug(f'Записано состояние {BestdealStatus.max_distance_center}')

                # async with state.proxy() as state_data:
                #     state_data[parameters_name] = parameter
                #     logger.info(f'Добавлен параметр {parameters_name}: {state_data[parameters_name]}')
                # await BestdealStatus.next()
    except:
        logger.exception('Поймано исключение - ошибка ввода пользователя для обработки параметров цены отеля')
        await message.answer('Ошибка в вводе цены - укажите целое число больше 0')


@logger.catch()
async def min_price_handler(message: Message, state: FSMContext) -> None:
    """Обрабатывает дату выезда из отеля и запрашивает цену минимальную за отель
    :param message: дата выезда"""
    logger.info(f'Запущен min_price_handler, message.text= {message.text}, message.message_id={message.message_id}')
    await parametrs('min_price', message, state)
    # BestdealStatus.min_price = str(message.text)
    BestdealStatus.max_price.set()
    await message.answer(f'Максимальная цена за отель: ')
    # state = dp.current_state(chat=message.chat.id, currency=message.message_id)
    # async with state.proxy() as state_date:
    #     currency = state_date.get('currency')
    #     await message.answer(f'Минимальная цена за отель: , ({currency})')
    #     logger.info('Осуществлен переход из min_price_handler в parametrs')
    #     await parametrs('min_price', message, state)
    #     BestdealStatus.max_price.set()
    #     await message.answer(f'Максимальная цена за отель: ')


@logger.catch()
async def max_price_handler(message: Message, state: FSMContext) -> None:
    """Обработчик максимальной цены запроса поиска отеля
    :param message: максимальная цена за отель"""
    logger.info('Запущен max_price_handler.')
    state = dp.current_state(chat=message.chat.id, currency=message.message_id)
    logger.info('Осуществлен переход из max_price_handler в parametrs')
    await parametrs('max_price', message, state)
    # BestdealStatus.max_price = str(message.text)
    BestdealStatus.min_distance_center.set()
    await message.answer('Минимальное расстояние до центра:')


async def min_distance_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода минимальной дистанции до центра
    :param: message: минимальное расстоние до центра
    """
    logger.info('Запущен min_distance_handler.')
    state = dp.current_state(chat=message.chat.id, distance_unit=message.message_id)
    # async with state.proxy() as state_data:
    #     distance_unit = state_data.get('distance_unit')
    await parametrs('min_distance', message, state)
    # BestdealStatus.min_distance_center = str(message.text)
    await message.answer(f'Максимальное расстояние до центра: ')


async def max_distance_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода максимальной дистанции до центра
    :param message:ответ пользователя по максимальному расстоянию до центра
    """
    logger.info('Запущен max_distance_handler')
    state = dp.current_state(chat=message.chat.id, distance_unit=message.message_id)
    await parametrs('max_distance', message, state)
    # BestdealStatus.max_distance_center = str(message.text)
    await message.answer('Количество отелей к выводу в результате (не более 25): ')


async def hotels_count_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода количества отелей к выводу в результате
    :param message: кол-во отелей
    """
    logger.info('Запущен hotels_count_handler.')
    try:
        if int(message.text) <= 25:
            BestdealStatus.hotels_count = int(message.text)
            logger.debug(f'Установлено {BestdealStatus.hotels_count}')
            BestdealStatus.get_photo.set()
            await message.answer('Показывать фотографии отелей?', reply_markup=answer.yes_no)

    except ValueError:
        await message.answer('Ошибка ввода. Можно вывести от 1-25 отелей включительно.')
        logger.exception('Поймано исключение - не коректный ввод количества отелей (от 1 -25 включительно).')

# async def check_in_out_handler(message: Message, state: FSMContext) -> None:
# async def check_in_input_handler(message: Message, state: FSMContext) -> None:
#     """Обработка ввода даты заезда в отель"""
#     correct = await set_check_in(message, state)
#     if correct:
#         await message.answer('Дата выезда: ')
#         await BestdealStatus.next()

# async def check_out_input_handler(message: Message, state: FSMContext) -> None:
#     """Обработка ввода даты выезда"""
#     correct = await set_check_out(message, state)
#     if correct:
#         keyboards = answer.get_yes_no_keyboard()
#         await message.answer('Показать фотографии отелей? ', reply_markup=keyboards)
#         await BestdealStatus.next()

async def get_photo_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода ответа на запрос ввывода фотографий отеля
    :param message: Ответ на вопрос показывать ли фотографии отелей
    """
    logger.info('Запущен get_photo_handler')
    get_photo_str = message.text.strip().lower()
    # async with state.proxy() as state_data:
    #     state_data['get_photo'] = get_photo_str == 'да'
    #     logger.info(f'Добавлен параметр запроса get_photo: {state_data["get_photo"]}')
    BestdealStatus.get_photo = get_photo_str

    if get_photo_str == 'да':
        await BestdealStatus.photo_count.set()
        await message.answer('Сколько фотографий отеля показать (не более 5)?', reply_markup=ReplyKeyboardRemove())
    elif get_photo_str == 'нет':
        await message.answer('Вывод без фотографий отелей.')
        await get_requests(message, state)


async def photo_count_handler(message: Message, state: FSMContext) -> None:
    """Обработка вывода количества фотографий отелей
    :param message: кол-во фотографий
    """
    logger.info('Запущен photo_count_handler.')
    photo_count_str = message.text.strip().lower()
    try:
        photo_count = int(photo_count_str)
        if photo_count <= 5:
            BestdealStatus.photo_count = photo_count
            logger.debug(f'Добавлен параметр photo_count {BestdealStatus.photo_count}')
            await state.finish()
            # async with state.proxy() as state_data:
            #     state_data['photo_count'] = photo_count
            #     logger.info(f'Добавлен параметр photo_count: {state_data["photo_count"]}')
            #     await state.finish()
            await get_requests(message, state)
    except ValueError:
        await message.answer('Допустим ввод только целых чисел от 1 до 5 включительно.')


async def get_requests(message: Message, state: FSMContext) -> None:
    """Обработка отправки запроса пользователя по отелю и обработка ответа API
    :param message: итоговый метод обработки и получения списка отелей со всей информацией по запросу
    """
    await message.answer('Ваш запрос принят, выполняю поиск отелей..', reply_markup=ReplyKeyboardRemove())
    await hotels.get_hotels(message, state)  #обращение к апи файлу
    await message.answer('Поиск отелей выполнен.', reply_markup=ReplyKeyboardRemove())
    await state.reset_state() #сброс состояний
