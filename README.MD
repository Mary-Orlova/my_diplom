#Поиск отелей в telegram 


Telegram-бот для анализа сайта Hotels.com и поиска подходящих пользователю отелей: https://t.me/journey_hotels_bot



#§Требования 

Автоматически можно установить все необходимые зависимости по клику на предложение от PyCharm или выполнив команду в терминале: pip install -r requirements.txt

⚐ Aiogram==2.22.1

⚐ Python-dotenv==0.20.0

⚐ requests==2.28.1

⚐ loguru==0.6.0


#Логирование

Используется библиотека loguru, уровень логов задается в файле main.py

from loguru import logger
logger.add('debug.log', format='{time} {level} {message}', level='INFO', rotation='1000KB', compression='zip')

Команды бота
✎ /start  - Запуск бота /приветствие по имени.

✎ /hello_world - Команда приветствия, сообщает пользователю о том, что он создан для поиска отелей и рекомендует запустить команду /help.

✎ /help - Команда помощи, знакомит пользователя с командами, которые можно использовать.

✎ /bestdeal - Команда поиска лучших предложений (возможность выбора минимальной/максимальной цены/дистанции).

✎ /highprice - Команда поиска ТОП отелей (дорогие).

✎ /lowprice - Команда поиска ТОП отелей (бюджетные).

✎ /history - Команда вывода истории пользователя по поиску отелей (лимит: последние 10).

✎ /delete_history - Команда удаления истории пользователя (не вынесена в подсказки пользователю, чтобы избежать случайного удаления записей).



#Пример работы с ботом

При нажатии на синюю кнопку появляются подсказки по командам , их так же можно вызвать при введении в окно сообщения «/»
￼
![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.29.47.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.29.54.png]

Команда поиска лучших предложений (возможность выбора минимальной/максимальной цены/дистанции).

1  Введите команду /bestdeal . Бот запросит город для поиска отеля (регистр не важен, следует использовать английский при выборе города).
Если будет недопустимый символ/цифры в название города - бот запрос повторно город для поиска.

2 Введите город.
При получении названия города бот предоставит клавиатуру для уточнения выбора. 

3 Уточните локацию из предложенного списка.

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.25.25.png]

4 Выбор даты заезда осуществляется по календарю - минимальная дата сегодняшний день.

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.25.32.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.25.45.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.25.59.png]

5 Аналогично выводится календарь и для даты отъезда (если дата отъезда проставлена раньше, чем дата заезда - они меняются местами).

6 Запрос от бота минимальной цены за отель

7 Запрос от бота максимальной цены за отель

8 Запрос от бота минимальной дистанции от центра до отеля

9 Запрос от бота максимальной дистанции от центра до отеля 

10 Запрос от бота по количеству отелей для вывода

11 Запрос от бота необходимости вывода фотографий отелей (максимум 25)

При положительном ответе бот уточнит количество фотографий (максимум 5)

Проверка на корректность ввода проходит сразу при получении ответа от пользователя (минимальной/максимальной цены/дистанции/количества отелей/ввод фотографий и при положительном ответе - количества фотографий).

_Если введен не корректный ответ на вопрос о выводе фотографий - засчитывается как вывод без фотографий отеля._

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.26.51.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.27.08.png]

12 После собранных запросов пользователя в чат направляются полученные параметры и уведомление о начале поиска.

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.27.27.png]

13 В случае успешного поиска сообщается кол-во подходящий найденных отелей и публикуется запрошенная информация.

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.28.56.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.29.03.png]

#Команда поиска ТОП отелей (дорогие).

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.32.08.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.32.20.png]

#Команда поиска ТОП отелей (бюджетные).
￼
![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.31.11.png]

![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.31.17.png]

#Запись в БД осуществляется после получения всех данных в методе  generate_hotels_descriptions (information_API -> hotels)
￼
![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2015.28.40.png]

#Команда вывода истории пользователя по поиску отелей (лимит: последние 10).

При вызове /history - обращение к database
￼
![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.29.26.png]

#Команда удаления истории пользователя (не вынесена в подсказки пользователю, чтобы избежать случайного удаления записей).

По команде /delete_history удаляются строки из БД по id-пользователя.
Если строки отсутствуют - выводится соответствующее сообщение.

￼![https://gitlab.skillbox.ru/mariia_orlova/python_basic_diploma/-/blob/bot_telegram/img/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-11-07%20%D0%B2%2014.30.20.png]

