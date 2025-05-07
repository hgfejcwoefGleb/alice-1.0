
from abc import ABC, abstractmethod
from registration_ydb import select_id_student
from request import Request
from state import STATE_RESPONSE_KEY
import intents

from registration_ydb import *
from schedule_queries import change_db_data, find_lesson_student, \
    find_by_week_day_lesson_student, find_by_week_day_lesson_lecturer, find_lesson_lecturer, insert_lesson
from utils import make_readable

class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    @abstractmethod
    def reply(self, request, pool):
        """Генерация ответа сцены"""
        raise NotImplementedError

    def move(self, request: Request):
        """Проверка и переход к следующей смене"""
        next_scene = self.handle_local_intents(request)
        print(next_scene)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_local_intents(self, request: Request):
        """Проверка локальных интентов,
           по которым происходит переход к
           другой сцене
        """
        raise NotImplementedError

    @abstractmethod
    def handle_global_intents(self, request: Request):
        """Проверка глобальных интентов,
           по которым происходит переход к
           другой сцене"""
        raise NotImplementedError

    def fallback(self, request: Request):
        return self.make_response(text="Извини, я не поняла твою просьбу. Переформулируй запрос или уточни, что я умею")

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, user_state_update=None):
        """Возврат ответа навыку"""
        response = {
            'text': text,
            'tts': tts if tts is not None else text
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id()
            },
            "user_state_update": {},
            "application_state": {},

        }
        if state is not None:
            webhook_response["session_state"].update(state)
        if user_state_update is not None:
            webhook_response["user_state_update"].update(user_state_update)
        return webhook_response

    """Дальше нужно прописать сцены, которые есть у нашего навыка"""


def is_registered(request: Request):
    """Функция проверяет, что сессия данного пользователя/на данном устройстве новая"""
    return len(request['state']['user']) != 0


def is_student(request: Request):  # перепишем с использованием интентов и сущностей
    return request['state']['user']['is_student'] == 'студент'


# переписать без elif

class Welcome(Scene):
    def handle_global_intents(self, request: Request):
        if intents.GET_HELP_IN_GENERAL in request.intents:
            return GetHelpInGeneral()
        elif intents.REGISTRATE in request.intents or not is_registered(request) or 'is_student' not in request['state']['user']:
            return Registration()
        #проверить работает ли
        elif 'user_data' not in request['state']['user'] or 'user_data' in request['state']['user'] and len(request['state']['user']['user_data']) == 0:
            return Registration()
        elif 'group_data' not in request['state']['user']:
            if is_student(request):
                return InsertGroupData()
            else:
                return IsStudent()
        #переписать логику для поиска, мб ищем по слотам
        elif intents.FIND_SCHEDULE_LESSON_NAME in request.intents:
            return FindScheduleLessonName()
        elif intents.FIND_SCHEDULE in request.intents and is_student(request):
            return FindScheduleStudent()
        elif intents.FIND_SCHEDULE in request.intents and not is_student(request):
            return FindScheduleLecturer()
        elif intents.CHANGE_USER_DATA in request.intents:
            return ChangeUserData()
        elif intents.CHANGE_SCHEDULE in request.intents:
            return ChangeSchedule()
        elif intents.ADD_LESSON in request.intents:
            return EnterIsGroupLessonInsert()
        elif intents.GET_HELP_REG in request.intents:
            return GetHelpReg()
        elif intents.GET_HELP_FIND_SCH in request.intents:
            return GetHelpFindSch()
        elif intents.GET_HELP_CHANGE_DATA in request.intents:
            return GetHelpChangeData()
        elif intents.GET_HELP_CHANGE_SCH in request.intents:
            return GetHelpChangeSch()
        elif intents.GET_HELP_ADD_SCH in request.intents:
            return GetHelpAddSch()
        # только для теста потом убрать
        else:
            return ChangeUserData()

    def handle_local_intents(self, request: Request):
        pass

    def reply(self, request: Request, pool):
        text = ('Привет! Я могу помочь с расписанием студентов Вышки.'
                'Ты хочешь узнать своё расписание на сегодня, завтра или найти пару по названию? '
                'Если хочешь узнать, что я умею, попроси справку, сказав: Алиса, покажи справку')
        return self.make_response(text=text)  # прописать кнопки


class Registration(Welcome):
    def reply(self, request: Request, pool):
        text = ('Чтобы узнать твое расписание мне нужно с тобой лучше познакомиться. '
                'Ты студент или преподаватель?')
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        return IsStudent()


class IsStudent(Registration):
    def reply(self, request: Request, pool):
        is_student = ""
        if 'is_student' not in request['state']['user'] or 'is_student' in request['state']['user'] and len(request['state']['user']['is_student']) == 0:
            is_student = request["request"]['command']# здесь должно быть использование сущностей/интентов
        text = ('Отлично, теперь расскажи про себя. '
                'Как тебя зовут? Назови свои ФИО '
                'Если ты студент, то назови еще номер группы'
                'Только в формате: "Иванов Иван Иванович 22БИ3"')
        return self.make_response(text=text, user_state_update={'is_student': is_student})

    def handle_local_intents(self, request: Request):
        return InsertGroupData() if is_student(request) else InsertUserData()


class InsertGroupData(Registration):
    def reply(self, request: Request, pool):
        # тут нужно подумать, как мы будет менять или получать id Группы, если она зарегана
        user_data = ""
        if 'user_data' not in request['state']['user'] or 'user_data' in request['state']['user'] and len(request['state']['user']['user_data']) == 0:
            user_data = request["request"]['command']
        # здесь должно быть использование сущностей/интентов
        text = ('Хорошо, теперь назови год своего поступления,'
                'образовательную программу, факультет, формат обучения '
                'очный или нет и уровень образования в формате: '
                '2022 Бизнес-информатика Факультет Информатики математики и компьютерных наук очный бакалавриат')
        return self.make_response(text=text, user_state_update={'user_data': user_data})

    def handle_local_intents(self, request: Request):
        return InsertUserData()


class InsertUserData(Registration):
    def reply(self, request: Request, pool):
        group_data = ""
        if is_student(request):
            user_data = request['state']['user']['user_data']
            group_name = "".join(user_data.split()[3:])
            # тут проверяем зарегана группа или нет
            edu_year = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_year']['value']
            edu_program = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_program']['value']
            faculty = request.intents[intents.ENTER_GROUP_DATA]['slots']['faculty']['value']
            edu_format = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_format']['value']
            edu_level = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_level']['value']
            group_data = [group_name, edu_year, edu_program, faculty, edu_format, edu_level]
            group = Group(*list(group_data))
            if is_group_reg(pool, group):
                id_group = select_id_group(pool, group)
                user_data = user_data.split()[:3]
                user_data.append(id_group)
            else:
                user_data = user_data.split()[:3]
                user_data.append(-1)
            # меняем id_group в сессии, если студент
        else:
            user_data = request["request"]['command'].split()
        registration_user(user_data, pool, is_student(request), group_data)
        user_data[-1] = str(user_data[-1])
        text = (
            'Очень приятно! Хочешь проверить свое расписание на сегодня, на какую-то другую дату или найти конкретный предмет?')
        return self.make_response(text=text,
                                  user_state_update={'user_data': " ".join(user_data), 'group_data': group_data})

    def handle_local_intents(self, request: Request):
        pass


# возможно переписать фразы в соответствии с интентами
#
class GetHelpInGeneral(Welcome):
    """"""

    def reply(self, request: Request, pool):
        text = ('Привет, я помогу узнать расписание твоих дисциплин '
                'Например, если ты хочешь узнать расписание по философии, то'
                'скажи: "Алиса когда у меня философия" или: Алиса, что у меня во вторник?.'
                ' Я могу подсказать расписание на конкретную дату, день недели '
                'или у нужного преподавателя. Если хочешь узнать, когда у тебя пара '
                'с преподавателем, скажите, когда у меня пара с Владимиром Владимировым Владимиряном? '
                'Главное, чтобы фамилия была правильной. Чтобы поменять данные, '
                'скажи: хочу поменять данные. Чтобы добавить пару, скажи: '
                '"Алиса, добавь пару". Чтобы получить справку по конкретной функции:'
                '"Алиса, как мне изменить данные/зарегистрироваться/найти расписание/изменить расписание/добавить расписание"')
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        if intents.GET_HELP_REG in request.intents:
            return GetHelpReg()
        elif intents.GET_HELP_FIND_SCH in request.intents:
            return  GetHelpFindSch()
        elif intents.GET_HELP_CHANGE_DATA in request.intents:
            return GetHelpChangeData()
        elif intents.GET_HELP_CHANGE_SCH in request.intents:
            return GetHelpChangeSch()
        elif intents.GET_HELP_ADD_SCH in request.intents:
            return GetHelpAddSch()

class ChangeUserData(Welcome):
    def reply(self, request: Request, pool):
        text = "Что ты хочешь поменять? Фамилию, имя, отчество номер группы или все в целом?"
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        return EnterNewData()


class EnterNewData(ChangeUserData):
    def reply(self, request: Request, pool):
        text = "Хорошо, я поняла, сейчас сделаем. Назови свои новые данные."
        #только для теста user_state_update={"is_student": "лектор"
        return self.make_response(text=text, user_state_update={"is_student": "лектор"})

    def handle_local_intents(self, request: Request):
        # if intents.CHANGE_ALL_DATA in request.intents:
        # return ChangeAllData()
        # elif intents.CHANGE_NAME in request.intents:
        #return ChangeOneAttr('name')
    # elif intents.CHANGE_SURNAME in request.intents:
        #return ChangeOneAttr('surname')
    # elif intents.CHANGE_FATHER_NAME in request.intents:
        #return ChangeOneAttr('father_name')
    # elif intents.CHANGE_GROUP in request.intents:
        return ChangeOneAttr('group')


# написать отдельно для препода
class ChangeAllData(ChangeUserData):
    def reply(self, request: Request, pool):
        new_data = request['request']['command']
        text = "Прекрасно, новые данные я запомнила!"
        change_db_data(pool, request['state']['user']['user_data'], new_data)
        return self.make_response(text=text, user_state_update={'user_data': new_data})

    def handle_local_intents(self, request: Request):
        pass


class ChangeOneAttr(ChangeUserData):
    def __init__(self, change_attr=None):
        self.change_attr = change_attr
        self.attr_dict = {
            'name': 0,
            'surname': 1,
            'father_name': 2,
            'group': 3
        }

    def reply(self, request: Request, pool):
        new_name = request['request']['command']
        text = 'Хорошо, теперь запомнила твои новые данные!'
        old_data = request['state']['user']['user_data']
        new_data = old_data.split()
        new_data[self.attr_dict[self.change_attr]] = new_name
        new_data = " ".join(new_data)
        change_db_data(pool, old_data, new_data)
        return self.make_response(text=text, user_state_update={'user_data': new_data})

    def handle_local_intents(self, request: Request):
        pass

#написать отдельно для препода

#он будто не нужен
class EnterIsGroupLesson(Welcome):
    def reply(self, request: Request, pool):
        text = ("Предметы, которые хочешь найти связаны с конкретной образовательной программой "
                "Или это это майноры, английский и другие предметы, которые проводятся "
                "для разных групп?")
        #тут с помощью интентов получаем дату, лектора и тп
        search_attr_val = request['request']['command']
        search_attr_name = request['request']['command']
        return self.make_response(text=text, user_state_update={'search_attr_val': search_attr_val, 'search_attr_name': search_attr_name})

    def handle_local_intents(self, request: Request):
        if is_student(request):
            return FindScheduleStudent()
        else:
            return FindScheduleLecturer()

class FindScheduleLessonName(Welcome):
    def reply(self, request, pool):
        text = ("Хорошо, назови предмет, по которому хочешь найти пары")
        return self.make_response(text=text)
    
    def handle_local_intents(self, request):
        if is_student(request):
            return FindScheduleByNameStudent()
        return FindScheduleByNameLecturer()

class FindScheduleByNameStudent(Welcome):
    def reply(self, request, pool):
        res = None
        search_attr_name = 'name'
        search_attr_val = request['request']['command']
        student_data = request['state']['user']['user_data'].split()
        group_data = request['state']['user']['group_data'].split()
        student = Student(*student_data)
        group = Group(*list(group_data.split()))
        id_student = select_id_student(pool, student)
        id_group = select_id_group(pool, group)
        res = find_lesson_student(pool, True, search_attr_name, search_attr_val, id_group, id_student)
        res.extend(find_lesson_student(pool, False, search_attr_name, search_attr_val, id_group, id_student))
        text = 'Конечно, вот расписание: '
        text = text + make_readable(res)
        return self.make_response(text=text)
    
    def handle_local_intents(self, request):
        pass

class FindScheduleByNameLecturer(Welcome):
    def reply(self, request, pool):
        text = 'Конечно, вот расписание: '
        search_attr_name = 'name'
        search_attr_val = request['request']['command']
        lecturer_date = request['state']['user']['user_data'].split()
        lecturer = Lecturer(*lecturer_date)
        id_lecturer = select_id_lecturer(pool, lecturer)
        res = find_lesson_lecturer(pool, 'GroupLesson', search_attr_name, search_attr_val, id_lecturer)
        res.extend(find_lesson_lecturer(pool, 'PersonalLesson', search_attr_name, search_attr_val, id_lecturer))
        text = text + make_readable(res)
        return self.make_response(text=text)
    
    def handle_local_intents(self, request):
        pass

class FindScheduleStudent(Welcome):
    def reply(self, request: Request, pool):
        search_attr_name = "".join(request.intents[intents.FIND_SCHEDULE]['slots'].keys())
        res = None
        text = 'Конечно, вот расписание: '
        student_data = request['state']['user']['user_data'].split()
        group_data = request['state']['user']['group_data'].split()
        student = Student(*student_data)
        group = Group(*list(group_data.split()))
        id_student = select_id_student(pool, student)
        id_group = select_id_group(pool, group)
        if search_attr_name == 'today' or search_attr_name == 'tomorrow':
            res = find_lesson_student(pool, True, search_attr_name, '', id_group, id_student)
            res.extend(find_lesson_student(pool, False, search_attr_name, '', id_group, id_student))
        elif search_attr_name == 'lesson_date':
            #тут выковыриваем дату из первого запроса
            search_attr_val = request.intents[intents.FIND_SCHEDULE]['slots'][search_attr_name]['value']
            res = find_lesson_student(pool, True, search_attr_name, search_attr_val, id_group, id_student)
            res.extend(find_lesson_student(pool, False, search_attr_name, search_attr_val, id_group, id_student))
        #elif search_attr_name == 'name': пока отдельный класс
        #    search_attr_val = request.intents[intents.FIND_SCHEDULE]['slots'][search_attr_name]['value']
        #    res = find_lesson_student(pool, is_group_lesson, search_attr_name, search_attr_val, id_group, id_student)
        elif search_attr_name == 'id_lecturer':
            lecturer = Lecturer(*request.intents[intents.FIND_SCHEDULE]['slots'][search_attr_name]['value'].split())
            search_attr_val = str(select_id_lecturer(pool, lecturer))
            res = find_lesson_student(pool, True, search_attr_name, search_attr_val, id_group, id_student)
            res.extend(find_lesson_student(pool, False, search_attr_name, search_attr_val, id_group, id_student))
        elif search_attr_name == 'week_day':
            week_day = request.intents[intents.FIND_SCHEDULE]['slots'][search_attr_name]['value']
            res = find_by_week_day_lesson_student(pool, True, id_group, id_student, week_day)
            res.extend(find_by_week_day_lesson_student(pool, False, id_group, id_student, week_day))
        text = text + make_readable(res)
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        pass



class FindScheduleLecturer(Welcome):
    def reply(self, request: Request, pool):
        text = 'Конечно, вот расписание: '
        search_attr_name = "".join(request.intents[intents.FIND_SCHEDULE]['slots'].keys())
        search_attr_val = request.intents[intents.FIND_SCHEDULE]['slots'][search_attr_name]['value']
        lecturer_date = request['state']['user']['user_data'].split()
        lecturer = Lecturer(*lecturer_date)
        id_lecturer = select_id_lecturer(pool, lecturer)
        if search_attr_name == 'week_day':
            res = find_by_week_day_lesson_lecturer(pool, 'GroupLesson', search_attr_val, id_lecturer)
            res.extend(find_by_week_day_lesson_lecturer(pool, 'PersonalLesson', search_attr_val, id_lecturer))
        else:
            res = find_lesson_lecturer(pool, 'GroupLesson', search_attr_name, search_attr_val, id_lecturer)
            res.extend(find_lesson_lecturer(pool, 'PersonalLesson', search_attr_name, search_attr_val, id_lecturer))
        text = text + make_readable(res)
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        pass

class EnterIsGroupLessonInsert(Welcome):
    def reply(self, request: Request, pool):
        text = ("Предметы, которые хочешь внести связаны с конкретной образовательной программой "
                "Или это это майноры, английский и другие предметы, которые проводятся "
                "для разных групп?")
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        return EnterLessonData()

class EnterLessonData(Welcome):
    def reply(self, request: Request, pool):
        is_group_lesson = True if request.intents[intents.ENTER_IS_GROUP_LESSON_INSERT]['slots'].get('group_lesson', 0) != 0 else False
        if not is_student(request) and is_group_lesson:
            text = "У какой группы будет проходить данный предмет. Назови название и год начала обучения?"
        else:
            text = ('Теперь расскажи все про предмет, '
                    'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"')
        return self.make_response(text=text, user_state_update={'is_group_lesson': is_group_lesson})

    def handle_local_intents(self, request: Request):
        is_group_lesson = request['state']['user']['is_group_lesson']
        if not is_student(request) and is_group_lesson:
            return IsGroupOfLectReg()
        return AddLesson()

class IsGroupOfLectReg(Welcome):
    def reply(self, request: Request, pool):
        if len(request['request']['command'].split()) > 2:
            name, edu_year = "".join(request['request']['command'].split()[:3]), request['request']['command'].split()[-1]
        else:
            name, edu_year = request['request']['command'].split()
        is_group_reg_v = "False"
        group = Group(name, edu_year)
        if is_group_reg(pool, group):
            text = ('Теперь расскажи все про предмет, '
                    'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"')
            is_group_reg_v = "True"
        else:
            text = ('Хорошо, теперь назови '
                'образовательную программу, факультет, формат обучения '
                'очный или нет и уровень образования в формате: '
                'Бизнес-информатика Факультет Информатики математики и компьютерных наук очный бакалавриат')
        return self.make_response(text=text, user_state_update={'group_data': name + " " + edu_year, 'is_group_reg': is_group_reg_v})
    
    def handle_local_intents(self, request):
        if request['state']['user']['is_group_reg'] == 'True':
            return AddLesson()
        return RegGroupLect()

class RegGroupLect(Welcome):
    def reply(self, request, pool):
        group_name, edu_year = request['state']['user']['group_data'].split()
        edu_program = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_program']['value']
        faculty = request.intents[intents.ENTER_GROUP_DATA]['slots']['faculty']['value']
        edu_format = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_format']['value']
        edu_level = request.intents[intents.ENTER_GROUP_DATA]['slots']['edu_level']['value']
        group_data = [group_name, edu_year, edu_program, faculty, edu_format, edu_level]
        group = Group(*group_data)
        reg_group(pool, group)
        text = ('Отлично, группа зарегистрирована. Теперь расскажи все про предмет, '
                    'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"')
        return self.make_response(text=text)
            
    def handle_local_intents(self, request):
        return AddLesson()
            
class AddLesson(Welcome):
    
    def reply(self, request: Request, pool):
        #тут вычленяем данные предмета из интентов
        lesson_data = request['request']['command'].split()
        group_data = request['state']['user']['group_data']
        if not is_student(request):
            group_data = group_data.split()
        group = Group(*group_data)
        is_group_lesson = request['state']['user']['is_group_lesson']
        if is_student(request):
            student = Student(*request['state']['user']['user_data'].split())
            last_elem = int(select_id_group(pool, group) if is_group_lesson else select_id_student(pool, student))
        else:
            last_elem = int(select_id_group(pool, group) if is_group_lesson else -1)
        lecturer_data = lesson_data[6:9]
        lesson_data = [lesson_data[0], lesson_data[1], lesson_data[3], lesson_data[4], 0, "".join(lesson_data[9:11]) + "".join(lesson_data[11:12]), True, True, lesson_data[-1], last_elem]
        #name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date
        #Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025
        #тут по данным лектора находим его id, id_student
        #черновик#черновик
        user_data = request['state']['user']['user_data'].split()#черновик #черновик
        #добавляем их в lesson_date
        insert_lesson(pool, lesson_data, is_student(request), is_group_lesson, user_data, lecturer_data)
        text = "Отлично, я запомнила новый предмет!"
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        pass




class ChangeSchedule(Welcome):
    #нужно написать функции для взаимодействия с самой БД
    pass


class GetHelpReg(GetHelpInGeneral):
    def reply(self, request: Request, pool):
        text=("1.Когда я спрошу студент ли ты? Просто ответь: 'Я студент' или 'Я преподаватель'"
              "2.Когда захочу узнать про ФИО и номер группы, то если ты студент напиши: "
              "'Валерий Иванов Евгеньевич 22БИ3', группу указывай именно в таком формате, а не"
              "просто число"
              "3.Когда захочу подробнее узнать про тебя, если ты студент, то напиши:"
              "2022 Бизнес-информатика Информатики математики и компьютерных наук очный бакалавриат")
        return self.make_response(text=text)
    
    def handle_local_intents(self, request):
        pass

#написать поиск по названию предмета
class GetHelpFindSch(GetHelpInGeneral):
    def reply(self, request, pool):
        text = ('1.Чтобы найти пары на сегодня/завтра спроси: "Алиса, какие пары сегодня/завтра?"'
                '2.Чтобы найти пары на день недели: "Какие пары во вторник?"'
                '3.Чтобы найти пары на конкретную дату: "Какие пары 21 апреля?"'
                '4.Чтобы узнать пары у конкретного препода: "Когда пары с Ивановым Иваном Ивановичем?"'
                '5.Чтобы узнать пары по названию предмета: Хочу узнать когда у меня конкретный предмет'
                'Когда я спрошу название предмета, то напиши его так, как указывал придобавлении: "Матанализ"')
        return self.make_response(text=text)


class GetHelpChangeData(GetHelpInGeneral):
    pass


class GetHelpChangeSch(GetHelpInGeneral):
    pass


class GetHelpAddSch(GetHelpInGeneral):
    def reply(self, request, pool):
         #(self, name, type_l, building, auditorium, id_lecturer, time, is_weekly, is_upper, lesson_date,
        #         id_student):
        text = ('1.Когда я спрошу про то, связаны ли предметы с твоей ОП или это майнор,'
                'английский и тп, то просто ответь: "Групповой", если предмет связан с ОП'
                'или "Индивидуальный"'
                '2.Когда я попрошу указать все про предмет, то укажи его данные так:'
                '"Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"'
                )
        return self.make_response(text=text)
    
    def handle_local_intents(self, request):
        pass


SCENES = {
    scene.id(): scene for scene in [
        Welcome,
        Registration,
        IsStudent,
        InsertGroupData,
        InsertUserData,
        GetHelpInGeneral,
        ChangeUserData,
        EnterNewData,
        ChangeAllData,
        ChangeOneAttr,
        EnterIsGroupLesson,
        FindScheduleLessonName,
        FindScheduleStudent,
        FindScheduleLecturer,
        EnterIsGroupLessonInsert,
        EnterLessonData,
        AddLesson,
        ChangeSchedule,
        GetHelpReg,
        GetHelpFindSch,
        GetHelpChangeData,
        GetHelpChangeSch,
        GetHelpAddSch,
        IsGroupOfLectReg,
        RegGroupLect
    ]
}

DEFAULT_SCENE = Welcome
