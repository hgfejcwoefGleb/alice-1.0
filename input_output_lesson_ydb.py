from datetime import datetime
from registration_ydb import *
import registration_ydb as R
#from pythonProject.Registration import *
import ydb
from typing import Union

#Функции для поиска информации
#везде смотрим на ID студента
#Продумать,чтобы пользователь вносил даты списком и они добавлялись в таблицу
#Продумать автоматическое инкрементировани ID!
#продумать получение id_lecturer при получении информации о паре
#при ситуации, когда препод хочет внести индвид. пару, айди студента может быть null
#написать отдельную функцию для вставки, которая бы принимала курсор
#сделать так, чтобы при вводе фамилии препода предлагались зареганные преподы

#возможно путаница с датами и типами данных
def find_lesson(pool: ydb.QuerySessionPool, is_group_lesson: bool, search_attr_name: str, search_attr_val: str,  is_student: bool,
                                            id_group: int, id_lecturer: int, id_student: int
                )-> list[ydb.convert._ResulSet]:
    """Поиск предмета для преподавателя и студента по атрибутам:
        id_lecturer, name, lesson_date
       """
    if is_group_lesson:
        return pool.execute_with_retries(f"""
            DECLARE ${search_attr_name} AS Utf8;
            DECLARE $id_group AS Int64;
            DECLARE $id_lecturer AS Int64
            
            SELECT * FROM GroupLesson
            WHERE {search_attr_name} = ${search_attr_name}""" + (not is_student and search_attr_name != 'id_lecturer') * " AND id_lecturer = $id_lecturer "
                                         + is_student * """AND id IN
            (SELECT id_group_lesson from GroupLessonGroup WHERE id_group = $id_group)
            """, {
            f'${search_attr_name}': search_attr_val,
            '$id_group': id_group,
            '$id_lecturer': id_lecturer
        })[0].rows
    else:
        return pool.execute_with_retries(f"""
            DECLARE ${search_attr_name} AS Utf8;
            DECLARE $id_student AS Int64;
            
            SELECT * FROM PersonalLesson AS PL 
            WHERE PL.id IN 
                        (SELECT PLS.id FROM PersonalLessonStudent as PLS
                        WHERE PLS.id_student = $id_student)
            AND PL.{search_attr_name} = ${search_attr_name} 
            """
        ,
{f'${search_attr_name}': search_attr_val,
           '$id_student':  id_student

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
            DECLARE $is_weekly AS Utf8;
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
            f'${field_2}':(id_obj, ydb.PrimitiveType.Int16),
        },
    )



def insert_lesson(user_data: list, lesson_data: list, is_student: bool, is_group_lesson: bool, pool: ydb.QuerySessionPool, lecturer_data: list[str]) -> None:
    """Функция вносит информацию о паре в БД"""
    if is_student:
        student = Student(*user_data)
        lecturer = Lecturer(*lecturer_data)
        #проверяем есть ли лектор в БД
        if not is_lecturer_reg(pool, lecturer):
            reg_lecturer(pool, lecturer)
        if is_group_lesson:
            # Логика для групповых занятий
            lesson = GroupLesson(*lesson_data)
            if not is_lesson_reg(pool, lesson, student.id_group):
                insert_lesson_data(pool, lesson, student.id_group)
            id_group_lesson = select_id_lesson(pool, lesson, lesson.id_group)
            insert_help_tables_data(pool, id_group_lesson, student.id_group, is_group_lesson)
        else:
            # Логика для персональных занятий - ИСПРАВЛЕННАЯ ВЕРСИЯ
            lesson = PersonalLesson(*lesson_data)
            id_student = select_id_student(pool, student)
            if not is_lesson_reg(pool, lesson, id_student):
                insert_lesson_data(pool, lesson, id_student)
            id_personal_lesson = select_id_lesson(pool, lesson, id_student)
            insert_help_tables_data(pool, id_personal_lesson, id_student, is_group_lesson)
    else:
        # Логика для преподавателей
        lecturer = Lecturer(*user_data)
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
                insert_lesson_data(pool, lesson, -1) #-1 означает, что это пара отдельно для преподавателя
            id_personal_lesson = select_id_lesson(pool, lesson, -1)
            insert_help_tables_data(pool, id_personal_lesson, -1, is_group_lesson)