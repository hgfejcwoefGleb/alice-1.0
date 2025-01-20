import psycopg2


class Group:
    def __init__(self, name, edu_year, edu_program, faculty, edu_format, edu_level, cur):
        self.name = name
        self.edu_year = edu_year
        self.edu_program = edu_program
        self.faculty = faculty
        self.edu_format = edu_format
        self.edu_level = edu_level
        cur.execute("INSERT INTO Group (name, edu_year, edu_program, faculty, edu_format, edu_level) "
                    "VALUES (%s, %s, %s, %s, %s, %s);", vars(self)) #??????????


class Student:
    def __int__(self, name, surname, father_name, id_group, cur):
        self.name = name
        self.surname = surname
        self.father_name = father_name
        self.id_group = id_group


class Lecturer:
    def __int__(self, name, surname, father_name, cur):
        self.name = name
        self.surname = surname
        self.father_name = father_name


class PersonalLesson:
    def __int__(self, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_student, cur):
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.id_student = id_student


class PersonalLessonStudent:
    def __int__(self, id_student, id_personal_lesson, cur):
        self.id_student = id_student
        self.id_personal_lesson = id_personal_lesson


class GroupLesson:
    def __int__(self, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_group, cur):
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.id_group = id_group


class GroupLessonGroup:
    def __int__(self, id_group_lesson, id_group, cur):
        self.id_group_lesson = id_group_lesson
        self.id_group = id_group


def connect():
    conn = psycopg2.connect(
        dbname='postres',
        user='admin',
        password='admin',
        host='localhost',
        port='5432'
        )
    cur = conn.cursor()
    return cur
#подключение к БД происходит один раз в начале регистрации
def registration(user_data, group_data): #приходит какая-то информация о пользователе
    cur = connect()
    group = Group(*group_data, cur)
    student = Student(*user_data, cur)

    """import psycopg2

with psycopg2.connect(
dbname="selecteldb",
user="postgres",
password="password",
host="localhost",
port="5432"
) as conn:
with conn.cursor() as cur:
    # Вставка данных
    cur.execute("INSERT INTO servers (server, cost) VALUES (%s, %s);", ("server1", 100))
    cur.execute("INSERT INTO servers (server, cost) VALUES (%s, %s);", ("server2", 200))
    cur.execute("INSERT INTO servers (server, cost) VALUES (%s, %s);", ("server3", 300))
    conn.commit()"""
    pass