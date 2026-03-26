### Локальное развертывание проекта

**Необходимые компоненты**
- Python 3.9+
- PostgreSQL 13+
- Виртуальное окружение (рекомендуется)

### 1. Настройка бэкенда
```bash
# Клонирование репозитория
git clone https://github.com/nalyzhang/FindServer.git
cd findproject

# Создание и активация виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# или venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env согласно вашей конфигурации
cd findproject

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Импорт списка ингредиентов
python manage.py import_ingredients

# Запуск сервера разработки
python manage.py runserver
```

### 2. Статика приложения

```bash
# Сбор статики
python manage.py collectstatic
```

### Доступ к приложению

- Бэкенд: http://localhost:8000

- Админка: http://localhost:8000/admin


# Форматы запросов и ответов API FindThePlace

## Регистрация пользователя
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/auth/users/`

**JSON-запрос:**
```json
{
    "username": "abc",
    "email": "abc@example.com",
    "password": "pass_0123",
    "first_name": "AB",
    "last_name": "C"
}
```

**JSON-ответ:**
```json
{
    "username": "abc",
    "last_name": "C",
    "first_name": "AB",
    "email": "abc@example.com",
    "id": 2
}
```

---

## Получение списка пользователей
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/auth/users/`

**JSON-ответ:**
```json
[
    {
        "id": 2,
        "username": "abc",
        "email": "abc@example.com",
        "first_name": "AB",
        "last_name": "C",
        "avatar": null,
        "avatar_url": null,
        "is_friend": false
    },
    {
        "id": 3,
        "username": "abcd",
        "email": "abcd@example.com",
        "first_name": "AB",
        "last_name": "CD",
        "avatar": null,
        "avatar_url": null,
        "is_friend": false
    },
    {
        "id": 1,
        "username": "admin",
        "email": "admin@find.ru",
        "first_name": "admin",
        "last_name": "admin",
        "avatar": null,
        "avatar_url": null,
        "is_friend": true
    }
]
```

---

## Получение токена (вход в аккаунт)
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/auth/token/login/`

**JSON-запрос:**
```json
{
    "email": "abc@example.com",
    "password": "pass_0123"
}
```

**JSON-ответ:**
```json
{
    "auth_token": "941931940cbb4869840842da3b90e1eaa2ba0774"
}
```

---

## Удаление токена (выход из аккаунта)
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/auth/token/logout/`

**JSON-запрос:**
```json
{
    "email": "abc@example.com",
    "password": "pass_0123"
}
```

---

## Смена пароля
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/auth/users/set_password/`

**JSON-запрос:**
```json
{
    "current_password": "pass_000123",
    "new_password": "password000123"
}
```

---

## Получение списка пользователей (исключая текущего)
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/users/`

**JSON-ответ:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 2,
            "username": "abc",
            "email": "abc@example.com",
            "first_name": "AB",
            "last_name": "C",
            "avatar": null,
            "avatar_url": null,
            "is_friend": false
        },
        {
            "id": 1,
            "username": "admin",
            "email": "admin@find.ru",
            "first_name": "admin",
            "last_name": "admin",
            "avatar": null,
            "avatar_url": null,
            "is_friend": true
        }
    ]
}
```

---

## Получение текущего профиля
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/auth/users/me/`

**JSON-ответ:**
```json
{
    "id": 3,
    "username": "abcd",
    "email": "abcd@example.com",
    "first_name": "AB",
    "last_name": "CD",
    "avatar": null,
    "avatar_url": null,
    "is_friend": false
}
```

---

## Получение профиля пользователя по ID
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/auth/users/1/`

**JSON-ответ:**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@find.ru",
    "first_name": "admin",
    "last_name": "admin",
    "avatar": null,
    "avatar_url": null,
    "is_friend": false
}
```

---

## Добавление в друзья по ID
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/users/1/friend/`

**JSON-ответ:**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@find.ru",
    "first_name": "admin",
    "last_name": "admin",
    "avatar": null,
    "avatar_url": null,
    "is_friend": true,
    "routes": [],
    "routes_count": 0
}
```

---

## Удаление из друзей по ID
- **Метод:** DELETE
- **URL:** `http://127.0.0.1:8000/api/v1/users/1/friend/`

---

## Получение списка друзей
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/users/friendslist/`

**JSON-ответ:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@find.ru",
            "first_name": "admin",
            "last_name": "admin",
            "avatar": null,
            "avatar_url": null,
            "is_friend": true
        }
    ]
}
```

---

## Создание локации
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/locations/`

**JSON-запрос:**
```json
{
    "latitude": 55.751244,
    "longitude": 37.618423,
    "radius": 100,
    "address": "Красная площадь, Москва",
    "time": "2024-03-26T10:00:00Z"
}
```

**JSON-ответ:**
```json
{
    "id": 1,
    "latitude": 55.751244,
    "longitude": 37.618423,
    "radius": 100.0,
    "address": "Красная площадь, Москва",
    "time": "2024-03-26T13:00:00+03:00"
}
```

---

## Создание маршрута
- **Метод:** POST
- **URL:** `http://127.0.0.1:8000/api/v1/routes/`

**JSON-запрос:**
```json
{
    "start_id": 3,
    "finish_id": 4,
    "distance": 1800,
    "time": "00:35:15",
    "date": "2024-03-26"
}
```

**JSON-ответ:**
```json
{
    "id": 2,
    "start": {
        "id": 3,
        "latitude": 59.941099,
        "longitude": 30.313698,
        "radius": 200.0,
        "address": "Эрмитаж, Санкт-Петербург",
        "time": "2024-03-26T15:00:00+03:00"
    },
    "finish": {
        "id": 4,
        "latitude": 59.950495,
        "longitude": 30.316612,
        "radius": null,
        "address": "Петропавловская крепость, Санкт-Петербург",
        "time": "2024-03-26T16:00:00+03:00"
    },
    "distance": 1800.0,
    "time": "00:35:15",
    "date": "2024-03-26"
}
```

---

## Получение списка маршрутов
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/routes/`

**JSON-ответ:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "start": {
                "id": 1,
                "latitude": 55.751244,
                "longitude": 37.618423,
                "radius": 100.0,
                "address": "Красная площадь, Москва",
                "time": "2024-03-26T13:00:00+03:00"
            },
            "finish": {
                "id": 2,
                "latitude": 55.734768,
                "longitude": 37.606783,
                "radius": 150.0,
                "address": "Парк Горького, Москва",
                "time": "2024-03-26T14:00:00+03:00"
            },
            "distance": 2500.0,
            "time": "00:45:30",
            "date": "2024-03-26"
        },
        {
            "id": 2,
            "start": {
                "id": 3,
                "latitude": 59.941099,
                "longitude": 30.313698,
                "radius": 200.0,
                "address": "Эрмитаж, Санкт-Петербург",
                "time": "2024-03-26T15:00:00+03:00"
            },
            "finish": {
                "id": 4,
                "latitude": 59.950495,
                "longitude": 30.316612,
                "radius": null,
                "address": "Петропавловская крепость, Санкт-Петербург",
                "time": "2024-03-26T16:00:00+03:00"
            },
            "distance": 1800.0,
            "time": "00:35:15",
            "date": "2024-03-26"
        }
    ]
}
```

---

## Получение маршрута по ID
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/routes/1/`

**JSON-ответ:**
```json
{
    "id": 1,
    "start": {
        "id": 1,
        "latitude": 55.751244,
        "longitude": 37.618423,
        "radius": 100.0,
        "address": "Красная площадь, Москва",
        "time": "2024-03-26T13:00:00+03:00"
    },
    "finish": {
        "id": 2,
        "latitude": 55.734768,
        "longitude": 37.606783,
        "radius": 150.0,
        "address": "Парк Горького, Москва",
        "time": "2024-03-26T14:00:00+03:00"
    },
    "distance": 2500.0,
    "time": "00:45:30",
    "date": "2024-03-26"
}
```

---

## Удаление маршрута по ID
- **Метод:** DELETE
- **URL:** `http://127.0.0.1:8000/api/v1/routes/2/`

---

## Получение статистики пользователя по ID
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/users/1/statistic`

**JSON-ответ:**
```json
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@find.ru",
        "first_name": "admin",
        "last_name": "admin",
        "avatar": null,
        "avatar_url": null,
        "is_friend": true
    },
    "routes": [
        {
            "id": 5,
            "start": {
                "id": 7,
                "latitude": 39.955223,
                "longitude": 43.401875,
                "radius": 300.0,
                "address": "Олимпийский парк, Сочи",
                "time": "2024-03-26T10:00:00+03:00"
            },
            "finish": {
                "id": 8,
                "latitude": 39.724858,
                "longitude": 43.577297,
                "radius": 180.0,
                "address": "Дендрарий, Сочи",
                "time": "2024-03-26T11:30:00+03:00"
            },
            "distance": 19500.0,
            "time": "02:45:20",
            "date": "2024-03-27"
        }
    ],
    "routes_count": 1,
    "average_radius": 300.0
}
```

---

## Получение статистики текущего пользователя
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/users/me/statistic`

**JSON-ответ:**
```json
{
    "user": {
        "id": 3,
        "username": "abcd",
        "email": "abcd@example.com",
        "first_name": "AB",
        "last_name": "CD",
        "avatar": null,
        "avatar_url": null,
        "is_friend": false
    },
    "routes": [
        {
            "id": 1,
            "start": {
                "id": 1,
                "latitude": 55.751244,
                "longitude": 37.618423,
                "radius": 100.0,
                "address": "Красная площадь, Москва",
                "time": "2024-03-26T13:00:00+03:00"
            },
            "finish": {
                "id": 2,
                "latitude": 55.734768,
                "longitude": 37.606783,
                "radius": 150.0,
                "address": "Парк Горького, Москва",
                "time": "2024-03-26T14:00:00+03:00"
            },
            "distance": 2500.0,
            "time": "00:45:30",
            "date": "2024-03-26"
        },
        {
            "id": 4,
            "start": {
                "id": 3,
                "latitude": 59.941099,
                "longitude": 30.313698,
                "radius": 200.0,
                "address": "Эрмитаж, Санкт-Петербург",
                "time": "2024-03-26T15:00:00+03:00"
            },
            "finish": {
                "id": 4,
                "latitude": 59.950495,
                "longitude": 30.316612,
                "radius": null,
                "address": "Петропавловская крепость, Санкт-Петербург",
                "time": "2024-03-26T16:00:00+03:00"
            },
            "distance": 5.0,
            "time": "01:13:52",
            "date": "2025-11-11"
        }
    ],
    "routes_count": 2,
    "average_radius": 150.0
}
```

---

## Получение статистик друзей
- **Метод:** GET
- **URL:** `http://127.0.0.1:8000/api/v1/users/statistics`

**JSON-ответ:**
```json
{
    "count": 1,
    "results": [
        {
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@find.ru",
                "first_name": "admin",
                "last_name": "admin",
                "avatar": null,
                "avatar_url": null,
                "is_friend": true
            },
            "routes": [
                {
                    "id": 5,
                    "start": {
                        "id": 7,
                        "latitude": 39.955223,
                        "longitude": 43.401875,
                        "radius": 300.0,
                        "address": "Олимпийский парк, Сочи",
                        "time": "2024-03-26T10:00:00+03:00"
                    },
                    "finish": {
                        "id": 8,
                        "latitude": 39.724858,
                        "longitude": 43.577297,
                        "radius": 180.0,
                        "address": "Дендрарий, Сочи",
                        "time": "2024-03-26T11:30:00+03:00"
                    },
                    "distance": 19500.0,
                    "time": "02:45:20",
                    "date": "2024-03-27"
                }
            ],
            "routes_count": 1
        }
    ]
}
```