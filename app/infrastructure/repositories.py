"""Реализации репозиториев."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Specialty,
    SpecialtyEducationOption,
    InterestingFact,
    News,
    FAQ,
    FAQDocument,
    Document,
    GalleryImage,
    DocumentFile,
    TestQuestion,
    AboutInfo,
    AdmissionInfo,
    SubmissionMethod,
    ImportantDate,
    Image,
)
from app.domain.repositories import (
    ISpecialtyRepository,
    IFactRepository,
    INewsRepository,
    IFAQRepository,
    IDocumentRepository,
    IGalleryRepository,
    IDocumentFileRepository,
    ITestQuestionRepository,
    IAboutRepository,
    IAdmissionRepository,
    IUserRepository,
)
from app.infrastructure.models import (
    SpecialtyModel,
    SpecialtyEducationModel,
    InterestingFactModel,
    NewsModel,
    FAQModel,
    DocumentModel,
    GalleryImageModel,
    DocumentFileModel,
    TestQuestionModel,
    AboutInfoModel,
    AdmissionInfoModel,
    UserModel,
    RefreshTokenModel,
)


def to_image(data: dict) -> Image:
    """Конвертировать dict в Image."""
    return Image(
        url=data.get("url", ""),
        alt=data.get("alt", ""),
        caption=data.get("caption"),
        thumbnail=data.get("thumbnail"),
    )


class SpecialtyRepository(ISpecialtyRepository):
    """Репозиторий специальностей."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int, include_education: bool = True) -> Optional[Specialty]:
        query = select(SpecialtyModel)
        if include_education:
            query = query.options(selectinload(SpecialtyModel.education_options))
        query = query.where(SpecialtyModel.id == id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return await self._to_domain(model, include_education)

    async def get_by_code(self, code: str, include_education: bool = True) -> Optional[Specialty]:
        query = select(SpecialtyModel)
        if include_education:
            query = query.options(selectinload(SpecialtyModel.education_options))
        query = query.where(SpecialtyModel.code == code)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return await self._to_domain(model, include_education)

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        form: Optional[str] = None,
        popular: Optional[bool] = None,
    ) -> tuple[list[Specialty], int]:
        offset = (page - 1) * limit

        # Построение условий фильтрации
        conditions = []
        if search:
            conditions.append(SpecialtyModel.name.ilike(f"%{search}%"))
        if form == "budget":
            # Фильтр по специальностям с бюджетными местами на любом уровне образования
            conditions.append(SpecialtyModel.id.in_(
                select(SpecialtyEducationModel.specialty_id).where(
                    SpecialtyEducationModel.budget_places > 0
                )
            ))
        elif form == "paid":
            # Фильтр по специальностям с платными местами на любом уровне образования
            conditions.append(SpecialtyModel.id.in_(
                select(SpecialtyEducationModel.specialty_id).where(
                    SpecialtyEducationModel.paid_places > 0
                )
            ))

        # Получение общего количества
        count_query = select(func.count()).select_from(SpecialtyModel)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Получение данных
        query = select(SpecialtyModel).options(selectinload(SpecialtyModel.education_options))
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        models = result.scalars().all()

        specialties = []
        for m in models:
            specialties.append(await self._to_domain(m, include_education=True))
        return specialties, total

    async def get_codes_with_budget_or_paid(self, has_budget: bool = True) -> list[str]:
        if has_budget:
            result = await self.session.execute(
                select(SpecialtyModel.code).join(SpecialtyEducationModel).where(
                    SpecialtyEducationModel.budget_places > 0
                )
            )
        else:
            result = await self.session.execute(
                select(SpecialtyModel.code).join(SpecialtyEducationModel).where(
                    SpecialtyEducationModel.paid_places > 0
                )
            )
        return [row[0] for row in result.all()]

    async def create(
        self,
        code: str,
        name: str,
        short_description: str = "",
        description: list[str] = None,
        exams: list[str] = None,
        images: list[dict] = None,
        documents: list[dict] = None,
        education_options: list[dict] = None,
    ) -> Specialty:
        model = SpecialtyModel(
            code=code,
            name=name,
            short_description=short_description,
            description=description or [],
            exams=exams or [],
            images=images or [],
            documents=documents or [],
        )
        self.session.add(model)
        try:
            await self.session.flush()  # Получаем model.id

            # Добавляем уровни образования
            if education_options:
                for opt in education_options:
                    edu_model = SpecialtyEducationModel(
                        specialty_id=model.id,
                        education_level=opt.get("education_level", "Основное общее"),
                        duration=opt.get("duration", ""),
                        budget_places=opt.get("budget_places", 0),
                        paid_places=opt.get("paid_places", 0),
                    )
                    self.session.add(edu_model)

            await self.session.commit()
            # Явно загружаем education_options после commit через отдельный запрос
            await self.session.refresh(model)
            # Используем selectinload для явной загрузки
            from sqlalchemy.orm import selectinload
            result = await self.session.execute(
                select(SpecialtyModel)
                .options(selectinload(SpecialtyModel.education_options))
                .where(SpecialtyModel.id == model.id)
            )
            model = result.scalar_one_or_none()
            return await self._to_domain(model, include_education=True)
        except Exception:
            await self.session.rollback()
            raise

    async def update(
        self,
        id: int,
        code: Optional[str] = None,
        name: Optional[str] = None,
        short_description: Optional[str] = None,
        description: Optional[list[str]] = None,
        exams: Optional[list[str]] = None,
        images: Optional[list[dict]] = None,
        documents: Optional[list[dict]] = None,
        education_options: Optional[list[dict]] = None,
    ) -> Specialty:
        model = await self.session.get(SpecialtyModel, id)
        if not model:
            raise ValueError(f"Specialty with id {id} not found")

        if code is not None:
            model.code = code
        if name is not None:
            model.name = name
        if short_description is not None:
            model.short_description = short_description
        if description is not None:
            model.description = description
        if exams is not None:
            model.exams = exams
        if images is not None:
            model.images = images
        if documents is not None:
            model.documents = documents

        # Обновляем уровни образования
        if education_options is not None:
            # Удаляем старые
            await self.session.execute(
                delete(SpecialtyEducationModel).where(
                    SpecialtyEducationModel.specialty_id == id
                )
            )
            # Добавляем новые
            for opt in education_options:
                edu_model = SpecialtyEducationModel(
                    specialty_id=id,
                    education_level=opt.get("education_level", "Основное общее"),
                    duration=opt.get("duration", ""),
                    budget_places=opt.get("budget_places", 0),
                    paid_places=opt.get("paid_places", 0),
                )
                self.session.add(edu_model)

        model.updated_at = datetime.utcnow()
        await self.session.commit()
        # Явно загружаем education_options после commit через отдельный запрос
        await self.session.refresh(model)
        result = await self.session.execute(
            select(SpecialtyModel)
            .options(selectinload(SpecialtyModel.education_options))
            .where(SpecialtyModel.id == model.id)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model, include_education=True)

    async def delete(self, id: int) -> bool:
        model = await self.session.get(SpecialtyModel, id)
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def _to_domain(self, model: SpecialtyModel, include_education: bool = True) -> Specialty:
        specialty = Specialty(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            code=model.code,
            name=model.name,
            short_description=model.short_description,
            description=model.description,
            exams=model.exams,
            images=[to_image(img) for img in model.images],
            documents=[to_image(doc) for doc in model.documents],
            education_options=[],
        )

        if include_education:
            # education_options уже загружены через selectinload
            for edu in model.education_options:
                specialty.education_options.append(SpecialtyEducationOption(
                    id=edu.id,
                    specialty_id=edu.specialty_id,
                    education_level=edu.education_level,
                    duration=edu.duration,
                    budget_places=edu.budget_places,
                    paid_places=edu.paid_places,
                ))

        return specialty


class FactRepository(IFactRepository):
    """Репозиторий интересных фактов."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[InterestingFact]:
        result = await self.session.execute(
            select(InterestingFactModel).where(InterestingFactModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def get_by_specialty_code(self, specialty_code: str) -> list[InterestingFact]:
        result = await self.session.execute(
            select(InterestingFactModel).where(
                InterestingFactModel.specialty_code == specialty_code
            )
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
    
    async def get_titles_by_specialty_code(self, specialty_code: str) -> list[dict]:
        result = await self.session.execute(
            select(InterestingFactModel.id, InterestingFactModel.title).where(
                InterestingFactModel.specialty_code == specialty_code
            )
        )
        rows = result.all()
        return [{"id": row.id, "title": row.title} for row in rows]
    
    def _to_domain(self, model: InterestingFactModel) -> InterestingFact:
        return InterestingFact(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            specialty_code=model.specialty_code,
            title=model.title,
            description=model.description,
            images=[to_image(img) for img in model.images],
        )


class NewsRepository(INewsRepository):
    """Репозиторий новостей."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[News]:
        result = await self.session.execute(
            select(NewsModel).where(NewsModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[News], int]:
        offset = (page - 1) * limit
        
        # Построение условий фильтрации
        conditions = []
        if search:
            conditions.append(
                or_(
                    NewsModel.title.ilike(f"%{search}%"),
                    # Для JSON-поля content потребуется отдельная логика
                )
            )
        
        # Получение общего количества
        count_query = select(func.count()).select_from(NewsModel)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        query = select(NewsModel).order_by(NewsModel.published_at.desc())
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        news_list = [self._to_domain(m) for m in models]
        return news_list, total
    
    async def get_by_slug(self, slug: str) -> Optional[News]:
        result = await self.session.execute(
            select(NewsModel).where(NewsModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def increment_views(self, slug: str) -> int:
        """Увеличение счётчика просмотров (оптимизированный запрос)."""
        from sqlalchemy import update
        
        # Один атомарный UPDATE вместо SELECT + UPDATE
        result = await self.session.execute(
            update(NewsModel)
            .where(NewsModel.slug == slug)
            .values(views=NewsModel.views + 1)
        )
        await self.session.commit()
        return result.rowcount
    
    def _to_domain(self, model: NewsModel) -> News:
        return News(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            title=model.title,
            slug=model.slug,
            preview_text=model.preview_text,
            content=model.content,
            preview_image=model.preview_image,
            gallery=[to_image(img) for img in model.gallery],
            published_at=model.published_at,
            views=model.views,
        )


class FAQRepository(IFAQRepository):
    """Репозиторий FAQ."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[FAQ]:
        result = await self.session.execute(
            select(FAQModel).where(FAQModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(self, category: Optional[str] = None) -> list[FAQ]:
        query = select(FAQModel)
        if category:
            query = query.where(FAQModel.category == category)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(
        self,
        question: str,
        answer: str | list[str],
        category: str,
        show_in_admission: bool,
        images: list[dict],
        documents: list[dict] | None = None,
        document_file_ids: list[int] | None = None,
    ) -> FAQ:
        model = FAQModel(
            question=question,
            answer=answer,
            category=category,
            show_in_admission=show_in_admission,
            images=images,
            documents=documents or [],
            document_file_ids=document_file_ids or [],
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(
        self,
        id: int,
        question: Optional[str] = None,
        answer: Optional[str | list[str]] = None,
        category: Optional[str] = None,
        show_in_admission: Optional[bool] = None,
        images: Optional[list[dict]] = None,
        documents: Optional[list[dict]] = None,
        document_file_ids: Optional[list[int]] = None,
    ) -> FAQ:
        model = await self.get_by_id(id)
        if not model:
            raise ValueError(f"FAQ with id {id} not found")

        db_model = await self.session.get(FAQModel, id)
        if question is not None:
            db_model.question = question
        if answer is not None:
            db_model.answer = answer
        if category is not None:
            db_model.category = category
        if show_in_admission is not None:
            db_model.show_in_admission = show_in_admission
        if images is not None:
            db_model.images = images
        if documents is not None:
            db_model.documents = documents
        if document_file_ids is not None:
            db_model.document_file_ids = document_file_ids

        db_model.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_domain(db_model)

    async def delete(self, id: int) -> bool:
        model = await self.session.get(FAQModel, id)
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    def _to_domain(self, model: FAQModel) -> FAQ:
        return FAQ(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            question=model.question,
            answer=model.answer,
            category=model.category,
            show_in_admission=model.show_in_admission,
            images=[to_image(img) for img in model.images],
            documents=[
                FAQDocument(
                    title=doc.get("title", ""),
                    file_url=doc.get("file_url", ""),
                    file_size=doc.get("file_size"),
                )
                for doc in model.documents
            ],
            document_file_ids=model.document_file_ids or [],
        )


class DocumentRepository(IDocumentRepository):
    """Репозиторий документов."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(self, category: Optional[str] = None) -> list[Document]:
        query = select(DocumentModel)
        if category:
            query = query.where(DocumentModel.category == category)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(
        self,
        title: str,
        category: str,
        file_url: str,
        file_size: Optional[int],
        images: list[dict],
    ) -> Document:
        model = DocumentModel(
            title=title,
            category=category,
            file_url=file_url,
            file_size=file_size,
            images=images,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(
        self,
        id: int,
        title: Optional[str] = None,
        category: Optional[str] = None,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        images: Optional[list[dict]] = None,
    ) -> Document:
        db_model = await self.session.get(DocumentModel, id)
        if not db_model:
            raise ValueError(f"Document with id {id} not found")

        if title is not None:
            db_model.title = title
        if category is not None:
            db_model.category = category
        if file_url is not None:
            db_model.file_url = file_url
        if file_size is not None:
            db_model.file_size = file_size
        if images is not None:
            db_model.images = images

        db_model.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_domain(db_model)

    async def delete(self, id: int) -> bool:
        model = await self.session.get(DocumentModel, id)
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    def _to_domain(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            title=model.title,
            category=model.category,
            file_url=model.file_url,
            file_size=model.file_size,
            images=[to_image(img) for img in model.images],
        )


class GalleryRepository(IGalleryRepository):
    """Репозиторий галереи."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[GalleryImage]:
        result = await self.session.execute(
            select(GalleryImageModel).where(GalleryImageModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def get_all(self, category: Optional[str] = None) -> list[GalleryImage]:
        query = select(GalleryImageModel)
        if category:
            query = query.where(GalleryImageModel.category == category)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
    
    def _to_domain(self, model: GalleryImageModel) -> GalleryImage:
        return GalleryImage(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            url=model.url,
            thumbnail=model.thumbnail,
            alt=model.alt,
            category=model.category,
            caption=model.caption,
            date_taken=model.date_taken,
        )


class DocumentFileRepository(IDocumentFileRepository):
    """Репозиторий файлов документов."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[DocumentFile]:
        result = await self.session.execute(
            select(DocumentFileModel).where(DocumentFileModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(self, category: Optional[str] = None) -> list[DocumentFile]:
        query = select(DocumentFileModel)
        if category:
            query = query.where(DocumentFileModel.category == category)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: DocumentFileModel) -> DocumentFile:
        return DocumentFile(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            title=model.title,
            file_url=model.file_url,
            file_size=model.file_size,
            category=model.category,
        )


class TestQuestionRepository(ITestQuestionRepository):
    """Репозиторий вопросов теста."""

    # Маппинг ответов на специальности (упрощённая логика)
    SPECIALTY_MAPPING = {
        "technic": ["15.02.19", "22.02.06"],  # Сварочное производство
        "it": ["09.02.07"],  # Информационные системы
        "economy": ["38.02.01"],  # Экономика и бухгалтерский учёт
        "service": ["43.02.15"],  # Поварское дело
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[TestQuestion]:
        result = await self.session.execute(
            select(TestQuestionModel).where(TestQuestionModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(self) -> list[TestQuestion]:
        result = await self.session.execute(select(TestQuestionModel))
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(
        self,
        text: str,
        options: list[str],
        answer_scores: list[dict] | None = None,
        image_url: Optional[str] = None,
        documents: list[dict] | None = None,
    ) -> TestQuestion:
        model = TestQuestionModel(
            text=text,
            options=options,
            answer_scores=answer_scores or [],
            image_url=image_url,
            documents=documents or [],
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(
        self,
        id: int,
        text: Optional[str] = None,
        options: Optional[list[str]] = None,
        answer_scores: Optional[list[dict]] = None,
        image_url: Optional[str] = None,
        documents: Optional[list[dict]] = None,
    ) -> TestQuestion:
        db_model = await self.session.get(TestQuestionModel, id)
        if not db_model:
            raise ValueError(f"TestQuestion with id {id} not found")

        if text is not None:
            db_model.text = text
        if options is not None:
            db_model.options = options
        if answer_scores is not None:
            db_model.answer_scores = answer_scores
        if image_url is not None:
            db_model.image_url = image_url
        if documents is not None:
            db_model.documents = documents

        db_model.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_domain(db_model)

    async def delete(self, id: int) -> bool:
        model = await self.session.get(TestQuestionModel, id)
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def validate_answer(self, question_id: int, selected: str) -> bool:
        result = await self.session.execute(
            select(TestQuestionModel.options).where(TestQuestionModel.id == question_id)
        )
        options = result.scalar()
        if not options:
            return False
        return selected in options
    
    async def calculate_recommendation(self, answers: list[dict]) -> dict:
        """
        Расчёт рекомендации на основе ответов.
        Использует answer_scores из БД для каждого вопроса.
        Считает баллы для каждого кода специальности напрямую.
        """
        from app.infrastructure.models import SpecialtyModel

        # Получаем все специальности из БД для маппинга кодов на данные
        result = await self.session.execute(select(SpecialtyModel))
        all_specialties = result.scalars().all()
        specialties_map = {s.code: s for s in all_specialties}

        # Счётчики для каждой специальности (по коду)
        scores: dict[str, int] = {}

        # Получаем все вопросы из БД
        questions = await self.get_all()
        questions_dict = {q.id: q for q in questions}

        # Анализ ответов
        for answer in answers:
            question_id = answer.get("question_id", 0)
            selected_raw = answer.get("selected", "")
            # Поддержка множественного выбора (список) или одиночного (строка)
            selected_list = selected_raw if isinstance(selected_raw, list) else [selected_raw]

            question = questions_dict.get(question_id)
            if not question:
                continue

            # Получаем answer_scores для вопроса
            answer_scores = question.answer_scores or []
            if isinstance(answer_scores, str):
                import json
                answer_scores = json.loads(answer_scores)

            # Для каждого выбранного ответа
            for selected in selected_list:
                # Ищем соответствующий ответ в answer_scores
                for score_entry in answer_scores:
                    if score_entry.get("answer", "").lower() == selected.lower():
                        # Добавляем баллы специальностям
                        specialty_codes = score_entry.get("specialties", [])
                        for code in specialty_codes:
                            scores[code] = scores.get(code, 0) + 1

        # Сортируем специальности по баллам
        sorted_codes = sorted(scores.keys(), key=lambda c: scores[c], reverse=True)

        # Формируем топ-3 рекомендаций
        top_specialties = []
        for code in sorted_codes[:3]:
            if scores[code] > 0 and code in specialties_map:
                spec = specialties_map[code]
                # Получаем данные об местах и duração из education_options
                total_budget = sum(eo.budget_places for eo in spec.education_options) if spec.education_options else 0
                total_paid = sum(eo.paid_places for eo in spec.education_options) if spec.education_options else 0
                duration = spec.education_options[0].duration if spec.education_options else ""
                top_specialties.append({
                    "code": spec.code,
                    "name": spec.name,
                    "duration": duration,
                    "budget_places": total_budget,
                })

        # Если ничего не набрано — дефолтная рекомендация
        if not top_specialties:
            top_specialties = [
                {
                    "code": "15.02.19",
                    "name": "Сварочное производство",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25,
                },
                {
                    "code": "21.02.03",
                    "name": "Сооружение и эксплуатация газонефтепроводов",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25,
                },
            ]
            recommendation_text = "Вам могут подойти технические специальности нашего колледжа!"
            motivation_text = "Рекомендуем пройти тест ещё раз или обратиться к приёмной комиссии для индивидуальной консультации."
        else:
            best = top_specialties[0]
            recommendation_text = f"Вам подойдёт направление «{best['name']}»!"
            motivation_text = f"На основе ваших ответов рекомендуем рассмотреть специальность {best['code']} {best['name']}."

        return {
            "recommendation": recommendation_text,
            "motivation": motivation_text,
            "recommended_specialties": top_specialties,
        }

    def _to_domain(self, model: TestQuestionModel) -> TestQuestion:
        return TestQuestion(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            text=model.text,
            options=model.options,
            answer_scores=model.answer_scores,
            image_url=model.image_url,
            documents=model.documents,
        )


class AboutRepository(IAboutRepository):
    """Репозиторий информации о колледже."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_info(self) -> AboutInfo:
        result = await self.session.execute(select(AboutInfoModel).limit(1))
        model = result.scalar_one_or_none()

        if not model:
            # Возвращаем данные по умолчанию
            return AboutInfo(
                title="Стрежевской филиал ОГБПОУ «Томский промышленно-гуманитарный колледж»",
                description=[
                    "Колледж готовит квалифицированных специалистов для нефтегазовой, химической и промышленной отраслей. Наши выпускники востребованы на ведущих предприятиях региона.",
                    "Мы делаем акцент на практику — студенты работают на современном оборудовании уже с первого курса. Лаборатории оснащены по последнему слову техники.",
                    "В колледже созданы все условия для всестороннего развития: спортивные секции, творческие студии и волонтёрские отряды.",
                ],
                images=[
                    Image(
                        url="https://example.com/images/main-building.jpg",
                        alt="Главный корпус колледжа",
                        caption="Главный корпус",
                    ),
                    Image(
                        url="https://example.com/images/workshop.jpg",
                        alt="Сварочная мастерская",
                        caption="Современная сварочная мастерская",
                    ),
                ],
            )

        return AboutInfo(
            title=model.title,
            description=model.description,
            images=[to_image(img) for img in model.images],
        )

    async def update(
        self,
        title: Optional[str] = None,
        description: Optional[list[str]] = None,
        images: Optional[list[dict]] = None,
    ) -> AboutInfo:
        result = await self.session.execute(select(AboutInfoModel).limit(1))
        model = result.scalar_one_or_none()

        if not model:
            # Создаём новую запись, если её нет
            model = AboutInfoModel(
                title=title or "Стрежевской филиал ОГБПОУ «Томский промышленно-гуманитарный колледж»",
                description=description or [],
                images=images or [],
            )
            self.session.add(model)
        else:
            # Обновляем существующую запись
            if title is not None:
                model.title = title
            if description is not None:
                model.description = description
            if images is not None:
                model.images = images
            model.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(model)

        return AboutInfo(
            title=model.title,
            description=model.description,
            images=[to_image(img) for img in model.images],
        )


class AdmissionRepository(IAdmissionRepository):
    """Репозиторий информации о приёмной кампании."""

    def __init__(self, session: AsyncSession, specialty_repository: SpecialtyRepository):
        self.session = session
        self.specialty_repository = specialty_repository
    
    async def get_admission_info(self, year: int) -> AdmissionInfo:
        result = await self.session.execute(
            select(AdmissionInfoModel).where(AdmissionInfoModel.year == year)
        )
        model = result.scalar_one_or_none()

        if not model:
            # Нет данных — возвращаем пустую структуру (пользователь заполнит через админку)
            return AdmissionInfo(
                year=year,
                specialties_admission=[],
                submission_methods=[],
                important_dates=[],
            )

        submission_methods = [
            SubmissionMethod(
                title=m.get("title", ""),
                description=m.get("description", ""),
                link=m.get("link"),
            )
            for m in model.submission_methods
        ]

        important_dates = [
            ImportantDate(
                title=d.get("title", ""),
                date=datetime.fromisoformat(d.get("date")) if isinstance(d.get("date"), str) else d.get("date"),
                description=d.get("description"),
            )
            for d in model.important_dates
        ]

        return AdmissionInfo(
            year=model.year,
            specialties_admission=model.specialties_admission,
            submission_methods=submission_methods,
            important_dates=important_dates,
        )


class UserRepository(IUserRepository):
    """Репозиторий пользователей."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional["User"]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> Optional["User"]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_username(self, username: str) -> Optional["User"]:
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def create(self, email: str, username: str, password: str, is_superuser: bool = False) -> "User":
        from app.core.jwt import get_password_hash
        
        user_model = UserModel(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=is_superuser,
        )
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        return self._to_domain(user_model)

    async def update(self, user: "User") -> "User":
        from app.core.jwt import get_password_hash

        result = await self.session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User with id {user.id} not found")

        # Обновляем поля
        if hasattr(user, 'email') and user.email:
            model.email = user.email
        if hasattr(user, 'username') and user.username:
            model.username = user.username
        if hasattr(user, 'is_active'):
            model.is_active = user.is_active
        if hasattr(user, 'is_superuser'):
            model.is_superuser = user.is_superuser

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update_with_password(self, user: "User", password: str) -> "User":
        """Обновление пользователя с паролем (с инвалидацией токенов)."""
        from app.core.jwt import get_password_hash

        result = await self.session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User with id {user.id} not found")

        # Обновляем поля
        if hasattr(user, 'email') and user.email:
            model.email = user.email
        if hasattr(user, 'username') and user.username:
            model.username = user.username
        if hasattr(user, 'is_active'):
            model.is_active = user.is_active
        if hasattr(user, 'is_superuser'):
            model.is_superuser = user.is_superuser

        # Обновляем пароль и инвалидируем все токены
        if password:
            model.hashed_password = get_password_hash(password)
            # Инвалидируем все refresh токены пользователя
            await self.delete_all_refresh_tokens(user.id)

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete_all_refresh_tokens(self, user_id: int) -> bool:
        """Удаление всех refresh токенов пользователя."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        )
        tokens = result.scalars().all()
        if not tokens:
            return False

        for token in tokens:
            await self.session.delete(token)
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def get_all(self, page: int = 1, limit: int = 10) -> tuple[list["User"], int]:
        offset = (page - 1) * limit
        
        # Общее количество
        count_result = await self.session.execute(select(func.count()).select_from(UserModel))
        total = count_result.scalar()
        
        # Пользователи
        result = await self.session.execute(
            select(UserModel).order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
        )
        models = result.scalars().all()
        users = [self._to_domain(m) for m in models]
        return users, total

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshTokenModel:
        """Сохранение refresh токена."""
        refresh_token = RefreshTokenModel(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> Optional[RefreshTokenModel]:
        """Получение refresh токена."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_refresh_token(self, token: str) -> bool:
        """Удаление refresh токена."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        refresh_token = result.scalar_one_or_none()
        if not refresh_token:
            return False
        
        await self.session.delete(refresh_token)
        await self.session.commit()
        return True

    async def delete_expired_refresh_tokens(self, user_id: int) -> None:
        """Удаление истёкших refresh токенов пользователя."""
        from datetime import datetime as dt
        await self.session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.expires_at < dt.now().replace(tzinfo=None)
            )
        )
        await self.session.commit()

    def _to_domain(self, model: UserModel) -> "User":
        from app.domain.models import User
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
