from typing import Union
from datetime import datetime

import ydb


class Lesson:
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date):
        # Общие атрибуты для всех уроков
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.is_weekly = is_weekly
        self.is_upper = is_upper
        self.lesson_date = lesson_date


class PersonalLesson(Lesson):
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date,
                 id_student):
        # Вызываем конструктор родительского класса для инициализации общих атрибутов
        super().__init__(name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date)
        # Уникальный атрибут для PersonalLesson
        self.id_student = id_student


class GroupLesson(Lesson):
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date,
                 id_group):
        # Вызываем конструктор родительского класса для инициализации общих атрибутов
        super().__init__(name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date)
        # Уникальный атрибут для GroupLesson
        self.id_group = id_group


class Group:
    def __init__(self, name, edu_year, edu_program, faculty, edu_format, edu_level):
        # print(name, edu_year, edu_program, faculty, edu_format, edu_level)
        self.name = name
        self.edu_year = str(edu_year)
        self.edu_program = edu_program
        self.faculty = faculty
        self.edu_format = edu_format
        self.edu_level = edu_level
        # cur.execute('INSERT INTO "Group" (name, edu_year, edu_program, faculty, edu_format, edu_level) '
        # 'VALUES (%s, %s, %s, %s, %s, %s);', list(vars(self).values())) #??????????
        # cur.execute("""INSERT INTO "Group" (name, edu_year, edu_program, faculty, edu_format, edu_level)
        # VALUES (2, 2, 2, 2, 2, 2);""")


class Student:
    def __init__(self, name, surname, father_name, id_group):
        self.name = name
        self.surname = surname
        self.father_name = father_name
        self.id_group = int(id_group)


class Lecturer:
    def __init__(self, name, surname, father_name):
        self.name = name
        self.surname = surname
        self.father_name = father_name


class PersonalLessonStudent:
    def __init__(self, id_student, id_personal_lesson):
        self.id_student = id_student
        self.id_personal_lesson = id_personal_lesson


class GroupLessonGroup:
    def __init__(self, id_group_lesson, id_group):
        self.id_group_lesson = id_group_lesson
        self.id_group = id_group


class LecturerGroup:
    def __int__(self, id_lecturer, id_group):
        self.id_lecturer = id_lecturer
        self.id_group = id_group

def get_group_records(pool: ydb.QuerySessionPool, group: Group, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $edu_year AS Utf8;

        SELECT {attr} FROM `Group`
        WHERE name = $name AND edu_year = $edu_year;
        """,
        {
            '$name': group.name,
            '$edu_year': group.edu_year,
        },
    )[0].rows

def select_id_group(pool: ydb.QuerySessionPool, group: Group)-> int:
    records = sorted(get_group_records(pool, group, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_group_reg(pool: ydb.QuerySessionPool, group: Group)-> bool:
    records = get_group_records(pool, group, True)
    return len(records) != 0

def get_lesson_records(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    unique_elem = ""
    table = ""
    if isinstance(lesson, GroupLesson):
        unique_elem = 'id_group'
        table = 'GroupLesson'
    if isinstance(lesson, PersonalLesson):
        unique_elem = 'id_student'
        table = 'PersonalLesson'
    return pool.execute_with_retries(
        f"""
            DECLARE ${unique_elem} AS Int64;
            DECLARE $lesson_date AS Date;
            DECLARE $time AS Utf8;

            SELECT {attr} FROM `{table}`
            WHERE {unique_elem} = ${unique_elem} AND lesson_date = $lesson_date AND time = $time;
            """,
        {
            f'${unique_elem}': (id_obj, ydb.PrimitiveType.Int64),
            '$lesson_date': (datetime.strptime(lesson.lesson_date, '%d.%m.%Y').date(), ydb.PrimitiveType.Date),
            '$time': lesson.time
        },
    )[0].rows

def select_id_lesson(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int)-> int:
    records = sorted(get_lesson_records(pool, lesson, id_obj, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_lesson_reg(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int)-> bool:
    records = get_lesson_records(pool, lesson, id_obj, True)
    return len(records) != 0

def get_student_records(pool: ydb.QuerySessionPool, student: Student, is_exist_check:bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int64;

        SELECT {attr} FROM `Student`
        WHERE name = $name AND surname = $surname AND father_name = $father_name AND id_group = $id_group;
        """,
        {
            '$name': student.name,
            '$surname': student.surname,
            '$father_name': student.father_name,
            '$id_group': (student.id_group, ydb.PrimitiveType.Int64),
        },
    )[0].rows

def select_id_student(pool: ydb.QuerySessionPool, student: Student)-> int:
    records = sorted(get_student_records(pool, student, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_student_reg(pool: ydb.QuerySessionPool, student: Student)-> bool:
    records = get_student_records(pool, student, True)
    return len(records) != 0

def get_lecturer_records(pool: ydb.QuerySessionPool, lecturer: Lecturer, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;

        SELECT {attr} FROM `Lecturer`
        WHERE name = $name AND surname = $surname AND father_name = $father_name;
        """,
        {
            '$name': lecturer.name,
            '$surname': lecturer.surname,
            '$father_name': lecturer.father_name,
        },
    )[0].rows

def select_id_lecturer(pool: ydb.QuerySessionPool, lecturer: Lecturer)-> int:
    records = sorted(get_lecturer_records(pool, lecturer, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_lecturer_reg(pool: ydb.QuerySessionPool, lecturer: Lecturer)-> bool:
    records = get_lecturer_records(pool, lecturer, True)
    return len(records) != 0


def connect_lecturer_with_group(pool: ydb.QuerySessionPool, id_group: int, id_lecturer: int):
    res = (pool.execute_with_retries
        (
        """
        DECLARE $id_lecturer AS Int64;
        DECLARE $id_group AS Int64;

        SELECT 1 FROM `LecturerGroup`
        WHERE id_lecturer = $id_lecturer AND id_group = $id_group;
        """,
        {
            "$id_lecturer": (id_lecturer, ydb.PrimitiveType.Int64),
            "$id_group": (id_group, ydb.PrimitiveType.Int64)
        },
    ))
    if len(res[0].rows) == 0:
        pool.execute_with_retries(
            """
            DECLARE $id_lecturer AS Int64;
            DECLARE $id_group AS Int64;

            INSERT INTO LecturerGroup(id_lecturer, id_group)
            VALUES ($id_lecturer, $id_group);
            """,
            {
                "$id_lecturer": (id_lecturer, ydb.PrimitiveType.Int64),
                "$id_group": (id_group, ydb.PrimitiveType.Int64)
            },
        )



def registration_user(user_data: list, pool: ydb.QuerySessionPool, is_student=True, group_data: list= None):
    """Регистрирует пользователя и группу в БД."""
    if is_student:
        group = Group(*group_data)
        student = Student(*user_data)
        # Проверяем, существует ли группа
        if not is_group_reg(pool, group):
            # Если группы нет, добавляем её
            reg_group(pool, group)
            #тут потенциально о
            student.id_group = select_id_group(pool, group)
            # Получаем id новой группы
        if not is_student_reg(pool, student):
            reg_student(pool, student, student.id_group)
        else:
            return -1  #пользователь зарегистрирован
    else:
        lecturer = Lecturer(*user_data)
        if not is_lecturer_reg(pool, lecturer):
            reg_lecturer(pool, lecturer)
        else:
            return -1 #пользователь зарегистрирован


def reg_group(pool: ydb.QuerySessionPool, group: Group) -> None:
    pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $edu_year AS Utf8;
        DECLARE $edu_program AS Utf8;
        DECLARE $faculty AS Utf8;
        DECLARE $edu_format AS Utf8;
        DECLARE $edu_level AS Utf8;

        INSERT INTO `Group` (name, edu_year, edu_program, faculty, edu_format, edu_level)
        VALUES ($name, $edu_year, $edu_program, $faculty, $edu_format, $edu_level);
        """,
        {
            '$name': group.name,
            '$edu_year': group.edu_year,
            '$edu_program': group.edu_program,
            '$faculty': group.faculty,
            '$edu_format': group.edu_format,
            '$edu_level': group.edu_level
        },
    )


def reg_student(pool: ydb.QuerySessionPool, student: Student, id_group: int) -> None:
    pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int64;

        INSERT INTO Student (name, surname, father_name, id_group)
        VALUES ($name, $surname, $father_name, $id_group);
        """,
        {
            '$name': student.name,
            '$surname': student.surname,
            '$father_name': student.father_name,
            '$id_group': (id_group, ydb.PrimitiveType.Int64),

        },
    )


def reg_lecturer(pool: ydb.QuerySessionPool, lecturer: Lecturer) -> None:
    pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;

        INSERT INTO Lecturer (name, surname, father_name)
        VALUES ($name, $surname, $father_name);
        """,
        {
            '$name': lecturer.name,
            '$surname': lecturer.surname,
            '$father_name': lecturer.father_name,
        },
    )

