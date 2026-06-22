# Rental

Система учёта аренды автомобилей и жилья: бронирования, арендаторы, доходы и расходы.

**Production:** https://dfrental.net (backend и админ-панель)

Backend на Django. Основной интерфейс для работы — **Django Admin** (django-admin-interface). Аутентификация через стандартный вход в админку (сессии Django). Публичный каталог в разработке — на production доступна заглушка и админ-панель.

## Стек

- **Backend:** Django 5, PostgreSQL 14
- **Админка:** django-admin-interface (кастомная тема)
- **Аутентификация:** Django Admin (сессии)
- **Фронт:** заглушка (статическая страница со ссылкой на админку)
- **Инфраструктура:** Docker Compose, Nginx, Gunicorn

## Требования

- Docker и Docker Compose
- **PostgreSQL 14+** (обязательно; SQLite не поддерживается — защита от пересечения бронирований реализована через PostgreSQL `ExclusionConstraint` на диапазонах дат)
- Файл `.env` в корне проекта (скопируйте из `.env.example` и при необходимости измените значения)

## Быстрый старт

1. Создайте `.env` в корне (скопируйте из `.env.example`, убедитесь, что `DATABASE_SQLITE=False` или переменная не задана).
2. Соберите и запустите контейнеры:

   ```bash
   docker compose up -d --build
   ```

3. Примените миграции и загрузите тему админки:

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py loaddata admin_interface_theme_rental
   docker compose exec backend python manage.py collectstatic --noinput
   ```

4. Создайте суперпользователя (если ещё не создан):

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

- Сайт: **http://localhost:8000/** (заглушка и ссылка на админку)
- Админка: **http://localhost:8000/admin/**

## Переменные окружения

Основные переменные задаются в `.env` (образец — `.env.example`):

| Переменная | Описание |
|------------|----------|
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Подключение к PostgreSQL (контейнер `db`) |
| `DB_HOST`, `DB_PORT` | Хост и порт БД (`db`, `5432` в Docker) |
| `SECRET_KEY` | Секретный ключ Django |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты через запятую |
| `CSRF_TRUSTED_ORIGINS` | Доверенные источники для CSRF |

## Особенности

- **Бронирования:** защита от пересечения дат на уровне БД (PostgreSQL `ExclusionConstraint`) и в сервисном слое (валидации в Python)
- **Финансы:** мультивалютный учёт доходов и расходов (USD / PESO)
- **Деплой:** CI/CD (GitHub Actions), автодеплой на VPS

## Структура проекта

- `backend/` — Django-приложение (users, fleet, properties, bookings, finance, public, core)
- `frontend_stub/` — статическая заглушка для корня сайта
- `nginx/` — конфигурация и образ Nginx (gateway)
- `backend/fixtures/` — фикстуры (в т.ч. тема админки)