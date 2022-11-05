import sqlite3
from loguru import logger
from typing import Tuple, List


@logger.catch()
def create_table() -> None:
    """ Подключается к базе и создаёт таблицы city_id и history если их не существует. """
    try:
        with sqlite3.connect("hotels.db") as connect:
            cursor = connect.cursor()
            logger.info('Подключен к SQLite.')
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            user_id INT NOT NULL,
                            date TEXT NOT NULL,
                            command TEXT NOT NULL, 
                            city TEXT NOT NULL,
                            hotels TEXT NOT NULL)""")
            connect.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if connect:
            connect.close()
            logger.info('Соединение с SQLite закрыто')


@logger.catch()
def add_in_db(user_info: Tuple, hotels: List[Tuple]) -> None:
    """ Запись в базу данных.
    :param user_info: информация пользователя;
    :param hotels: отели. """
    total_hotels = ''
    for i in hotels:
        hotel = ''
        hotel += str(i) + '%'
        total_hotels += hotel + '\t\t'
    user_info = list(user_info)
    user_info.append(total_hotels)

    create_table()
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""INSERT INTO users (user_id, date, command, city, hotels) VALUES(?, ?, ?, ?, ?)""", user_info)
        connect.commit()
    logger.info('Таблица БД обновлена.')


@logger.catch()
def show_history(user_id: int, limit: str) -> List:
    """ Функция вывода истории пользователя из БД.
    :param user_id: id пользователя;
    :param limit: последние 10;
    возвращает: историю пользователя. """
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        result = """SELECT date, command, city, hotels FROM users WHERE user_id = ? ORDER BY date DESC LIMIT = ?"""
        information = cursor.execute(result, (user_id, limit,))
    return information.fetchall()


@logger.catch()
def delete_history(id_string):
    """ Удаление истории пользователя.
    :param id_string: id пользователя. """
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""DELETE from users WHERE id = ?""", (id_string,))
    logger.info('Пользователь удалил историю.')
