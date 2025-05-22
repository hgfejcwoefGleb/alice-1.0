import psycopg2


#продумать заполнение таблиц, в соответствии с тем, как они свзяаны
#писать сразу нормально с обработкой ошибок
#id должен обновляться автоматически
#добавить в группу атрибут Date, который бы отражал на какие даты стоят пары
#проверить код на соответствие задумке -> все объекты как на схеме
class Group:
    def __init__(self, ID, name, edu_year, edu_program, faculty, edu_format, edu_level):
        #print(name, edu_year, edu_program, faculty, edu_format, edu_level)
        self.ID = ID
        self.name = name
        self.edu_year = edu_year
        self.edu_program = edu_program
        self.faculty = faculty
        self.edu_format = edu_format
        self.edu_level = edu_level
        #cur.execute('INSERT INTO "Group" (name, edu_year, edu_program, faculty, edu_format, edu_level) '
        #'VALUES (%s, %s, %s, %s, %s, %s);', list(vars(self).values())) #??????????
        #cur.execute("""INSERT INTO "Group" (name, edu_year, edu_program, faculty, edu_format, edu_level)
        #VALUES (2, 2, 2, 2, 2, 2);""")


class Student:
    def __init__(self, ID, name, surname, father_name, id_group):
        self.ID = ID
        self.name = name
        self.surname = surname
        self.father_name = father_name
        self.id_group = id_group


class Lecturer:
    def __init__(self, ID, name, surname, father_name):
        self.ID = ID
        self.name = name
        self.surname = surname
        self.father_name = father_name


class PersonalLesson:
    def __init__(self, ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, lesson_date, id_student):
        self.ID = ID
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.lesson_date = lesson_date
        self.id_student = id_student


class PersonalLessonStudent:
    def __init__(self, id_student, id_personal_lesson):
        self.id_student = id_student
        self.id_personal_lesson = id_personal_lesson


class GroupLesson:
    def __init__(self, ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, lesson_date, id_group):
        self.ID = ID
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.lesson_date = lesson_date
        self.id_group = id_group


class GroupLessonGroup:
    def __init__(self, id_group_lesson, id_group):
        self.id_group_lesson = id_group_lesson
        self.id_group = id_group


class LecturerGroup:
    def __int__(self, id_lecturer, id_group):
        self.id_lecturer = id_lecturer
        self.id_group = id_group

def connect():
    conn = psycopg2.connect(
        dbname='postgres',
        user='admin',
        password='1234',
        host='localhost',
        port='5432',
        options='-c search_path="Course_work"'
    )
    cur = conn.cursor()
    return conn, cur

def is_group_reg(group):
    """Проверяет, существует ли группа в БД."""
    conn, cur = connect()
    cur.execute('SELECT id FROM "Group" WHERE name = %s AND edu_year = %s;', (group.name, group.edu_year))
    res = cur.fetchone()
    cur.close()
    conn.close()
    print(res)
    return res is not None

def registration_user(user_data, group_data=None, is_student=True):
    """Регистрирует пользователя и группу в БД."""
    if group_data is None:
        group_data = []
    conn, cur = connect()
    if is_student:
        group = Group(*group_data)
        student = Student(*user_data)
        # Проверяем, существует ли группа
        if not is_group_reg(group):
            # Если группы нет, добавляем её
            cur.execute(
                'INSERT INTO "Group" (name, edu_year, edu_program, faculty, edu_format, edu_level) '
                'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;',
                (group.name, group.edu_year, group.edu_program, group.faculty, group.edu_format, group.edu_level)
            )
            group_id = cur.fetchone()[0]  # Получаем id новой группы
            print(f"Добавлена новая группа с id: {group_id}")
        else:
            # Если группа уже существует, получаем её id
            cur.execute('SELECT id FROM "Group" WHERE name = %s AND edu_year = %s;', (group.name, group.edu_year))
            group_id = cur.fetchone()[0]

        # Вставляем студента
        cur.execute(
            'INSERT INTO student (name, surname, father_name, id_group) VALUES (%s, %s, %s, %s);',
            (student.name, student.surname, student.father_name, group_id)
        )
    else:
        lecturer = Lecturer(*user_data)
        cur.execute(
            'INSERT INTO lecturer (id, name, surname, father_name) VALUES (%s, %s, %s, %s);',
            (lecturer.ID, lecturer.name, lecturer.surname, lecturer.father_name)
        )
    conn.commit()
    cur.close()
    conn.close()



