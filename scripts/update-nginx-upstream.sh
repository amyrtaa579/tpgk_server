#!/bin/bash
# Скрипт для обновления IP адресов в конфигурации nginx
# Запускать при перезапуске контейнеров

set -e

# Получение IP адресов контейнеров
API_IP=$(docker inspect anmicius-api --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
MINIO_IP=$(docker inspect anmicius-minio --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')

if [ -z "$API_IP" ] || [ -z "$MINIO_IP" ]; then
    echo "Ошибка: не удалось получить IP адреса контейнеров"
    exit 1
fi

echo "Обновление конфигурации nginx..."
echo "API IP: $API_IP"
echo "MinIO IP: $MINIO_IP"

# Обновление конфигурации nginx
sed -i "s/server [0-9.]*:8000;/server ${API_IP}:8000;/" /root/anmicius-api/nginx/nginx.conf
sed -i "s/server [0-9.]*:9000;/server ${MINIO_IP}:9000;/" /root/anmicius-api/nginx/nginx.conf
sed -i "s/server [0-9.]*:9001;/server ${MINIO_IP}:9001;/" /root/anmicius-api/nginx/nginx.conf

# Перезапуск nginx
docker restart anmicius-nginx

echo "Конфигурация обновлена!"
