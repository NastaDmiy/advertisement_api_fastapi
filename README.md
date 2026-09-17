# advertisement_api_fastapi

REST API для сайта объявлений купли/продажи на FastAPI. Сервис докеризован.

## Стек

- Python 3.12
- FastAPI 0.115
- SQLAlchemy 2.0
- Pydantic 2.x
- SQLite
- Docker

## Установка и запуск локально

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Запуск в Docker

Сборка образа:

```bash
docker build -t advertisement_api_fastapi .
```

Запуск контейнера:

```bash
docker run -d -p 8000:8000 --name adv_api advertisement_api_fastapi
```

Остановка:

```bash
docker stop adv_api
```

## Документация

После запуска доступна автоматическая документация:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API методы

### POST /advertisement — создать объявление

**Тело запроса:**

```json
{
  "title": "Продам квартиру",
  "description": "3-комнатная в центре",
  "price": 5500000,
  "author": "Иван Петров"
}
```

**Ответ:** `201 Created`

### GET /advertisement — поиск объявлений по полям

**Query-параметры (все опциональны):**

- `title` — поиск по заголовку (частичное совпадение)
- `author` — поиск по автору
- `min_price` — минимальная цена
- `max_price` — максимальная цена

**Пример:** `GET /advertisement?title=квартира&min_price=1000000`

**Ответ:** `200 OK` — массив объявлений

### GET /advertisement/{advertisement_id} — получить по ID

**Ответ:** `200 OK` — объект объявления

Если не найдено — `404 Not Found`.

### PATCH /advertisement/{advertisement_id} — редактировать (частичное обновление)

**Тело запроса** (любые поля):

```json
{
  "price": 5200000
}
```

**Ответ:** `200 OK` — обновлённое объявление.

Обновляются только переданные поля, остальные сохраняются.

### DELETE /advertisement/{advertisement_id} — удалить

**Ответ:** `200 OK`

Если не найдено — `404 Not Found`.
