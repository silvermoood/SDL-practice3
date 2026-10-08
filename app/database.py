import logging
import os
import sys

import psycopg2


def setup_logging():
    """
    Настройка вывода сообщений.
    По умолчанию сообщения идут в stderr.
    Если задан LOG_FILE, сообщения дополнительно
    записываются в файл.
    """

    log_file = os.getenv("LOG_FILE")

    handlers = [
        logging.StreamHandler(sys.stderr)
    ]

    if log_file:
        handlers.append(
            logging.FileHandler(
                log_file,
                encoding="utf-8"
            )
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers
    )


def connect_to_database(
    host,
    port,
    database,
    user,
    password
):
    """
    Подключение к PostgreSQL.
    """

    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password
        )

        logging.info(
            "Подключение к базе данных успешно."
        )

        print(
            "Подключение к базе данных выполнено успешно."
        )

        return connection

    except psycopg2.Error:
        logging.error(
            "Не удалось подключиться к базе данных.",
            exc_info=True
        )

        print(
            "Не удалось подключиться к базе данных."
        )

        print(
            "Проверьте адрес сервера, имя пользователя и пароль."
        )

        return None


def execute_query(
    connection,
    query,
    params=None,
    fetch=False
):
    """
    Универсальное выполнение SQL-запроса.
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)

            result = None

            if fetch:
                result = cursor.fetchall()

            connection.commit()

            logging.info(
                "SQL-запрос выполнен успешно."
            )

            return result

    except psycopg2.Error:
        connection.rollback()

        logging.error(
            "Ошибка выполнения SQL-запроса.",
            exc_info=True
        )

        print(
            "Не удалось выполнить операцию."
        )

        print(
            "Проверьте введённые данные и повторите попытку."
        )

        return None