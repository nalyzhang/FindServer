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