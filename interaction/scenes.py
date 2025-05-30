from abc import ABC, abstractmethod
from datetime import datetime

import intents
from request import Request
from schedule_queries import (change_db_data, find_by_week_day_lesson_lecturer,
                              find_by_week_day_lesson_student,
                              find_lesson_lecturer, find_lesson_student,
                              insert_lesson)
from state import STATE_RESPONSE_KEY
from utils import make_readable

from registration_ydb import *
from registration_ydb import select_id_student
from news_title import news_title

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
        return self.make_response(
            text="Извини, я не поняла твою просьбу. Переформулируй запрос или уточни, что я умею."
        )

    def make_response(
        self,
        text,
        tts=None,
        card=None,
        state=None,
        buttons=None,
        user_state_update=None,
    ):
        """Возврат ответа навыку"""
        response = {"text": text, "tts": tts if tts is not None else text}
        if card is not None:
            response["card"] = card
        if buttons is not None:
            response["buttons"] = buttons
        webhook_response = {
            "response": response,
            "version": "1.0",
            STATE_RESPONSE_KEY: {"scene": self.id()},
            "user_state_update": {},
            "application_state": {},
        }
        if state is not None:
            webhook_response["session_state"].update(state)
        if user_state_update is not None:
            webhook_response["user_state_update"].update(user_state_update)
            if len(user_state_update) == 0:
                webhook_response["user_state_update"] = {}
        return webhook_response

    """Дальше нужно прописать сцены, которые есть у нашего навыка"""


def is_registered(request: Request):
    """Функция проверяет, что сессия данного пользователя/на данном устройстве новая"""
    return len(request["state"]["user"]) != 0


def is_student(request: Request):  
    return request["state"]["user"]["is_student"] == "студент"


class Welcome(Scene):
    def handle_global_intents(self, request: Request):
        if intents.GET_HELP_IN_GENERAL in request.intents:
            return GetHelpInGeneral()
        elif intents.RESET_DATA in request.intents:
            return ResetData()
        elif (
            intents.REGISTRATE in request.intents
            or not is_registered(request)
            or "is_student" not in request["state"]["user"]
        ):
            return Registration()
        elif (
            "user_data" not in request["state"]["user"]
            or "user_data" in request["state"]["user"]
            and len(request["state"]["user"]["user_data"]) == 0
        ):
            return Registration()
        elif "group_data" not in request["state"]["user"]:
            if is_student(request):
                return InsertGroupData()
            else:
                return IsStudent()
        elif intents.START_NEWS in request.intents:
            return StartNews()
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
        elif intents.GET_HELP_NEWS in request.intents:
            return GetHelpNews()
        

    def handle_local_intents(self, request: Request):
        pass

    def reply(self, request: Request, pool):
        text = (
            "Привет! Я могу помочь с расписанием студентов Вышки. "
            "Ты хочешь узнать своё расписание на сегодня, завтра или найти пару по названию? "
            "Если хочешь узнать, что я умею, попроси справку, сказав: Алиса, покажи справку."
        )
        return self.make_response(
            text=text,
            buttons=[
                {
                    "title": "Расписание ЕЛК",
                    "payload": {},
                    "url": "https://lk.hse.ru/schedule",
                    "hide": True,
                },
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )  


class ResetData(Welcome):
    def reply(self, request, pool):
        text = "Данные успешно сброшены"
        return self.make_response(text=text, user_state_update={"user_data": ""})

    def handle_local_intents(self, request):
        pass


class Fallback(Welcome):
    def reply(self, request, pool):
        return self.make_response(
            text="Извини, я не поняла твою просьбу. Переформулируй запрос или уточни, что я умею. ",
            buttons=[
                {"title": "Добавь предмет", "hide": True},
                {"title": "Поменять данные", "hide": True},
            ],
        )

    def handle_local_intents(self, request):
        if intents.ADD_LESSON in request.intents:
            return EnterIsGroupLessonInsert()


class Registration(Welcome):
    def reply(self, request: Request, pool):
        text = (
            "Чтобы узнать твое расписание мне нужно с тобой лучше познакомиться. "
            "Ты студент или преподаватель?"
        )
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Студент", "hide": True},
                {"title": "Преподаватель", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        return IsStudent()


class IsStudent(Registration):
    def reply(self, request: Request, pool):
        is_student = ""
        if (
            "is_student" not in request["state"]["user"]
            or "is_student" in request["state"]["user"]
            and len(request["state"]["user"]["is_student"]) == 0
        ):
            is_student = request["request"][
                "command"
            ]
        text = (
            "Отлично, теперь расскажи про себя. "
            "Как тебя зовут? Назови свои ФИО "
            "Если ты студент, то назови еще номер группы "
            'Только в формате: "Иванов Иван Иванович 22БИ3"'
        )
        return self.make_response(
            text=text, user_state_update={"is_student": is_student}
        )

    def handle_local_intents(self, request: Request):
        return InsertGroupData() if is_student(request) else InsertUserData()


class InsertNewGroupData(Registration):
    def reply(self, request: Request, pool):
        new_group_name = request["request"]["command"]
        user_data = f'{" ".join(request['state']['user']['user_data'].split()[:3])} {"".join(new_group_name.split())}'
        text = (
            "Хорошо, теперь назови год своего поступления,"
            "образовательную программу, факультет, формат обучения "
            "очный или нет и уровень образования в формате: "
            "2022 Бизнес-информатика Факультет Информатики математики и компьютерных наук очный бакалавриат"
        )
        return self.make_response(text=text, user_state_update={"user_data": user_data})

    def handle_local_intents(self, request: Request):
        return InsertUserData()


class InsertGroupData(Registration):
    def reply(self, request: Request, pool):
        user_data = request["state"]["user"].get("user_data", "")
        if (
            "user_data" not in request["state"]["user"]
            or "user_data" in request["state"]["user"]
            and len(request["state"]["user"]["user_data"]) == 0
        ):
            user_data = request["request"]["command"]
        text = (
            "Хорошо, теперь назови год своего поступления,"
            "образовательную программу, факультет, формат обучения "
            "очный или нет и уровень образования в формате: "
            "2022 Бизнес-информатика Факультет Информатики математики и компьютерных наук очный бакалавриат"
        )
        return self.make_response(text=text, user_state_update={"user_data": user_data})

    def handle_local_intents(self, request: Request):
        return InsertUserData()


class InsertUserData(Registration):
    def reply(self, request: Request, pool):
        group_data = ""
        if is_student(request):
            user_data = request["state"]["user"]["user_data"]
            group_name = "".join(user_data.split()[3:])
            edu_year = request.intents[intents.ENTER_GROUP_DATA]["slots"]["edu_year"][
                "value"
            ]
            edu_program = request.intents[intents.ENTER_GROUP_DATA]["slots"][
                "edu_program"
            ]["value"]
            faculty = request.intents[intents.ENTER_GROUP_DATA]["slots"]["faculty"][
                "value"
            ]
            edu_format = request.intents[intents.ENTER_GROUP_DATA]["slots"][
                "edu_format"
            ]["value"]
            edu_level = request.intents[intents.ENTER_GROUP_DATA]["slots"]["edu_level"][
                "value"
            ]
            group_data = [
                group_name,
                edu_year,
                edu_program,
                faculty,
                edu_format,
                edu_level,
            ]
            group = Group(*list(group_data))
            if is_group_reg(pool, group):
                id_group = select_id_group(pool, group)
                user_data = user_data.split()[:3]
                user_data.append(id_group)
            else:
                user_data = user_data.split()[:3]
                user_data.append(-1)
        else:
            user_data = request["request"]["command"].split()
        registration_user(user_data, pool, is_student(request), group_data)
        user_data[-1] = str(user_data[-1])
        text = "Очень приятно! Хочешь проверить свое расписание на сегодня, на какую-то другую дату или найти конкретный предмет?"
        return self.make_response(
            text=text,
            user_state_update={
                "user_data": " ".join(user_data),
                "group_data": group_data,
            },
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass


#
class GetHelpInGeneral(Welcome):
    """"""

    def reply(self, request: Request, pool):
        text = (
            "Привет, я помогу узнать расписание твоих дисциплин. "
            "Например, если ты хочешь узнать расписание по философии, то "
            'скажи: "Алиса когда у меня философия" или: Алиса, что у меня во вторник?. '
            " Я могу подсказать расписание на конкретную дату, день недели "
            "или у нужного преподавателя. Если хочешь узнать, когда у тебя пара "
            "с преподавателем, скажите, когда у меня пара с Владимиром Владимировым Владимиряном? "
            "Главное, чтобы фамилия была правильной. Чтобы поменять данные, "
            "скажи: хочу поменять данные. Чтобы добавить пару, скажи: "
            '"Алиса, добавь пару". Чтобы получить справку по конкретной функции: '
            '"Алиса, как мне изменить данные/зарегистрироваться/найти расписание/изменить расписание/добавить расписание/посмотреть новости"'

        )
        return self.make_response(
            text=text, buttons=[{"title": "Добавь предмет", "hide": True}]
        )

    def handle_local_intents(self, request: Request):
        if intents.GET_HELP_REG in request.intents:
            return GetHelpReg()
        elif intents.GET_HELP_FIND_SCH in request.intents:
            return GetHelpFindSch()
        elif intents.GET_HELP_CHANGE_DATA in request.intents:
            return GetHelpChangeData()
        elif intents.GET_HELP_CHANGE_SCH in request.intents:
            return GetHelpChangeSch()
        elif intents.GET_HELP_ADD_SCH in request.intents:
            return GetHelpAddSch()
        elif intents.ADD_LESSON in request.intents:
            return EnterIsGroupLessonInsert()


class ChangeUserData(Welcome):
    def reply(self, request: Request, pool):
        text = "Что ты хочешь поменять? Фамилию, имя, отчество номер группы или все в целом?"
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Фамилию", "hide": True},
                {"title": "Имя", "hide": True},
                {"title": "Отчество", "hide": True},
                {"title": "Группу", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        return EnterNewData()


class EnterNewData(ChangeUserData):

    def reply(self, request: Request, pool):
        text = "Хорошо, я поняла, сейчас сделаем. Назови свои новые данные."
        change_attr = "all"
        if intents.CHANGE_ALL_DATA in request.intents:
            change_attr = "all"
        elif intents.CHANGE_NAME in request.intents:
            change_attr = "name"
        elif intents.CHANGE_SURNAME in request.intents:
            change_attr = "surname"
        elif intents.CHANGE_FATHER_NAME in request.intents:
            change_attr = "father_name"
        elif intents.CHANGE_GROUP in request.intents:
            change_attr = "group"
        return self.make_response(
            text=text, user_state_update={"change_attr": change_attr}
        )

    def handle_local_intents(self, request: Request):
        change_attr = request["state"]["user"]["change_attr"]

        if change_attr == "all":
            return ChangeAllData()
        elif change_attr == "group":
            return InsertNewGroupData()
        else:
            return ChangeOneAttr()


class ChangeAllData(ChangeUserData):
    def reply(self, request: Request, pool):
        new_data = request["request"]["command"]
        text = "Прекрасно, новые данные я запомнила!"
        change_db_data(pool, request["state"]["user"]["user_data"], new_data)
        return self.make_response(
            text=text,
            user_state_update={"user_data": new_data},
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass


class ChangeOneAttr(ChangeUserData):
    def reply(self, request: Request, pool):
        self.attr_dict = {"surname": 0, "name": 1, "father_name": 2, "group": 3}
        change_attr = request["state"]["user"]["change_attr"]
        new_name = request["request"]["command"]
        text = "Хорошо, теперь запомнила твои новые данные!"
        old_data = request["state"]["user"]["user_data"]
        new_data = old_data.split()
        new_data[self.attr_dict[change_attr]] = new_name
        new_data = " ".join(new_data)
        change_db_data(pool, old_data, new_data)
        return self.make_response(
            text=text,
            user_state_update={"user_data": new_data},
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass




class EnterIsGroupLesson(Welcome):
    def reply(self, request: Request, pool):
        text = (
            "Предметы, которые хочешь найти связаны с конкретной образовательной программой "
            "Или это это майноры, английский и другие предметы, которые проводятся "
            "для разных групп?"
        )
        search_attr_val = request["request"]["command"]
        search_attr_name = request["request"]["command"]
        return self.make_response(
            text=text,
            user_state_update={
                "search_attr_val": search_attr_val,
                "search_attr_name": search_attr_name,
            },
            buttons=[
                {"title": "Групповой", "hide": True},
                {"title": "Индивидуальный", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        if is_student(request):
            return FindScheduleStudent()
        else:
            return FindScheduleLecturer()


class FindScheduleLessonName(Welcome):
    def reply(self, request, pool):
        text = "Хорошо, назови предмет, по которому хочешь найти пары"
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        if is_student(request):
            return FindScheduleByNameStudent()
        return FindScheduleByNameLecturer()


class FindScheduleByNameStudent(Welcome):
    def reply(self, request, pool):
        res = None
        search_attr_name = "name"
        search_attr_val = request["request"]["command"]
        student_data = request["state"]["user"]["user_data"].split()
        group_data = request["state"]["user"]["group_data"]
        student = Student(*student_data)
        group = Group(*group_data)
        id_student = select_id_student(pool, student)
        id_group = select_id_group(pool, group)
        res = find_lesson_student(
            pool, True, search_attr_name, search_attr_val, id_group, id_student
        )
        res.extend(
            find_lesson_student(
                pool, False, search_attr_name, search_attr_val, id_group, id_student
            )
        )
        text = "Конечно, вот расписание: "
        text = text + make_readable(res)
        if len(text) == len("Конечно, вот расписание: "):
            text = "У тебя нет пар"
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request):
        pass


class FindScheduleByNameLecturer(Welcome):
    def reply(self, request, pool):
        text = "Конечно, вот расписание: "
        search_attr_name = "name"
        search_attr_val = request["request"]["command"]
        lecturer_date = request["state"]["user"]["user_data"].split()[:3]
        lecturer = Lecturer(*lecturer_date)
        id_lecturer = select_id_lecturer(pool, lecturer)
        res = find_lesson_lecturer(
            pool, "GroupLesson", search_attr_name, search_attr_val, id_lecturer
        )
        print(f"GRoup{res}")
        print(
            find_lesson_lecturer(
                pool, "PersonalLesson", search_attr_name, search_attr_val, id_lecturer
            )
        )
        res.extend(
            find_lesson_lecturer(
                pool, "PersonalLesson", search_attr_name, search_attr_val, id_lecturer
            )
        )
        text = text + make_readable(res)
        if len(text) == len("Конечно, вот расписание: "):
            text = "У тебя нет пар"
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        pass


class FindScheduleStudent(Welcome):
    def reply(self, request: Request, pool):
        search_attr_name = "".join(
            request.intents[intents.FIND_SCHEDULE]["slots"].keys()
        )
        res = None
        text = "Конечно, вот расписание: "
        student_data = request["state"]["user"]["user_data"].split()
        group_data = request["state"]["user"]["group_data"]
        student = Student(*student_data)
        group = Group(*group_data)
        id_student = select_id_student(pool, student)
        id_group = select_id_group(pool, group)
        if search_attr_name == "today" or search_attr_name == "tomorrow":
            res = find_lesson_student(
                pool, True, search_attr_name, "", id_group, id_student
            )
            res.extend(
                find_lesson_student(
                    pool, False, search_attr_name, "", id_group, id_student
                )
            )
        elif search_attr_name == "lesson_date":
            search_attr_dict = request.intents[intents.FIND_SCHEDULE]["slots"][
                search_attr_name
            ]["value"]
            day = search_attr_dict["day"]
            month = search_attr_dict["month"]
            if "year" not in search_attr_dict.keys():
                year = datetime.now().year
            else:
                year = search_attr_dict["year"]
            search_attr_val = datetime.strptime(
                f"{day}.{month}.{year}", "%d.%m.%Y"
            ).date()
            res = find_lesson_student(
                pool, True, search_attr_name, search_attr_val, id_group, id_student
            )
            res.extend(
                find_lesson_student(
                    pool, False, search_attr_name, search_attr_val, id_group, id_student
                )
            )
        elif search_attr_name == "id_lecturer":
            lecturer_data_dict = request.intents[intents.FIND_SCHEDULE]["slots"][
                search_attr_name
            ]["value"]
            lecturer = Lecturer(
                *[
                    lecturer_data_dict["last_name"],
                    lecturer_data_dict["first_name"],
                    lecturer_data_dict["patronymic_name"],
                ]
            )
            search_attr_val = select_id_lecturer(pool, lecturer)
            res = find_lesson_student(
                pool, True, search_attr_name, search_attr_val, id_group, id_student
            )
            res.extend(
                find_lesson_student(
                    pool, False, search_attr_name, search_attr_val, id_group, id_student
                )
            )
        elif search_attr_name == "week_day":
            week_day = request.intents[intents.FIND_SCHEDULE]["slots"][
                search_attr_name
            ]["value"]
            res = find_by_week_day_lesson_student(
                pool, True, id_group, id_student, week_day
            )
            res.extend(
                find_by_week_day_lesson_student(
                    pool, False, id_group, id_student, week_day
                )
            )
        text = text + make_readable(res)
        if len(text) == len("Конечно, вот расписание: "):
            text = "У тебя нет пар"
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass


class FindScheduleLecturer(Welcome):
    def reply(self, request: Request, pool):
        text = "Конечно, вот расписание: "
        search_attr_name = "".join(
            request.intents[intents.FIND_SCHEDULE]["slots"].keys()
        )
        if search_attr_name == "lesson_date":
            search_attr_dict = request.intents[intents.FIND_SCHEDULE]["slots"][
                search_attr_name
            ]["value"]
            day = search_attr_dict["day"]
            month = search_attr_dict["month"]
            if "year" not in search_attr_dict.keys():
                year = datetime.now().year
            else:
                year = search_attr_dict["year"]
            search_attr_val = datetime.strptime(
                f"{day}.{month}.{year}", "%d.%m.%Y"
            ).date()
        else:
            search_attr_val = request.intents[intents.FIND_SCHEDULE]["slots"][
                search_attr_name
            ]["value"]
        lecturer_date = request["state"]["user"]["user_data"].split()[:3]
        lecturer = Lecturer(*lecturer_date)
        id_lecturer = select_id_lecturer(pool, lecturer)
        if search_attr_name == "week_day":
            res = find_by_week_day_lesson_lecturer(
                pool, "GroupLesson", search_attr_val, id_lecturer
            )
            res.extend(
                find_by_week_day_lesson_lecturer(
                    pool, "PersonalLesson", search_attr_val, id_lecturer
                )
            )
        else:
            res = find_lesson_lecturer(
                pool, "GroupLesson", search_attr_name, search_attr_val, id_lecturer
            )
            res.extend(
                find_lesson_lecturer(
                    pool,
                    "PersonalLesson",
                    search_attr_name,
                    search_attr_val,
                    id_lecturer,
                )
            )
        text = text + make_readable(res)
        if len(text) == len("Конечно, вот расписание: "):
            text = "У тебя нет пар"
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass


class EnterIsGroupLessonInsert(Welcome):
    def reply(self, request: Request, pool):
        text = (
            "Предметы, которые хочешь внести связаны с конкретной образовательной программой "
            "Или это это майноры, английский и другие предметы, которые проводятся "
            "для разных групп?"
        )
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Групповой", "hide": True},
                {"title": "Индивидуальный", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        return EnterLessonData()


class EnterLessonData(Welcome):
    def reply(self, request: Request, pool):
        is_group_lesson = (
            True
            if request.intents[intents.ENTER_IS_GROUP_LESSON_INSERT]["slots"].get(
                "group_lesson", 0
            )
            != 0
            else False
        )
        if not is_student(request) and is_group_lesson:
            text = "У какой группы будет проходить данный предмет. Назови название и год начала обучения?"
        else:
            text = (
                "Теперь расскажи все про предмет, "
                'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"'
            )
        return self.make_response(
            text=text, user_state_update={"is_group_lesson": is_group_lesson}
        )

    def handle_local_intents(self, request: Request):
        is_group_lesson = request["state"]["user"]["is_group_lesson"]
        if not is_student(request) and is_group_lesson:
            return IsGroupOfLectReg()
        return AddLesson()


class IsGroupOfLectReg(Welcome):
    def reply(self, request: Request, pool):
        if len(request["request"]["command"].split()) > 2:
            name, edu_year = (
                "".join(request["request"]["command"].split()[:3]),
                request["request"]["command"].split()[-1],
            )
        else:
            name, edu_year = request["request"]["command"].split()
        is_group_reg_v = "False"
        group = Group(name, edu_year)
        if is_group_reg(pool, group):
            text = (
                "Теперь расскажи все про предмет, "
                'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"'
            )
            is_group_reg_v = "True"
        else:
            text = (
                "Хорошо, теперь назови "
                "образовательную программу, факультет, формат обучения "
                "очный или нет и уровень образования в формате: "
                "Бизнес-информатика Факультет Информатики математики и компьютерных наук очный бакалавриат"
            )
        return self.make_response(
            text=text,
            user_state_update={
                "group_data": [name, edu_year],
                "is_group_reg": is_group_reg_v,
            },
        )

    def handle_local_intents(self, request):
        if request["state"]["user"]["is_group_reg"] == "True":
            return AddLesson()
        return RegGroupLect()


class RegGroupLect(Welcome):
    def reply(self, request, pool):
        group_data = request["state"]["user"]["group_data"]
        group_name, edu_year = group_data[0], group_data[1]
        edu_program = request.intents[intents.ENTER_GROUP_DATA]["slots"]["edu_program"][
            "value"
        ]
        faculty = request.intents[intents.ENTER_GROUP_DATA]["slots"]["faculty"]["value"]
        edu_format = request.intents[intents.ENTER_GROUP_DATA]["slots"]["edu_format"][
            "value"
        ]
        edu_level = request.intents[intents.ENTER_GROUP_DATA]["slots"]["edu_level"][
            "value"
        ]
        group_data = [group_name, edu_year, edu_program, faculty, edu_format, edu_level]
        group = Group(*group_data)
        reg_group(pool, group)
        text = (
            "Отлично, группа зарегистрирована. Теперь расскажи все про предмет, "
            'который хочешь добавить. Например, "Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"'
        )
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        return AddLesson()


class AddLesson(Welcome):

    def reply(self, request: Request, pool):
        lesson_data = request["request"]["command"].split()
        group_data = request["state"]["user"]["group_data"]
        group = Group(*group_data)
        is_group_lesson = request["state"]["user"]["is_group_lesson"]
        if is_student(request):
            student = Student(*request["state"]["user"]["user_data"].split())
            last_elem = int(
                select_id_group(pool, group)
                if is_group_lesson
                else select_id_student(pool, student)
            )
        else:
            last_elem = int(select_id_group(pool, group) if is_group_lesson else -1)
        print(len(lesson_data))
        diff = len(lesson_data) - 13
        lecturer_data = lesson_data[6 + diff : 9 + diff]
        if len(lesson_data) == 13:
            lesson_data = [
                lesson_data[0],
                lesson_data[1],
                lesson_data[3],
                lesson_data[4],
                0,
                "".join(lesson_data[9:11]) + "".join(lesson_data[11:12]),
                True,
                True,
                lesson_data[-1],
                last_elem,
            ]
        else:

            lesson_data = [
                " ".join(lesson_data[0 : diff + 1]),
                lesson_data[1 + diff],
                lesson_data[3 + diff],
                lesson_data[4 + diff],
                0,
                "".join(lesson_data[9 + diff : 11 + diff])
                + "".join(lesson_data[11 + diff : 12 + diff]),
                True,
                True,
                lesson_data[-1],
                last_elem,
            ]

        user_data = request["state"]["user"]["user_data"].split()  
        insert_lesson(
            pool,
            lesson_data,
            is_student(request),
            is_group_lesson,
            user_data,
            lecturer_data,
        )
        text = "Отлично, я запомнила новый предмет!"
        return self.make_response(
            text=text,
            buttons=[
                {"title": "Добавить предмет", "hide": True},
                {"title": "Расписание на завтра", "hide": True},
                {"title": "Какие пары сегодня", "hide": True},
            ],
        )

    def handle_local_intents(self, request: Request):
        pass


class ChangeSchedule(Welcome):
    # нужно написать функции для взаимодействия с самой БД
    pass


class GetHelpReg(GetHelpInGeneral):
    def reply(self, request: Request, pool):
        text = (
            "1.Когда я спрошу студент ли ты? Просто ответь: 'Я студент' или 'Я преподаватель'"
            "2.Когда захочу узнать про ФИО и номер группы, то если ты студент напиши: "
            "'Валерий Иванов Евгеньевич 22БИ3', группу указывай именно в таком формате, а не "
            "просто число "
            "3.Когда захочу подробнее узнать про тебя, если ты студент, то напиши: "
            "2022 Бизнес-информатика Информатики математики и компьютерных наук очный бакалавриат"
        )
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        pass


class GetHelpFindSch(GetHelpInGeneral):
    def reply(self, request, pool):
        text = (
            '1.Чтобы найти пары на сегодня/завтра спроси: "Алиса, какие пары сегодня/завтра?" '
            '2.Чтобы найти пары на день недели: "Какие пары во вторник?" '
            '3.Чтобы найти пары на конкретную дату: "Какие пары 21 апреля?" ' 
            '4.Чтобы узнать пары у конкретного препода: "Когда пары с Ивановым Иваном Ивановичем?" '
            "5.Чтобы узнать пары по названию предмета: Хочу узнать когда у меня конкретный предмет"
            'Когда я спрошу название предмета, то напиши его так, как указывал придобавлении: "Матанализ"'
        )
        return self.make_response(text=text)


class GetHelpChangeData(GetHelpInGeneral):
    def reply(self, request, pool):
        text = (
            'Чтобы изменить данные скажи, "Хочу поменять данные" '
            "Если хочешь изменить что-то одно, то напиши: "
            '"Изменить фамилию/имя/отчество/номер группы" или'
            'можно изменить все данные, сказав: "Измени все" '
            "Когда я попрошу назвать новые данные, то назоваи только новые данные: "
            '"Иванов", "Валерий", "Иванов Валерий Евпатиевич 22УБ3"'
        )
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        pass


class GetHelpChangeSch(GetHelpInGeneral):
    pass


class GetHelpAddSch(GetHelpInGeneral):
    def reply(self, request, pool):

        text = (
            "1.Когда я спрошу про то, связаны ли предметы с твоей ОП или это майнор,"
            'английский и тп, то просто ответь: "Групповой", если предмет связан с ОП'
            'или "Индивидуальный" '
            "2.Когда я попрошу указать все про предмет, то укажи его данные так: "
            '"Матанализ семинар корпус Родионова 303 аудитория Петренко Петр Петрович 12:00-13:20 12.04.2025"'
        )
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        pass

class GetHelpNews(GetHelpInGeneral):
    def reply(self, request, pool):
        pass

    def handle_local_intents(self, request):
        pass

class StartNews(Welcome):
    def reply(self, request, pool):
        text = "Привет! Я расскажу тебе о последних новостях Высшей Школы Экономики"
        one = "Давай определимся по какой рубрике ты хочешь узнать новость."
        two = "1.Поступающим, 2.Образование, 3.Наука, 4.Экспертиза, 5.Общество, 6.Свободное общение, 7.Университетская жизнь, 8.Приоритет 2030, 9.Программа развития 2030, 10.Все новости"
        three = "Скажи, пожалуйста, название выбранной рубрики:"
        text +=  f'{one} \n{two} \n{three}'
        return self.make_response(text=text)

    def handle_local_intents(self, request):
        return Headings()

class Headings(Welcome):
    def reply(self, request, pool):
        if intents.NEWS_TITLE in request.intents:
            type_chose = request.intents[intents.NEWS_TITLE]["slots"]['rubrics']['value']
        else:
            type_chose = request["state"]["user"]["type_chose"]
        headings_t, headings_l, subs, number_of_news = news_title(type_chose) # сказал название конкретной рубрики

        TEXT4 = "Отлично! Показываю тебе названия последних заголовков новостей по выбранной рубрике:"
        headings = ''
        for i in range(len(headings_t)):
            headings += str(i + 1) + '. ' + str(headings_t[i]) + '\n'
        TEXT4 += '\n' + headings + "\n" + 'Назови цифру новости, которую хочешь прочитать: ' #выводим пользователю (Тут в интентах надо добавить цифру от 1 до 7)
        return self.make_response(text = TEXT4, user_state_update = {'headings_t': headings_t, 'headings_l': headings_l, 'subs': subs, 'type_chose': type_chose, 'number_of_news': number_of_news})


    def handle_local_intents(self, request):
        return ResNews()

class ResNews(Welcome):
    def reply(self, request, pool):
        title_chose = request.intents[intents.RES_NEWS]['slots']['number']['value']
        headings_t = request["state"]["user"]['headings_t']
        headings_l = request["state"]["user"]['headings_l']
        subs = request["state"]["user"]['subs']
        number_of_news = request["state"]["user"]['number_of_news']
        if title_chose < 1 or title_chose > number_of_news:
            return self.make_response("Новости под такой цифрой нет. Назови, пожалуйста, цифру из тех, которые есть.")
        res_link = headings_l[title_chose - 1]
        title = headings_t[title_chose - 1]
        sub = subs[title_chose - 1]
        TEXT5 = f'Отлично! Показываю новость: \n{title}: \n{sub} \nТакже даю ссылку, если хочешь ознакомиться с новостью подробнее и посмотреть картинки: {res_link} \nЕсли хочешь посмотреть еще другую новость, скажи "Хочу посмотреть другую новость"'
        return self.make_response(TEXT5)

    def handle_local_intents(self, request):
        if intents.CONTIN_NEWS in request.intents:
            return StartNews()





SCENES = {
    scene.id(): scene
    for scene in [
        Welcome,
        Registration,
        IsStudent,
        InsertNewGroupData,
        InsertGroupData,
        InsertUserData,
        GetHelpInGeneral,
        ChangeUserData,
        EnterNewData,
        ChangeAllData,
        ChangeOneAttr,
        EnterIsGroupLesson,
        FindScheduleLessonName,
        FindScheduleByNameStudent,
        FindScheduleByNameLecturer,
        FindScheduleStudent,
        FindScheduleLecturer,
        EnterIsGroupLessonInsert,
        EnterLessonData,
        AddLesson,
        IsGroupOfLectReg,
        RegGroupLect,
        ChangeSchedule,
        GetHelpReg,
        GetHelpFindSch,
        GetHelpChangeData,
        GetHelpChangeSch,
        GetHelpAddSch,
        ResetData,
        StartNews,
        Headings,
        ResNews
    ]
}

DEFAULT_SCENE = Welcome
