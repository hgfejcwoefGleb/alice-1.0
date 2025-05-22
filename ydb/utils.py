from datetime import datetime

def make_readable(lessons_list: list[dict])-> str:
    text = ""
    #тут возможно придется поменять или как-то доставать имя предмета,
    #если он будет в нечитаемом виде
    for lesson in lessons_list:
        if lesson['auditorium'] != 'online':
            text += f"{lesson['name']} {lesson['type']} в {lesson['time']} в {lesson['auditorium']} аудитории в корпусе {lesson['building']}\n"
        else:
            text += f"{lesson['name']} {lesson['type']} в {lesson['time']} {lesson['auditorium']}\n"
    return text

def quarter():
    today = datetime.date.today()

    if datetime.date(2024, 3, 25) <= today <= datetime.date(2024, 6, 20):
        return 4
    elif datetime.date(2023, 12, 21) <= today <= datetime.date(2024, 3, 24):
        return 3
    elif datetime.date(2023, 10, 25) <= today <= datetime.date(2023, 12, 20):
        return 2
    else:
        return 1