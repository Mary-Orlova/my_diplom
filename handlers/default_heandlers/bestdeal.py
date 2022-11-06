from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from states.status_info import HotelStatus
from information_API import hotels
from loguru import logger
from loader import dp, bot
from keyboards.inline import answer, mycalendar


def register_handlers_bestdeal(dp):
    dp.register_message_handler(command_handler,
                                commands=['lowprice', 'highprice', 'bestdeal'], state='*')
    dp.register_message_handler(city_name_handler, state=HotelStatus.city)
    dp.register_callback_query_handler(keyboard_handler, state=HotelStatus.city)
    dp.register_callback_query_handler(callback_calendar, state=HotelStatus.check_in)
    dp.register_callback_query_handler(callback_check_out, state=HotelStatus.check_out)
    dp.register_message_handler(min_price_handler, state=HotelStatus.min_price)
    dp.register_message_handler(max_price_handler, state=HotelStatus.max_price)
    dp.register_message_handler(min_distance_handler, state=HotelStatus.min_distance)
    dp.register_message_handler(max_distance_handler, state=HotelStatus.max_distance)
    dp.register_message_handler(hotels_count_handler, state=HotelStatus.hotels_count)
    dp.register_message_handler(get_photo_handler, state=HotelStatus.get_photo)
    dp.register_message_handler(photo_count_handler, state=HotelStatus.photo_count)
    dp.register_message_handler(get_requests, state=HotelStatus.photo_count)


@logger.catch()
@dp.callback_query_handler(state=HotelStatus.check_in)
async def callback_calendar(call: CallbackQuery, state: FSMContext) -> None:
    """ Вызывается в случае получения запроса обратного вызова от кнопок календаря telegram_bot_calendar.
    :param call: полученный результат от нажатия на календарь - дата выезда;
    :param state: HotelStatus.check_in. """
    logger.debug(f'Метод callback_calendar вызван')
    result, keyboard, step = await mycalendar.create_calendar(call, is_process=True)  # Создали новый календарь

    if not result and keyboard:  # Продолжаем отсылать шаги, пока не выберут дату "result"
        await call.message.edit_text(f'Укажите {step} заезда', reply_markup=keyboard)

    elif result:
        # Дата выбрана, сохраняем и создаем новый календарь
        await call.message.edit_text(f'Выбрана дата заезда: {result}')
        async with state.proxy() as state_data:
            state_data['check_in'] = result
        logger.debug(f'Записано состояние {HotelStatus.check_in} state_data["check_in"] = {result}')
        await call.answer('Укажите дату выезда')
        calendar, step = await mycalendar.create_calendar(call, min_date=result)
        await call.message.answer(f'Укажите {step} отъезда', reply_markup=calendar)
        await HotelStatus.check_out.set()


@logger.catch()
@dp.callback_query_handler(state=HotelStatus.check_out)
async def callback_check_out(call: CallbackQuery, state: FSMContext) -> None:
    """ Обработка установки даты отъезда.
    :param call: передается ответ от нажатия на клавиатуру пользователем - дата выезда;
    :param state: HotelStatus.check_out. """
    logger.info(f'Запущена функция обработки даты выезда check_out ')
    result, keyboard, step = await mycalendar.create_calendar(call, is_process=True)  # Создали новый календарь

    if not result and keyboard:  # Продолжаем отсылать шаги, пока не выберут дату "result"
        await call.message.edit_text(f'Укажите {step} выезда', reply_markup=keyboard)

    elif result:
        # Дата выбрана, сохраняем
        chat_id = call.message.chat.id
        await call.message.edit_text(f'Выбрана дата выезда: {result}')
        async with state.proxy() as state_data:
            if result < state_data['check_in']:
                state_data['check_in'], state_data['check_out'] = result, state_data['check_in']
                logger.info(f'Изменено: {state_data["check_in"]}, {state_data["check_out"]}')
                await bot.send_message(chat_id, f'Изменено: {state_data["check_in"]}, {state_data["check_out"]}')
            else:
                state_data['check_out'] = result
        logger.debug(f'Записано состояние {HotelStatus.check_out} state_data["check_out"] = {result}')
        async with state.proxy() as state_data:
            if state_data.get('order') == "/bestdeal":
                await bot.send_message(chat_id, 'Минимальная цена за отель: ')
                await HotelStatus.min_price.set()
            else:
                await HotelStatus.hotels_count.set()
                await bot.send_message(chat_id, 'Количество отелей к выводу в результате (не более 25): ')


@logger.catch()
@dp.callback_query_handler(state=HotelStatus.city)  # декоратор для реализации обработки объекта запроса
async def keyboard_handler(call: CallbackQuery, state: FSMContext) -> None:
    """ Вызов клавиатуры.
    :param call: CallbackQuery;
    :param state: HotelStatus.city. """
    logger.info(f'Метод  keyboard_handler вызван (поиск и выбор города)')
    info = dict(call)
    chat_id = call.message.chat.id
    city_id = str(call['data'])

    logger.info(f'сейчас в callbacks_handler, city_id ={city_id}')
    # В callback_query.data code+id города, a callback_query весь словарь

    if city_id.startswith('code'):
        loc_name = await hotels.exact_location(info, city_id)
        logger.info(f"Город: {loc_name} выбран")
        async with state.proxy() as state_data:
            state_data['city_name'] = str(loc_name)
            logger.debug(f'Записан город: {state_data["city_name"]}')
        logger.info('Был осуществлен переход из callbacks_handler в set_city_id')
        await set_city_id(city_id, state=state)
        await bot.delete_message(chat_id, message_id=call.message.message_id)
        await bot.send_message(chat_id, f'Локация выбрана {loc_name}')

        calendar, step = await mycalendar.create_calendar(call)
        await call.message.answer(f'Укажите {step} заезда', reply_markup=calendar)
        await HotelStatus.check_in.set()

    elif city_id == 'cancel':
        logger.info(f'Закрыто пользователем')
        reply_text = "Пользователь отменил выбор. Можете повторить выбранную команду /bestdeal или выбрать другую."
        await bot.send_message(chat_id, text=reply_text)
        await bot.delete_message(chat_id, message_id=call.message.message_id)


@logger.catch()
async def command_handler(message: Message, state: FSMContext):
    """ Начальный метод обработчик состояний - устанавливает city.
    :param message: передано сообщение пользователя-команда;
    :param state: первичное состояние ддя команд bestdeal / lowprice/ hightprice. """
    logger.info(f'Первичная команда для обработки  = {message.text}')
    async with state.proxy() as state_date:
        state_date['order'] = message.text
    await message.answer('В каком городе будем искать отель?')
    logger.info('Осуществлен переход из command_handler1 в city_name_input_handler')
    await HotelStatus.city.set()


@logger.catch()
async def city_name_handler(message: Message, state: FSMContext) -> None:
    """ Обработка (city_id) ввода названия города - если похожих несколько, то уточняется город.
    :param message: передано введенное сообщение пользователя;
    :param state: состояние по городу. """
    if any(ext in message.text for ext in ['1234567890!#$%&*()+=/"`[]<>@№:;']):
        await message.answer('Имя города не должно содержать цифры или символы. Введите корректное имя города:')
        await command_handler(message, state=HotelStatus.city)
    else:
        logger.info(f'Осуществлен переход из city_name_input_handler в hotels.get_locations, состояние {state} ')
        await hotels.get_locations(message)


@logger.catch()
async def set_city_id(city_id: str, state: FSMContext) -> None:
    """ Обработка установки city_id для выбранного пользователем города
    :param city_id: id города в формате code+номер id
    :param state: обработка HotelStatus.city. """
    logger.info(f'Запущен set_city_id, проверка id города {city_id[4:]}')
    async with state.proxy() as state_data:
        state_data['city'] = str(city_id[4:])
    logger.debug(f'Записано состояние {HotelStatus.city} state_data["city"]= {str(city_id[4:])}')


@logger.catch()
async def parametrs(parameters_name: str, message: Message, state: FSMContext) -> None:
    """ Обработка ввода цены и расстояния запроса поиска отеля (для минимальной и максимальной).
    :param parameters_name:переданные параметры для проверки пользователем (MIN/MAX цена и MIN/MAX расстояние.)
    :param message: сообщение переданое на обработку;
    :param state: преданное состояние. """
    logger.debug(f'Запущен parametrs')

    parameter_str = message.text
    logger.debug(f'{parameter_str}')

    try:
        parameter = int(parameter_str)
        if parameter >= 0:
            async with state.proxy() as state_data:
                if parameters_name == 'max_price' and parameter <= int(state_data['min_price']):
                    state_data['min_price'], state_data['max_price'] = parameter, state_data['min_price']
                    logger.info(f'Изменено: MIN {state_data["min_price"]}, MAX {state_data["max_price"]}')
                elif parameters_name == 'max_distance' and parameter <= int(state_data['min_distance']):
                    state_data['min_distance'], state_data['max_distance'] = parameter, state_data[
                                'min_distance']
                    logger.info(
                            f'Изменено: max_dis {state_data["min_distance"]}, min_dis {state_data["max_distance"]}')
                else:
                    state_data[parameters_name] = parameter
            logger.info(f'Добавлен параметр {parameters_name} = parameter')
            await HotelStatus.next()
    except ValueError:
        logger.exception('Поймано исключение - ошибка ввода пользователя для обработки параметров цены отеля')
        await message.answer('Ошибка в вводе - укажите целое число больше 0')

    # try:
    #     parameter = int(parameter_str)
    #     if parameter >= 0:
    #         async with state.proxy() as state_data:
    #             if parameters_name == 'max_price' and parameter <= int(state_data['min_price']):
    #                 state_data['min_price'], state_data['max_price'] = parameter, state_data['min_price']
    #                 logger.info(f'Изменено: MIN {state_data["min_price"]}, MAX {state_data["max_price"]}')
    #             elif parameters_name == 'max_distance' and parameter <= int(state_data['min_distance']):
    #                 state_data['min_distance'], state_data['max_distance'] = parameter, state_data['min_distance']
    #                 logger.info(f'Изменено: maxdis {state_data["min_distance"]}, mindis {state_data["max_distance"]}')
    #             else:
    #                 state_data[parameters_name] = parameter
    #         logger.info(f'Добавлен параметр {parameters_name} = parameter')
    #         await HotelStatus.next()
    # except ValueError:
    #     logger.exception('Поймано исключение - ошибка ввода пользователя для обработки параметров цены отеля')
    #     parameters_name = await message.answer('Ошибка в вводе  - укажите целое число больше 0')


@logger.catch()
@dp.message_handler(state=HotelStatus.min_price)
async def min_price_handler(message: Message, state: FSMContext) -> None:
    """Обрабатывает минимальную цену за отель.
    :param message: дата выезда
    :param state: HotelStatus.min_price"""
    logger.info(f'Запущен min_price_handler, message.text= {message.text}')
    await parametrs('min_price', message, state)
    await message.answer('Максимальная цена за отель: ')


@logger.catch()
@dp.message_handler(state=HotelStatus.max_price)
async def max_price_handler(message: Message, state: FSMContext) -> None:
    """Обработчик максимальной цены запроса поиска отеля
    :param message: максимальная цена за отель
    :param state: HotelStatus.max_price"""
    logger.info('Запущен max_price_handler.')
    logger.info('Осуществлен переход из max_price_handler в parametrs')
    await parametrs('max_price', message, state)
    await message.answer('Минимальное расстояние до центра:')


@logger.catch()
@dp.message_handler(state=HotelStatus.min_distance)
async def min_distance_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода минимальной дистанции до центра.
    :param: message: минимальное расстояние до центра."""
    logger.info('Запущен min_distance_handler.')
    await parametrs('min_distance', message, state)
    await message.answer(f'Максимальное расстояние до центра: ')


@logger.catch()
@dp.message_handler(state=HotelStatus.min_distance)
async def max_distance_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода максимальной дистанции до центра
    :param message:ответ пользователя по максимальному расстоянию до центра
    :param state: HotelStatus.min_distance
    """
    logger.info('Запущен max_distance_handler')
    await parametrs('max_distance', message, state)
    await message.answer('Количество отелей к выводу в результате (не более 25): ')


@logger.catch()
@dp.message_handler(state=HotelStatus.hotels_count)
async def hotels_count_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода количества отелей к выводу в результате
    :param message: кол-во отелей
    :param state: HotelStatus.hotels_count
    """
    logger.info('Запущен hotels_count_handler.')
    try:
        if 0 < int(message.text) <= 25:
            async with state.proxy() as state_date:
                state_date['hotels_count'] = message.text
            logger.debug(f'Установлено {HotelStatus.hotels_count}  state_date[hotel_count] = {message.text}')
            await HotelStatus.next()
            await message.answer('Показывать фотографии отелей?', reply_markup=answer.yes_no)
    except ValueError:
        await message.answer('Ошибка ввода. Можно вывести от 1-25 отелей включительно.')
        logger.exception('Поймано исключение - не корректный ввод количества отелей (от 1 -25 включительно).')


@logger.catch()
@dp.message_handler(state=HotelStatus.get_photo)
async def get_photo_handler(message: Message, state: FSMContext) -> None:
    """Обработка ввода ответа на запрос вывода фотографий отеля.
    :param message: Ответ на вопрос показывать ли фотографии отелей;
    :param state: HotelStatus.get_photo."""
    logger.info('Запущен get_photo_handler')
    get_photo_str = message.text.strip().lower()
    async with state.proxy() as state_data:
        state_data['get_photo'] = get_photo_str
        logger.info(f'Добавлен параметр запроса get_photo: {HotelStatus.get_photo}'
                    f'state_data["get_photo"]= {get_photo_str}')
    if get_photo_str == 'да':
        await HotelStatus.next()
        await message.answer('Сколько фотографий отеля показать (не более 5)?', reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Вывод без фотографий отелей.')
        await get_requests(message, state)


@logger.catch()
@dp.message_handler(state=HotelStatus.photo_count)
async def photo_count_handler(message: Message, state: FSMContext) -> None:
    """Обработка вывода количества фотографий отелей
    :param message: кол-во фотографий
    :param  state состояние HotelStatus.photo_count
    """
    logger.info('Запущен photo_count_handler.')
    photo_count_str = message.text.strip().lower()
    try:
        photo_count = int(photo_count_str)
        if (photo_count >= 1) and (photo_count <= 5):
            async with state.proxy() as state_data:
                state_data['photo_count'] = photo_count
            logger.debug(f'Добавлен параметр photo_count {HotelStatus.photo_count} '
                         f'state_data["photo_count"]= {photo_count}')
            await get_requests(message, state)
    except ValueError:
        logger.debug('Поймано исключение - недопустимый ввод значения количества фотографий.')
        await message.answer('Допустим ввод только целых чисел от 1 до 5 включительно.')


@logger.catch()
async def get_requests(message: Message, state: FSMContext) -> None:
    """ Обработка отправки запроса пользователя по отелю и обработка ответа API.
    :param message: итоговый метод обработки и получения списка отелей со всей информацией по запросу;
    :param state передача состояний. """
    async with state.proxy() as data:
        text = f'Команда: {data["order"]}' \
               f'\nГород: {data["city_name"]}' \
               f'\nКоличество отелей: {data["hotels_count"]}'\
                f'\nПоказывать фотографию: {data["get_photo"]}'\
                f'\nДата заезда: {data["check_in"]}'\
                f'\nДата выезда: {data["check_out"]}'\

        if data.get('get_photo') == 'да':
            text += f'\nКоличество-фотографий: {data["photo_count"]}'\

        if data.get("order") == '/bestdeal':
            text += f'\nМинимальная цена: {data["min_price"]}'\
                f'\nМаксимальная цена: {data["max_price"]}'\
                f'\nМинимальная дистанция от центра: {data["min_distance"]}'\
                f'\nМаксимальная дистанция от центра: {data["max_distance"]}'

    await bot.send_message(message.chat.id, text)
    await message.answer('Ваш запрос принят, выполняю поиск отелей..')
    await hotels.get_hotels(message, state)

    await state.finish()
