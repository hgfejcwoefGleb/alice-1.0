# Расписание ВШЭ для Алисы

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YDB](https://img.shields.io/badge/database-Yandex%20Database-important)](https://ydb.tech/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Голосовой навык для Алисы, помогающий студентам и преподавателям НИУ ВШЭ работать с расписанием занятий.

## 🔍 Возможности

- 📅 Просмотр расписания (сегодня/завтра/конкретная дата)
- 🔍 Поиск пар по названию предмета или преподавателю
- 👨‍🎓 Персонализация для студентов и преподавателей
- ✏️ Добавление новых занятий в расписание
- 🔄 Изменение персональных данных
- 📱 Поддержка голосовых и текстовых запросов

## 🛠 Технологии

- **Язык**: Python 3.8+
- **База данных**: Yandex Database (YDB)
- **Архитектура**: Сценарная модель (Finite State Machine)
- **Интеграция**: Яндекс Диалоги API

  🏗 Структура проекта

Или альтернативный вариант с подсветкой синтаксиса (если поддерживается):

````markdown
## 🏗 Структура проекта

```text
alice-1.0/
├── scenes/               # Диалоговые сценарии
│   ├── registration.py   # Регистрация пользователей
│   ├── schedule.py       # Работа с расписанием
│   └── ...               
├── ydb_queries/          # Запросы к YDB
│   ├── registration.py   # Регистрационные запросы
│   └── schedule.py       # Запросы расписания
├── state.py              # Управление состоянием
├── request.py            # Обработка запросов
├── handler.py            # Главный обработчик
└── requirements.txt      # Зависимости

📝 Примеры использования
Типовые запросы:
"Какие пары сегодня?"
"Когда у меня философия?"
"Покажи расписание на среду"
🛠 Разработка
Основные компоненты
Сценарии (scenes/):

Welcome - начальная сцена

Registration - регистрация пользователей

Schedule - работа с расписанием

Работа с YDB:

python
# Пример запроса
def find_lesson_student(pool, is_group, attr_name, attr_val, group_id, student_id):
    query = f"""
    SELECT * FROM lessons 
    WHERE {attr_name} = '{attr_val}' 
    AND group_id = {group_id}
    """
    return pool.retry_operation_sync(lambda s: s.transaction().execute(query))
