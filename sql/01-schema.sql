CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    course INTEGER NOT NULL CHECK (course BETWEEN 1 AND 6)
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    group_id INTEGER NOT NULL,

    CONSTRAINT fk_students_group
        FOREIGN KEY (group_id)
        REFERENCES groups(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    teacher_id INTEGER NOT NULL,

    CONSTRAINT fk_subjects_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    grade INTEGER CHECK (grade BETWEEN 2 AND 5),

    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollments_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT unique_student_subject
        UNIQUE (student_id, subject_id)
);