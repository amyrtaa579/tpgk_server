"""Интеграционные тесты с реальным API через HTTP."""

import pytest
import httpx
import asyncio
from typing import Optional


# Базовый URL API (из переменных окружения или по умолчанию)
API_BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Получение базового URL API."""
    return API_BASE_URL


@pytest.fixture(scope="session")
def http_client(api_base_url: str) -> httpx.Client:
    """Создание HTTP клиента для интеграционных тестов."""
    return httpx.Client(base_url=api_base_url, timeout=10.0)


class TestIntegrationHealth:
    """Интеграционные тесты health check."""

    def test_health_check(self, http_client: httpx.Client):
        """Проверка доступности API."""
        response = http_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_endpoint(self, http_client: httpx.Client):
        """Проверка корневого endpoint."""
        response = http_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Anmicius API"
        assert "version" in data
        assert data["docs"] == "/docs"


class TestIntegrationAbout:
    """Интеграционные тесты /about."""

    def test_get_about(self, http_client: httpx.Client):
        """Получение информации о колледже."""
        response = http_client.get("/api/v1/about")
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "description" in data
        assert "images" in data
        assert isinstance(data["description"], list)


class TestIntegrationAdmission:
    """Интеграционные тесты /admission."""

    def test_get_admission(self, http_client: httpx.Client):
        """Получение информации о приёмной кампании."""
        response = http_client.get("/api/v1/admission")
        
        assert response.status_code == 200
        data = response.json()
        assert "year" in data
        assert "specialties_admission" in data
        assert "submission_methods" in data

    def test_get_admission_with_year(self, http_client: httpx.Client):
        """Получение информации за конкретный год."""
        response = http_client.get("/api/v1/admission?year=2025")
        
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2025


class TestIntegrationSpecialties:
    """Интеграционные тесты /specialties."""

    def test_get_specialties(self, http_client: httpx.Client):
        """Получение списка специальностей."""
        response = http_client.get("/api/v1/specialties")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "items" in data

    def test_get_specialties_pagination(self, http_client: httpx.Client):
        """Проверка пагинации."""
        response = http_client.get("/api/v1/specialties?page=1&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5

    def test_get_specialties_search(self, http_client: httpx.Client):
        """Проверка поиска."""
        response = http_client.get("/api/v1/specialties?search=свар")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestIntegrationFacts:
    """Интеграционные тесты /facts."""

    def test_get_facts_by_specialty(self, http_client: httpx.Client):
        """Получение фактов по специальности."""
        response = http_client.get("/api/v1/specialties/15.02.19/facts")
        
        # Может вернуть 200 с пустым списком или 404 если специальность не найдена
        assert response.status_code in [200, 404]


class TestIntegrationNews:
    """Интеграционные тесты /news."""

    def test_get_news(self, http_client: httpx.Client):
        """Получение списка новостей."""
        response = http_client.get("/api/v1/news")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data


class TestIntegrationFAQ:
    """Интеграционные тесты /faq."""

    def test_get_faq(self, http_client: httpx.Client):
        """Получение списка FAQ."""
        response = http_client.get("/api/v1/faq")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_faq_by_category(self, http_client: httpx.Client):
        """Фильтрация FAQ по категории."""
        response = http_client.get("/api/v1/faq?category=Общее")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestIntegrationDocuments:
    """Интеграционные тесты /documents."""

    def test_get_documents(self, http_client: httpx.Client):
        """Получение списка документов."""
        response = http_client.get("/api/v1/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestIntegrationGallery:
    """Интеграционные тесты /images."""

    def test_get_gallery(self, http_client: httpx.Client):
        """Получение галереи."""
        response = http_client.get("/api/v1/images")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestIntegrationTest:
    """Интеграционные тесты профориентации."""

    def test_get_test_questions(self, http_client: httpx.Client):
        """Получение вопросов теста."""
        response = http_client.get("/api/v1/test/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_submit_test_results(self, http_client: httpx.Client):
        """Отправка результатов теста (пустые ответы для проверки)."""
        # Отправляем тестовые ответы
        answers = [
            {"question_id": i + 1, "selected": "Вариант 1"}
            for i in range(10)
        ]
        
        response = http_client.post(
            "/api/v1/test/results",
            json={"answers": answers}
        )
        
        # Может вернуть 200 с результатом или 422 если вопросы не найдены
        assert response.status_code in [200, 422]


class TestIntegrationErrors:
    """Интеграционные тесты обработки ошибок."""

    def test_404_endpoint(self, http_client: httpx.Client):
        """Проверка обработки несуществующих endpoints."""
        response = http_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_pagination(self, http_client: httpx.Client):
        """Проверка обработки некорректной пагинации."""
        response = http_client.get("/api/v1/specialties?page=-1")
        # FastAPI возвращает 422 для ошибок валидации параметров
        assert response.status_code == 422

    def test_invalid_limit(self, http_client: httpx.Client):
        """Проверка обработки некорректного лимита."""
        response = http_client.get("/api/v1/specialties?limit=100")
        # FastAPI возвращает 422 для ошибок валидации параметров
        assert response.status_code == 422
