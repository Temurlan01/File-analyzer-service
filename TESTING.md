# Инструкция по тестированию сервиса

## Запуск сервера

```bash
python manage.py runserver
```

Сервис будет доступен по адресу `http://127.0.0.1:8000`

## Тестирование через браузер

### 1. Главная страница (UI)
Откройте в браузере: `http://127.0.0.1:8000`

- Нажмите кнопку "Скачать данные"
- Наблюдайте за прогрессом скачивания
- После завершения проверьте список файлов
- Выберите файлы и нажмите "Произвести расчёты"
- Проверьте результаты статистики

## Тестирование API через curl

### 2. Запуск скачивания
```bash
curl -X POST http://127.0.0.1:8000/api/start-download/
```

Ожидаемый ответ:
```json
{
  "start_time_nsk": "2026-07-23 18:15:30",
  "names_received": 15,
  "downloaded_count": 15
}
```

### 3. Получение списка файлов (с пагинацией)
```bash
curl http://127.0.0.1:8000/api/files/
```

С пагинацией:
```bash
curl "http://127.0.0.1:8000/api/files/?page=1&size=10"
```

Ожидаемый ответ:
```json
{
  "total_items": 15,
  "total_pages": 2,
  "current_page": 1,
  "items": [
    {
      "id": 1,
      "filename": "file1.txt",
      "downloaded_at": "2026-07-23 18:15:30"
    }
  ]
}
```

### 4. Расчёт статистики (выбранные файлы)
```bash
curl -X POST http://127.0.0.1:8000/api/calculate/ \
  -H "Content-Type: application/json" \
  -d '{"filenames": ["file1.txt", "file2.txt"], "select_all_in_db": false}'
```

### 5. Расчёт статистики (все файлы)
```bash
curl -X POST http://127.0.0.1:8000/api/calculate/ \
  -H "Content-Type: application/json" \
  -d '{"select_all_in_db": true}'
```

Ожидаемый ответ:
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
      "2": 3
    }
  },
  "processed_files_count": 2
}
```

## Тестирование Admin endpoints

### 6. Сброс прогресса кандидата
```bash
curl -X DELETE http://127.0.0.1:8000/api/admin/candidates/candidate_ivan_petrov_2026/progress/
```

Ожидаемый ответ:
```json
{
  "reset": true
}
```

### 7. Снятие бана и сброс счётчиков
```bash
curl -X DELETE http://127.0.0.1:8000/api/admin/clients/127.0.0.1/throttling/
```

Ожидаемый ответ:
```json
{
  "reset": true
}
```

## Запуск unit-тестов

```bash
python manage.py test analyzer
```

Ожидаемый результат:
```
Creating test database for alias 'default'...
.........
----------------------------------------------------------------------
Ran 9 tests in 0.050s

OK
Destroying test database for alias 'default'...
```

## Проверка конфигурации

Проверьте файл `.env`:
```env
TARGET_API_BASE=http://91.199.149.128:18001
TARGET_CANDIDATE_ID=candidate_ivan_petrov_2026
ADMIN_TOKEN=admin_secret_token
```

## Проверка Django Admin

1. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

2. Откройте `http://127.0.0.1:8000/admin/`
3. Войдите под созданным пользователем
4. Проверьте модель DownloadedFile в админке

## Проверка внешнего API напрямую

Для проверки работы внешнего API можно использовать curl:

### Получение имён файлов
```bash
curl http://91.199.149.128:18001/api/files/names \
  -H "X-Candidate-Id: candidate_ivan_petrov_2026"
```

### Скачивание файлов
```bash
curl -X POST http://91.199.149.128:18001/api/files/download \
  -H "Content-Type: application/json" \
  -H "X-Candidate-Id: candidate_ivan_petrov_2026" \
  -d '{"file_names": ["file1.txt", "file2.txt"]}' \
  --output files.zip
```

### Отметка файлов как скачанные
```bash
curl -X POST http://91.199.149.128:18001/api/files/downloaded \
  -H "Content-Type: application/json" \
  -H "X-Candidate-Id: candidate_ivan_petrov_2026" \
  -d '{"file_names": ["file1.txt", "file2.txt"]}'
```

## Возможные ошибки и решения

### Ошибка 429 Too Many Requests
- Подождите указанное в заголовке `Retry-After` время
- Или используйте admin endpoint для сброса throttling

### Ошибка 403 Forbidden
- Клиент заблокирован на 30 минут
- Используйте admin endpoint для снятия бана

### Ошибка подключения к внешнему API
- Проверьте `TARGET_API_BASE` в `.env`
- Проверьте доступность `http://91.199.149.128:18001`

### Ошибка SECRET_KEY
- Добавьте в `.env`: `SECRET_KEY=your-secret-key-here`
