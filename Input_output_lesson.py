from nntplib import GroupInfo

import Registration as R
from pythonProject.Registration import *


#Функции для поиска информации
#везде смотрим на ID студента
#Продумать,чтобы пользователь вносил даты списком и они добавлялись в таблицу
#Продумать автоматическое инкрементировани ID!
#продумать получение id_lecturer при получении информации о паре
#при ситуации, когда препод хочет внести индвид. пару, айди студента может быть null
#написать отдельную функцию для вставки, которая бы принимала курсор
def find_by_lecturer_name(student: R.Student, lecturer: R.Lecturer, is_group_lesson: bool)-> list:
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

def find_by_date()-> list:
    """Вход - дату и объект класса Student
    """

    pass

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


def insert_lesson(user_data: list, lesson_data: list, group_data: list, is_student: bool, is_group_lesson: bool)-> None:
    """Функция вносит информацию о паре в БД"""
    conn, cur = R.connect()
    if is_student:
        student = Student(*user_data)
        if is_group_lesson:
            #тут должны получать ID последний из таблицы
            lesson = GroupLesson(*lesson_data)
            glg = GroupLessonGroup( lesson.ID, student.id_group)
            cur.execute("insert into GroupLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_group)"
                        "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (1, lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                         lesson.time, lesson.week_day, lesson.is_upper, student.id_group))
            cur.execute("insert into GroupLessonGroup(ID, id_group_lesson, id_group)"
                        "values (%s, %s, %s)", (glg.id_group_lesson, glg.id_group))
        else:
            lesson = PersonalLesson(*lesson_data)
            pls = PersonalLessonStudent(student.ID, lesson.ID)
            cur.execute(
                "insert into PersonalLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_student)"
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (1, lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                 lesson.time, lesson.week_day, lesson.is_upper, student.ID))
            cur.execute("insert into PersonalLessonStudent(ID, id_student, id_personal_lesson)"
                        "values (%s, %s, %s)", (pls.id_student, pls.id_personal_lesson))
    else:
        lecturer = Lecturer(*user_data)
        if is_group_lesson:
            lesson = GroupLesson(*lesson_data)
            if cur.execute("select * from LecturerGroup where id_lecturer = %s and id_group = %s;", (lecturer.ID, lesson.id_group)) is None:
                cur.execute("insert into LecturerGroup(id_lecturer, id_group)"
                            "values (%s, %s)", (lecturer.ID, lesson.id_group))
            glg = GroupLessonGroup(lesson.ID, lesson.id_group)
            cur.execute(
                "insert into GroupLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_group)"
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (1, lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                 lesson.time, lesson.week_day, lesson.is_upper, lesson.id_group))
            cur.execute("insert into GroupLessonGroup(ID, id_group_lesson, id_group)"
                        "values (%s, %s, %s)", (glg.id_group_lesson, glg.id_group))
        else:
            lesson = PersonalLesson(*lesson_data)
            cur.execute(
                "insert into PersonalLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper)"
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (1, lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                 lesson.time, lesson.week_day, lesson.is_upper))
    conn.commit()
    cur.close()
    conn.close()









