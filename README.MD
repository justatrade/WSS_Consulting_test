# Сервис обработки заявок пользователей

## Описание проекта
Сервис для обработки заявок пользователей. Пользователи могут регистрироваться, аутентифицироваться, создавать, редактировать и закрывать заявки. Сервис поддерживает JWT-аутентификацию, отправку email для подтверждения регистрации и REST API для работы с заявками.

## Функциональные возможности
- Регистрация пользователей с подтверждением по email.
- Аутентификация пользователей через JWT (access и refresh токены).
- Создание, редактирование, закрытие и просмотр заявок.
- Просмотр списка заявок с пагинацией и сортировкой.
- Получение информации о текущем пользователе.

## Технологии и стек
- **Backend**: FastAPI
- **База данных**: PostgreSQL
- **ORM**: SQLAlchemy
- **Миграции**: Alembic
- **Аутентификация**: JWT
- **Контейнеризация**: Docker, Docker-compose
- **Управление зависимостями**: Poetry
- **Линтеры**: flake8, mypy, isort, pylint, black

## Инструкции по установке и запуску

### 1. Установка зависимостей
Убедитесь, что у вас установлены Docker и Docker-compose. Затем выполните:

```bash
docker-compose up --build
```

## Примеры использования API

### Endpoint'ы, доступные без JWT-токена

#### 1. Регистрация пользователя
Регистрация нового пользователя. После регистрации на email пользователя отправляется ссылка для подтверждения.

```bash
curl -X POST "http://localhost:8001/users/register" \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "password": "password"}'
```

#### 2. Аутентификация
Аутентификация пользователя. В ответ возвращаются access и refresh токены.

```bash
curl -X POST "http://localhost:8001/auth/login" \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "password": "password"}'
```

Пример ответа:

```json
{
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token",
  "token_type": "bearer"
}
```

#### 3. Подтверждение регистрации
Подтверждение регистрации по коду, отправленному на email.

```bash
curl -X POST \
  "http://localhost:8001/auth/confirm-login" \
  -H "accept: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

### Endpoint'ы, требующие JWT-токена
Для доступа к этим endpoint'ам необходимо добавить заголовок Authorization с JWT-токеном:
```bazaar
Authorization: Bearer <access_token>
```

#### 1. Получение информации о текущем пользователе
```bash
curl -X GET "http://localhost:8001/users/me" \
-H "Authorization: Bearer <access_token>"
```

#### 2. Создание заявки
```bash
curl -X POST "http://localhost:8001/tickets" \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{"title": "New Ticket", "description": "Some description"}'
```

#### 3. Получение списка заявок
```bash
curl -X GET "http://localhost:8001/tickets" \
-H "Authorization: Bearer <access_token>"
```

#### 4. Получение заявки по ID
```bash
curl -X GET "http://localhost:8001/tickets/1" \
-H "Authorization: Bearer <access_token>"
```

#### 5. Редактирование заявки
```bash
curl -X PUT "http://localhost:8001/tickets/1" \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{"title": "Updated Title", "description": "Updated description"}'
```

#### 6. Закрытие заявки
```bash
curl -X POST "http://localhost:8001/tickets/1/close" \
-H "Authorization: Bearer <access_token>"
```

#### 7. Обновление токенов
Используйте refresh токен для получения нового access токена.

```bash
curl -X POST "http://localhost:8001/auth/refresh" \
-H "Content-Type: application/json" \
-d '{"refresh_token": "your-refresh-token"}'
```

Пример ответа:

```json
{
  "access_token": "new-access-token",
  "token_type": "bearer"
}
```