import sys
from abc import ABC, abstractmethod
import inspect
from request import Request
from state import STATE_RESPONSE_KEY
import intents
from ..ydb.registration_ydb import *


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

#переписать без elif

class Welcome(Scene):
    def handle_global_intents(self, request: Request):
        if intents.GET_HELP_IN_GENERAL in request.intents:
            return GetHelpInGeneral()
        elif intents.REGISTRATE in request.intents or not is_registered(request):
            return Registration()
        elif intents.FIND_SCHEDULE in request.intents:
            return FindSchedule()
        elif intents.CHANGE_USER_DATA in request.intents:
            return ChangeUserData()
        elif intents.CHANGE_SCHEDULE in request.intents:
            return ChangeSchedule()
        elif intents.ADD_LESSON in request.intents:
            return AddLesson()
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
            return IsStudent()

    def handle_local_intents(self, request: Request):
        pass

    def reply(self, request: Request, pool):
        text = ('Привет! Я могу помочь с расписанием студентов Вышки.'
                'Ты хочешь узнать своё расписание на сегодня, завтра или найти пару по названию? '
                'Если хочешь узнать, что я умею, попроси справку')
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
        is_student = request["request"]['command']  # здесь должно быть использование сущностей/интентов
        text = ('Отлично, теперь расскажи про себя. '
                'Как тебя зовут? Назови свои ФИО '
                'Если ты студент, то назови еще номер группы')
        return self.make_response(text=text, user_state_update={'is_student': is_student})

    def handle_local_intents(self, request: Request):
        return InsertGroupData() if is_student(request) else InsertUserData()


class InsertGroupData(Registration):
    def reply(self, request: Request, pool):
        # тут нужно подумать, как мы будет менять или получать id Группы, если она зарегана
        user_data = request["request"]['command']
        # здесь должно быть использование сущностей/интентов
        text = ('Хорошо, теперь назови год своего поступления,'
                'образовательную программу, факультет, формат обучения '
                'очный или нет и уровень образования')
        return self.make_response(text=text, user_state_update={'user_data': user_data})

    def handle_local_intents(self, request: Request):
        return InsertUserData()


class InsertUserData(Registration):
    def reply(self, request: Request, pool):
        group_data = []
        user_data = ""
        if is_student(request):
            user_data = request['state']['user']['user_data']
            # тут проверяем зарегана группа или нет
            group_data = request["request"]['command']
            group = Group(*list(group_data.split()))
            if is_group_reg(pool, group):
                id_group = select_id_group(pool, group)
                user_data = user_data.split()[:3]
                user_data.append(id_group)
            else:
                user_data = list(user_data.split())
            # меняем id_group в сессии, если студент
        else:
            user_data = user_data.split()
        registration_user(user_data, pool, is_student(request), group_data.split())
        text = (
            'Очень приятно! Хочешь проверить свое расписание на сегодня, на какую-то другую дату или найти конкретный предмет?')
        return self.make_response(text=text, user_state_update={'user_data': " ".join(user_data), 'group_data': group_data})

    def handle_local_intents(self, request: Request):
        pass

#возможно переписать фразы в соответствии с интентами
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
                '"Алиса как мне изменить данные/зарегистрироваться/найти расписание/изменить расписание/добавить расписание"')
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        pass

class ChangeUserData(Welcome):
    def reply(self, request: Request, pool):
        text = "Что ты хочешь поменять? Фамилию, имя, отчество номер группы или все в целом?"
        return self.make_response(text=text)

    def handle_local_intents(self, request: Request):
        if intents.CHANGE_ALL_DATA in request.intents:
            return ChangeAllData()
        elif intents.CHANGE_NAME in request.intents:
            return ChangeName()
        elif intents.CHANGE_SURNAME in request.intents:
            return ChangeSurname()
        elif intents.CHANGE_FATHER_NAME in request.intents:
            return ChangeFatherName()
        elif intents.CHANGE_GROUP in request.intents:
            return ChangeGroup()

#перенести эту функцию в ydd
def change_db_data(pool: ydb.QuerySessionPool, user_data_old: str, user_data_new):
    """Функция по изменению данных пользователя в БД"""
    student = Student(*user_data_old)
    id_student = select_id_student(pool, student)
    student = Student(*user_data_new)
    pool.execute_with_retries(
        f"""
        DECLARE $id AS Int16; 
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int16;
        
        UPSERT INTO Student(id, name, surname, father_name, id_group)
        VALUES ($id, $name, $surname, $father_name, $id_group)
        """,
        {
            '$id': id_student,
            '$name': student.name,
            '$surname': student.surname,
            '$father_name': student.father_name,
            '$id_group': student.id_group,
        }
    )

class ChangeAllData(ChangeUserData):
    def reply(self, request: Request, pool):
        new_data = request['request']['command']

        text = "Все данные успешно изменены!"
        return self.make_response(text=text, user_state_update={'user_data': new_data})

    def handle_local_intents(self, request: Request):
        pass




class ChangeName:
    pass


class ChangeSurname:
    pass


class ChangeFatherName:
    pass


class ChangeGroup:
    pass


class FindSchedule(Welcome):
    pass

class ChangeSchedule(Welcome):
    pass


class AddLesson(Welcome):
    pass

class GetHelpReg(GetHelpInGeneral):
    pass


class GetHelpFindSch(GetHelpInGeneral):
    pass


class GetHelpChangeData(GetHelpInGeneral):
    pass


class GetHelpChangeSch(GetHelpInGeneral):
    pass


class GetHelpAddSch(GetHelpInGeneral):
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
        ChangeAllData,
        ChangeName,
        ChangeSurname,
        ChangeFatherName,
        ChangeGroup,
        FindSchedule,
        ChangeSchedule,
        AddLesson,
        GetHelpReg,
        GetHelpFindSch,
        GetHelpChangeData,
        GetHelpChangeSch,
        GetHelpAddSch
    ]
}

DEFAULT_SCENE = Welcome
