# Документация API

Все эндпоинты доступны с префиксом `/api/v1`.

## Пример сценария работы
Ниже приведён один из базовых сценариев использования сервиса для управления
сотрудниками и их правами в организации:
1. **Создать организацию.** Отправить `POST /organization/create` с данными
   владельца.
2. **Войти под владельцем.** Выполнить `POST /login/password` и получить пары
   токенов в cookie.
3. **Пригласить сотрудника.** Запросить `POST /organization/invite` и передать
   `expiresInHours` и `operatorId`. Получить ссылку с токеном.
4. **Зарегистрировать сотрудника.** Новый пользователь отправляет `POST
   /organization/register/{invite_token}` со своими данными.
5. **Просмотреть список пользователей.** Владелец вызывает `POST
   /organization/users` и получает страницу пользователей.
6. **Выдать права пользователю.** Через `POST
   /organization/users/{user_id}/permissions` передаются новые разрешения.


## Аутентификация

### POST `/login/password`
Аутентификация по email/паролю.
**Тело запроса** (`LoginPasswordRequest`):
```json
{
  "email": "user@example.com",
  "password": "secret",
  "organizationId": "org-slug"
}
```
**Ответ**
```json
{
  "accessToken": "<jwt>",
  "refreshToken": "<jwt>"
}
```
В оба cookie помещаются выданные токены.

### GET `/login/refresh`
Обновление access token по refresh токену из cookie. Тело запроса отсутствует.
В ответе cookie `accessToken` перезаписывается. Тело ответа отсутствует.

### POST `/logout`
Отзыв refresh токена и очистка cookie.
Ответ: `{"detail": "ok"}`.

### GET `/login/user`
Текущий пользователь и его разрешения. Требуется заголовок `Authorization: Bearer <accessToken>`.
Ответ: объект `UserOutput`.
Пример:
```json
{
  "id": 1,
  "email": "owner@example.com",
  "login": "owner",
  "avatarUrl": null,
  "permissions": {
    "auth": ["OWNER"]
  },
  "permVersion": 1,
  "operatorId": 42
}
```

## Организации

### POST `/organization/create`
Создание организации и владельца.
**Тело запроса** (`OrganizationCreateRequest`):
```json
{
  "organizationName": "Acme Corp",
  "organizationSlug": "acme-corp",
  "email": "owner@example.com",
  "login": "owner",
  "password": "secret",
  "operatorId": 42
}
```
**Ответ**
```json
{
  "organizationId": "acme-corp"
}
```

### POST `/organization/invite`
Доступно только владельцу. Генерирует токен‑инвайт.
Тело запроса (`InviteRequest`):
```json
{
  "expiresInHours": 24,
  "operatorId": 100
}
```
Ответ содержит `inviteToken` и URL:
```json
{
  "inviteToken": "<token>",
  "url": "https://.../<token>"
}
```

### POST `/organization/register/{invite_token}`
Регистрация по токену‑инвайту.
Тело запроса (`RegisterRequest`):
```json
{
  "email": "new@example.com",
  "login": "newuser",
  "password": "secret"
}
```
**Ответ**
```json
{
  "id": 5
}
```

### POST `/organization/users`
Возвращает список пользователей организации. Тело запроса (`PaginationModel`)
со стандартными полями `page` и `size`.
Ответ: объект `PaginatedUsers`.
Пример:
```json
{
  "items": [
    {
      "id": 1,
      "email": "owner@example.com",
      "login": "owner",
      "avatarUrl": null,
      "permissions": {
        "auth": ["OWNER"]
      },
      "permVersion": 1,
      "operatorId": 42
    }
  ],
  "total": 1,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

### POST `/organization/users/{user_id}/permissions`
Обновление разрешений пользователя. Тело запроса (`PermissionEdit`):
```json
{
  "permissions": {
    "calls": ["READ", "WRITE"]
  }
}
```
Ответ: `200 OK` при успешном обновлении.
Пример:
```json
{
  "detail": "ok"
}
```

## Безопасность

### GET `/.well-known/jwks.json`
Публичный RSA‑ключ для проверки подписи JWT.
Ответ соответствует схеме `JWKS`.
Пример:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "alg": "RS256",
      "use": "sig",
      "n": "...",
      "e": "AQAB",
      "kid": "0"
    }
  ]
}
```