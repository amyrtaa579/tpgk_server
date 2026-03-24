"""ORM модели базы данных."""

from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    ARRAY,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base


class SpecialtyModel(Base):
    """ORM модель специальности."""
    
    __tablename__ = "specialties"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    duration: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    budget_places: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    paid_places: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qualification: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    exams: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    is_popular: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    facts: Mapped[list["InterestingFactModel"]] = relationship(
        "InterestingFactModel",
        back_populates="specialty",
        cascade="all, delete-orphan",
    )


class InterestingFactModel(Base):
    """ORM модель интересного факта."""
    
    __tablename__ = "interesting_facts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specialty_code: Mapped[str] = mapped_column(String(20), ForeignKey("specialties.code", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    specialty: Mapped["SpecialtyModel"] = relationship("SpecialtyModel", back_populates="facts")


class NewsModel(Base):
    """ORM модель новости."""
    
    __tablename__ = "news"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    preview_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preview_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gallery: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FAQModel(Base):
    """ORM модель часто задаваемого вопроса."""

    __tablename__ = "faq"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | list[str]] = mapped_column(JSON, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    show_in_admission: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    documents: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentModel(Base):
    """ORM модель документа."""
    
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalleryImageModel(Base):
    """ORM модель изображения галереи."""
    
    __tablename__ = "gallery_images"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail: Mapped[str] = mapped_column(String(500), nullable=False)
    alt: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_taken: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestQuestionModel(Base):
    """ORM модель вопроса теста."""

    __tablename__ = "test_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    documents: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AboutInfoModel(Base):
    """ORM модель информации о колледже."""
    
    __tablename__ = "about_info"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    images: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdmissionInfoModel(Base):
    """ORM модель информации о приёмной кампании."""

    __tablename__ = "admission_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    specialties_admission: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    submission_methods: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    important_dates: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    faq_highlights: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserModel(Base):
    """ORM модель пользователя (администратора)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Refresh токены
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class RefreshTokenModel(Base):
    """ORM модель refresh токена."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="refresh_tokens")
