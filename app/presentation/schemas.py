"""Pydantic схемы для API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# === Общие схемы ===

class ImageSchema(BaseModel):
    """Схема изображения."""
    url: str
    alt: str
    caption: Optional[str] = None


class ImageWithThumbnailSchema(BaseModel):
    """Схема изображения с превью."""
    url: str
    thumbnail: str
    alt: str
    caption: Optional[str] = None


class PaginationSchema(BaseModel):
    """Схема пагинации."""
    total: int
    page: int
    limit: int


# === About ===

class AboutResponse(BaseModel):
    """Ответ /about."""
    title: str
    description: list[str]
    images: list[ImageSchema]


class AboutUpdateSchema(BaseModel):
    """Обновление информации о колледже."""
    title: Optional[str] = None
    description: Optional[list[str]] = None
    images: Optional[list[ImageSchema]] = None


# === Admission ===

class SpecialtyAdmissionSchema(BaseModel):
    """Схема специальности для приёма."""
    code: str
    name: str
    budget_places: int
    paid_places: int
    exams: list[str]
    duration: str


class SubmissionMethodSchema(BaseModel):
    """Схема способа подачи документов."""
    title: str
    description: str
    link: Optional[str] = None


class ImportantDateSchema(BaseModel):
    """Схема важной даты."""
    title: str
    date: datetime
    description: Optional[str] = None
    
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class FAQHighlightSchema(BaseModel):
    """Схема вопроса FAQ для приёма."""
    question: str
    answer: str | list[str]


class AdmissionResponse(BaseModel):
    """Ответ /admission."""
    year: int
    specialties_admission: list[SpecialtyAdmissionSchema]
    submission_methods: list[SubmissionMethodSchema]
    important_dates: list[ImportantDateSchema]
    faq_highlights: list[FAQHighlightSchema]


# === Specialties ===

class SpecialtyListItemSchema(BaseModel):
    """Элемент списка специальностей."""
    code: str
    name: str
    short_description: str
    images: list[ImageSchema]


class SpecialtiesResponse(BaseModel):
    """Ответ /specialties."""
    total: int
    page: int
    limit: int
    items: list[SpecialtyListItemSchema]


class InterestingFactPreviewSchema(BaseModel):
    """Превью интересного факта."""
    id: int
    title: str


class SpecialtyDetailImageSchema(BaseModel):
    """Схема изображения для детали специальности."""
    url: str
    alt: str
    caption: Optional[str] = None


class SpecialtyDetailResponse(BaseModel):
    """Ответ /specialties/{code}."""
    code: str
    name: str
    description: list[str]
    duration: str
    budget_places: int
    paid_places: int
    qualification: str
    exams: list[str]
    interesting_facts_preview: list[InterestingFactPreviewSchema]
    images: list[SpecialtyDetailImageSchema]


# === Facts ===

class FactTitleSchema(BaseModel):
    """Схема заголовка факта."""
    id: int
    title: str


class FactDetailResponse(BaseModel):
    """Ответ /facts/{id}."""
    id: int
    title: str
    description: list[str]
    images: list[ImageSchema]


# === News ===

class NewsListItemSchema(BaseModel):
    """Элемент списка новостей."""
    id: int
    title: str
    slug: str
    preview_text: str
    preview_image: Optional[str]
    published_at: datetime


class NewsListResponse(BaseModel):
    """Ответ /news."""
    total: int
    page: int
    limit: int
    items: list[NewsListItemSchema]


class GalleryItemSchema(BaseModel):
    """Элемент галереи новости."""
    url: str
    thumbnail: str
    alt: str
    caption: Optional[str] = None


class NewsDetailResponse(BaseModel):
    """Ответ /news/{slug}."""
    id: int
    title: str
    slug: str
    content: list[str]
    gallery: list[GalleryItemSchema]
    published_at: datetime
    views: int


# === FAQ ===

class FAQItemSchema(BaseModel):
    """Элемент FAQ."""
    id: int
    question: str
    answer: str | list[str]
    category: str
    show_in_admission: bool
    images: list[ImageSchema]
    documents: list[ImageSchema]


class FAQItemCreateSchema(BaseModel):
    """Создание элемента FAQ."""
    question: str
    answer: str | list[str]
    category: str = "general"
    show_in_admission: bool = False
    images: list[ImageSchema] = []
    documents: list[ImageSchema] = []


class FAQItemUpdateSchema(BaseModel):
    """Обновление элемента FAQ."""
    question: Optional[str] = None
    answer: Optional[str | list[str]] = None
    category: Optional[str] = None
    show_in_admission: Optional[bool] = None
    images: Optional[list[ImageSchema]] = None
    documents: Optional[list[ImageSchema]] = None


# === Documents ===

class DocumentItemSchema(BaseModel):
    """Элемент документа."""
    id: int
    title: str
    category: str
    file_url: str
    file_size: Optional[int]
    images: list[ImageSchema]


class DocumentItemCreateSchema(BaseModel):
    """Создание документа."""
    title: str
    category: str = "general"
    file_url: str
    file_size: Optional[int] = None
    images: list[ImageSchema] = []


class DocumentItemUpdateSchema(BaseModel):
    """Обновление документа."""
    title: Optional[str] = None
    category: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    images: Optional[list[ImageSchema]] = None


# === Gallery ===

class GalleryItemDetailSchema(BaseModel):
    """Элемент галереи."""
    id: int
    url: str
    thumbnail: str
    alt: str
    category: str
    caption: Optional[str] = None
    date_taken: Optional[datetime]


class GalleryItemCreateSchema(BaseModel):
    """Создание элемента галереи."""
    url: str
    thumbnail: str
    alt: str
    category: str
    caption: Optional[str] = None
    date_taken: Optional[datetime] = None


class GalleryItemUpdateSchema(BaseModel):
    """Обновление элемента галереи."""
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    alt: Optional[str] = None
    category: Optional[str] = None
    caption: Optional[str] = None
    date_taken: Optional[datetime] = None


# === Test ===

class TestQuestionSchema(BaseModel):
    """Вопрос теста."""
    id: int
    text: str
    options: list[str]
    image_url: Optional[str]
    documents: list[ImageSchema]


class TestQuestionCreateSchema(BaseModel):
    """Создание вопроса теста."""
    text: str
    options: list[str]
    image_url: Optional[str] = None
    documents: list[ImageSchema] = []


class TestQuestionUpdateSchema(BaseModel):
    """Обновление вопроса теста."""
    text: Optional[str] = None
    options: Optional[list[str]] = None
    image_url: Optional[str] = None
    documents: Optional[list[ImageSchema]] = None


class TestAnswerSchema(BaseModel):
    """Ответ на вопрос теста."""
    question_id: int
    selected: str


class TestRequest(BaseModel):
    """Запрос на прохождение теста."""
    answers: list[TestAnswerSchema]


class TestResultResponse(BaseModel):
    """Результат теста."""
    recommendation: str
    motivation: str
    recommended_specialties: list[str]


# === Error ===

class ErrorResponse(BaseModel):
    """Схема ошибки."""
    detail: str
    status_code: Optional[int] = None


# === Auth ===

class TokenSchema(BaseModel):
    """Схема токена доступа."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshSchema(BaseModel):
    """Схема для refresh токена."""
    refresh_token: str


class UserCreateSchema(BaseModel):
    """Схема создания пользователя."""
    email: str
    username: str
    password: str


class UserUpdateSchema(BaseModel):
    """Схема обновления пользователя."""
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponseSchema(BaseModel):
    """Схема ответа с пользователем."""
    id: int
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UsersListResponseSchema(BaseModel):
    """Схема списка пользователей."""
    total: int
    page: int
    limit: int
    items: list[UserResponseSchema]


class LoginSchema(BaseModel):
    """Схема входа."""
    username: str
    password: str
