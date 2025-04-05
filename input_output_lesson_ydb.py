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
def find_by_lecturer_name(student: R.Student, lecturer: R.Lecturer, is_group_lesson: bool, pool: ydb.QuerySessionPool)-> list:
    """Вход - объекты класса Student, Lecturer
       """
    conn, cur = R.connect()
    if is_group_lesson:
        cur.execute("select * from group_lesson where id_lecturer = %s and id_group_lesson in ("
                    "select id from GroupLessonGroup where id_group = %s)", lecturer.ID, student.id_group)
    else:
        cur.execute("select * from personal_lesson as p_l where p_l.ID in "
                    "(select p_l_s.ID from personal_lesson_student as p_l_s where p_l_s.id_student = %s);", student.ID)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def find_by_lesson_name(lesson_name: str, student: R.Student, is_group_lesson: bool)-> list:
    """Вход - название предмета и объект класса Studen
    """
    conn, cur = R.connect()
    if is_group_lesson:
        cur.execute("select * from group_lesson where name = %s and id_group_lesson in ("
                    "select id from GroupLessonGroup where id_group = %s)", lesson_name, student.id_group)
    else:
        cur.execute("select * from personal_lesson as p_l where p_l.ID in "
                    "(select p_l_s.ID from personal_lesson_student as p_l_s where p_l_s.id_student = %s) and p_l.name = %s"
                    ,student.ID, lesson_name)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def find_by_date(lesson_date: str, student: R.Student, is_group_lesson: bool)-> list:
    """Вход - дату и объект класса Student
    """
    conn, cur = R.connect()
    if is_group_lesson:
        cur.execute("select * from group_lesson where lesson_date = %s and id_group_lesson in ("
                    "select id from GroupLessonGroup where id_group = %s);", lesson_date, student.id_group)
    else:
        cur.execute("select * from personal_lesson as p_l where p_l.ID in "
                    "(select p_l_s.ID from personal_lesson_student as p_l_s where p_l_s.id_student = %s) and p_l.lesson_date = %s"
                    , student.ID, lesson_date)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res




def find_by_week_day(week_day: str, student: R.Student, is_group_lesson: bool)-> list:
    """Вход - день недели, объект класса Student.
    """
    conn, cur = R.connect()
    if is_group_lesson:
        cur.execute("select * from group_lesson where week_day = %s and id_group_lesson in ("
                    "select id from GroupLessonGroup where id_group = %s);", week_day, student.id_group)
    else:
        cur.execute("select * from personal_lesson as p_l where p_l.ID in "
                    "(select p_l_s.ID from personal_lesson_student as p_l_s where p_l_s.id_student = %s) and p_l.week_day = %s"
                    , student.ID, week_day)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

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
            DECLARE $week_day AS Utf8;
            DECLARE $is_upper AS Bool;
            DECLARE $lesson_date AS Date;
            DECLARE ${unique_elem} AS Int64;

            INSERT INTO {table}(name, type, building, auditorium, id_lecturer, time, week_day, is_upper, lesson_date, {unique_elem})
            VALUES ($name, $type, $building, $auditorium, $id_lecturer, $time, $week_day, $is_upper, $lesson_date, ${unique_elem});
        """,
        {
            '$name': lesson.name,
            '$type': lesson.type_l,
            '$building': lesson.building,
            '$auditorium': lesson.auditorium,
            '$id_lecturer': (lesson.id_lecturer, ydb.PrimitiveType.Int64),
            '$time': lesson.time,
            '$week_day': lesson.week_day,
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



def insert_lesson(user_data: list, lesson_data: list, is_student: bool, is_group_lesson: bool, pool: ydb.QuerySessionPool) -> None:
    """Функция вносит информацию о паре в БД"""
    if is_student:
        student = Student(*user_data)
        if is_group_lesson:
            # Логика для групповых занятий
            lesson = GroupLesson(*lesson_data)
            insert_lesson_data(pool, lesson, student.id_group)
            id_group_lesson = select_id_lesson(pool, lesson, lesson.id_group)
            insert_help_tables_data(pool, id_group_lesson, student.id_group, is_group_lesson)
        else:
            # Логика для персональных занятий - ИСПРАВЛЕННАЯ ВЕРСИЯ
            lesson = PersonalLesson(*lesson_data)
            id_student = select_id_student(pool, student)
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
            insert_lesson_data(pool, lesson, lesson.id_group)
            id_group_lesson = select_id_lesson(pool, lesson, lesson.id_group)
            insert_help_tables_data(pool, id_group_lesson, lesson.id_group, is_group_lesson)
        else:
            lesson = PersonalLesson(*lesson_data)
            id_lecturer = select_id_lecturer(pool, lecturer)
            lesson.id_lecturer = id_lecturer
            insert_lesson_data(pool, lesson, -1) #-1 означает, что это пара отдельно для преподавателя