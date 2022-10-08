# Социальная сеть для публикации личных дневников
## Спринт 6 — hw05_final

### Описание
Социальная сеть авторов с реализацией механизмов подписок на интересующих пользователей, организацией их в группы.

### Технологии
- Python 3.7
- Django 2.2.19
- Requests 2.26.0
- Pillow 9.0.1
- HTML 5.0
- CSS 3.0
- Bootstrap 5.0.1

### Запуск проекта в dev-режиме
Клонируем проект:
```git clone https://github.com/AnthonyHol/hw05_final.git
```

Переходим в папку с проектом и устанавливаем виртуальное окружение:
```python -m venv venv
```

Активируем виртуальное окружение:
```source venv/Scripts/activate
```

Устанавливаем зависимости:
`python -m pip install --upgrade pip`
`pip install -r requirements.txt`

Выполняем миграции:
`python yatube/manage.py makemigrations`
`python yatube/manage.py migrate`

Создаем суперпользователя:
`python yatube/manage.py createsuperuser`

В папку, где находится файл settings.py, добавляем файл .env, куда прописываем секретный ключ следующим образом:
`SECRET_KEY='Секретный ключ'`

Запускаем проект:
`python yatube/manage.py runserver`

Проект будет доступен по адресу `http://127.0.0.1:8000/`
Переход на админ-панель доступен по адресу `http://127.0.0.1:8000/admin/`

Автор: [Холкин Антон](https://github.com/AnthonyHol/ "Холкин Антон")
