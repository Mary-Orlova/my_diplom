import sqlite3
from loguru import logger
from typing import Tuple, List


@logger.catch()
def create_table() -> None:
    """Подключается к базе и создаёт таблицы city_id и history если их не существует"""
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INT,
                        date TEXT,
                        hotels TEXT)""")


@logger.catch()
def add_in_db(user_info: Tuple, hotels: List[Tuple]) -> None:
    """
    Запись в базу данных
    user_info: информация пользователя
    hotels: отели
    """
    total_hotels = ''
    for i in hotels:
        hotel = ''
        for j in i:
            hotel += str(j) + '%'
        total_hotels += hotel + '\t\t'
    user_info = list(user_info)
    user_info.append(total_hotels)

    create_table()
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("""INSERT INTO user_id, date, command, city, hotels)
        VALUES(?, ?, ?, ?)""", user_info)
    logger.info('Создана таблица БД')


@logger.catch()
def show_history(user_id: int, limit: str) -> List:
    """Функция вывода истории пользователя из БД
    user_id: id пользователя
    возвращает: историю пользователя
    """
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        result = f"""SELECT * FROM (SELECT * FROM users WHERE user_id = ? ORDER BY id ?)"""
        infomation = cursor.execute(result, (user_id, limit))
    return infomation.fetchall()


@logger.catch()
def delete_history(id_string):
    """Удаление истории пользователя
    id_string: id пользователя"""
    with sqlite3.connect("hotels.db") as connect:
        cursor = connect.cursor()
        cursor.execute("DELETE from users WHERE id = ?", (id_string,))
    logger.info('Пользователь удалил историю')
