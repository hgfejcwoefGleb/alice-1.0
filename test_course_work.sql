create table "Group"
(
	id serial primary key check (id > 0),
	name text not null,
	edu_year int not null,
	edu_program text not null, 
	faculty text not null, 
	edu_format text not null,
	edu_level text not null
);

create table Student
(
	id serial primary key check (id > 0),
	name text not null,
	surname text not null,
	father_name text,
	id_group int references "Group"(id) on update cascade on delete set null
);

create table Lecturer
(
	id serial primary key check (id > 0),
	name text not null, 
	surname text not null,
	father_name text not NULL
);

create table PersonalLesson
(
	id serial primary key check (id > 0),
	name text not null,
	type text not null,
	building text not null,
	auditorium text not null,
	id_lecturer int references Lecturer(id) on update cascade on delete set null,
	time text not null,
	week_day text not null,
	is_upper bool,
	lesson_date date, 
	id_student int references Student(id) on update cascade on delete cascade
);

create table PersonalLessonStudent
(
	id_student int references Student(id) on update cascade on delete cascade,
	id_personal_lesson int references Personal_lesson(id) on update cascade on delete cascade
);

create table GroupLesson
(
	id serial primary key check (id > 0),
	name text not null,
	type text not null,
	building text not null,
	auditorium text not null,
	id_lecturer int references Lecturer(id) on update cascade on delete set null,
	time text not null,
	week_day text not null,
	is_upper bool,
	lesson_date date,
	id_group int references "Group"(id) on update cascade on delete cascade
);

CREATE TABLE GroupLessonGroup
(
	id_group_lesson int not null references GroupLesson(id) on update cascade on delete cascade,
	id_group int not null references "Group"(id) on update cascade on delete cascade
);

CREATE TABLE LecturerGroup
(
	id_lecturer int NOT null references Lecturer(id) on update cascade on delete cascade,
	id_group int NOT null references "Group"(id) on update cascade on delete cascade
);