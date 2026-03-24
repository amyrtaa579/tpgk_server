#!/bin/bash
# Скрипт для запуска тестов

set -e

echo "=========================================="
echo "Запуск тестов Anmicius API"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest не найден. Устанавливаем зависимости...${NC}"
    pip install -r requirements.txt
fi

# Режим запуска
MODE="${1:-unit}"

case $MODE in
    "unit")
        echo -e "${YELLOW}Запуск unit-тестов...${NC}"
        pytest tests/test_api.py -v --tb=short
        ;;
    "integration")
        echo -e "${YELLOW}Запуск интеграционных тестов...${NC}"
        echo "Убедитесь, что API запущен на http://localhost:8000"
        pytest tests/test_integration.py -v --tb=short
        ;;
    "all")
        echo -e "${YELLOW}Запуск всех тестов...${NC}"
        pytest tests/ -v --tb=short
        ;;
    "coverage")
        echo -e "${YELLOW}Запуск тестов с покрытием...${NC}"
        pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term-missing
        ;;
    *)
        echo "Использование: $0 [unit|integration|all|coverage]"
        echo "  unit        - Запуск unit-тестов (по умолчанию)"
        echo "  integration - Запуск интеграционных тестов"
        echo "  all         - Запуск всех тестов"
        echo "  coverage    - Запуск тестов с отчётом о покрытии"
        exit 1
        ;;
esac

echo -e "${GREEN}=========================================="
echo "Тесты завершены успешно!"
echo "==========================================${NC}"
