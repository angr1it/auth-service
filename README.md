# Auth Service

## Цель и задача
Auth Service выступает единым центром управления учётными записями, ролями и разрешениями
для многокомпонентной микросервисной архитектуры.

---

## Функциональность
- Аутентификация по email/паролю с использованием JWT (RS256)
- Регистрация организаций и создание владельца
- Приглашение пользователей по токену‑инвайту
- RBAC с хранением разрешений в JSON
- Проверка `perm_version` и отзыв токенов при изменении прав
- Refresh‑токены, хранимые и отзываемые в базе данных
- JWKS‑эндпоинт (`/.well‑known/jwks.json`) для верификации подписи

---

## Стек технологий
- Python 3.12
- FastAPI 0.111
- SQLAlchemy 2.0 (async)
- PostgreSQL 15+
- python‑jose + cryptography
- passlib[argon2] — безопасное хеширование паролей

---

## Архитектура и токены

### Access Token (JWT)
```json
{
  "sub": 1,
  "org": "org-slug",
  "login": "user1",
  "pv": 1,
  "iat": 1680000000,
  "exp": 1680003600,
  "jti": "..."
}
```
**Описание полей**  
`sub` — идентификатор пользователя  
`org` — идентификатор организации  
`login` — логин пользователя  
`pv` — версия разрешений (perm_version)  
`iat` — время выпуска (Unix‑timestamp)  
`exp` — время истечения (Unix‑timestamp)  
`jti` — уникальный идентификатор токена  

### Refresh Token
- Хранится в таблице `refresh_token`
- Отзыв выполняется установкой `revoked_at`
- Срок действия и связь с пользователем контролируются в БД

### Формат разрешений
```json
{
  "calls": ["READ", "WRITE"],
  "auth":  ["INVITE_USER", "DELETE_USER"]
}
```
Каждый ключ — ресурс/модуль, значение — список действий, разрешённых пользователю.

---


## Контракты API (основные)

### Аутентификация
- `POST /login/password` — вход по email/паролю
- `GET /login/refresh` — обновление access токена по refresh токену
- `POST /logout` — выход, отзыв refresh токена, очистка cookie

### Организации
- `POST /organization/create` — регистрация новой организации и владельца
- `POST /organization/invite` — инвайт нового пользователя (только ORG_OWNER)
- `POST /organization/register/{invite_token}` — регистрация по токену инвайта

### Пользователи и разрешения
- `GET /login/user` — текущий пользователь и его права
- `POST /organization/users` — список пользователей организации (пагинация)
- `POST /organization/users/{user_id}/permissions` — обновление прав пользователя

### Безопасность
- `GET /.well-known/jwks.json` — публичный ключ для верификации JWT

---

### Endpoint's

#### POST `/login/password`
```json
// запрос
{
  "email": "user@example.com",
  "password": "secret",
  "organizationId": "org-slug"
}

// ответ
{
  "accessToken": "<jwt>",
  "refreshToken": "<jwt>"
}
```
**Поля запроса**  
`email` — email пользователя  
`password` — пароль  
`organizationId` — slug организации  

**Поля ответа**  
`accessToken` — краткоживущий токен доступа  
`refreshToken` — долгоживущий токен обновления  


#### GET `/login/refresh`
Получает `refreshToken` из cookie, выдаёт новый `accessToken`.
Без тела запроса; тело ответа пустое — токен приходит в cookie.

#### POST `/logout`
Отзывает `refreshToken` (записывает `revoked_at`) и очищает оба cookie.

### Организации `/api/v1/organization`

#### POST `/organization/create`
```json
// запрос
{
  "organizationName": "Acme Corp",
  "organizationSlug": "acme-corp",
  "email": "owner@example.com",
  "login": "owner",
  "password": "secret",
  "operatorId": 42
}

// ответ
{
  "organizationId": "acme-corp"
}
```
**Поля запроса**  
`organizationName` — название организации  
`organizationSlug` — необязательный slug (строка ≤ 64 симв.)  
`email` — email владельца  
`login` — логин владельца  
`password` — пароль владельца  
`operatorId` — необязательный ID оператора  

**Поля ответа**  
`organizationId` — slug созданной организации  

#### POST `/organization/invite`
Только для владельцев (роль ORG_OWNER).  
Запрос (`InviteRequest`):  
```json
{
  "expiresInHours": 24,
  "operatorId": 100
}
```  
Ответ содержит `inviteToken` и URL для регистрации.

#### POST `/organization/register/{invite_token}`
```json
// запрос
{
  "email": "new@example.com",
  "login": "newuser",
  "password": "secret"
}

// ответ
{
  "id": 5
}
```
**Поля запроса**  
`email` — email пользователя  
`login` — логин пользователя  
`password` — пароль пользователя  

**Поля ответа**  
`id` — идентификатор созданного пользователя  

### Пользователи и разрешения

#### GET `/login/user`
Возвращает сведения о текущем пользователе и его разрешениях.

#### POST `/organization/users`
Параметры пагинации (`page`, `size`).  
Ответ — объект `PaginatedUsers` с полями `items`, `total`, `pages`.

#### POST `/organization/users/{user_id}/permissions`
Обновляет права конкретного пользователя. Тело запроса:
```json
{
  "permissions": {
    "calls": ["READ", "WRITE"]
  }
}
```

### Безопасность
`GET /.well-known/jwks.json` — возвращает публичный ключ для проверки подписи JWT.

---

## Обновление прав
- При изменении разрешений увеличивается `perm_version` пользователя.
- Если `pv` токена не совпадает с текущим `perm_version`, accessToken считается недействительным.

---

## Жизненный цикл пользователя
1. Владелец создаёт организацию (`/organization/create`).
2. Генерирует инвайт (`/organization/invite`).
3. Приглашённый пользователь регистрируется (`/organization/register/{token}`).
4. Авторизуется (`/login/password`).
5. Обновляет токен при необходимости (`/login/refresh`).
6. Получает свои данные (`/login/user`).

---

## Примечания
- JWT подписаны алгоритмом RS256.  
- Refresh‑токены дополнительно вали‑дируются по наличию в БД и признаку `revoked_at`.  
- Любой сервис может проверить подпись через JWKS‑эндпоинт.