class Lesson:
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date):
        # Общие атрибуты для всех уроков
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = int(id_lecturer)
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
        self.id_student = int(id_student)


class GroupLesson(Lesson):
    def __init__(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date,
                 id_group):
        # Вызываем конструктор родительского класса для инициализации общих атрибутов
        super().__init__(name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date)
        # Уникальный атрибут для GroupLesson
        self.id_group = int(id_group)


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
