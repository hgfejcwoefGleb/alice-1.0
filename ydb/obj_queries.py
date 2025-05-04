def get_group_records(pool: ydb.QuerySessionPool, group: Group, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $edu_year AS Utf8;

        SELECT {attr} FROM `Group`
        WHERE name = $name AND edu_year = $edu_year;
        """,
        {
            '$name': group.name,
            '$edu_year': group.edu_year,
        },
    )[0].rows

def select_id_group(pool: ydb.QuerySessionPool, group: Group)-> int:
    records = sorted(get_group_records(pool, group, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_group_reg(pool: ydb.QuerySessionPool, group: Group)-> bool:
    records = get_group_records(pool, group, True)
    return len(records) != 0

def get_lesson_records(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    unique_elem = ""
    table = ""
    if isinstance(lesson, GroupLesson):
        unique_elem = 'id_group'
        table = 'GroupLesson'
    if isinstance(lesson, PersonalLesson):
        unique_elem = 'id_student'
        table = 'PersonalLesson'
    return pool.execute_with_retries(
        f"""
            DECLARE ${unique_elem} AS Int64;
            DECLARE $lesson_date AS Date;
            DECLARE $time AS Utf8;

            SELECT {attr} FROM `{table}`
            WHERE {unique_elem} = ${unique_elem} AND lesson_date = $lesson_date AND time = $time;
            """,
        {
            f'${unique_elem}': (id_obj, ydb.PrimitiveType.Int64),
            '$lesson_date': (datetime.strptime(lesson.lesson_date, '%d.%m.%Y').date(), ydb.PrimitiveType.Date),
            '$time': lesson.time
        },
    )[0].rows

def select_id_lesson(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int)-> int:
    records = sorted(get_lesson_records(pool, lesson, id_obj, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_lesson_reg(pool: ydb.QuerySessionPool, lesson: Union[GroupLesson, PersonalLesson], id_obj: int)-> bool:
    records = get_lesson_records(pool, lesson, id_obj, True)
    return len(records) != 0

def get_student_records(pool: ydb.QuerySessionPool, student: Student, is_exist_check:bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int64;

        SELECT {attr} FROM `Student`
        WHERE name = $name AND surname = $surname AND father_name = $father_name AND id_group = $id_group;
        """,
        {
            '$name': student.name,
            '$surname': student.surname,
            '$father_name': student.father_name,
            '$id_group': (student.id_group, ydb.PrimitiveType.Int64),
        },
    )[0].rows

def select_id_student(pool: ydb.QuerySessionPool, student: Student)-> int:
    records = sorted(get_student_records(pool, student, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_student_reg(pool: ydb.QuerySessionPool, student: Student)-> bool:
    records = get_student_records(pool, student, True)
    return len(records) != 0

def get_lecturer_records(pool: ydb.QuerySessionPool, lecturer: Lecturer, is_exist_check: bool)-> list[ydb.convert._Row]:
    attr = 'id'
    if is_exist_check:
        attr = '1'
    return pool.execute_with_retries(
        f"""
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;

        SELECT {attr} FROM `Lecturer`
        WHERE name = $name AND surname = $surname AND father_name = $father_name;
        """,
        {
            '$name': lecturer.name,
            '$surname': lecturer.surname,
            '$father_name': lecturer.father_name,
        },
    )[0].rows

def select_id_lecturer(pool: ydb.QuerySessionPool, lecturer: Lecturer)-> int:
    records = sorted(get_lecturer_records(pool, lecturer, False), key=lambda x: x.id, reverse=True)
    return records[0].id

def is_lecturer_reg(pool: ydb.QuerySessionPool, lecturer: Lecturer)-> bool:
    records = get_lecturer_records(pool, lecturer, True)
    return len(records) != 0


def connect_lecturer_with_group(pool: ydb.QuerySessionPool, id_group: int, id_lecturer: int):
    res = (pool.execute_with_retries
        (
        """
        DECLARE $id_lecturer AS Int64;
        DECLARE $id_group AS Int64;

        SELECT 1 FROM `LecturerGroup`
        WHERE id_lecturer = $id_lecturer AND id_group = $id_group;
        """,
        {
            "$id_lecturer": (id_lecturer, ydb.PrimitiveType.Int64),
            "$id_group": (id_group, ydb.PrimitiveType.Int64)
        },
    ))
    if len(res[0].rows) == 0:
        pool.execute_with_retries(
            """
            DECLARE $id_lecturer AS Int64;
            DECLARE $id_group AS Int64;

            INSERT INTO LecturerGroup(id_lecturer, id_group)
            VALUES ($id_lecturer, $id_group);
            """,
            {
                "$id_lecturer": (id_lecturer, ydb.PrimitiveType.Int64),
                "$id_group": (id_group, ydb.PrimitiveType.Int64)
            },
        )

