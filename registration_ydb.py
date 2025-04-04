import ydb


class Group:
    def __init__(self, name, edu_year, edu_program, faculty, edu_format, edu_level):
        # print(name, edu_year, edu_program, faculty, edu_format, edu_level)
        self.name = name
        self.edu_year = edu_year
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
        self.id_group = id_group


class Lecturer:
    def __init__(self, name, surname, father_name):
        self.name = name
        self.surname = surname
        self.father_name = father_name


class PersonalLesson:
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, lesson_date,
                 id_student):
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
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, lesson_date,
                 id_group):
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


def is_group_reg(pool: ydb.QuerySessionPool, group):
    """Проверяет, существует ли группа в БД.
    :returns bool"""
    res = (pool.execute_with_retries
        (
        """
        DECLARE $edu_year AS Utf8;
        DECLARE $name AS Utf8;
    
        SELECT id FROM `Group`
        WHERE name = $name AND edu_year = $edu_year;
        """,
        {"$edu_year": group.edu_year,
         "$name": group.name
         },
    ))
    return len(res[0].rows) != 0


def select_id_group(pool: ydb.QuerySessionPool, group: Group):
    return pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $edu_year AS Utf8;

        SELECT id FROM `Group`
        WHERE name = $name AND edu_year = $edu_year;
        """,
        {
            '$name': group.name,
            '$edu_year': group.edu_year,
        },
    )[0].rows[0].id


def registration_user(user_data: list, group_data: list, pool: ydb.QuerySessionPool, is_student=True, ):
    """Регистрирует пользователя и группу в БД."""
    if is_student:
        group = Group(*group_data)
        student = Student(*user_data)
        # Проверяем, существует ли группа
        if not is_group_reg(pool, group):
            # Если группы нет, добавляем её
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
            # Возможно не сработает, потому что не сразу добавилось
        id_group = select_id_group(pool, group)  # Получаем id новой группы
        pool.execute_with_retries(
            """
            DECLARE $name AS Utf8;
            DECLARE $surname AS Utf8;
            DECLARE $father_name AS Utf8;
            DECLARE $id_group AS Int16;

            INSERT INTO Student (name, surname, father_name, id_group)
            VALUES ($name, $surname, $father_name, $id_group);
            """,
            {
                '$name': student.name,
                '$surname': student.surname,
                '$father_name': student.father_name,
                '$id_group': (id_group, ydb.PrimitiveType.Int16),

            },
        )
    else:
        lecturer = Lecturer(*user_data)
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