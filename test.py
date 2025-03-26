from Registration import *
from Input_output_lesson import *
#(id, name, edu_year, edu_program, faculty, edu_format, edu_level)
#(id, name, surname, father_name, id_group)
#(id, name, surname, father_name)
#GroupLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_group)
#PersonalLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_student)

#registration_user([2, 'Вася', 'Иванов', 'Евпатиевич', 0], [2, '22БИ3', 2022, 'БИ', 'ИМИКН', 'очно', 'бакалавр'], True)
#при запуске и вставке с пользователем без группы работает
#при запуске и наличии группы тоже работает
#registration_user([2, 'Вася', 'Петров', 'Олегович', 0], [2, '22БИ3', 2022, 'БИ', 'ИМИКН', 'очно', 'бакалавр'], True)
#внесение препода тоже работает
#registration_user([2, 'Алексей', 'Вбивалкин', 'Петрович'], is_student=False)
"""self.ID = ID
        self.name = name
        self.type_l = type_l
        self.building = building
        self.auditorium = auditorium
        self.id_lecturer = id_lecturer
        self.time = time
        self.week_day = week_day
        self.is_upper = is_upper
        self.lesson_date = lesson_date
        self.id_group = id_group"""
#работает
#insert_lesson([1, 'Вася', 'Иванов', 'Евпатиевич', 1], [1, 'Матан', 'семинар', 'Родионова',
                                                  #'303', 2, '12:00', 'вторник', True, '12.04.2004',1], True, True)
#работает
#insert_lesson([1, 'Вася', 'Иванов', 'Евпатиевич', 1], [1, 'Матан', 'семинар', 'Родионова',
#                                                      '303', 2, '12:00', 'вторник', True, '12.04.2004',1], True, False)
#работает
#insert_lesson([2, 'Вася', 'Иванов', 'Евпатиевич'], [1, 'Матан', 'семинар', 'Родионова',
#                                               '303', 2, '12:00', 'вторник', True, '12.04.2004',1], False, True)

#работает
#insert_lesson([2, 'Вася', 'Иванов', 'Евпатиевич'], [1, 'Матан', 'семинар', 'Родионова',
#                                                 '303', 2, '12:00', 'вторник', True, '12.04.2004',1], False, False)
#INSERT INTO PersonalLesson(name, type, building, auditorium, id_lecturer, time, week_day, is_upper)
#insert into GroupLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_group)
#insert into PersonalLesson(ID, name, type_l, building, auditorium, id_lecturer, time, week_day, is_upper, id_student)