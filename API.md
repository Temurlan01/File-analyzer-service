# API Documentation

## Базовый URL
```
http://127.0.0.1:8000
```

## Authentication

### Candidate Identification
Для идентификации используется заголовок `X-Candidate-Id`. Если заголовок не передан, идентификация происходит по IP-адресу.

### Admin Authentication
Для admin endpoints требуется заголовок `X-Admin-Token`. Токен настраивается через переменную окружения `ADMIN_TOKEN`.

---

## Endpoints

### 1. Запуск скачивания файлов

**POST** `/api/start-download/`

Запускает процесс скачивания всего каталога файлов из внешнего API.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
None

**Response (200 OK):**
```json
{
  "start_time_nsk": "2026-07-23 18:15:30",
  "names_received": 15,
  "downloaded_count": 15
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Error description"
}
```

**Описание полей:**
- `start_time_nsk` - время начала скачивания в часовом поясе Новосибирск (UTC+7)
- `names_received` - общее количество полученных имён файлов
- `downloaded_count` - количество успешно скачанных файлов

---

### 2. Получение списка файлов

**GET** `/api/files/`

Получает список скачанных файлов с пагинацией.

**Query Parameters:**
- `page` (optional, default: 1) - номер страницы
- `size` (optional, default: 10) - количество файлов на странице

**Example:**
```
GET /api/files/?page=1&size=10
```

**Response (200 OK):**
```json
{
  "total_items": 15,
  "total_pages": 2,
  "current_page": 1,
  "items": [
    {
      "id": 1,
      "filename": "000d7d0a-acef-4c95-b92d-1aa496b1858a.txt",
      "downloaded_at": "2026-07-23 18:15:30"
    }
  ]
}
```

**Описание полей:**
- `total_items` - общее количество файлов
- `total_pages` - общее количество страниц
- `current_page` - текущая страница
- `items` - массив файлов
  - `id` - уникальный идентификатор файла в базе
  - `filename` - имя файла
  - `downloaded_at` - время скачивания в формате YYYY-MM-DD HH:MM:SS

---

### 3. Расчёт статистики

**POST** `/api/calculate/`

Рассчитывает статистику по цифрам (0-9) в содержимом выбранных файлов.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "filenames": ["file1.txt", "file2.txt"],
  "select_all_in_db": false
}
```

**Описание полей:**
- `filenames` - массив имён файлов для анализа (опционально)
- `select_all_in_db` - если `true`, анализируются все файлы в базе (опционально)

**Один из параметров должен быть указан.**

**Response (200 OK):**
```json
{
  "global_stats": {
    "0": 5,
    "1": 3,
    "2": 7,
    "3": 2,
    "4": 4,
    "5": 6,
    "6": 1,
    "7": 8,
    "8": 9,
    "9": 0
  },
  "file_stats": {
    "file1.txt": {
      "0": 1,
      "1": 2,
      "2": 3,
      "3": 0,
      "4": 0,
      "5": 0,
      "6": 0,
      "7": 0,
      "8": 0,
      "9": 0
    }
  },
  "processed_files_count": 2
}
```

**Описание полей:**
- `global_stats` - общая статистика по всем выбранным файлам (количество каждой цифры 0-9)
- `file_stats` - статистика по каждому файлу отдельно
- `processed_files_count` - количество обработанных файлов

**Response (400 Bad Request):**
```json
{
  "error": "Не выбраны файлы"
}
```

---

### 4. Сброс прогресса кандидата (Admin)

**DELETE** `/api/admin/candidates/{candidate_id}/progress/`

Сбрасывает прогресс скачивания для указанного кандидата. Кандидат сможет начать скачивание заново.

**Request Headers:**
```
X-Admin-Token: your_admin_token
```

**URL Parameters:**
- `candidate_id` - идентификатор кандидата (его X-Candidate-Id или IP-адрес)

**Response (200 OK):**
```json
{
  "reset": true
}
```

**Response (403 Forbidden):**
```json
{
  "error": "Invalid or missing admin token"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Error description"
}
```

---

### 5. Снятие бана и сброс счётчиков (Admin)

**DELETE** `/api/admin/clients/{client_ip}/throttling/`

Снимает бан и обнуляет счётчики частоты запросов для указанного IP-адреса.

**Request Headers:**
```
X-Admin-Token: your_admin_token
```

**URL Parameters:**
- `client_ip` - IP-адрес клиента

**Response (200 OK):**
```json
{
  "reset": true
}
```

**Response (403 Forbidden):**
```json
{
  "error": "Invalid or missing admin token"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Error description"
}
```

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 400 | Неверные параметры запроса |
| 403 | Доступ запрещён (неверный admin токен или клиент заблокирован) |
| 429 | Превышен лимит частоты запросов (для внешнего API) |
| 500 | Внутренняя ошибка сервера |

---

## Конфигурация

### Переменные окружения (.env)

```env
# Базовый URL внешнего API
TARGET_API_BASE=http://91.199.149.128:18001

# Идентификатор кандидата
TARGET_CANDIDATE_ID=candidate_ivan_petrov_2026

# Admin токен для admin endpoints
ADMIN_TOKEN=admin_secret_token

# Django SECRET_KEY
SECRET_KEY=your-secret-key-here

# Режим отладки
DEBUG=True

# Разрешённые хосты
ALLOWED_HOSTS=*
```

---

## Примеры использования

### Python (requests)

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Запуск скачивания
response = requests.post(f"{BASE_URL}/api/start-download/")
print(response.json())

# Получение списка файлов
response = requests.get(f"{BASE_URL}/api/files/?page=1&size=10")
files = response.json()

# Расчёт статистики
response = requests.post(
    f"{BASE_URL}/api/calculate/",
    json={
        "filenames": ["file1.txt", "file2.txt"],
        "select_all_in_db": False
    }
)
stats = response.json()

# Сброс прогресса (admin)
response = requests.delete(
    f"{BASE_URL}/api/admin/candidates/candidate_id/progress/",
    headers={"X-Admin-Token": "admin_secret_token"}
)
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://127.0.0.1:8000";

// Запуск скачивания
fetch(`${BASE_URL}/api/start-download/`, {
  method: 'POST'
})
  .then(res => res.json())
  .then(data => console.log(data));

// Получение списка файлов
fetch(`${BASE_URL}/api/files/?page=1&size=10`)
  .then(res => res.json())
  .then(data => console.log(data));

// Расчёт статистики
fetch(`${BASE_URL}/api/calculate/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filenames: ['file1.txt', 'file2.txt'],
    select_all_in_db: false
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Rate Limiting

Внешний API имеет ограничения на частоту запросов:
- При превышении лимита возвращается код 429 с заголовком `Retry-After`
- При продолжении нарушений клиент блокируется на 30 минут (код 403)
- Сервис автоматически обрабатывает эти ошибки и делает паузы

Для снятия бана используйте admin endpoint `/api/admin/clients/{client_ip}/throttling/`.
