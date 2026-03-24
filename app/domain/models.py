"""Базовые классы доменной модели."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class BaseEntity:
    """Базовый класс для всех сущностей."""
    
    id: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Image:
    """Модель изображения."""
    
    url: str
    alt: str
    caption: Optional[str] = None
    thumbnail: Optional[str] = None


@dataclass
class Specialty(BaseEntity):
    """Специальность колледжа."""
    
    code: str = ""
    name: str = ""
    short_description: str = ""
    description: list[str] = field(default_factory=list)
    duration: str = ""
    budget_places: int = 0
    paid_places: int = 0
    qualification: str = ""
    exams: list[str] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    is_popular: bool = False


@dataclass
class InterestingFact(BaseEntity):
    """Интересный факт о специальности."""
    
    specialty_code: str = ""
    title: str = ""
    description: list[str] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)


@dataclass
class News(BaseEntity):
    """Новость колледжа."""
    
    title: str = ""
    slug: str = ""
    preview_text: str = ""
    content: list[str] = field(default_factory=list)
    preview_image: Optional[str] = None
    gallery: list[Image] = field(default_factory=list)
    published_at: datetime = field(default_factory=datetime.utcnow)
    views: int = 0


@dataclass
class FAQ(BaseEntity):
    """Часто задаваемый вопрос."""
    
    question: str = ""
    answer: str | list[str] = ""
    category: str = ""
    show_in_admission: bool = False
    images: list[Image] = field(default_factory=list)


@dataclass
class Document(BaseEntity):
    """Документ для скачивания."""
    
    title: str = ""
    category: str = ""
    file_url: str = ""
    file_size: Optional[int] = None
    images: list[Image] = field(default_factory=list)


@dataclass
class GalleryImage(BaseEntity):
    """Изображение в галерее."""
    
    url: str = ""
    thumbnail: str = ""
    alt: str = ""
    category: str = ""
    caption: Optional[str] = None
    date_taken: Optional[datetime] = None


@dataclass
class TestQuestion(BaseEntity):
    """Вопрос профориентационного теста."""
    
    text: str = ""
    options: list[str] = field(default_factory=list)
    image_url: Optional[str] = None


@dataclass
class TestAnswer:
    """Ответ пользователя на вопрос теста."""
    
    question_id: int
    selected: str


@dataclass
class TestResult:
    """Результат прохождения теста."""
    
    recommendation: str
    motivation: str
    recommended_specialties: list[str]


@dataclass
class AboutInfo:
    """Информация о колледже."""
    
    title: str
    description: list[str]
    images: list[Image]


@dataclass
class SubmissionMethod:
    """Способ подачи документов."""
    
    title: str
    description: str
    link: Optional[str] = None


@dataclass
class ImportantDate:
    """Важная дата приёмной кампании."""
    
    title: str
    date: datetime
    description: Optional[str] = None


@dataclass
class AdmissionInfo:
    """Информация о приёмной кампании."""

    year: int
    specialties_admission: list[dict]
    submission_methods: list[SubmissionMethod]
    important_dates: list[ImportantDate]
    faq_highlights: list[dict]


@dataclass
class User:
    """Пользователь (администратор)."""

    id: int
    email: str
    username: str
    hashed_password: str = ""
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
