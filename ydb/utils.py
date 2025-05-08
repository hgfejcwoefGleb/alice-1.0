def make_readable(lessons_list: list[dict])-> str:
    text = ""
    #тут возможно придется поменять или как-то доставать имя предмета,
    #если он будет в нечитаемом виде
    for lesson in lessons_list:
        if lesson['auditorium' != 'online']:
            text += f"{lesson['name']} {lesson['type']} в {lesson['time']} в {lesson['auditorium']} аудитории в корпусе {lesson['building']}\n"
        else:
            text += f"{lesson['name']} {lesson['type']} в {lesson['time']} {lesson['auditorium']}\n"
    return text