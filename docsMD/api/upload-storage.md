# Загрузка файлов и хранилище MinIO

API использует **MinIO** — S3-совместимое объектное хранилище для загрузки и хранения изображений и документов.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Хранилище** | MinIO (S3-совместимое) |
| **Версия** | latest |
| **Endpoint (внутренний)** | `minio:9000` |
| **Публичный URL** | `https://minio.anmicius.ru/anmicius-media` |
| **Bucket** | `anmicius-media` |
| **Протокол** | HTTPS (в production) |

## Архитектура хранилища

### Структура бакета

```
anmicius-media/
├── images/
│   ├── common/          # Общие изображения (о колледже и т.д.)
│   ├── specialties/     # Изображения специальностей
│   ├── news/            # Изображения новостей
│   ├── facts/           # Изображения фактов
│   └── gallery/         # Фотогалерея
└── documents/
    ├── licenses/        # Лицензии
    ├── accreditations/  # Аккредитации
    ├── admission/       # Документы приёмной кампании
    └── other/           # Прочие документы
```

### URL файлов

Файлы доступны по публичному URL:

```
https://minio.anmicius.ru/anmicius-media/{object_name}
```

Пример:
```
https://minio.anmicius.ru/anmicius-media/images/specialties/abc123def456.jpg
```

---

## Эндпоинты загрузки файлов

Все эндпоинты требуют **JWT-аутентификации**.

### POST /admin/upload/image

Загрузка изображения в MinIO.

**Content-Type:** `multipart/form-data`

**Параметры:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `file` | File | Да | Файл изображения |
| `category` | string | Нет | Категория (подпапка), по умолчанию `common` |

**Поддерживаемые форматы:**
- JPEG (`image/jpeg`)
- PNG (`image/png`)
- GIF (`image/gif`)
- WebP (`image/webp`)

**Ограничения:**
- Максимальный размер: **10 МБ**

**Пример запроса (cURL):**

```bash
curl -X POST https://api.anmicius.ru/admin/upload/image?category=news \
  -H "Authorization: Bearer eyJhbGci..." \
  -F "file=@photo.jpg"
```

**Ответ (200 OK):**

```json
{
  "url": "https://minio.anmicius.ru/anmicius-media/images/news/abc123def456.jpg",
  "filename": "photo.jpg",
  "size": 245678,
  "content_type": "image/jpeg"
}
```

**Ошибка (400 Bad Request):**

```json
{
  "detail": "Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP"
}
```

---

### POST /admin/upload/document

Загрузка документа в MinIO.

**Content-Type:** `multipart/form-data`

**Параметры:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `file` | File | Да | Файл документа |
| `category` | string | Нет | Категория (подпапка), по умолчанию `common` |

**Поддерживаемые форматы:**
- PDF (`application/pdf`)
- DOC (`application/msword`)
- DOCX (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- XLS (`application/vnd.ms-excel`)
- XLSX (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
- TXT (`text/plain`)

**Ограничения:**
- Максимальный размер: **50 МБ**

**Пример запроса (cURL):**

```bash
curl -X POST https://api.anmicius.ru/admin/upload/document?category=licenses \
  -H "Authorization: Bearer eyJhbGci..." \
  -F "file=@license.pdf"
```

**Ответ (200 OK):**

```json
{
  "url": "https://minio.anmicius.ru/anmicius-media/documents/licenses/xyz789abc.pdf",
  "filename": "license.pdf",
  "size": 1048576,
  "content_type": "application/pdf"
}
```

---

### GET /admin/upload/minio/list

Получение списка файлов в MinIO.

**Параметры запроса:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prefix` | string | Нет | Префикс для фильтрации (например, `images/news/`) |

**Пример запроса:**

```bash
curl -X GET "https://api.anmicius.ru/admin/upload/minio/list?prefix=images/news/" \
  -H "Authorization: Bearer eyJhbGci..."
```

**Ответ (200 OK):**

```json
{
  "objects": [
    {
      "key": "images/news/abc123def.jpg",
      "size": 245678,
      "last_modified": "2025-01-15T10:30:00"
    },
    {
      "key": "images/news/xyz456ghi.png",
      "size": 512345,
      "last_modified": "2025-01-16T14:20:00"
    }
  ],
  "total": 2
}
```

---

## Программное использование

### Python (с использованием httpx)

```python
import httpx
import asyncio

async def upload_image(token: str, file_path: str, category: str = "common"):
    """Загрузка изображения в MinIO."""
    async with httpx.AsyncClient(base_url="https://api.anmicius.ru") as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "image/jpeg")}
            data = {"category": category}
            
            response = await client.post(
                "/admin/upload/image",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                return response.json()["url"]
            else:
                raise Exception(f"Upload failed: {response.text}")

# Пример использования
url = asyncio.run(upload_image(
    token="eyJhbGci...",
    file_path="./photo.jpg",
    category="news"
))
print(f"Файл загружен: {url}")
```

### Загрузка документа

```python
async def upload_document(token: str, file_path: str, category: str = "other"):
    """Загрузка документа в MinIO."""
    async with httpx.AsyncClient(base_url="https://api.anmicius.ru") as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "application/pdf")}
            data = {"category": category}
            
            response = await client.post(
                "/admin/upload/document",
                headers=headers,
                files=files,
                data=data
            )
            
            return response.json()
```

---

## Минимальная реализация (внутренности)

### Сервис MinIO

Сервис расположен в `app/infrastructure/minio_service.py`.

**Ключевые функции:**

```python
def upload_file_from_bytes(
    bucket: str,
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Загрузка файла из bytes, возврат публичного URL."""
```

**Генерация уникального имени файла:**

```python
def generate_unique_filename(original_filename: str) -> str:
    """UUID + оригинальное расширение."""
    # Пример: "photo.jpg" -> "abc123def456.jpg"
```

### Процесс загрузки

```
1. Клиент отправляет файл (multipart/form-data)
       ↓
2. Проверка Content-Type (белый список)
       ↓
3. Проверка размера файла (лимит)
       ↓
4. Генерация уникального имени (UUID)
       ↓
5. Загрузка в MinIO (put_object)
       ↓
6. Формирование публичного URL
       ↓
7. Возврат ответа с URL, именем, размером
```

---

## Безопасность

### Валидация файлов

| Проверка | Описание |
|----------|----------|
| **Content-Type** | Белый список MIME-типов |
| **Размер** | 10 МБ для изображений, 50 МБ для документов |
| **Имя файла** | UUID для избежания коллизий |

### JWT-аутентификация

Все эндпоинты загрузки требуют валидного JWT-токена. Анонимная загрузка файлов **запрещена**.

### Рекомендации для Production

1. **Включите HTTPS** для MinIO (`minio_secure=true`)
2. **Измените доступы** MinIO (не используйте `minioadmin` по умолчанию)
3. **Настройте CORS** для публичного доступа к файлам
4. **Мониторинг** использования хранилища
5. **Бэкапы** бакета на регулярной основе

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `MINIO_ENDPOINT` | Внутренний endpoint MinIO | `minio:9000` |
| `MINIO_ACCESS_KEY` | Access Key | `minioadmin_change_in_production` |
| `MINIO_SECRET_KEY` | Secret Key | `minioadmin_change_in_production` |
| `MINIO_BUCKET` | Имя бакета | `anmicius-media` |
| `MINIO_SECURE` | Использовать HTTPS | `false` |
| `MINIO_PUBLIC_URL` | Публичный URL MinIO | `https://minio.anmicius.ru/anmicius-media` |

---

## Troubleshooting

### Ошибка: "Недопустимый тип файла"

**Причина:** Файл имеет неподдерживаемый MIME-type.

**Решение:** Проверьте формат файла. Для изображений: JPEG, PNG, GIF, WebP. Для документов: PDF, DOC, DOCX, XLS, XLSX, TXT.

### Ошибка: "Размер файла превышает максимальный"

**Причина:** Файл больше допустимого лимита (10 МБ для изображений, 50 МБ для документов).

**Решение:** Сожмите файл или разделите на части.

### Ошибка: "Ошибка получения списка файлов"

**Причина:** MinIO не запущен или недоступен.

**Решение:**
```bash
docker-compose ps  # Проверить статус контейнера
docker-compose logs minio  # Посмотреть логи
```

---

## Связанные документы

- [Админ-эндпоинты](./admin-endpoints.md) — CRUD операции с сущностями
- [Кэширование](./caching.md) — кэширование публичных данных
- [Аутентификация](./authentication.md) — JWT-токены
