import getpass
import json
import os

from database import (
    connect_to_database,
    setup_logging
)

from operations import (
    select_all,
    select_by_one_filter,
    select_by_multiple_filters,
    update_one,
    update_many,
    insert_one,
    insert_many,
    insert_student_with_enrollments
)


def load_config():
    with open(
        "app/config.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def choose_table(config):
    tables = list(config["tables"].keys())

    print("\nДоступные таблицы:")

    for index, table in enumerate(
        tables,
        start=1
    ):
        print(f"{index}. {table}")

    try:
        choice = int(
            input("Выберите таблицу: ")
        )

        if 1 <= choice <= len(tables):
            return tables[choice - 1]

    except ValueError:
        pass

    print("Некорректный выбор.")
    return None


def choose_column(config, table):
    columns = config["tables"][table]["columns"]

    print("\nДоступные колонки:")

    for index, column in enumerate(
        columns,
        start=1
    ):
        print(f"{index}. {column}")

    try:
        choice = int(
            input("Выберите колонку: ")
        )

        if 1 <= choice <= len(columns):
            return columns[choice - 1]

    except ValueError:
        pass

    print("Некорректный выбор.")
    return None


def get_value():
    return input("Введите значение: ")


def select_menu(connection, config):
    while True:
        print("\n=== ПРОСМОТР ДАННЫХ ===")
        print("1. Вывести всю таблицу")
        print("2. Фильтр по одной колонке")
        print("3. Фильтр по нескольким колонкам")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == "0":
            return

        table = choose_table(config)

        if not table:
            continue

        if choice == "1":

            select_all(
                connection,
                config,
                table
            )

        elif choice == "2":

            column = choose_column(
                config,
                table
            )

            if not column:
                continue

            value = get_value()

            select_by_one_filter(
                connection,
                config,
                table,
                column,
                value
            )

        elif choice == "3":

            filters = {}

            print(
                "\nВведите условия фильтрации."
            )

            while True:
                column = choose_column(
                    config,
                    table
                )

                if not column:
                    break

                value = get_value()

                filters[column] = value

                more = input(
                    "Добавить ещё условие? (y/n): "
                ).lower()

                if more != "y":
                    break

            if filters:
                select_by_multiple_filters(
                    connection,
                    config,
                    table,
                    filters
                )

        else:
            print("Некорректный выбор.")


def update_menu(connection, config):
    while True:
        print("\n=== ИЗМЕНЕНИЕ ДАННЫХ ===")
        print("1. Изменить одну запись")
        print("2. Изменить несколько записей")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == "0":
            return

        table = choose_table(config)

        if not table:
            continue

        if choice == "1":

            try:
                record_id = int(
                    input("Введите ID записи: ")
                )
            except ValueError:
                print("ID должен быть числом.")
                continue

            editable = (
                config["tables"][table]
                ["editable_columns"]
            )

            print("\nДоступные поля для изменения:")

            for index, column in enumerate(
                editable,
                start=1
            ):
                print(
                    f"{index}. {column}"
                )

            updates = {}

            while True:
                try:
                    number = int(
                        input(
                            "Выберите поле "
                            "(0 — закончить): "
                        )
                    )
                except ValueError:
                    print(
                        "Введите номер."
                    )
                    continue

                if number == 0:
                    break

                if not (
                    1 <= number <= len(editable)
                ):
                    print(
                        "Некорректный номер."
                    )
                    continue

                column = editable[
                    number - 1
                ]

                value = input(
                    f"Новое значение для "
                    f"{column}: "
                )

                updates[column] = value

            if updates:
                update_one(
                    connection,
                    config,
                    table,
                    record_id,
                    updates
                )

        elif choice == "2":

            filter_column = choose_column(
                config,
                table
            )

            if not filter_column:
                continue

            raw_values = input(
                "Введите значения через запятую: "
            )

            filter_values = [
                value.strip()
                for value in raw_values.split(",")
                if value.strip()
            ]

            editable = (
                config["tables"][table]
                ["editable_columns"]
            )

            print("\nКолонка для изменения:")

            for index, column in enumerate(
                editable,
                start=1
            ):
                print(
                    f"{index}. {column}"
                )

            try:
                number = int(
                    input("Выберите колонку: ")
                )

                if not (
                    1 <= number <= len(editable)
                ):
                    print(
                        "Некорректный номер."
                    )
                    continue

            except ValueError:
                print(
                    "Введите номер."
                )
                continue

            update_column = editable[
                number - 1
            ]

            new_value = input(
                "Введите новое значение: "
            )

            update_many(
                connection,
                config,
                table,
                filter_column,
                filter_values,
                update_column,
                new_value
            )

        else:
            print("Некорректный выбор.")


def insert_menu(connection, config):
    while True:
        print("\n=== ДОБАВЛЕНИЕ ДАННЫХ ===")
        print("1. Добавить одну запись")
        print("2. Добавить несколько записей")
        print(
            "3. Добавить студента "
            "с предметами"
        )
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == "0":
            return

        if choice == "3":
            insert_student_menu(connection)
            continue

        table = choose_table(config)

        if not table:
            continue

        insert_columns = (
            config["tables"][table]
            ["insert_columns"]
        )

        if choice == "1":

            values = {}

            print(
                "\nВведите значения полей."
            )

            for column in insert_columns:
                values[column] = input(
                    f"{column}: "
                )

            insert_one(
                connection,
                config,
                table,
                values
            )

        elif choice == "2":

            print(
                "\nКолонки для вставки:"
            )

            for index, column in enumerate(
                insert_columns,
                start=1
            ):
                print(
                    f"{index}. {column}"
                )

            raw_columns = input(
                "Введите номера колонок "
                "через запятую: "
            )

            try:
                numbers = [
                    int(number.strip())
                    for number in
                    raw_columns.split(",")
                ]
            except ValueError:
                print(
                    "Некорректный ввод."
                )
                continue

            columns = []

            for number in numbers:
                if not (
                    1 <= number <=
                    len(insert_columns)
                ):
                    print(
                        "Некорректный номер."
                    )
                    columns = []
                    break

                columns.append(
                    insert_columns[number - 1]
                )

            if not columns:
                continue

            try:
                count = int(
                    input(
                        "Сколько записей добавить? "
                    )
                )
            except ValueError:
                print(
                    "Количество должно быть числом."
                )
                continue

            rows = []

            for row_number in range(
                count
            ):
                print(
                    f"\nЗапись №{row_number + 1}"
                )

                row = []

                for column in columns:
                    row.append(
                        input(
                            f"{column}: "
                        )
                    )

                rows.append(row)

            insert_many(
                connection,
                config,
                table,
                columns,
                rows
            )

        else:
            print("Некорректный выбор.")


def insert_student_menu(connection):
    print(
        "\n=== ДОБАВЛЕНИЕ СТУДЕНТА "
        "С ПРЕДМЕТАМИ ==="
    )

    first_name = input(
        "Имя: "
    )

    middle_name = input(
        "Отчество: "
    )

    last_name = input(
        "Фамилия: "
    )

    email = input(
        "Email: "
    )

    try:
        group_id = int(
            input(
                "ID группы: "
            )
        )
    except ValueError:
        print(
            "ID группы должен быть числом."
        )
        return

    enrollments = []

    print(
        "\nДобавление предметов."
    )

    while True:
        try:
            subject_id = int(
                input(
                    "ID предмета "
                    "(0 — закончить): "
                )
            )
        except ValueError:
            print(
                "ID предмета должен быть числом."
            )
            continue

        if subject_id == 0:
            break

        try:
            grade = int(
                input(
                    "Оценка (2-5): "
                )
            )
        except ValueError:
            print(
                "Оценка должна быть числом."
            )
            continue

        if not 2 <= grade <= 5:
            print(
                "Оценка должна быть от 2 до 5."
            )
            continue

        enrollments.append(
            (
                subject_id,
                grade
            )
        )

        more = input(
            "Добавить ещё предмет? (y/n): "
        ).lower()

        if more != "y":
            break

    insert_student_with_enrollments(
        connection,
        first_name,
        middle_name,
        last_name,
        email,
        group_id,
        enrollments
    )


def main():
    setup_logging()

    config = load_config()

    host = os.getenv(
        "DB_HOST",
        "localhost"
    )

    port = os.getenv(
        "DB_PORT",
        "5432"
    )

    database = os.getenv(
        "DB_NAME",
        "university"
    )

    print("=== Университетская база данных ===")
    print()
    print(
        "Введите данные пользователя "
        "PostgreSQL."
    )

    user = input(
        "Пользователь: "
    )

    password = getpass.getpass(
        "Пароль: "
    )

    connection = connect_to_database(
        host,
        port,
        database,
        user,
        password
    )

    if connection is None:
        return

    try:
        while True:
            print("\n==============================")
            print("        ГЛАВНОЕ МЕНЮ")
            print("==============================")
            print("1. Просмотр данных")
            print("2. Изменение данных")
            print("3. Добавление данных")
            print("0. Выход")

            choice = input(
                "Выберите действие: "
            )

            if choice == "1":
                select_menu(
                    connection,
                    config
                )

            elif choice == "2":
                update_menu(
                    connection,
                    config
                )

            elif choice == "3":
                insert_menu(
                    connection,
                    config
                )

            elif choice == "0":
                print(
                    "Работа программы завершена."
                )
                break

            else:
                print(
                    "Некорректный выбор."
                )

    finally:
        connection.close()

        print(
            "Соединение с базой данных закрыто."
        )


if __name__ == "__main__":
    main()