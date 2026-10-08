-- ==========================================
-- Учебные группы
-- ==========================================

INSERT INTO groups (name, course)
VALUES
    ('ИБ222', 4),
    ('ИВТ232', 4),
    ('ПМ241', 3),
    ('ИТСС215', 3)
ON CONFLICT (name) DO NOTHING;


-- ==========================================
-- Преподаватели
-- ==========================================

INSERT INTO teachers
    (first_name, middle_name, last_name, email)
VALUES
    ('Александр', 'Викторович', 'Иванов', 'aivanov@hse.ru'),
    ('Елена', 'Сергеевна', 'Петрова', 'epetrova@hse.ru'),
    ('Сергей', 'Александрович', 'Сидоров', 'ssidorov@hse.ru'),
    ('Мария', 'Андреевна', 'Кузнецова', 'mkuznetsova@hse.ru')
ON CONFLICT (email) DO NOTHING;


-- ==========================================
-- Студенты
-- ==========================================

INSERT INTO students
    (first_name, middle_name, last_name, email, group_id)
VALUES
    (
        'Ольга',
        'Сергеевна',
        'Смирнова',
        'ossmirnova@hse.ru',
        (SELECT id FROM groups WHERE name = 'ИБ222')
    ),
    (
        'Иван',
        'Александрович',
        'Петров',
        'iappetrov@hse.ru',
        (SELECT id FROM groups WHERE name = 'ИБ222')
    ),
    (
        'Анна',
        'Дмитриевна',
        'Соколова',
        'adsokolova@hse.ru',
        (SELECT id FROM groups WHERE name = 'ИВТ232')
    ),
    (
        'Дмитрий',
        'Алексеевич',
        'Кузнецов',
        'dakuznetsov@hse.ru',
        (SELECT id FROM groups WHERE name = 'ПМ241')
    )
ON CONFLICT (email) DO NOTHING;


-- ==========================================
-- Предметы
-- ==========================================

INSERT INTO subjects (name, teacher_id)
VALUES
    (
        'Базы данных',
        (SELECT id FROM teachers WHERE email = 'aivanov@hse.ru')
    ),
    (
        'Программирование',
        (SELECT id FROM teachers WHERE email = 'epetrova@hse.ru')
    ),
    (
        'Компьютерные сети',
        (SELECT id FROM teachers WHERE email = 'ssidorov@hse.ru')
    ),
    (
        'Математический анализ',
        (SELECT id FROM teachers WHERE email = 'mkuznetsova@hse.ru')
    )
ON CONFLICT (name) DO NOTHING;


-- ==========================================
-- Записи студентов на предметы
-- ==========================================

INSERT INTO enrollments (student_id, subject_id, grade)
VALUES
    (
        (SELECT id FROM students WHERE email = 'ossmirnova@hse.ru'),
        (SELECT id FROM subjects WHERE name = 'Базы данных'),
        5
    ),
    (
        (SELECT id FROM students WHERE email = 'ossmirnova@hse.ru'),
        (SELECT id FROM subjects WHERE name = 'Программирование'),
        4
    ),
    (
        (SELECT id FROM students WHERE email = 'iappetrov@hse.ru'),
        (SELECT id FROM subjects WHERE name = 'Базы данных'),
        5
    ),
    (
        (SELECT id FROM students WHERE email = 'adsokolova@hse.ru'),
        (SELECT id FROM subjects WHERE name = 'Компьютерные сети'),
        4
    ),
    (
        (SELECT id FROM students WHERE email = 'dakuznetsov@hse.ru'),
        (SELECT id FROM subjects WHERE name = 'Математический анализ'),
        5
    )
ON CONFLICT (student_id, subject_id) DO NOTHING;