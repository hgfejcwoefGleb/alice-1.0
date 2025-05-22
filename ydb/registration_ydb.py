from models import *
from obj_queries import *

import ydb


def registration_user(
    user_data: list,
    pool: ydb.QuerySessionPool,
    is_student=True,
    group_data: list = None,
):
    """Регистрирует пользователя и группу в БД."""
    if is_student:
        group = Group(*group_data)
        student = Student(*user_data)
        if not is_group_reg(pool, group):
            reg_group(pool, group)
            student.id_group = select_id_group(pool, group)
        if not is_student_reg(pool, student):
            reg_student(pool, student, student.id_group)
        else:
            return -1  
    else:
        lecturer = Lecturer(*user_data)
        if not is_lecturer_reg(pool, lecturer):
            reg_lecturer(pool, lecturer)
        else:
            return -1  


def reg_group(pool: ydb.QuerySessionPool, group: Group) -> None:
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
            "$name": group.name,
            "$edu_year": group.edu_year,
            "$edu_program": group.edu_program,
            "$faculty": group.faculty,
            "$edu_format": group.edu_format,
            "$edu_level": group.edu_level,
        },
    )


def reg_student(pool: ydb.QuerySessionPool, student: Student, id_group: int) -> None:
    pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;
        DECLARE $id_group AS Int64;

        INSERT INTO Student (name, surname, father_name, id_group)
        VALUES ($name, $surname, $father_name, $id_group);
        """,
        {
            "$name": student.name,
            "$surname": student.surname,
            "$father_name": student.father_name,
            "$id_group": (id_group, ydb.PrimitiveType.Int64),
        },
    )


def reg_lecturer(pool: ydb.QuerySessionPool, lecturer: Lecturer) -> None:
    pool.execute_with_retries(
        """
        DECLARE $name AS Utf8;
        DECLARE $surname AS Utf8;
        DECLARE $father_name AS Utf8;

        INSERT INTO Lecturer (name, surname, father_name)
        VALUES ($name, $surname, $father_name);
        """,
        {
            "$name": lecturer.name,
            "$surname": lecturer.surname,
            "$father_name": lecturer.father_name,
        },
    )
