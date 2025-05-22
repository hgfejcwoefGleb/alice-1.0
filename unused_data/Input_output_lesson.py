
import Registration as R
from pythonProject.Registration import *


#Функции для поиска информации
#везде смотрим на ID студента
#Продумать,чтобы пользователь вносил даты списком и они добавлялись в таблицу
#Продумать автоматическое инкрементировани ID!
#продумать получение id_lecturer при получении информации о паре
#при ситуации, когда препод хочет внести индвид. пару, айди студента может быть null
#написать отдельную функцию для вставки, которая бы принимала курсор
#сделать так, чтобы при вводе фамилии препода предлагались зареганные преподы
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


def insert_lesson(user_data: list, lesson_data: list, is_student: bool, is_group_lesson: bool) -> None:
    """Функция вносит информацию о паре в БД"""
    conn, cur = R.connect()
    try:
        if is_student:
            student = Student(*user_data)
            if is_group_lesson:
                # Логика для групповых занятий
                lesson = GroupLesson(*lesson_data)
                cur.execute(
                    "INSERT INTO GroupLesson(name, type, building, auditorium, id_lecturer, time, week_day, is_upper, id_group) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID",
                    (lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                     lesson.time, lesson.week_day, lesson.is_upper, student.id_group)
                )
                lesson_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO GroupLessonGroup(id_group_lesson, id_group) VALUES (%s, %s)",
                    (lesson_id, student.id_group)
                )
            else:
                # Логика для персональных занятий - ИСПРАВЛЕННАЯ ВЕРСИЯ
                lesson = PersonalLesson(*lesson_data)

                # 1. Вставляем занятие и получаем его реальный ID
                cur.execute(
                    "INSERT INTO PersonalLesson(name, type, building, auditorium, id_lecturer, time, week_day, is_upper, id_student) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID",
                    (lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lesson.id_lecturer,
                     lesson.time, lesson.week_day, lesson.is_upper, student.ID)
                )
                lesson_id = cur.fetchone()[0]
                #conn.commit()
                # 2. Вставляем связь студента с занятием
                cur.execute(
                    "INSERT INTO PersonalLessonStudent(id_student, id_personal_lesson) VALUES (%s, %s)",
                    (student.ID, lesson_id)
                )
        else:
            # Логика для преподавателей
            lecturer = Lecturer(*user_data)
            if is_group_lesson:
                lesson = GroupLesson(*lesson_data)
                cur.execute(
                    "SELECT 1 FROM LecturerGroup WHERE id_lecturer = %s AND id_group = %s",
                    (lecturer.ID, lesson.id_group)
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO LecturerGroup(id_lecturer, id_group) VALUES (%s, %s)",
                        (lecturer.ID, lesson.id_group)
                    )
                cur.execute(
                    "INSERT INTO GroupLesson(name, type, building, auditorium, id_lecturer, time, week_day, is_upper, id_group) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID",
                    (lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lecturer.ID,
                     lesson.time, lesson.week_day, lesson.is_upper, lesson.id_group)
                )
                lesson_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO GroupLessonGroup(id_group_lesson, id_group) VALUES (%s, %s)",
                    (lesson_id, lesson.id_group)
                )
            else:
                lesson = PersonalLesson(*lesson_data)
                cur.execute(
                    "INSERT INTO PersonalLesson(name, type, building, auditorium, id_lecturer, time, week_day, is_upper) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID",
                    (lesson.name, lesson.type_l, lesson.building, lesson.auditorium, lecturer.ID,
                     lesson.time, lesson.week_day, lesson.is_upper)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()









