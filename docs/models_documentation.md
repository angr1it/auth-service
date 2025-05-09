# Документация по моделям и связям

## Общая структура

Проект использует SQLAlchemy ORM с декларативной моделью (`declarative_base`) и асинхронной сессией.
Модели представляют пользователей, организации, ресурсы, разрешения и связанные токены.

---

## Схема связей

| Модель               | Поле              | Ссылается на                  | Тип связи           | Назначение |
|----------------------|-------------------|-------------------------------|----------------------|------------|
| `User`               | `organization_id` | `Organization.id`             | many-to-one          | Пользователь состоит в организации |
| `UserPermission`     | `user_id`         | `User.id`                     | many-to-one          | Промежуточная таблица many-to-many |
|                      | `permission_id`   | `Permission.id`               | many-to-one          | Промежуточная таблица many-to-many |
| `Permission`         | `resource_id`     | `Resource.id`                 | many-to-one          | Разрешение привязано к ресурсу |
| `RefreshToken`       | `user_id`         | `User.id`                     | many-to-one          | Один пользователь имеет множество refresh-токенов |
| `RegistrationToken`  | `organization_id` | `Organization.id`             | many-to-one          | Токен инвайта в организацию |
|                      | `created_by`      | `User.id`                     | many-to-one          | Кто создал инвайт |

---

## Описание моделей

### Organization

```python
class Organization(Base):
    id: str
    name: str | None
    users: list[User]
    registration_tokens: list[RegistrationToken]
```

- **users** — все пользователи, принадлежащие организации.
- **registration_tokens** — инвайт-токены, связанные с организацией.

---

### User

```python
class User(Base):
    id: int
    organization_id: str
    email: str
    login: str
    password_hash: str
    permissions: list[UserPermission]
    refresh_tokens: list[RefreshToken]
    created_registration_tokens: list[RegistrationToken]
```

- **permissions** — список разрешений через `UserPermission`.
- **refresh_tokens** — токены для обновления JWT.
- **created_registration_tokens** — токены, созданные этим пользователем.

---

### Permission

```python
class Permission(Base):
    id: int
    resource_id: int
    code: str
    description: str | None
    users: list[UserPermission]
```

- **resource** — указывает, к какому ресурсу относится разрешение.
- Уникальность обеспечивается по паре `(resource_id, code)`.

---

### Resource

```python
class Resource(Base):
    id: int
    name: str
    description: str | None
    permissions: list[Permission]
```

- **permissions** — все разрешения, связанные с ресурсом.

---

### UserPermission

```python
class UserPermission(Base):
    id: int
    user_id: int
    permission_id: int
```

- **user** и **permission** — связи many-to-one.
- Ограничение уникальности `(user_id, permission_id)`.

---

### RefreshToken

```python
class RefreshToken(Base):
    jti: str
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None
```

- Хранит информацию о JWT refresh токенах.

---

### RegistrationToken

```python
class RegistrationToken(Base):
    jti: str
    organization_id: str
    created_by: int
    expires_at: datetime
    used_at: datetime | None
```

- **organization** — к какой организации принадлежит.
- **creator** — кто создал инвайт.

---

## Ограничения целостности

- Уникальные ключи:
  - `Permission`: (`resource_id`, `code`)
  - `UserPermission`: (`user_id`, `permission_id`)
- `cascade="all, delete-orphan"` используется для зависимых списков.


## Обзор связей

### 1. `User` — `Organization`
- **Тип:** many-to-one
- **Колонка:** `User.organization_id → Organization.id`
- **Связи:**
  - `User.organization` ←→ `Organization.users`
- **Описание:** Пользователь принадлежит одной организации, организация содержит много пользователей.
- **Каскад:** (опционально) `cascade="all, delete-orphan"` на стороне `Organization.users`.

---

### 2. `User` — `UserPermission` — `Permission` (many-to-many)
- **Тип:** many-to-many через промежуточную таблицу `UserPermission`
- **Колонки:**
  - `UserPermission.user_id → User.id`
  - `UserPermission.permission_id → Permission.id`
- **Связи:**
  - `User.permissions` ←→ `UserPermission.user`
  - `Permission.users` ←→ `UserPermission.permission`
- **Описание:** Пользователь может иметь множество разрешений, каждое разрешение — у многих пользователей.
- **Ограничение:** `UniqueConstraint("user_id", "permission_id")` в `UserPermission`
- **Каскад:** `cascade="all, delete-orphan"` на обеих сторонах.

---

### 3. `Permission` — `Resource`
- **Тип:** many-to-one
- **Колонка:** `Permission.resource_id → Resource.id`
- **Связи:**
  - `Permission.resource` ←→ `Resource.permissions`
- **Описание:** Каждое разрешение относится к ресурсу (например, `read:document`)
- **Ограничение:** `UniqueConstraint("resource_id", "code")`

---

### 4. `RefreshToken` — `User`
- **Тип:** many-to-one
- **Колонка:** `RefreshToken.user_id → User.id`
- **Связи:**
  - `RefreshToken.user` ←→ `User.refresh_tokens`
- **Описание:** Пользователь может иметь несколько refresh-токенов (JWT).
- **Каскад:** `cascade="all, delete-orphan"` у `User.refresh_tokens`.

---

### 5. `RegistrationToken` — `Organization`
- **Тип:** many-to-one
- **Колонка:** `RegistrationToken.organization_id → Organization.id`
- **Связи:**
  - `RegistrationToken.organization` ←→ `Organization.registration_tokens`
- **Описание:** Организация имеет инвайт-токены для регистрации новых пользователей.
- **Каскад:** `cascade="all, delete-orphan"` у `Organization.registration_tokens`.

---

### 6. `RegistrationToken` — `User` (creator)
- **Тип:** many-to-one
- **Колонка:** `RegistrationToken.created_by → User.id`
- **Связи:**
  - `RegistrationToken.creator` ←→ `User.created_registration_tokens`
- **Описание:** Хранится информация о том, кто сгенерировал инвайт.
- **Каскад:** Не требуется — инвайт может жить дольше пользователя.

---

## 💡 Бизнес-логика, отражённая в связях

- Пользователь должен принадлежать организации.
- Разрешения задаются через промежуточную таблицу `UserPermission`, обеспечивая расширяемость.
- Каждое разрешение привязано к конкретному ресурсу (например, `edit:project`).
- Refresh-токены позволяют реализовать logout/revoke по JWT.
- Registration-токены позволяют реализовать инвайты и массовую регистрацию.

---

## 🛠️ Ограничения целостности

- `Permission`: уникальная пара `(resource_id, code)`
- `UserPermission`: уникальная пара `(user_id, permission_id)`
- Все `relationship(..., back_populates=...)` строго симметричны.
- Используется `cascade="all, delete-orphan"` в связях списков зависимостей.

## Итоги

Модель отражает следующую бизнес-логику:

- Пользователь состоит в организации.
- У пользователя есть доступ к разрешениям через ресурсы.
- Разрешения привязаны к конкретным действиям над ресурсами.
- Все связи двусторонние и согласованы через `relationship(..., back_populates=...)`.