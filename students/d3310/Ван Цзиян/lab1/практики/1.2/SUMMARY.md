# Практика 1.2: Полный CRUD API с SQLModel и FastAPI - ЗАВЕРШЕНО

## Обзор проекта

Полнофункциональный REST API для управления воинами, профессиями и навыками с использованием FastAPI, SQLModel и Alembic. Проект реализует полный CRUD функционал с правильной обработкой связей между таблицами.

## Реализованные функции

### 1. Модели данных (models.py)
- **WarriorDefault**: входная модель для создания воинов
- **Warrior**: полная модель воина с таблицей и связями
- **WarriorProfessions**: модель для отображения связей с профессией
- **Profession**: модель профессии с каскадным удалением
- **ProfessionDefault**: входная модель для создания профессий
- **Skill**: модель навыка
- **SkillWarriorLink**: промежуточная таблица для связи многие-ко-многим
- **RaceType**: перечисление для рас воинов

### 2. API Endpoints (main.py)

#### GET endpoints
- `GET /` - главная страница
- `GET /warriors/` - получить всех воинов
- `GET /warriors_list` - получить список воинов
- `GET /warrior/{warrior_id}` - получить воина с вложенной профессией
- `GET /skills/` - получить все навыки
- `GET /professions/` - получить все профессии
- `GET /professions_list` - получить список профессий
- `GET /profession/{profession_id}` - получить профессию по ID

#### POST endpoints
- `POST /warrior` - создать воина
- `POST /skills/` - создать навык
- `POST /professions/` - создать профессию
- `POST /profession` - создать профессию

#### PATCH endpoints
- `PATCH /warrior/{warrior_id}` - обновить воина

#### DELETE endpoints
- `DELETE /warrior/{warrior_id}` - удалить воина
- `DELETE /profession/{profession_id}` - удалить профессию
- `DELETE /skill/{skill_id}` - удалить навык

## Технические особенности

### 1. Безопасная валидация данных
```python
# Использование model_validate() для безопасного преобразования
warrior = Warrior.model_validate(warrior)
profession = Profession.model_validate(prof)
```

### 2. Разделение входных и выходных моделей
```python
# Входная модель без id и связей
class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")

# Полная модель с таблицей
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)
```

### 3. Правильная обработка связей
```python
# Модель для отображения вложенных объектов
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None

# Использование response_model для правильной сериализации
@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior
```

### 4. Каскадное удаление
```python
# Настройка каскадного удаления в связях
class Profession(SQLModel, table=True):
    warriors_prof: List["Warrior"] = Relationship(
        back_populates="profession",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    )

class Warrior(WarriorDefault, table=True):
    profession: Optional[Profession] = Relationship(
        back_populates="warriors_prof",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    )
```

### 5. Частичные обновления
```python
@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session: Session = Depends(get_session)) -> Warrior:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior
```

### 6. Правильная обработка ошибок
```python
# Проверка существования объекта перед операциями
if not warrior:
    raise HTTPException(status_code=404, detail="Warrior not found")
```

## Структура проекта

```
практики/1.2/
├── main.py                 # FastAPI приложение с endpoints
├── models.py               # SQLModel модели данных
├── connection.py           # Настройка подключения к БД
├── requirements.txt        # Зависимости проекта
├── alembic.ini            # Конфигурация Alembic
├── README.md              # Документация проекта
├── warriors.db            # SQLite база данных
└── alembic/               # Миграции базы данных
    ├── env.py
    └── versions/
```

## Примеры использования

### Создание воина
```bash
curl -X POST http://localhost:8000/warrior \
  -H "Content-Type: application/json" \
  -d '{
    "race": "junior",
    "name": "Test Warrior",
    "level": 1,
    "profession_id": 1
  }'
```

### Получение воина с профессией
```bash
curl http://localhost:8000/warrior/1
```

### Обновление воина
```bash
curl -X PATCH http://localhost:8000/warrior/1 \
  -H "Content-Type: application/json" \
  -d '{"level": 5, "name": "Updated Name"}'
```

### Удаление воина
```bash
curl -X DELETE http://localhost:8000/warrior/1
```

## Запуск проекта

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
alembic upgrade head
```

### 3. Запуск сервера
```bash
uvicorn main:app --reload
```

### 4. Доступ к API
- API доступен по адресу: http://localhost:8000
- Автоматическая документация: http://localhost:8000/docs
- Альтернативная документация: http://localhost:8000/redoc

## Результат

Проект полностью реализует все требования практики 1.2:

- **Create (POST)**: Создание воинов, профессий, навыков
- **Read (GET)**: Получение списков и отдельных объектов с правильной сериализацией связей
- **Update (PATCH)**: Частичное обновление объектов
- **Delete (DELETE)**: Удаление объектов с каскадным поведением

### Ключевые достижения:
- Правильное использование SQLModel для ORM
- Безопасная валидация данных через Pydantic
- Корректная обработка связей между таблицами
- Настройка каскадного удаления
- Полная типизация API
- Правильная обработка ошибок
- Разделение входных и выходных моделей

