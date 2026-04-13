# Развёртывание и деплой

Проект развёртывается через **Docker Compose** с полной инфраструктурой: PostgreSQL, Redis, MinIO, FastAPI, Nginx (SSL) и Certbot.

## Обзор

| Компонент | Технология | Порт |
|-----------|-----------|------|
| **API** | FastAPI + Uvicorn | 8000 (внутренний) |
| **База данных** | PostgreSQL 15 | 5432 |
| **Кэш** | Redis 7 | 6379 |
| **Хранилище** | MinIO | 9000 (API), 9001 (Console) |
| **Реверс-прокси** | Nginx + SSL | 80, 443, 4443 |
| **SSL сертификаты** | Certbot (Let's Encrypt) | — |

---

## Архитектура развёртывания

```
                    ┌──────────────────┐
                    │   Интернет       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Nginx        │ ← SSL (443), HTTP (80)
                    │  (Reverse Proxy) │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │   FastAPI   │  │   MinIO    │  │Admin Panel │
     │   (:8000)   │  │   (:9000)  │  │  (static)  │
     └──────┬─────┘  └────────────┘  └────────────┘
            │
     ┌──────┴──────┬──────────────┐
     │             │              │
     ▼             ▼              ▼
┌──────────┐ ┌──────────┐  ┌──────────┐
│PostgreSQL│ │  Redis   │  │  MinIO   │
│  (:5432) │ │  (:6379) │  │(internal)│
└──────────┘ └──────────┘  └──────────┘
```

---

## Быстрый старт (Development)

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/anmicius/anmicius-api.git
cd anmicius-api

# 2. Настроить окружение
cp .env.example .env
# Отредактировать .env (изменить пароли, JWT_SECRET_KEY)

# 3. Запустить все сервисы
docker-compose up -d

# 4. Применить миграции БД
docker-compose exec api alembic upgrade head

# 5. Проверить статус
docker-compose ps
```

API доступен по адресу: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

### Создание первого пользователя

```bash
# Регистрация через API
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@anmicius.ru",
    "username": "admin",
    "password": "Str0ng!Pass123"
  }'

# Сделать суперпользователем (через SQL)
docker-compose exec postgres psql -U anmicius -d anmicius_db -c \
  "UPDATE users SET is_superuser = true WHERE username = 'admin';"
```

---

## Production развёртывание

### 1. Подготовка сервера

**Минимальные требования:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB SSD
- OS: Ubuntu 22.04 LTS

**Установка Docker:**

```bash
# Установка Docker
curl -fsSL https://get.docker.com | sh

# Установка Docker Compose
apt-get install docker-compose-plugin

# Добавить пользователя в группу docker
usermod -aG docker $USER
```

### 2. Настройка окружения

```bash
# Создать директорию проекта
mkdir -p /opt/anmicius-api
cd /opt/anmicius-api

# Клонировать репозиторий
git clone https://github.com/anmicius/anmicius-api.git .

# Создать .env
cp .env.example .env
nano .env
```

**Критичные настройки `.env` для Production:**

```bash
# ОБЯЗАТЕЛЬНО измените!
JWT_SECRET_KEY=<сгенерировать случайную строку 64+ символов>
POSTGRES_PASSWORD=<сильный пароль>
MINIO_ACCESS_KEY=<сильный пароль>
MINIO_SECRET_KEY=<сильный пароль>

# SSL
SSL_EMAIL=admin@anmicius.ru
MAIN_DOMAIN=api.anmicius.ru

# CORS
CORS_ORIGINS=https://anmicius.ru,https://admin.anmicius.ru
```

**Генерация JWT_SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. Настройка Nginx и SSL

**Конфигурация Nginx** (`nginx/nginx.conf`):

```nginx
upstream api_backend {
    server api:8000;
}

upstream minio_backend {
    server minio:9000;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name api.anmicius.ru minio.anmicius.ru;

    location /.well-known/acme-challenge/ {
        root /var/www;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# API HTTPS
server {
    listen 443 ssl http2;
    server_name api.anmicius.ru;

    ssl_certificate /etc/letsencrypt/live/api.anmicius.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.anmicius.ru/privkey.pem;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $https;
    }
}

# MinIO HTTPS
server {
    listen 443 ssl http2;
    server_name minio.anmicius.ru;

    ssl_certificate /etc/letsencrypt/live/minio.anmicius.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minio.anmicius.ru/privkey.pem;

    location / {
        proxy_pass http://minio_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Получение SSL-сертификатов:**

```bash
# Остановить сервисы
docker-compose down

# Запустить только Nginx для ACME challenge
docker-compose up -d nginx

# Получить сертификаты
docker-compose run --rm certbot certbot certonly \
  --webroot --webroot-path=/var/www \
  -d api.anmicius.ru \
  -d minio.anmicius.ru \
  --email admin@anmicius.ru \
  --agree-tos \
  --no-eff-email

# Запустить все сервисы
docker-compose up -d
```

### 4. Запуск Production

```bash
# Применить миграции
docker-compose exec api alembic upgrade head

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f api
```

---

## Docker Compose сервисы

### PostgreSQL

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: anmicius
    POSTGRES_PASSWORD: anmicius_secret_password
    POSTGRES_DB: anmicius_db
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U anmicius -d anmicius_db"]
```

**Volume:** `postgres_data` — постоянное хранение данных БД.

### Redis

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
```

**AOF (Append-Only File):** Включён для персистентности кэша.

### MinIO

```yaml
minio:
  image: minio/minio:latest
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  command: server /data --console-address ":9001"
  volumes:
    - minio_data:/data
```

**MinIO Console:** `http://localhost:9001` (логин: `minioadmin`, пароль: `minioadmin`)

### FastAPI

```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    POSTGRES_HOST: postgres
    MINIO_ENDPOINT: minio:9000
  volumes:
    - ./app:/app/app  # Hot-reload для разработки
  depends_on:
    postgres:
      condition: service_healthy
```

### Nginx

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    - certbot_etc:/etc/letsencrypt
```

### Certbot

```yaml
certbot:
  image: certbot/certbot
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
  volumes:
    - certbot_etc:/etc/letsencrypt
```

**Автоматическое обновление** сертификатов каждые 12 часов.

---

## Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только API
docker-compose logs -f api

# Последние 100 строк
docker-compose logs --tail=100 api
```

### Health Check

```bash
curl https://api.anmicius.ru/health
```

**Пример ответа:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "services": {
    "database": {"status": "ok"},
    "redis": {"status": "ok"},
    "minio": {"status": "ok"}
  }
}
```

### Статистика контейнеров

```bash
# Использование ресурсов
docker stats

# Только контейнеры проекта
docker-compose top
```

---

## Обновление приложения

```bash
# 1. Остановить API
docker-compose stop api

# 2. Собрать новый образ
docker-compose build api

# 3. Применить миграции
docker-compose run --rm api alembic upgrade head

# 4. Запустить API
docker-compose start api

# 5. Проверить статус
docker-compose ps
curl https://api.anmicius.ru/health
```

### Автоматическое обновление (CI/CD)

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Деплой новой версии..."

# Pull последних изменений
git pull origin main

# Сборка и перезапуск
docker-compose build api
docker-compose stop api
docker-compose run --rm api alembic upgrade head
docker-compose start api

echo "✅ Деплой завершён!"
```

---

## Безопасность

### Контрольный список

- [ ] **Изменён JWT_SECRET_KEY** на случайную строку
- [ ] **Изменены пароли** PostgreSQL и MinIO
- [ ] **Включён HTTPS** для всех эндпоинтов
- [ ] **CORS** настроен на конкретные origins
- [ ] **DEBUG=false** в production
- [ ] **Брандмауэр** блокирует неиспользуемые порты
- [ ] **Бэкапы** БД настроены (cron + pg_dump)
- [ ] **Мониторинг** логов и метрик

### Брандмауэр (UFW)

```bash
# Разрешить SSH
ufw allow 22/tcp

# Разрешить HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Включить UFW
ufw enable
```

### Бэкапы PostgreSQL

```bash
#!/bin/bash
# scripts/backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

docker-compose exec -T postgres pg_dump -U anmicius anmicius_db | gzip > \
  "$BACKUP_DIR/anmicius_db_$DATE.sql.gz"

# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

**Cron (ежедневно в 2:00):**
```cron
0 2 * * * /opt/anmicius-api/scripts/backup_db.sh
```

---

## Troubleshooting

### Контейнер не запускается

```bash
# Проверить логи
docker-compose logs api

# Проверить зависимости
docker-compose ps

# Перезапустить сервис
docker-compose restart api
```

### Ошибка подключения к БД

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Проверить логи PostgreSQL
docker-compose logs postgres

# Протестировать подключение
docker-compose exec postgres psql -U anmicius -d anmicius_db -c "SELECT 1;"
```

### MinIO недоступен

```bash
# Проверить, создан ли бакет
docker-compose exec minio-init cat /proc/1/cmdline

# Войти в MinIO Console
# http://localhost:9001 (логин: minioadmin, пароль: minioadmin)
```

### SSL сертификаты не получены

```bash
# Проверить DNS-записи
nslookup api.anmicius.ru

# Проверить Nginx
docker-compose logs nginx

# Попробовать вручную
docker-compose run --rm certbot certbot certonly \
  --webroot --webroot-path=/var/www \
  -d api.anmicius.ru
```

---

## Переменные окружения

| Переменная | Описание | Production значение |
|------------|----------|---------------------|
| `JWT_SECRET_KEY` | Секретный ключ JWT | `<random 64+ chars>` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `<strong password>` |
| `MINIO_ACCESS_KEY` | MinIO access key | `<strong password>` |
| `MINIO_SECRET_KEY` | MinIO secret key | `<strong password>` |
| `DEBUG` | Режим отладки | `false` |
| `CORS_ORIGINS` | Разрешённые origins | `https://anmicius.ru,...` |
| `SSL_EMAIL` | Email для Let's Encrypt | `admin@anmicius.ru` |
| `MAIN_DOMAIN` | Основной домен | `api.anmicius.ru` |

---

## Связанные документы

- [Архитектура](./architecture.md) — структура приложения
- [Миграции](./migrations.md) — применение миграций в production
- [Безопасность](./errors.md#безопасность) — рекомендации
