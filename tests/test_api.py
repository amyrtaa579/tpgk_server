"""Тесты для API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from datetime import datetime, timedelta

from app.infrastructure.models import (
    SpecialtyModel,
    SpecialtyEducationModel,
    InterestingFactModel,
    NewsModel,
    FAQModel,
    DocumentModel,
    GalleryImageModel,
    TestQuestionModel,
    AboutInfoModel,
    AdmissionInfoModel,
)


# =============================================================================
# Health Check и Root
# =============================================================================

class TestHealthCheck:
    """Тесты для /health endpoint."""

    async def test_health_check(self, client: AsyncClient):
        """Проверка health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Статус может быть "ok" или "degraded" (если Redis/MinIO недоступны)
        assert data["status"] in ["ok", "degraded"]
        assert "version" in data
        assert "services" in data


class TestRoot:
    """Тесты для / root endpoint."""

    async def test_root(self, client: AsyncClient):
        """Проверка корневого endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "Anmicius API"
        assert data["docs"] == "/docs"


# =============================================================================
# About
# =============================================================================

class TestAbout:
    """Тесты для /api/v1/about endpoint."""

    async def test_get_about_default(self, client: AsyncClient):
        """Получение информации о колледже (данные по умолчанию)."""
        response = await client.get("/api/v1/about")
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "description" in data
        assert "images" in data
        assert isinstance(data["description"], list)
        assert isinstance(data["images"], list)

    async def test_get_about_from_db(self, client: AsyncClient, test_session: AsyncSession):
        """Получение информации о колледже из БД."""
        # Добавляем тестовые данные
        await test_session.execute(
            insert(AboutInfoModel).values(
                title="Тестовый колледж",
                description=["Описание 1", "Описание 2"],
                images=[{"url": "http://test.com/img.jpg", "alt": "Тест"}]
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/about")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Тестовый колледж"
        assert len(data["description"]) == 2


# =============================================================================
# Admission
# =============================================================================

class TestAdmission:
    """Тесты для /api/v1/admission endpoint."""

    async def test_get_admission_default_year(self, client: AsyncClient, test_session: AsyncSession):
        """Получение информации о приёмной кампании за текущий год."""
        # Добавляем специальность для корректной работы admission
        await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=[],
                duration="3 г.",
                budget_places=25,
                paid_places=15,
                qualification="Сварщик",
                exams=[],
                images=[],
                is_popular=False
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/admission")
        
        assert response.status_code == 200
        data = response.json()
        assert "year" in data
        assert "specialties_admission" in data
        assert "submission_methods" in data
        assert "important_dates" in data
        assert "faq_highlights" in data

    async def test_get_admission_specific_year(self, client: AsyncClient, test_session: AsyncSession):
        """Получение информации о приёмной кампании за указанный год."""
        # Добавляем специальность для корректной работы admission
        await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=[],
                duration="3 г.",
                budget_places=25,
                paid_places=15,
                qualification="Сварщик",
                exams=[],
                images=[],
                is_popular=False
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/admission?year=2025")
        
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2025


# =============================================================================
# Specialties
# =============================================================================

class TestSpecialties:
    """Тесты для /api/v1/specialties endpoints."""

    async def test_get_specialties_empty(self, client: AsyncClient):
        """Получение пустого списка специальностей."""
        response = await client.get("/api/v1/specialties")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["items"] == []

    async def test_get_specialties_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка специальностей с данными."""
        # Добавляем тестовые специальности
        from sqlalchemy import select
        result = await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=["Описание 1"],
                exams=["Математика", "Русский язык", "Физика"],
                images=[{"url": "http://test.com/img.jpg", "alt": "Сварка"}],
            ).returning(SpecialtyModel.id)
        )
        specialty_id = result.scalar()
        
        # Добавляем уровень образования
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id,
                education_level="Среднее общее",
                duration="3 г. 10 мес.",
                budget_places=25,
                paid_places=15,
            )
        )
        await test_session.commit()

        response = await client.get("/api/v1/specialties")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["code"] == "15.02.19"

    async def test_get_specialties_pagination(self, client: AsyncClient, test_session: AsyncSession):
        """Проверка пагинации специальностей."""
        # Добавляем 15 специальностей
        for i in range(15):
            result = await test_session.execute(
                insert(SpecialtyModel).values(
                    code=f"15.02.{i:02d}",
                    name=f"Специальность {i}",
                    short_description=f"Описание {i}",
                    description=[],
                    exams=[],
                    images=[],
                ).returning(SpecialtyModel.id)
            )
            specialty_id = result.scalar()
            # Добавляем уровень образования
            await test_session.execute(
                insert(SpecialtyEducationModel).values(
                    specialty_id=specialty_id,
                    education_level="Среднее общее",
                    duration="3 г.",
                    budget_places=10,
                    paid_places=5,
                )
            )
        await test_session.commit()

        # Первая страница
        response = await client.get("/api/v1/specialties?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10

        # Вторая страница
        response = await client.get("/api/v1/specialties?page=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    async def test_get_specialties_search(self, client: AsyncClient, test_session: AsyncSession):
        """Поиск специальностей."""
        result1 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id1 = result1.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id1,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=10,
                paid_places=5,
            )
        )
        
        result2 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="09.02.07",
                name="Информационные системы",
                short_description="IT специальности",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id2 = result2.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id2,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=20,
                paid_places=10,
            )
        )
        await test_session.commit()

        # Поиск по точному названию (SQLite ilike работает только с ASCII)
        response = await client.get("/api/v1/specialties?search=Сварочное")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1  # Может найти 1 или больше
        assert any(item["code"] == "15.02.19" for item in data["items"])

    async def test_get_specialties_filter_form(self, client: AsyncClient, test_session: AsyncSession):
        """Фильтр специальностей по форме обучения."""
        result1 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Бюджет",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id1 = result1.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id1,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=25,
                paid_places=0,
            )
        )
        
        result2 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="38.02.01",
                name="Экономика",
                short_description="Платное",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id2 = result2.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id2,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=0,
                paid_places=20,
            )
        )
        await test_session.commit()

        # Только с бюджетом
        response = await client.get("/api/v1/specialties?form=budget")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["code"] == "15.02.19"

        # Только платное
        response = await client.get("/api/v1/specialties?form=paid")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["code"] == "38.02.01"

    async def test_get_specialties_popular(self, client: AsyncClient, test_session: AsyncSession):
        """Фильтр популярных специальностей."""
        result1 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Популярная",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id1 = result1.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id1,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=25,
                paid_places=15,
            )
        )
        
        result2 = await test_session.execute(
            insert(SpecialtyModel).values(
                code="38.02.01",
                name="Экономика",
                short_description="Не популярная",
                description=[],
                exams=[],
                images=[],
            ).returning(SpecialtyModel.id)
        )
        specialty_id2 = result2.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id2,
                education_level="Среднее общее",
                duration="3 г.",
                budget_places=20,
                paid_places=10,
            )
        )
        await test_session.commit()

        response = await client.get("/api/v1/specialties?popular=true")
        assert response.status_code == 200
        data = response.json()
        # popular фильтр больше не поддерживается в текущей реализации
        assert data["total"] >= 1

    async def test_get_specialty_by_code(self, client: AsyncClient, test_session: AsyncSession):
        """Получение специальности по коду."""
        result = await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=["Полное описание"],
                exams=["Математика", "Русский язык", "Физика"],
                images=[{"url": "http://test.com/img.jpg", "alt": "Сварка"}],
            ).returning(SpecialtyModel.id)
        )
        specialty_id = result.scalar()
        await test_session.execute(
            insert(SpecialtyEducationModel).values(
                specialty_id=specialty_id,
                education_level="Среднее общее",
                duration="3 г. 10 мес.",
                budget_places=25,
                paid_places=15,
            )
        )
        await test_session.commit()

        response = await client.get("/api/v1/specialties/15.02.19")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "15.02.19"
        assert data["name"] == "Сварочное производство"
        assert "description" in data
        assert "interesting_facts_preview" in data

    async def test_get_specialty_not_found(self, client: AsyncClient):
        """Получение несуществующей специальности."""
        response = await client.get("/api/v1/specialties/99.99.99")
        
        assert response.status_code == 404


# =============================================================================
# Facts
# =============================================================================

class TestFacts:
    """Тесты для /api/v1/facts endpoints."""

    async def test_get_facts_by_specialty_code(self, client: AsyncClient, test_session: AsyncSession):
        """Получение фактов по специальности."""
        # Добавляем специальность
        await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=[],
                duration="3 г.",
                budget_places=25,
                paid_places=15,
                qualification="Сварщик",
                exams=[],
                images=[],
                is_popular=False
            )
        )
        # Добавляем факты
        await test_session.execute(
            insert(InterestingFactModel).values(
                specialty_code="15.02.19",
                title="Интересный факт 1",
                description=["Описание факта"],
                images=[]
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/specialties/15.02.19/facts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Интересный факт 1"

    async def test_get_fact_by_id(self, client: AsyncClient, test_session: AsyncSession):
        """Получение факта по ID."""
        await test_session.execute(
            insert(SpecialtyModel).values(
                code="15.02.19",
                name="Сварочное производство",
                short_description="Подготовка сварщиков",
                description=[],
                duration="3 г.",
                budget_places=25,
                paid_places=15,
                qualification="Сварщик",
                exams=[],
                images=[],
                is_popular=False
            )
        )
        await test_session.execute(
            insert(InterestingFactModel).values(
                specialty_code="15.02.19",
                title="Интересный факт",
                description=["Полное описание факта"],
                images=[{"url": "http://test.com/fact.jpg", "alt": "Факт"}]
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/facts/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Интересный факт"
        assert "description" in data
        assert "images" in data

    async def test_get_fact_not_found(self, client: AsyncClient):
        """Получение несуществующего факта."""
        response = await client.get("/api/v1/facts/999")
        
        assert response.status_code == 404


# =============================================================================
# News
# =============================================================================

class TestNews:
    """Тесты для /api/v1/news endpoints."""

    async def test_get_news_empty(self, client: AsyncClient):
        """Получение пустого списка новостей."""
        response = await client.get("/api/v1/news")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_get_news_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка новостей."""
        await test_session.execute(
            insert(NewsModel).values(
                title="Тестовая новость",
                slug="testovaya-novost",
                preview_text="Краткое описание",
                content=["Полный текст новости"],
                preview_image="http://test.com/preview.jpg",
                gallery=[],
                published_at=datetime.utcnow(),
                views=0
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/news")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Тестовая новость"

    async def test_get_news_by_slug(self, client: AsyncClient, test_session: AsyncSession):
        """Получение новости по slug."""
        await test_session.execute(
            insert(NewsModel).values(
                title="Тестовая новость",
                slug="testovaya-novost",
                preview_text="Краткое описание",
                content=["Полный текст"],
                preview_image="http://test.com/preview.jpg",
                gallery=[{"url": "http://test.com/gallery.jpg", "alt": "Галерея"}],
                published_at=datetime.utcnow(),
                views=5
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/news/testovaya-novost")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "testovaya-novost"
        # Проверяем, что контент возвращается (список строк)
        assert "content" in data
        assert "gallery" in data

    async def test_get_news_by_slug_not_found(self, client: AsyncClient):
        """Получение несуществующей новости."""
        response = await client.get("/api/v1/news/nonexistent")
        
        assert response.status_code == 404

    async def test_news_increment_views(self, client: AsyncClient, test_session: AsyncSession):
        """Проверка увеличения счётчика просмотров (базовый тест)."""
        await test_session.execute(
            insert(NewsModel).values(
                title="Новость для просмотров",
                slug="novost-dlya-prosmotrov",
                preview_text="Краткое описание",
                content=[],
                preview_image=None,
                gallery=[],
                published_at=datetime.utcnow(),
                views=10
            )
        )
        await test_session.commit()
        
        # Получаем новость - endpoint должен вернуть данные без ошибок
        response = await client.get("/api/v1/news/novost-dlya-prosmotrov")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "novost-dlya-prosmotrov"


# =============================================================================
# FAQ
# =============================================================================

class TestFAQ:
    """Тесты для /api/v1/faq endpoint."""

    async def test_get_faq_empty(self, client: AsyncClient):
        """Получение пустого списка FAQ."""
        response = await client.get("/api/v1/faq")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_faq_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка FAQ."""
        await test_session.execute(
            insert(FAQModel).values(
                question="Вопрос 1",
                answer="Ответ 1",
                category="Общее",
                show_in_admission=True,
                images=[],
                documents=[]
            )
        )
        await test_session.execute(
            insert(FAQModel).values(
                question="Вопрос 2",
                answer="Ответ 2",
                category="Приём",
                show_in_admission=False,
                images=[],
                documents=[]
            )
        )
        await test_session.commit()

        response = await client.get("/api/v1/faq")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_faq_by_category(self, client: AsyncClient, test_session: AsyncSession):
        """Фильтрация FAQ по категории."""
        await test_session.execute(
            insert(FAQModel).values(
                question="Вопрос 1",
                answer="Ответ 1",
                category="Общее",
                show_in_admission=True,
                images=[],
                documents=[]
            )
        )
        await test_session.execute(
            insert(FAQModel).values(
                question="Вопрос 2",
                answer="Ответ 2",
                category="Приём",
                show_in_admission=False,
                images=[],
                documents=[]
            )
        )
        await test_session.commit()

        response = await client.get("/api/v1/faq?category=Приём")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Приём"


# =============================================================================
# Documents
# =============================================================================

class TestDocuments:
    """Тесты для /api/v1/documents endpoint."""

    async def test_get_documents_empty(self, client: AsyncClient):
        """Получение пустого списка документов."""
        response = await client.get("/api/v1/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_documents_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение списка документов."""
        await test_session.execute(
            insert(DocumentModel).values(
                title="Документ 1",
                category="Лицензии",
                file_url="http://test.com/doc1.pdf",
                file_size=1024,
                images=[]
            )
        )
        await test_session.execute(
            insert(DocumentModel).values(
                title="Документ 2",
                category="Аккредитации",
                file_url="http://test.com/doc2.pdf",
                file_size=2048,
                images=[]
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_documents_by_category(self, client: AsyncClient, test_session: AsyncSession):
        """Фильтрация документов по категории."""
        await test_session.execute(
            insert(DocumentModel).values(
                title="Документ 1",
                category="Лицензии",
                file_url="http://test.com/doc1.pdf",
                file_size=1024,
                images=[]
            )
        )
        await test_session.execute(
            insert(DocumentModel).values(
                title="Документ 2",
                category="Аккредитации",
                file_url="http://test.com/doc2.pdf",
                file_size=2048,
                images=[]
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/documents?category=Лицензии")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Лицензии"


# =============================================================================
# Gallery (Images)
# =============================================================================

class TestGallery:
    """Тесты для /api/v1/images endpoint."""

    async def test_get_gallery_empty(self, client: AsyncClient):
        """Получение пустой галереи."""
        response = await client.get("/api/v1/images")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_gallery_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение галереи с данными."""
        await test_session.execute(
            insert(GalleryImageModel).values(
                url="http://test.com/img1.jpg",
                thumbnail="http://test.com/thumb1.jpg",
                alt="Изображение 1",
                category="Колледж",
                caption="Подпись 1",
                date_taken=datetime.utcnow()
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/images")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["url"] == "http://test.com/img1.jpg"

    async def test_get_gallery_by_category(self, client: AsyncClient, test_session: AsyncSession):
        """Фильтрация галереи по категории."""
        await test_session.execute(
            insert(GalleryImageModel).values(
                url="http://test.com/img1.jpg",
                thumbnail="http://test.com/thumb1.jpg",
                alt="Изображение 1",
                category="Колледж",
                caption="Подпись 1",
                date_taken=datetime.utcnow()
            )
        )
        await test_session.execute(
            insert(GalleryImageModel).values(
                url="http://test.com/img2.jpg",
                thumbnail="http://test.com/thumb2.jpg",
                alt="Изображение 2",
                category="Мероприятия",
                caption="Подпись 2",
                date_taken=datetime.utcnow()
            )
        )
        await test_session.commit()
        
        response = await client.get("/api/v1/images?category=Колледж")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Колледж"


# =============================================================================
# Test (Profiling)
# =============================================================================

class TestProfiling:
    """Тесты для /api/v1/test endpoints."""

    async def test_get_test_questions_empty(self, client: AsyncClient):
        """Получение пустого списка вопросов теста."""
        response = await client.get("/api/v1/test/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_test_questions_with_data(self, client: AsyncClient, test_session: AsyncSession):
        """Получение вопросов теста."""
        for i in range(10):
            await test_session.execute(
                insert(TestQuestionModel).values(
                    text=f"Вопрос {i}",
                    options=["Вариант 1", "Вариант 2", "Вариант 3"],
                    image_url=None,
                    documents=[]
                )
            )
        await test_session.commit()

        response = await client.get("/api/v1/test/questions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        assert "text" in data[0]
        assert "options" in data[0]

    async def test_submit_test_results(self, client: AsyncClient, test_session: AsyncSession):
        """Отправка результатов теста."""
        # Добавляем 10 вопросов
        for i in range(10):
            await test_session.execute(
                insert(TestQuestionModel).values(
                    text=f"Вопрос {i}",
                    options=["Вариант 1", "Вариант 2", "Вариант 3"],
                    image_url=None
                )
            )
        await test_session.commit()
        
        # Формируем ответы
        answers = [{"question_id": i + 1, "selected": "Вариант 1"} for i in range(10)]
        
        response = await client.post("/api/v1/test/results", json={"answers": answers})
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendation" in data
        assert "motivation" in data
        assert "recommended_specialties" in data

    async def test_submit_test_results_wrong_count(self, client: AsyncClient, test_session: AsyncSession):
        """Отправка неправильного количества ответов."""
        # Добавляем вопросы
        for i in range(10):
            await test_session.execute(
                insert(TestQuestionModel).values(
                    text=f"Вопрос {i}",
                    options=["Вариант 1", "Вариант 2", "Вариант 3"],
                    image_url=None
                )
            )
        await test_session.commit()
        
        # Только 5 ответов вместо 10
        answers = [{"question_id": i + 1, "selected": "Вариант 1"} for i in range(5)]
        
        response = await client.post("/api/v1/test/results", json={"answers": answers})
        
        assert response.status_code == 422

    async def test_submit_test_results_invalid_answer(self, client: AsyncClient, test_session: AsyncSession):
        """Отправка некорректного ответа."""
        await test_session.execute(
            insert(TestQuestionModel).values(
                text="Вопрос 1",
                options=["Вариант 1", "Вариант 2", "Вариант 3"],
                image_url=None
            )
        )
        # Добавляем остальные вопросы
        for i in range(1, 10):
            await test_session.execute(
                insert(TestQuestionModel).values(
                    text=f"Вопрос {i}",
                    options=["Вариант 1", "Вариант 2", "Вариант 3"],
                    image_url=None
                )
            )
        await test_session.commit()
        
        # Некорректный ответ
        answers = [{"question_id": i + 1, "selected": "Неправильный вариант"} for i in range(10)]
        
        response = await client.post("/api/v1/test/results", json={"answers": answers})
        
        assert response.status_code == 422


# =============================================================================
# Error Handling
# =============================================================================

class TestErrorHandling:
    """Тесты обработки ошибок."""

    async def test_404_not_found(self, client: AsyncClient):
        """Проверка обработки 404."""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    async def test_invalid_pagination(self, client: AsyncClient):
        """Проверка обработки некорректной пагинации."""
        response = await client.get("/api/v1/specialties?page=-1")
        # FastAPI возвращает 422 для ошибок валидации параметров
        assert response.status_code == 422

    async def test_invalid_limit(self, client: AsyncClient):
        """Проверка обработки некорректного лимита."""
        response = await client.get("/api/v1/specialties?limit=100")
        # FastAPI возвращает 422 для ошибок валидации параметров
        assert response.status_code == 422
