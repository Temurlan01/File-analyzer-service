# File Analyzer Service

Django REST Framework-сервис для загрузки файлов из внешнего API и анализа их содержимого.

> Учебный pet-проект, демонстрирующий интеграцию с внешним API, обработку rate limit, пагинацию и расчёт статистики.

## Что это

Сервис позволяет:

- запускать загрузку каталога файлов из внешнего API;
- хранить загруженные файлы и метаданные в SQLite;
- просматривать файлы с серверной пагинацией;
- выбирать отдельные файлы или весь набор;
- считать частоту цифр `0–9` в содержимом файлов;
- получать общую и покомпонентную статистику;
- управлять прогрессом кандидатов и throttling через admin endpoints.

## Зачем

Проект решает типовую интеграционную задачу: надёжно получить данные из внешнего сервиса, сохранить их локально и предоставить удобный API/UI для последующего анализа. В реализации учтены ответы `429`/`403`, `Retry-After`, ограничения внешнего API и конфигурация через `.env`.

## Стек

- **Python 3.9+**
- **Django 6**
- **Django REST Framework**
- **SQLite**
- **requests** — интеграция с внешним API
- **python-dotenv** — конфигурация
- **Alpine.js + Tailwind CSS CDN** — интерфейс
- **drf-spectacular / OpenAPI** — API-документация

## Быстрый старт

```bash
git clone https://github.com/Temurlan01/File-analyzer-service.git
cd File-analyzer-service
python -m venv .venv

# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Создайте `.env` в корне проекта:

```env
TARGET_API_BASE=http://your-api-url:8000
TARGET_CANDIDATE_ID=your_candidate_id
ADMIN_TOKEN=change-me
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

```bash
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000.

## API

| Метод | Endpoint | Назначение |
|---|---|---|
| `POST` | `/api/start-download/` | Запустить загрузку файлов |
| `GET` | `/api/files/?page=1&size=10` | Получить список файлов |
| `POST` | `/api/calculate/` | Рассчитать статистику по выбранным файлам |
| `DELETE` | `/api/admin/candidates/{candidate_id}/progress/` | Сбросить прогресс |
| `DELETE` | `/api/admin/clients/{client_ip}/throttling/` | Снять throttling |

Подробные схемы запросов и ответов находятся в [API.md](API.md), инструкции по тестированию — в [TESTING.md](TESTING.md).

## Скриншоты и демо

Живой демо-сервер не настроен. Для демонстрации запустите проект локально и сделайте скриншоты главной страницы, списка файлов и блока статистики. Готовые изображения можно добавить в `docs/screenshots/` и подключить здесь:

```md
![Главная страница](docs/screenshots/home.png)
![Статистика](docs/screenshots/statistics.png)
```

## Структура

```text
analyzer/    # модели, API views и интеграция с внешним API
core/        # настройки Django и маршрутизация
templates/   # HTML-интерфейс
API.md       # документация API
TESTING.md   # сценарии проверки
```

## Лицензия

Лицензия пока не указана.
