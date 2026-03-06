# Rental

Система учёта аренды: автомобили, бронирования, арендаторы, доходы и расходы. Backend на Django, REST API, админка с темой django-admin-interface. Публичный интерфейс в разработке — доступна заглушка и админ-панель.

## Стек

- **Backend:** Django 5, DRF, Djoser (JWT), PostgreSQL 14
- **Админка:** django-admin-interface (кастомная тема)
- **Фронт:** заглушка (статическая страница со ссылкой на админку)
- **Инфраструктура:** Docker Compose, Nginx как единая точка входа

## Требования

- Docker и Docker Compose
- Файл `.env` в корне проекта (скопируйте из `.env.example` и при необходимости измените значения)

## Быстрый старт

1. Создайте `.env` в корне (скопируйте из `.env.example` и при необходимости измените значения).
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

- Сайт: **http://localhost:8000/** (заглушка и ссылка на админку).
- Админка: **http://localhost:8000/admin/**.

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
| `DATABASE_SQLITE` | `False` — использовать Postgres |

## Структура проекта

- `backend/` — Django-приложение (users, fleet, bookings, finance, api, core)
- `frontend_stub/` — статическая заглушка для корня сайта
- `nginx/` — конфигурация и образ Nginx (gateway)
- `backend/fixtures/` — фикстуры (в т.ч. тема админки)
