import logging

from psycopg2 import sql


def get_table_columns(config, table):
    return config["tables"][table]["columns"]


def print_rows(rows):
    if not rows:
        print("Записей не найдено.")
        return

    for row in rows:
        print(row)


def select_all(connection, config, table):
    """
    6.1.1 Просмотр таблицы без фильтра.
    """

    columns = get_table_columns(config, table)

    query = sql.SQL(
        "SELECT {} FROM {}"
    ).format(
        sql.SQL(", ").join(
            map(sql.Identifier, columns)
        ),
        sql.Identifier(table)
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        print_rows(rows)

        logging.info(
            "Выполнен SELECT всех записей из таблицы %s.",
            table
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка SELECT из таблицы %s.",
            table
        )

        print(
            "Не удалось получить данные."
        )

        return False


def select_by_one_filter(
    connection,
    config,
    table,
    column,
    value
):
    """
    6.1.2 Фильтрация по одной колонке.
    """

    allowed_columns = get_table_columns(
        config,
        table
    )

    if column not in allowed_columns:
        print(
            "Такая колонка недоступна для поиска."
        )
        return False

    query = sql.SQL(
        "SELECT {} FROM {} WHERE {} = %s"
    ).format(
        sql.SQL(", ").join(
            map(sql.Identifier, allowed_columns)
        ),
        sql.Identifier(table),
        sql.Identifier(column)
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (value,)
            )

            rows = cursor.fetchall()

        print_rows(rows)

        logging.info(
            "Выполнен поиск в %s по колонке %s.",
            table,
            column
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка поиска в таблице %s.",
            table
        )

        print(
            "Не удалось выполнить поиск."
        )

        return False


def select_by_multiple_filters(
    connection,
    config,
    table,
    filters
):
    """
    6.1.3 Фильтрация по нескольким условиям.
    """

    allowed_columns = get_table_columns(
        config,
        table
    )

    for column in filters:
        if column not in allowed_columns:
            print(
                f"Колонка {column} недоступна."
            )
            return False

    conditions = []
    values = []

    for column, value in filters.items():
        conditions.append(
            sql.SQL("{} = %s").format(
                sql.Identifier(column)
            )
        )

        values.append(value)

    query = sql.SQL(
        "SELECT {} FROM {} WHERE {}"
    ).format(
        sql.SQL(", ").join(
            map(sql.Identifier, allowed_columns)
        ),
        sql.Identifier(table),
        sql.SQL(" AND ").join(conditions)
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                values
            )

            rows = cursor.fetchall()

        print_rows(rows)

        logging.info(
            "Выполнен поиск по нескольким условиям "
            "в таблице %s.",
            table
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка многопараметрического поиска."
        )

        print(
            "Не удалось выполнить поиск."
        )

        return False


def update_one(
    connection,
    config,
    table,
    record_id,
    updates
):
    """
    6.2.1 Изменение одной записи.
    """

    editable_columns = (
        config["tables"][table]["editable_columns"]
    )

    for column in updates:
        if column not in editable_columns:
            print(
                f"Колонка {column} недоступна для изменения."
            )
            return False

    if not updates:
        print("Нет данных для изменения.")
        return False

    set_parts = []
    values = []

    for column, value in updates.items():
        set_parts.append(
            sql.SQL("{} = %s").format(
                sql.Identifier(column)
            )
        )

        values.append(value)

    values.append(record_id)

    query = sql.SQL(
        "UPDATE {} SET {} WHERE id = %s"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(set_parts)
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                values
            )

            if cursor.rowcount == 0:
                connection.rollback()

                print(
                    "Запись с таким ID не найдена."
                )

                return False

        connection.commit()

        logging.info(
            "Изменена запись ID=%s в таблице %s.",
            record_id,
            table
        )

        print(
            "Запись успешно изменена."
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка изменения записи."
        )

        print(
            "Не удалось изменить запись."
        )

        return False


def update_many(
    connection,
    config,
    table,
    filter_column,
    filter_values,
    update_column,
    new_value
):
    """
    6.2.2 Массовое изменение записей.
    """

    allowed_columns = get_table_columns(
        config,
        table
    )

    editable_columns = (
        config["tables"][table]["editable_columns"]
    )

    if filter_column not in allowed_columns:
        print(
            "Недопустимая колонка для фильтрации."
        )
        return False

    if update_column not in editable_columns:
        print(
            "Недопустимая колонка для изменения."
        )
        return False

    if not filter_values:
        print(
            "Не указаны значения для фильтра."
        )
        return False

    placeholders = sql.SQL(", ").join(
        [sql.Placeholder()] * len(filter_values)
    )

    query = sql.SQL(
        "UPDATE {} SET {} = %s "
        "WHERE {} IN ({})"
    ).format(
        sql.Identifier(table),
        sql.Identifier(update_column),
        sql.Identifier(filter_column),
        placeholders
    )

    params = [new_value] + filter_values

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                params
            )

            affected = cursor.rowcount

        connection.commit()

        logging.info(
            "Массово изменено записей: %s.",
            affected
        )

        print(
            f"Изменено записей: {affected}"
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка массового изменения."
        )

        print(
            "Не удалось изменить записи."
        )

        return False


def insert_one(
    connection,
    config,
    table,
    values
):
    """
    6.3.1 Добавление одной записи.
    """

    allowed_columns = (
        config["tables"][table]["insert_columns"]
    )

    for column in values:
        if column not in allowed_columns:
            print(
                f"Колонка {column} недоступна для вставки."
            )
            return False

    if not values:
        print("Нет данных для вставки.")
        return False

    columns = list(values.keys())
    data = list(values.values())

    query = sql.SQL(
        "INSERT INTO {} ({}) "
        "VALUES ({}) RETURNING id"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(
            map(sql.Identifier, columns)
        ),
        sql.SQL(", ").join(
            [sql.Placeholder()] * len(columns)
        )
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                data
            )

            new_id = cursor.fetchone()[0]

        connection.commit()

        logging.info(
            "Добавлена запись ID=%s в таблицу %s.",
            new_id,
            table
        )

        print(
            f"Запись успешно добавлена. ID = {new_id}"
        )

        return new_id

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка добавления записи."
        )

        print(
            "Не удалось добавить запись."
        )

        return None


def insert_many(
    connection,
    config,
    table,
    columns,
    rows
):
    """
    6.4.1 Добавление нескольких записей.
    """

    allowed_columns = (
        config["tables"][table]["insert_columns"]
    )

    for column in columns:
        if column not in allowed_columns:
            print(
                f"Колонка {column} недоступна для вставки."
            )
            return False

    if not rows:
        print("Нет данных для вставки.")
        return False

    placeholders = sql.SQL(", ").join(
        [sql.Placeholder()] * len(columns)
    )

    query = sql.SQL(
        "INSERT INTO {} ({}) VALUES ({})"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(
            map(sql.Identifier, columns)
        ),
        placeholders
    )

    try:
        with connection.cursor() as cursor:
            for row in rows:
                cursor.execute(
                    query,
                    row
                )

        connection.commit()

        logging.info(
            "Добавлено строк: %s в таблицу %s.",
            len(rows),
            table
        )

        print(
            f"Добавлено строк: {len(rows)}"
        )

        return True

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка массовой вставки."
        )

        print(
            "Не удалось добавить строки."
        )

        return False


def insert_student_with_enrollments(
    connection,
    first_name,
    middle_name,
    last_name,
    email,
    group_id,
    enrollments
):
    """
    6.3.2 / 6.4.2
    Добавление студента и связанных записей
    в enrollments.
    """

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO students
                    (
                        first_name,
                        middle_name,
                        last_name,
                        email,
                        group_id
                    )
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    first_name,
                    middle_name,
                    last_name,
                    email,
                    group_id
                )
            )

            student_id = cursor.fetchone()[0]

            for subject_id, grade in enrollments:
                cursor.execute(
                    """
                    INSERT INTO enrollments
                        (
                            student_id,
                            subject_id,
                            grade
                        )
                    VALUES
                        (%s, %s, %s)
                    """,
                    (
                        student_id,
                        subject_id,
                        grade
                    )
                )

        connection.commit()

        logging.info(
            "Добавлен студент ID=%s "
            "и связанные записи.",
            student_id
        )

        print(
            "Студент и связанные записи "
            "успешно добавлены."
        )

        print(
            f"ID студента: {student_id}"
        )

        return student_id

    except Exception:
        connection.rollback()

        logging.exception(
            "Ошибка добавления связанных записей."
        )

        print(
            "Не удалось добавить связанные записи."
        )

        return None