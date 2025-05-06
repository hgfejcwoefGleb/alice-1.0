from ydb import QuerySessionPool
from obj_queries import *
from registration_ydb import *
import ydb
from typing import Union
from datetime import datetime, timedelta

week_days_dict = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 7
}
# Функции для поиска информации
# везде смотрим на ID студента
# Продумать,чтобы пользователь вносил даты списком и они добавлялись в таблицу
# Продумать автоматическое инкрементировани ID!
# продумать получение id_lecturer при получении информации о паре
# при ситуации, когда препод хочет внести индвид. пару, айди студента может быть null
# написать отдельную функцию для вставки, которая бы принимала курсор
# сделать так, чтобы при вводе фамилии препода предлагались зареганные преподы
#ловить ошибки, когда нет чего-то в БД

def find_lesson_student(pool: QuerySessionPool, is_group_lesson: bool, search_attr_name: str, search_attr_val: str,
                          id_group: int =-1,  id_student: int =-1)-> list:
    """
    Функция, которая ищет пары
    по name, id_lecturer, lesson_date
    :param pool:
    :param is_group_lesson:
    :param search_attr_name:
    :param search_attr_val:
    :param id_group:
    :param id_student:
    :return list:
    Если нужного значения нет, то выводится пустой список
    """
    if search_attr_name == 'today':
        search_attr_name = 'lesson_date'
        search_attr_val = datetime.now().date()
    elif search_attr_name == 'tomorrow':
        search_attr_name = 'lesson_date'
        search_attr_val = (datetime.now() + timedelta(days=1)).date()
    dtype = 'Utf8' if search_attr_name == 'name' else 'Int64' if search_attr_name == 'id_lecturer' else 'Date'
    if is_group_lesson:
        return pool.execute_with_retries(f"""
            DECLARE ${search_attr_name} AS {dtype};
            DECLARE $id_group AS Int64;

            SELECT * FROM GroupLesson
            WHERE {search_attr_name} = ${search_attr_name} AND id IN
            (SELECT id_group_lesson from GroupLessonGroup WHERE id_group = $id_group)
            """, {
                                             f'${search_attr_name}': (search_attr_val, ydb.PrimitiveType.Date
                                             if search_attr_name == 'lesson_date' else ydb.PrimitiveType.Int64 if search_attr_name == 'id_lecturer'
                                             else ydb.PrimitiveType.Utf8),
                                             '$id_group': id_group,
                                         })[0].rows
    else:
        return pool.execute_with_retries(f"""
            DECLARE ${search_attr_name} AS {dtype};
            DECLARE $id_student AS Int64;

            SELECT * FROM PersonalLesson AS PL 
            WHERE PL.id IN 
                        (SELECT PLS.id_personal_lesson FROM PersonalLessonStudent as PLS
                        WHERE PLS.id_student = $id_student)
            AND PL.{search_attr_name} = ${search_attr_name} 
            """
                                         ,
                                         {f'${search_attr_name}': (search_attr_val, ydb.PrimitiveType.Date
                                             if search_attr_name == 'lesson_date' else ydb.PrimitiveType.Int64 if search_attr_name == 'id_lecturer'
                                             else ydb.PrimitiveType.Utf8),
                                          '$id_student': id_student

                                          })[0].rows

def find_by_week_day_lesson_student(pool: ydb.QuerySessionPool, is_group_lesson: bool,
                                    id_group: int, id_student: int, week_day: str)-> list:
    if is_group_lesson:
        return pool.execute_with_retries(f"""
                    DECLARE $lesson_date AS Int64;
                    DECLARE $id_group AS Int64;

                    SELECT * FROM GroupLesson
                    WHERE DateTime::GetDayOfWeek(lesson_date) = $lesson_date AND id IN
                    (SELECT id_group_lesson from GroupLessonGroup WHERE id_group = $id_group)
                    """, {
            f'$lesson_date': week_days_dict[week_day],
            '$id_group': id_group,
        })[0].rows
    elif not is_group_lesson:
        return pool.execute_with_retries(f"""
                    DECLARE $lesson_date AS Int64;
                    DECLARE $id_student AS Int64;

                    SELECT * FROM PersonalLesson AS PL 
                    WHERE PL.id IN 
                                (SELECT PLS.id_personal_lesson FROM PersonalLessonStudent as PLS
                                WHERE PLS.id_student = $id_student)
                    AND (DateTime::GetDayOfWeek(PL.lesson_date)) = $lesson_date 
                    """
                                  ,
                                  {f'$lesson_date': week_days_dict[week_day],
                                   '$id_student': id_student
                                   })[0].rows

def find_lesson_lecturer(pool: QuerySessionPool, table_name: str, search_attr_name: str,
                         search_attr_val: str,
                         id_lecturer: int) -> list:
    """
    Функция, которая ищет пары
    по name, lesson_date
    :param pool:
    :param table_name:
    :param search_attr_name:
    :param search_attr_val:
    :param id_lecturer:
    :return list:
    Если нужного значения нет, то выводится пустой список
    """
    if search_attr_name == 'today':
        search_attr_name = 'lesson_date'
        search_attr_val = datetime.now().date()
    elif search_attr_name == 'tomorrow':
        search_attr_name = 'lesson_date'
        search_attr_val = (datetime.now() + timedelta(days=1)).date()

    dtype = 'Utf8' if search_attr_name == 'name' else 'Date'
    return pool.execute_with_retries(f"""
        DECLARE ${search_attr_name} AS {dtype};
        DECLARE $id_lecturer AS Int64;

        SELECT * FROM {table_name}
        WHERE {search_attr_name} = ${search_attr_name} AND id_lecturer = $id_lecturer
        """, {
        f'${search_attr_name}': (search_attr_val, ydb.PrimitiveType.Date
                                             if search_attr_name == 'lesson_date'
                                             else ydb.PrimitiveType.Utf8),
        '$id_lecturer': id_lecturer,
    })[0].rows

def find_by_week_day_lesson_lecturer(pool: ydb.QuerySessionPool, table_name: str,
                                     week_day: str, id_lecturer: int)-> list:
    return pool.execute_with_retries(f"""
                        DECLARE $lesson_date AS Int64;
                        DECLARE $id_lecturer AS Int64;

                        SELECT * FROM {table_name}
                        WHERE DateTime::GetDayOfWeek(lesson_date) = $lesson_date AND id_lecturer = $id_lecturer
                        """, {
        f'$lesson_date': week_days_dict[week_day],
        '$id_lecturer': id_lecturer,
    })[0].rows

def insert_lesson_data(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_elem: int):
    unique_elem = ""
    table = ""
    if isinstance(lesson, GroupLesson):
        unique_elem = 'id_group'
        table = 'GroupLesson'
    if isinstance(lesson, PersonalLesson):
        unique_elem = 'id_student'
        table = 'PersonalLesson'
    pool.execute_with_retries(
        f"""
            DECLARE $name AS Utf8;
            DECLARE $type AS Utf8;
            DECLARE $building AS Utf8;
            DECLARE $auditorium AS Utf8;
            DECLARE $id_lecturer AS Int64;
            DECLARE $time AS Utf8;
            DECLARE $is_weekly AS Bool;
            DECLARE $is_upper AS Bool;
            DECLARE $lesson_date AS Date;
            DECLARE ${unique_elem} AS Int64;

            INSERT INTO {table}(name, type, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date, {unique_elem})
            VALUES ($name, $type, $building, $auditorium, $id_lecturer, $time, $is_weekly, $is_upper, $lesson_date, ${unique_elem});
        """,
        {
            '$name': lesson.name,
            '$type': lesson.type_l,
            '$building': lesson.building,
            '$auditorium': lesson.auditorium,
            '$id_lecturer': (lesson.id_lecturer, ydb.PrimitiveType.Int64),
            '$time': lesson.time,
            '$is_weekly': lesson.is_weekly,
            '$is_upper': (lesson.is_upper, ydb.PrimitiveType.Bool),
            '$lesson_date': (datetime.strptime(lesson.lesson_date, '%d.%m.%Y').date(), ydb.PrimitiveType.Date),
            f'${unique_elem}': (id_elem, ydb.PrimitiveType.Int64)
        }
    )


def insert_help_tables_data(pool: ydb.QuerySessionPool, id_lesson: int, id_obj: int, is_group_lesson: bool):
    table, field_1, field_2 = 'GroupLessonGroup', 'id_group_lesson', 'id_group'
    if not is_group_lesson:
        table, field_1, field_2 = 'PersonalLessonStudent', 'id_personal_lesson', 'id_student',
    pool.execute_with_retries(
        f"""
        DECLARE ${field_1} AS Int16;
        DECLARE ${field_2} AS Int16;

        INSERT INTO {table}({field_1}, {field_2})
        VALUES (${field_1}, ${field_2});
        """,
        {
            f'${field_1}': (id_lesson, ydb.PrimitiveType.Int16),
            f'${field_2}': (id_obj, ydb.PrimitiveType.Int16),
        },
    )


def insert_lesson(pool: ydb.QuerySessionPool, lesson_data: list, is_student: bool, is_group_lesson: bool,
                  user_data: list, lecturer_data: list[str] = None) -> None:
    """Функция вносит информацию о паре в БД"""
    if is_student:
        id_lecturer = lesson_data[4]
        student = Student(*user_data)
        lecturer = Lecturer(*lecturer_data)
        # проверяем есть ли лектор в БД
        if not is_lecturer_reg(pool, lecturer):
            reg_lecturer(pool, lecturer)
            id_lecturer = select_id_lecturer(pool, lecturer)
        if is_group_lesson:
            # Логика для групповых занятий
            lesson = GroupLesson(*lesson_data)
            lesson.id_lecturer = id_lecturer
            if not is_lesson_reg(pool, lesson, student.id_group):
                insert_lesson_data(pool, lesson, student.id_group)
                id_group_lesson = select_id_lesson(pool, lesson, lesson.id_group)
                insert_help_tables_data(pool, id_group_lesson, student.id_group, is_group_lesson)
        elif not is_group_lesson:
            # Логика для персональных занятий
            lesson = PersonalLesson(*lesson_data)
            lesson.id_lecturer = id_lecturer
            id_student = select_id_student(pool, student)
            if not is_lesson_reg(pool, lesson, id_student):
                insert_lesson_data(pool, lesson, id_student)
            id_personal_lesson = select_id_lesson(pool, lesson, id_student)
            
            insert_help_tables_data(pool, id_personal_lesson, id_student, is_group_lesson)
    else:
        # Логика для преподавателей
        lecturer = Lecturer(*user_data[:3])
        if is_group_lesson:
            lesson = GroupLesson(*lesson_data)
            
            id_lecturer = select_id_lecturer(pool, lecturer)
            lesson.id_lecturer = id_lecturer
            connect_lecturer_with_group(pool, lesson.id_group, id_lecturer)
            if not is_lesson_reg(pool, lesson, lesson.id_group):
                insert_lesson_data(pool, lesson, lesson.id_group)
                id_group_lesson = select_id_lesson(pool, lesson, lesson.id_group)
                insert_help_tables_data(pool, id_group_lesson, lesson.id_group, is_group_lesson)
        else:
            lesson = PersonalLesson(*lesson_data)
            id_lecturer = select_id_lecturer(pool, lecturer)
            lesson.id_lecturer = id_lecturer
            if not is_lesson_reg(pool, lesson, -1):
                insert_lesson_data(pool, lesson, -1)  # -1 означает, что это пара отдельно для преподавателя
            id_personal_lesson = select_id_lesson(pool, lesson, -1)
            insert_help_tables_data(pool, id_personal_lesson, -1, is_group_lesson)


def change_db_data(pool: ydb.QuerySessionPool, user_data_old: str, user_data_new: str):
    """Функция по изменению данных пользователя в БД"""
    student = Student(*list(user_data_old.split()))
    student.id_group = int(student.id_group)
    id_student = select_id_student(pool, student)
    student.id_group = int(student.id_group)
    student = Student(*list(user_data_new.split()))
    student.id_group = int(student.id_group)
    pool.execute_with_retries(
        f"""
        DECLARE $id AS Int64; 
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int64;

        UPSERT INTO Student(id, name, surname, father_name, id_group)
        VALUES ($id, $name, $surname, $father_name, $id_group)
        """,
        {
            '$id': (id_student, ydb.PrimitiveType.Int64),
            '$name': student.name,
            '$surname': student.surname,
            '$father_name': student.father_name,
            '$id_group': (student.id_group, ydb.PrimitiveType.Int64),
        }
    )


