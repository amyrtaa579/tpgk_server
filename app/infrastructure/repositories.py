"""Реализации репозиториев."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Specialty,
    InterestingFact,
    News,
    FAQ,
    Document,
    GalleryImage,
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
    ITestQuestionRepository,
    IAboutRepository,
    IAdmissionRepository,
    IUserRepository,
)
from app.infrastructure.models import (
    SpecialtyModel,
    InterestingFactModel,
    NewsModel,
    FAQModel,
    DocumentModel,
    GalleryImageModel,
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
    
    async def get_by_id(self, id: int) -> Optional[Specialty]:
        result = await self.session.execute(
            select(SpecialtyModel).where(SpecialtyModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)
    
    async def get_by_code(self, code: str) -> Optional[Specialty]:
        result = await self.session.execute(
            select(SpecialtyModel).where(SpecialtyModel.code == code)
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
        form: Optional[str] = None,
        popular: Optional[bool] = None,
    ) -> tuple[list[Specialty], int]:
        offset = (page - 1) * limit
        
        # Построение условий фильтрации
        conditions = []
        if search:
            conditions.append(SpecialtyModel.name.ilike(f"%{search}%"))
        if form == "budget":
            conditions.append(SpecialtyModel.budget_places > 0)
        elif form == "paid":
            conditions.append(SpecialtyModel.paid_places > 0)
        if popular is True:
            conditions.append(SpecialtyModel.is_popular == True)
        
        # Получение общего количества
        count_query = select(func.count()).select_from(SpecialtyModel)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        query = select(SpecialtyModel)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        specialties = [self._to_domain(m) for m in models]
        return specialties, total
    
    async def get_codes_with_budget_or_paid(self, has_budget: bool = True) -> list[str]:
        if has_budget:
            result = await self.session.execute(
                select(SpecialtyModel.code).where(SpecialtyModel.budget_places > 0)
            )
        else:
            result = await self.session.execute(
                select(SpecialtyModel.code).where(SpecialtyModel.paid_places > 0)
            )
        return [row[0] for row in result.all()]
    
    def _to_domain(self, model: SpecialtyModel) -> Specialty:
        return Specialty(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            code=model.code,
            name=model.name,
            short_description=model.short_description,
            description=model.description,
            duration=model.duration,
            budget_places=model.budget_places,
            paid_places=model.paid_places,
            qualification=model.qualification,
            exams=model.exams,
            images=[to_image(img) for img in model.images],
            is_popular=model.is_popular,
        )


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
    
    async def increment_views(self, slug: str) -> None:
        from sqlalchemy import update
        
        result = await self.session.execute(
            select(NewsModel.views).where(NewsModel.slug == slug)
        )
        current_views = result.scalar()
        if current_views is not None:
            await self.session.execute(
                update(NewsModel)
                .where(NewsModel.slug == slug)
                .values(views=current_views + 1)
            )
            await self.session.commit()
    
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
    ) -> FAQ:
        model = FAQModel(
            question=question,
            answer=answer,
            category=category,
            show_in_admission=show_in_admission,
            images=images,
            documents=documents or [],
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
            documents=[to_image(doc) for doc in model.documents],
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
        image_url: Optional[str] = None,
        documents: list[dict] | None = None,
    ) -> TestQuestion:
        model = TestQuestionModel(
            text=text,
            options=options,
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
        Каждая специальность получает баллы за соответствующие ответы.
        """
        # Счётчики для различных направлений
        scores = {
            "welder": 0,  # Сварщики
            "builder": 0,  # Сооруженцы
            "cook": 0,  # Повара
            "chemist": 0,  # Химики
            "kip": 0,  # КИП, электрики
            "robot": 0,  # Роботизированные системы
            "operator": 0,  # Операторы химических производств
        }
        
        # Анализ ответов
        for answer in answers:
            selected = answer.get("selected", "").lower()
            question_id = answer.get("question_id", 0)
            
            # Вопрос 1: Любишь ли ты работать физически?
            if question_id == 1:
                if "да" in selected:
                    scores["welder"] += 2
                    scores["builder"] += 2
                    scores["cook"] += 1
                else:
                    scores["chemist"] += 1
                    scores["kip"] += 1
                    scores["robot"] += 1
            
            # Вопрос 2: Какая работа нравится?
            if question_id == 2:
                if "ручн" in selected or "физическ" in selected:
                    scores["welder"] += 2
                    scores["builder"] += 2
                    scores["cook"] += 2
                    scores["kip"] += 1
                elif "автоматизированн" in selected:
                    scores["kip"] += 2
                    scores["robot"] += 3  # Больше баллов для робототехники
                elif "творческ" in selected:
                    scores["cook"] += 2
                elif "интеллектуальн" in selected:
                    scores["chemist"] += 1
                    scores["kip"] += 1
                    scores["robot"] += 1
                    scores["operator"] += 1
                elif "компьютер" in selected:
                    scores["robot"] += 2  # Компьютеры -> робототехника
            
            # Вопрос 3: Работа на открытом воздухе?
            if question_id == 3:
                if "да" in selected:
                    scores["welder"] += 2
                    scores["builder"] += 3
                else:
                    scores["chemist"] += 1
                    scores["cook"] += 1
                    scores["kip"] += 1
            
            # Вопрос 4: Предметы в школе
            if question_id == 4:
                if "биолог" in selected or "хим" in selected:
                    scores["chemist"] += 2
                    scores["cook"] += 1
                    scores["welder"] += 1
                if "математик" in selected or "физик" in selected:
                    scores["kip"] += 2
                    scores["robot"] += 2
                    scores["welder"] += 1
                    scores["builder"] += 1
                if "геометр" in selected:
                    scores["welder"] += 2
                    scores["builder"] += 2
                if "физкультур" in selected:
                    scores["welder"] += 1
                    scores["builder"] += 1
            
            # Вопрос 5: Маска
            if question_id == 5:
                if "сварочн" in selected:
                    scores["welder"] += 3
            
            # Вопрос 6: Прибор (Амперметр)
            if question_id == 6:
                if "амперметр" in selected or "дозиметр" in selected:
                    scores["kip"] += 3
                    scores["robot"] += 2
            
            # Вопрос 7: Спиртовка
            if question_id == 7:
                if "спиртовк" in selected or "горелк" in selected:
                    scores["chemist"] += 3
            
            # Вопрос 8: Инструмент
            if question_id == 8:
                if "сварочн" in selected or "шлифовальн" in selected:
                    scores["welder"] += 3
                elif "колб" in selected or "пробирк" in selected:
                    scores["chemist"] += 3
                elif "вес" in selected or "миксер" in selected:
                    scores["cook"] += 3
                elif "отвертк" in selected or "ключ" in selected:
                    scores["kip"] += 2
                    scores["robot"] += 2
            
            # Вопрос 9: Торт
            if question_id == 9:
                if "наполеон" in selected or "красный бархат" in selected:
                    scores["cook"] += 3
            
            # Вопрос 10: Лампа
            if question_id == 10:
                if "лампа" in selected:
                    scores["kip"] += 3
                    scores["robot"] += 2
                elif "светодиодн" in selected:
                    scores["robot"] += 3  # LED -> робототехника
            
            # Вопрос 11: Прибор учета электроэнергии
            if question_id == 11:
                if "прибор учет" in selected or "электроэнерг" in selected:
                    scores["kip"] += 3
                    scores["robot"] += 2
                elif "газоанализатор" in selected:
                    scores["chemist"] += 2
                    scores["operator"] += 2
            
            # Вопрос 12: Миксер кондитерский
            if question_id == 12:
                if "миксер" in selected:
                    scores["cook"] += 3
            
            # Вопрос 13: Перчатки
            if question_id == 13:
                if "сварщик" in selected:
                    scores["welder"] += 3
            
            # Вопрос 14: Химическое производство
            if question_id == 14:
                if "химическ" in selected:
                    scores["chemist"] += 2
                    scores["operator"] += 3
            
            # Вопрос 15: Трубопровод
            if question_id == 15:
                if "трубопровод" in selected:
                    scores["builder"] += 3
        
        # Определяем топ-3 специальности
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Формируем рекомендации на основе лучших результатов
        top_specialties = []
        recommendation_text = ""
        motivation_text = ""
        
        # Логика рекомендаций
        if sorted_scores[0][0] == "welder" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "15.02.19",
                    "name": "Сварочное производство",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                },
                {
                    "code": "15.01.05",
                    "name": "Сварщик (ручной и частично механизированной сварки)",
                    "duration": "1 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам отлично подойдёт направление «Сварочное производство»!"
            motivation_text = "Вы любите работать руками, интересуетесь техникой и готовы к физической работе. Сварщики — востребованная профессия с высокой зарплатой."
        
        elif sorted_scores[0][0] == "builder" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "21.02.03",
                    "name": "Сооружение и эксплуатация газонефтепроводов и газонефтехранилищ",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам подойдёт направление «Сооружение и эксплуатация газонефтепроводов»!"
            motivation_text = "Вы готовы работать на открытом воздухе и заниматься строительством. Это стабильная профессия в нефтегазовой отрасли."
        
        elif sorted_scores[0][0] == "cook" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "19.02.10",
                    "name": "Технология продукции общественного питания",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам подойдёт направление «Поварское дело»!"
            motivation_text = "У вас есть творческие способности и интерес к приготовлению пищи. Повара — всегда востребованная профессия."
        
        elif sorted_scores[0][0] == "chemist" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "18.02.12",
                    "name": "Технология аналитического контроля химических соединений",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам подойдёт направление «Химическая технология»!"
            motivation_text = "У вас есть интерес к химии и точным наукам. Химики-аналитики работают в лабораториях и на производствах."
        
        elif sorted_scores[0][0] == "kip" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "15.01.37",
                    "name": "Слесарь-наладчик КИПиА",
                    "duration": "1 г. 10 мес.",
                    "budget_places": 25
                },
                {
                    "code": "13.01.10",
                    "name": "Электромонтер по ремонту и обслуживанию электрооборудования",
                    "duration": "1 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам подойдёт направление «Контрольно-измерительные приборы и автоматика»!"
            motivation_text = "У вас технический склад ума и интерес к электронике. Специалисты КИПиА и электрики — востребованы на любом производстве."
        
        elif sorted_scores[0][0] == "robot" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "15.02.18",
                    "name": "Техническая эксплуатация роботизированного производства",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 50
                }
            ]
            recommendation_text = "Вам подойдёт направление «Роботизированное производство»!"
            motivation_text = "Вас интересуют автоматизация и роботы. Это современная и перспективная область промышленности."
        
        elif sorted_scores[0][0] == "operator" and sorted_scores[0][1] > 0:
            top_specialties = [
                {
                    "code": "18.01.35",
                    "name": "Аппаратчик-оператор производства химических соединений",
                    "duration": "1 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам подойдёт направление «Оператор химического производства»!"
            motivation_text = "Вы готовы работать на химическом производстве. Это стабильная работа с хорошими перспективами."
        
        else:
            # Если ни одна специальность не набрала баллов
            top_specialties = [
                {
                    "code": "15.02.19",
                    "name": "Сварочное производство",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                },
                {
                    "code": "21.02.03",
                    "name": "Сооружение и эксплуатация газонефтепроводов",
                    "duration": "3 г. 10 мес.",
                    "budget_places": 25
                }
            ]
            recommendation_text = "Вам могут подойти технические специальности нашего колледжа!"
            motivation_text = "Рекомендуем пройти тест ещё раз или обратиться к приёмной комиссии для индивидуальной консультации."
        
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
            # Получаем специальности с местами
            codes = await self.specialty_repository.get_codes_with_budget_or_paid(has_budget=True)
            specialties_data = []
            
            for code in codes[:5]:  # Берём первые 5 для примера
                specialty = await self.specialty_repository.get_by_code(code)
                if specialty:
                    specialties_data.append({
                        "code": specialty.code,
                        "name": specialty.name,
                        "budget_places": specialty.budget_places,
                        "paid_places": specialty.paid_places,
                        "exams": specialty.exams,
                        "duration": specialty.duration,
                    })
            
            # Данные по умолчанию
            return AdmissionInfo(
                year=year,
                specialties_admission=specialties_data if specialties_data else [
                    {
                        "code": "15.02.19",
                        "name": "Сварочное производство",
                        "budget_places": 25,
                        "paid_places": 15,
                        "exams": ["Математика", "Русский язык", "Физика"],
                        "duration": "3 г. 10 мес.",
                    },
                    {
                        "code": "22.02.06",
                        "name": "Сварочное производство (по отраслям)",
                        "budget_places": 25,
                        "paid_places": 15,
                        "exams": ["Математика", "Русский язык", "Физика"],
                        "duration": "3 г. 10 мес.",
                    },
                ],
                submission_methods=[
                    SubmissionMethod(
                        title="Лично в приёмную комиссию",
                        description="г. Стрежевой, ул. Промышленная, д. 15, каб. 101",
                        link=None,
                    ),
                    SubmissionMethod(
                        title="Через портал Госуслуги",
                        description="Подайте заявление онлайн, не выходя из дома",
                        link="https://www.gosuslugi.ru",
                    ),
                    SubmissionMethod(
                        title="Почтой России",
                        description="Отправьте документы заказным письмом с уведомлением",
                        link=None,
                    ),
                ],
                important_dates=[
                    ImportantDate(
                        title="Начало приёма документов",
                        date=datetime(year, 6, 20),
                        description=None,
                    ),
                    ImportantDate(
                        title="Завершение приёма документов (бюджет)",
                        date=datetime(year, 8, 15),
                        description="Для поступающих по результатам ЕГЭ",
                    ),
                ],
                faq_highlights=[
                    {
                        "question": "Можно ли подать документы без ЕГЭ?",
                        "answer": "Да, для выпускников колледжей и техникумов предусмотрены вступительные испытания на базе колледжа.",
                    },
                    {
                        "question": "Есть ли общежитие?",
                        "answer": "Да, иногородним студентам предоставляется общежитие. Количество мест ограничено.",
                    },
                ],
            )
        
        # Конвертация данных из модели
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
            faq_highlights=model.faq_highlights,
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
