"""Интерфейсы репозиториев."""

from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models import (
    Specialty,
    InterestingFact,
    News,
    FAQ,
    Document,
    GalleryImage,
    DocumentFile,
    TestQuestion,
    AboutInfo,
    AdmissionInfo,
)


class IRepository(ABC):
    """Базовый интерфейс репозитория."""
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[object]:
        """Получить сущность по ID."""
        pass


class ISpecialtyRepository(IRepository, ABC):
    """Интерфейс репозитория специальностей."""

    @abstractmethod
    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        form: Optional[str] = None,
        popular: Optional[bool] = None,
    ) -> tuple[list[Specialty], int]:
        """Получить список специальностей с пагинацией."""
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Specialty]:
        """Получить специальность по коду."""
        pass

    @abstractmethod
    async def get_codes_with_budget_or_paid(self, has_budget: bool = True) -> list[str]:
        """Получить коды специальностей с бюджетными/платными местами."""
        pass

    @abstractmethod
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
        """Создать специальность."""
        pass

    @abstractmethod
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
        """Обновить специальность."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить специальность."""
        pass


class IFactRepository(IRepository, ABC):
    """Интерфейс репозитория интересных фактов."""
    
    @abstractmethod
    async def get_by_specialty_code(self, specialty_code: str) -> list[InterestingFact]:
        """Получить факты по специальности."""
        pass
    
    @abstractmethod
    async def get_titles_by_specialty_code(self, specialty_code: str) -> list[dict]:
        """Получить только заголовки фактов по специальности."""
        pass


class INewsRepository(IRepository, ABC):
    """Интерфейс репозитория новостей."""
    
    @abstractmethod
    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[News], int]:
        """Получить список новостей с пагинацией."""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[News]:
        """Получить новость по slug."""
        pass
    
    @abstractmethod
    async def increment_views(self, slug: str) -> None:
        """Увеличить счётчик просмотров."""
        pass


class IFAQRepository(IRepository, ABC):
    """Интерфейс репозитория FAQ."""

    @abstractmethod
    async def get_all(self, category: Optional[str] = None) -> list[FAQ]:
        """Получить все вопросы с фильтрацией по категории."""
        pass

    @abstractmethod
    async def create(
        self,
        question: str,
        answer: str | list[str],
        category: str,
        show_in_admission: bool,
        images: list[dict],
        documents: list[dict] | None = None,
    ) -> FAQ:
        """Создать вопрос FAQ."""
        pass

    @abstractmethod
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
        """Обновить вопрос FAQ."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить вопрос FAQ."""
        pass


class IDocumentRepository(IRepository, ABC):
    """Интерфейс репозитория документов."""

    @abstractmethod
    async def get_all(self, category: Optional[str] = None) -> list[Document]:
        """Получить все документы с фильтрацией по категории."""
        pass

    @abstractmethod
    async def create(
        self,
        title: str,
        category: str,
        file_url: str,
        file_size: Optional[int],
        images: list[dict],
    ) -> Document:
        """Создать документ."""
        pass

    @abstractmethod
    async def update(
        self,
        id: int,
        title: Optional[str] = None,
        category: Optional[str] = None,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        images: Optional[list[dict]] = None,
    ) -> Document:
        """Обновить документ."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить документ."""
        pass


class IGalleryRepository(IRepository, ABC):
    """Интерфейс репозитория галереи."""

    @abstractmethod
    async def get_all(self, category: Optional[str] = None) -> list[GalleryImage]:
        """Получить все изображения с фильтрацией по категории."""
        pass


class IDocumentFileRepository(IRepository, ABC):
    """Интерфейс репозитория файлов документов."""

    @abstractmethod
    async def get_all(self, category: Optional[str] = None) -> list[DocumentFile]:
        """Получить все файлы с фильтрацией по категории."""
        pass


class ITestQuestionRepository(IRepository, ABC):
    """Интерфейс репозитория вопросов теста."""

    @abstractmethod
    async def get_all(self) -> list[TestQuestion]:
        """Получить все вопросы теста."""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[TestQuestion]:
        """Получить вопрос по ID."""
        pass

    @abstractmethod
    async def create(
        self,
        text: str,
        options: list[str],
        image_url: Optional[str] = None,
        documents: list[dict] | None = None,
    ) -> TestQuestion:
        """Создать вопрос теста."""
        pass

    @abstractmethod
    async def update(
        self,
        id: int,
        text: Optional[str] = None,
        options: Optional[list[str]] = None,
        image_url: Optional[str] = None,
        documents: Optional[list[dict]] = None,
    ) -> TestQuestion:
        """Обновить вопрос теста."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить вопрос теста."""
        pass

    @abstractmethod
    async def validate_answer(self, question_id: int, selected: str) -> bool:
        """Проверить валидность ответа."""
        pass

    @abstractmethod
    async def calculate_recommendation(self, answers: list[dict]) -> dict:
        """Рассчитать рекомендацию по ответам."""
        pass


class IAboutRepository(ABC):
    """Интерфейс репозитория информации о колледже."""

    @abstractmethod
    async def get_info(self) -> AboutInfo:
        """Получить информацию о колледже."""
        pass

    @abstractmethod
    async def update(
        self,
        title: Optional[str] = None,
        description: Optional[list[str]] = None,
        images: Optional[list[dict]] = None,
    ) -> AboutInfo:
        """Обновить информацию о колледже."""
        pass


class IAdmissionRepository(ABC):
    """Интерфейс репозитория приёмной кампании."""

    @abstractmethod
    async def get_admission_info(self, year: int) -> AdmissionInfo:
        """Получить информацию о приёмной кампании."""
        pass


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей."""

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional["User"]:
        """Получить пользователя по ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        """Получить пользователя по email."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional["User"]:
        """Получить пользователя по username."""
        pass

    @abstractmethod
    async def create(self, email: str, username: str, password: str, is_superuser: bool = False) -> "User":
        """Создать нового пользователя."""
        pass

    @abstractmethod
    async def update(self, user: "User") -> "User":
        """Обновить пользователя."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить пользователя."""
        pass

    @abstractmethod
    async def get_all(self, page: int = 1, limit: int = 10) -> tuple[list["User"], int]:
        """Получить всех пользователей с пагинацией."""
        pass
