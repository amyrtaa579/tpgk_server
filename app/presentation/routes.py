"""API роутеры."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Body

from app.application.use_cases import (
    GetAboutInfoUseCase,
    GetAdmissionInfoUseCase,
    GetSpecialtiesUseCase,
    GetSpecialtyByCodeUseCase,
    GetFactTitlesBySpecialtyUseCase,
    GetFactByIdUseCase,
    GetNewsUseCase,
    GetNewsBySlugUseCase,
    GetFAQUseCase,
    GetDocumentsUseCase,
    GetGalleryUseCase,
    GetTestQuestionsUseCase,
    SubmitTestAnswersUseCase,
)
from app.presentation.schemas import (
    AboutResponse,
    AdmissionResponse,
    SpecialtiesResponse,
    SpecialtyDetailResponse,
    FactTitleSchema,
    FactDetailResponse,
    NewsListResponse,
    NewsDetailResponse,
    FAQItemSchema,
    DocumentItemSchema,
    GalleryItemDetailSchema,
    TestQuestionSchema,
    TestRequest,
    TestResultResponse,
)
from app.infrastructure.repositories import (
    SpecialtyRepository,
    FactRepository,
    NewsRepository,
    FAQRepository,
    DocumentRepository,
    GalleryRepository,
    TestQuestionRepository,
    AboutRepository,
    AdmissionRepository,
)
from app.infrastructure.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


def create_v1_router() -> APIRouter:
    """Создать роутер API v1."""
    router = APIRouter(prefix="/api/v1", tags=["API v1"])
    
    # === /about ===
    @router.get("/about", response_model=AboutResponse, summary="Информация о колледже")
    async def get_about(session: AsyncSession = Depends(get_db_session)):
        """Получение общей информации о колледже."""
        repository = AboutRepository(session)
        use_case = GetAboutInfoUseCase(repository)
        result = await use_case.execute()
        return result
    
    # === /admission ===
    @router.get("/admission", response_model=AdmissionResponse, summary="Информация о приёмной кампании")
    async def get_admission(
        year: Optional[int] = Query(None, description="Год поступления"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение всей информации о приёмной кампании."""
        specialty_repo = SpecialtyRepository(session)
        repository = AdmissionRepository(session, specialty_repo)
        use_case = GetAdmissionInfoUseCase(repository)
        result = await use_case.execute(year)
        return result
    
    # === /specialties ===
    @router.get("/specialties", response_model=SpecialtiesResponse, summary="Список специальностей")
    async def get_specialties(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=50, description="Элементов на странице"),
        search: Optional[str] = Query(None, description="Поиск по названию"),
        form: Optional[str] = Query(None, description="Форма обучения: budget или paid"),
        popular: Optional[bool] = Query(None, description="Только популярные"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение списка всех специальностей с фильтрацией и пагинацией."""
        repository = SpecialtyRepository(session)
        use_case = GetSpecialtiesUseCase(repository)
        result = await use_case.execute(page=page, limit=limit, search=search, form=form, popular=popular)
        return result
    
    # === /specialties/{code} ===
    @router.get("/specialties/{code}", response_model=SpecialtyDetailResponse, summary="Детали специальности")
    async def get_specialty(
        code: str,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение полной информации о конкретной специальности."""
        specialty_repo = SpecialtyRepository(session)
        fact_repo = FactRepository(session)
        use_case = GetSpecialtyByCodeUseCase(specialty_repo, fact_repo)
        result = await use_case.execute(code)
        return result
    
    # === /specialties/{code}/facts ===
    @router.get("/specialties/{code}/facts", response_model=list[FactTitleSchema], summary="Факты специальности")
    async def get_specialty_facts(
        code: str,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение заголовков интересных фактов для специальности."""
        repository = FactRepository(session)
        use_case = GetFactTitlesBySpecialtyUseCase(repository)
        result = await use_case.execute(code)
        return result
    
    # === /facts/{fact_id} ===
    @router.get("/facts/{fact_id}", response_model=FactDetailResponse, summary="Детали факта")
    async def get_fact(
        fact_id: int,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение полного содержимого интересного факта."""
        repository = FactRepository(session)
        use_case = GetFactByIdUseCase(repository)
        result = await use_case.execute(fact_id)
        return result
    
    # === /news ===
    @router.get("/news", response_model=NewsListResponse, summary="Список новостей")
    async def get_news(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(9, ge=1, le=20, description="Новостей на странице"),
        search: Optional[str] = Query(None, description="Поиск по заголовку"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение списка новостей с пагинацией."""
        repository = NewsRepository(session)
        use_case = GetNewsUseCase(repository)
        result = await use_case.execute(page=page, limit=limit, search=search)
        return result
    
    # === /news/{slug} ===
    @router.get("/news/{slug}", response_model=NewsDetailResponse, summary="Детали новости")
    async def get_news_by_slug(
        slug: str,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение полной новости с содержимым и галереей."""
        repository = NewsRepository(session)
        use_case = GetNewsBySlugUseCase(repository)
        result = await use_case.execute(slug)
        return result
    
    # === /faq ===
    @router.get("/faq", response_model=list[FAQItemSchema], summary="Часто задаваемые вопросы")
    async def get_faq(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение списка FAQ с фильтрацией по категории."""
        repository = FAQRepository(session)
        use_case = GetFAQUseCase(repository)
        result = await use_case.execute(category=category)
        return result
    
    # === /documents ===
    @router.get("/documents", response_model=list[DocumentItemSchema], summary="Документы")
    async def get_documents(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение списка документов для скачивания."""
        repository = DocumentRepository(session)
        use_case = GetDocumentsUseCase(repository)
        result = await use_case.execute(category=category)
        return result
    
    # === /images ===
    @router.get("/images", response_model=list[GalleryItemDetailSchema], summary="Галерея изображений")
    async def get_gallery(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение общей фотогалереи колледжа."""
        repository = GalleryRepository(session)
        use_case = GetGalleryUseCase(repository)
        result = await use_case.execute(category=category)
        return result
    
    # === /test/questions ===
    @router.get("/test/questions", response_model=list[TestQuestionSchema], summary="Вопросы теста")
    async def get_test_questions(
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение всех вопросов профориентационного теста."""
        repository = TestQuestionRepository(session)
        use_case = GetTestQuestionsUseCase(repository)
        result = await use_case.execute()
        return result
    
    # === /test/results ===
    @router.post("/test/results", response_model=TestResultResponse, summary="Результат теста")
    async def submit_test_results(
        request: TestRequest = Body(..., description="Ответы пользователя"),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Отправка ответов на тест и получение персональной рекомендации."""
        answers = [{"question_id": a.question_id, "selected": a.selected} for a in request.answers]
        
        repository = TestQuestionRepository(session)
        specialty_repo = SpecialtyRepository(session)
        use_case = SubmitTestAnswersUseCase(repository, specialty_repo)
        result = await use_case.execute(answers)
        return result
    
    return router
