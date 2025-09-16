# Личный Финансовый Менеджер

## Краткое описание

Этот проект реализует сервис управления личными финансами на базе FastAPI, SQLModel, PostgreSQL и Alembic. Включает регистрацию/авторизацию пользователей, JWT-аутентификацию, управление доходами/расходами, бюджетами, целями и визуальный дашборд на главной странице.

---

## Ключевые файлы и структура

```
app/
  main.py                # Точка входа FastAPI, подключение роутеров и шаблонов
  templates/index.html   # Главная страница: логин, дашборд, JS-логика
  api/v1/                # Все основные API (users, finances, budgets, goals, categories)
  models/                # ORM-модели (User, Finance, Budget, Goal, Category)
  schemas/               # Pydantic-схемы для валидации и сериализации
  core/                  # Конфиг, безопасность (JWT, hash)
  db/                    # Сессия, инициализация, base для Alembic
```

---

## Ключевые моменты кода

### 1. Авторизация и JWT

- `app/api/v1/user.py`:
  - Регистрация: POST `/api/v1/users/register` — принимает UserCreate, возвращает UserRead
  - Логин: POST `/api/v1/users/login` — принимает username/password, возвращает access_token (JWT)
  - Используется OAuth2PasswordRequestForm для совместимости с Swagger UI
- `app/core/security.py`:
  - Хэширование паролей через passlib (bcrypt)
  - Генерация и декодирование JWT-токенов

### 2. CRUD-операции

- Пример (финансы):
```python
@router.get("/", response_model=List[FinanceRead])
def read_finances(...):
    finances = db.exec(select(Finance).where(Finance.user_id == current_user.id)).scalars().all()
    return [FinanceRead.model_validate(f, from_attributes=True) for f in finances]
```
- Аналогично реализованы budgets, goals, categories.

### 3. Главная страница (index.html)

- JS-логика:
  - После логина отправляется запрос на `/api/v1/users/login`, сохраняется access_token
  - Для получения данных используются fetch-запросы к `/api/v1/finances/`, `/api/v1/budgets/`, `/api/v1/goals/`
  - После загрузки данных считается:
    - Total Income: сумма всех Finance с type = 'Income'
    - Total Expenses: сумма всех Finance с type = 'Expenses'
    - Budget: сумма всех Budget
    - Goal: сумма всех Goal.target_amount
  - Если `Total Income - Total Expenses < Budget`, показывается красное предупреждение
  - В противном случае — зелёное сообщение

### 4. Пример JS-фрагмента для алерта
```javascript
function checkAlert() {
    if(window._income !== undefined && window._expenses !== undefined && window._budget !== undefined){
        if(window._income - window._expenses < window._budget){
            document.getElementById('alert').innerText = 'Alert: Income minus Expenses is less than Budget!';
            document.getElementById('ok').innerText = '';
        } else {
            document.getElementById('alert').innerText = '';
            document.getElementById('ok').innerText = 'All is within budget.';
        }
    }
}
```

---

## Как запустить

1. Установить зависимости: `pip install -r requirements.txt`
2. Настроить .env с параметрами БД и секретом
3. Инициализировать БД: `python -m app.db.init_db`
4. Запустить сервер: `uvicorn app.main:app --reload`
5. Открыть [http://127.0.0.1:8000/](http://127.0.0.1:8000/) — главная страница
6. Для тестирования API использовать Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Примечания
- Все основные проверки и бизнес-логика реализованы на сервере, а визуализация и алерты — на клиенте (index.html)
- Для полноценной работы требуется PostgreSQL
- JWT-токен используется для авторизации во всех защищённых API 