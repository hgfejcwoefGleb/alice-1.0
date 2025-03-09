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
    def __init__(self, ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, date, id_student):
        self.ID = ID
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.date = date
        self.id_student = id_student


class PersonalLessonStudent:
    def __init__(self, id_student, id_personal_lesson):
        self.id_student = id_student
        self.id_personal_lesson = id_personal_lesson


class GroupLesson:
    def __init__(self, ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, date, id_group):
        self.ID = ID
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.date = date
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
        port='5432'
    )
    cur = conn.cursor()
    return conn, cur

#id передаются в списках user_data, group_data
#подключение к БД происходит один раз в начале регистрации
def registration_user(user_data, group_data, is_student):  #приходит какая-то информация о пользователе
    """Происходит получение информации о пользователе и группе и данные заносятся в таблицу student или lecturer"""
    conn, cur = connect()
    if is_student:
        group = Group(*group_data)
        student = Student(*user_data)
        if not is_group_reg(group):  #сначала заполняется таблица группы, если группы нет
            cur.execute("insert into group (id, name, edu_year, edu_program, faculty, edu_format, edu_level) "
                        "values (%s, %s, %s, %s, %s, %s);", (1, group.name, group.edu_year, group.edu_program,
                                                             group.faculty, group.edu_format, group.edu_level))
        cur.execute(f"insert into student (id, name, surname, father_name, id_group) values (%s, %s, %s, %s, %s);",
                    (2, student.name, student.surname, student.father_name, student.id_group))
    else:
        lecturer = Lecturer(*user_data)
        cur.execute(f"insert into lecturer (id, name, surname, father_name) values (%s, %s, %s, %s);",
                    (1, lecturer.name, lecturer.surname, lecturer.father_name))
    conn.commit()
    cur.close()
    conn.close()


def is_group_reg(group):
    """Можно на вход принимать только группу и проверять по name, edu_year в таблице.
        Если группа есть в таблице возвращает все ее атрибуты, иначе None
    """
    conn, cur = connect()
    cur.execute(f"select * from group where name={group.name} and edu_year={group.edu_year}")
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res is not None


