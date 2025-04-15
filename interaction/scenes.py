import sys
from abc import ABC, abstractmethod
import inspect
from request import Request
from state import STATE_RESPONSE_KEY
import intents
from registration_ydb import *


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
        raise NotImplementedError

    @abstractmethod
    def handle_global_intents(self, request: Request):
        raise NotImplementedError

    def fallback(self, request: Request):
        pass

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, user_state_update=None):
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


class Welcome(Scene):
    def handle_global_intents(self, request: Request):
        print(is_registered(request))
        if intents.GET_HELP in request.intents:
            return GetHelp()
        elif intents.REGISTRATE in request.intents or not is_registered(request):
            return Registration()
        elif intents.FIND_SCHEDULE in request.intents:
            return Find_schedule()

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
        print(user_data)  # здесь должно быть использование сущностей/интентов
        text = ('Хорошо, теперь назови год своего поступления,'
                'образовательную программу, факультет, формат обучения'
                'очный или нет и уровень образования')
        return self.make_response(text=text, user_state_update={'user_data': user_data})

    def handle_local_intents(self, request: Request):
        return InsertUserData()


class InsertUserData(Registration):
    def reply(self, request: Request, pool):
        group_data = []
        if is_student(request):
            user_data = request['state']['user']['user_data']
            # тут проверяем зарегана группа или нет
            group_data = request["request"]['command']
            group = Group(*group_data.split())
            if is_group_reg(pool, group):
                id_group = select_id_group(pool, group)
            user_data = user_data.split()[:3]
            user_data.append(id_group)
            # меняем id_group в сессии, если студент
        else:
            user_data = user_data.split()
        registration_user(user_data, pool, is_student(request), group_data)
        text = (
            'Очень приятно! Хочешь проверить свое расписание на сегодня, на какую-то другую дату или найти конкретный предмет?')
        return self.make_response(text=text, user_state_update={'user_data': " ".join(user_data)})

    def handle_local_intents(self, request: Request):
        pass


class GetHelp(Welcome):
    pass


class FindSchedule(Welcome):
    pass


SCENES = {
    scene.id(): scene for scene in [Welcome, Registration, IsStudent, InsertUserData, GetHelp, FindSchedule]
}

DEFAULT_SCENE = Welcome