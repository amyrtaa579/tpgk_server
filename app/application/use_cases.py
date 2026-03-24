"""Use Cases для всех эндпоинтов API."""

from datetime import datetime
from typing import Optional

from app.domain.models import (
    AboutInfo,
    AdmissionInfo,
    Specialty,
    InterestingFact,
    News,
    FAQ,
    Document,
    GalleryImage,
    TestQuestion,
    TestAnswer,
    TestResult,
)
from app.domain.repositories import (
    IAboutRepository,
    IAdmissionRepository,
    ISpecialtyRepository,
    IFactRepository,
    INewsRepository,
    IFAQRepository,
    IDocumentRepository,
    IGalleryRepository,
    ITestQuestionRepository,
)
from app.core.exceptions import NotFoundException, BadRequestException, ValidationException


class GetAboutInfoUseCase:
    """Получение информации о колледже."""
    
    def __init__(self, repository: IAboutRepository):
        self.repository = repository
    
    async def execute(self) -> AboutInfo:
        return await self.repository.get_info()


class GetAdmissionInfoUseCase:
    """Получение информации о приёмной кампании."""
    
    def __init__(self, repository: IAdmissionRepository):
        self.repository = repository
    
    async def execute(self, year: Optional[int] = None) -> AdmissionInfo:
        if year is None:
            year = datetime.now().year
        return await self.repository.get_admission_info(year)


class GetSpecialtiesUseCase:
    """Получение списка специальностей с пагинацией."""
    
    def __init__(self, repository: ISpecialtyRepository):
        self.repository = repository
    
    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        form: Optional[str] = None,
        popular: Optional[bool] = None,
    ) -> dict:
        if page < 1:
            raise BadRequestException("Номер страницы должен быть >= 1")
        if limit < 1 or limit > 50:
            raise BadRequestException("Лимит должен быть от 1 до 50")
        if form and form not in ("budget", "paid"):
            raise BadRequestException("Некорректное значение form. Допустимы: budget, paid")
        
        specialties, total = await self.repository.get_all(
            page=page, limit=limit, search=search, form=form, popular=popular
        )
        
        items = [
            {
                "code": s.code,
                "name": s.name,
                "short_description": s.short_description,
                "images": [{"url": img.url, "alt": img.alt} for img in s.images],
            }
            for s in specialties
        ]
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items,
        }


class GetSpecialtyByCodeUseCase:
    """Получение специальности по коду."""
    
    def __init__(self, repository: ISpecialtyRepository, fact_repository: IFactRepository):
        self.repository = repository
        self.fact_repository = fact_repository
    
    async def execute(self, code: str) -> dict:
        specialty = await self.repository.get_by_code(code)
        if not specialty:
            raise NotFoundException(f"Специальность с кодом {code} не найдена")
        
        facts_preview = await self.fact_repository.get_titles_by_specialty_code(code)
        
        return {
            "code": specialty.code,
            "name": specialty.name,
            "description": specialty.description,
            "duration": specialty.duration,
            "budget_places": specialty.budget_places,
            "paid_places": specialty.paid_places,
            "qualification": specialty.qualification,
            "exams": specialty.exams,
            "interesting_facts_preview": facts_preview,
            "images": [{"url": img.url, "alt": img.alt, "caption": img.caption} for img in specialty.images],
        }


class GetFactTitlesBySpecialtyUseCase:
    """Получение заголовков фактов по специальности."""
    
    def __init__(self, repository: IFactRepository):
        self.repository = repository
    
    async def execute(self, specialty_code: str) -> list[dict]:
        return await self.repository.get_titles_by_specialty_code(specialty_code)


class GetFactByIdUseCase:
    """Получение полного факта по ID."""
    
    def __init__(self, repository: IFactRepository):
        self.repository = repository
    
    async def execute(self, fact_id: int) -> dict:
        # Получаем все факты и ищем по ID (в реальной реализации будет get_by_id)
        # Для упрощения предполагаем, что репозиторий вернёт факт
        fact = await self.repository.get_by_id(fact_id)
        if not fact:
            raise NotFoundException(f"Факт с ID {fact_id} не найден")
        
        return {
            "id": fact.id,
            "title": fact.title,
            "description": fact.description,
            "images": [{"url": img.url, "alt": img.alt, "caption": img.caption} for img in fact.images],
        }


class GetNewsUseCase:
    """Получение списка новостей с пагинацией."""
    
    def __init__(self, repository: INewsRepository):
        self.repository = repository
    
    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> dict:
        if page < 1:
            raise BadRequestException("Номер страницы должен быть >= 1")
        if limit < 1 or limit > 20:
            raise BadRequestException("Лимит должен быть от 1 до 20")
        
        news_list, total = await self.repository.get_all(page=page, limit=limit, search=search)
        
        items = [
            {
                "id": n.id,
                "title": n.title,
                "slug": n.slug,
                "preview_text": n.preview_text,
                "preview_image": n.preview_image,
                "published_at": n.published_at.isoformat(),
            }
            for n in news_list
        ]
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items,
        }


class GetNewsBySlugUseCase:
    """Получение новости по slug."""
    
    def __init__(self, repository: INewsRepository):
        self.repository = repository
    
    async def execute(self, slug: str) -> dict:
        news = await self.repository.get_by_slug(slug)
        if not news:
            raise NotFoundException(f"Новость с slug {slug} не найдена")
        
        await self.repository.increment_views(slug)
        
        return {
            "id": news.id,
            "title": news.title,
            "slug": news.slug,
            "content": news.content,
            "gallery": [
                {
                    "url": img.url,
                    "thumbnail": img.thumbnail or img.url,
                    "alt": img.alt,
                    "caption": img.caption,
                }
                for img in news.gallery
            ],
            "published_at": news.published_at.isoformat(),
            "views": news.views,
        }


class GetFAQUseCase:
    """Получение списка FAQ."""

    def __init__(self, repository: IFAQRepository):
        self.repository = repository

    async def execute(self, category: Optional[str] = None) -> list[dict]:
        faq_list = await self.repository.get_all(category=category)

        return [
            {
                "id": f.id,
                "question": f.question,
                "answer": f.answer,
                "category": f.category,
                "show_in_admission": f.show_in_admission,
                "images": [{"url": img.url, "alt": img.alt, "caption": img.caption} for img in f.images],
                "documents": [{"url": doc.url, "alt": doc.alt, "caption": doc.caption} for doc in f.documents],
            }
            for f in faq_list
        ]


class GetDocumentsUseCase:
    """Получение списка документов."""
    
    def __init__(self, repository: IDocumentRepository):
        self.repository = repository
    
    async def execute(self, category: Optional[str] = None) -> list[dict]:
        documents = await self.repository.get_all(category=category)
        
        return [
            {
                "id": d.id,
                "title": d.title,
                "category": d.category,
                "file_url": d.file_url,
                "file_size": d.file_size,
                "images": [{"url": img.url, "alt": img.alt} for img in d.images],
            }
            for d in documents
        ]


class GetGalleryUseCase:
    """Получение галереи изображений."""
    
    def __init__(self, repository: IGalleryRepository):
        self.repository = repository
    
    async def execute(self, category: Optional[str] = None) -> list[dict]:
        images = await self.repository.get_all(category=category)
        
        return [
            {
                "id": img.id,
                "url": img.url,
                "thumbnail": img.thumbnail,
                "alt": img.alt,
                "category": img.category,
                "caption": img.caption,
                "date_taken": img.date_taken.isoformat() if img.date_taken else None,
            }
            for img in images
        ]


class GetTestQuestionsUseCase:
    """Получение вопросов профориентационного теста."""

    def __init__(self, repository: ITestQuestionRepository):
        self.repository = repository

    async def execute(self) -> list[dict]:
        questions = await self.repository.get_all()

        return [
            {
                "id": q.id,
                "text": q.text,
                "options": q.options,
                "image_url": q.image_url,
                "documents": [{"url": doc.url, "alt": doc.alt, "caption": doc.caption} for doc in q.documents],
            }
            for q in questions
        ]


class SubmitTestAnswersUseCase:
    """Отправка ответов на тест и получение рекомендации."""
    
    def __init__(self, repository: ITestQuestionRepository, specialty_repository: ISpecialtyRepository):
        self.repository = repository
        self.specialty_repository = specialty_repository
    
    async def execute(self, answers: list[dict]) -> dict:
        # Валидация количества ответов
        if len(answers) != 10:
            raise ValidationException("Должно быть ровно 10 ответов")
        
        # Валидация каждого ответа
        for answer in answers:
            question_id = answer.get("question_id")
            selected = answer.get("selected")
            
            if question_id is None or selected is None:
                raise ValidationException("Каждый ответ должен содержать question_id и selected")
            
            is_valid = await self.repository.validate_answer(question_id, selected)
            if not is_valid:
                raise ValidationException(f"Некорректный ответ для вопроса {question_id}")
        
        # Расчёт рекомендации
        result = await self.repository.calculate_recommendation(answers)
        
        return result
