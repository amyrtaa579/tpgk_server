#!/bin/bash

# Скрипт для получения SSL-сертификатов Let's Encrypt
# Использование: ./scripts/ssl-cert.sh your-email@example.com

set -e

EMAIL=$1

if [ -z "$EMAIL" ]; then
    echo "❌ Ошибка: Укажите email"
    echo "Использование: $0 your-email@example.com"
    exit 1
fi

echo "📜 Получение SSL-сертификатов для доменов..."

# Создаём директорию для webroot
mkdir -p nginx/www/.well-known/acme-challenge

# Получаем сертификаты для всех доменов используя docker run с host сетью
docker run --rm --network host \
    -v "$(pwd)/nginx/www:/var/www" \
    -v anmicius-api_certbot_etc:/etc/letsencrypt \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d anmicius.ru \
    -d www.anmicius.ru \
    -d api.anmicius.ru \
    -d admin.anmicius.ru \
    -d minio.anmicius.ru

echo ""
echo "✅ SSL-сертификаты успешно получены!"
echo ""
echo "Перезапустите Nginx для применения сертификатов:"
echo "  docker-compose restart nginx"
