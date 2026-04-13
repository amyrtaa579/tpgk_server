# Модели данных и Pydantic схемы

Описание всех бизнес-моделей (Domain layer) и Pydantic схем (Presentation layer).

## Бизнес-модели (Domain Layer)

Бизнес-модели определены как Python dataclass в `app/domain/models.py`. Они не зависят от фреймворков.

### BaseEntity

Базовый класс для всех сущностей:

```python
@dataclass
class BaseEntity:
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Image

```python
@dataclass
class Image:
    url: str = ""
    alt: str = ""
    caption: str = ""
    thumbnail: Optional[str] = None
```

### Specialty

```python
@dataclass
class Specialty:
    code: str = ""                              # Уникальный код (09.02.07)
    name: str = ""                              # Название
    short_description: str = ""                 # Краткое описание
    description: list[str] = None              # Полное описание (массив абзацев)
    exams: list[str] = None                    # Вступительные экзамены
    images: list[Image] = None                 # Изображения
    documents: list[Image] = None              # Документы
    education_options: list[SpecialtyEducationOption] = None  # Уровни образования
```

### SpecialtyEducationOption

```python
@dataclass
class SpecialtyEducationOption:
    specialty_id: Optional[int] = None
    education_level: str = ""          # "На базе 9 классов"
    duration: str = ""                 # "3 года 10 месяцев"
    budget_places: int = 0            # Количество бюджетных мест
    paid_places: int = 0              # Количество платных мест
```

### InterestingFact

```python
@dataclass
class InterestingFact:
    specialty_code: str = ""           # FK → Specialty.code
    title: str = ""                    # Заголовок факта
    description: list[str] = None     # Описание (массив абзацев)
    images: list[Image] = None        # Изображения
```

### News

```python
@dataclass
class News:
    title: str = ""
    slug: str = ""                     # URL-friendly идентификатор
    preview_text: str = ""             # Текст превью
    content: list[str] = None         # Содержание (массив абзацев)
    preview_image: Optional[Image] = None
    gallery: list[Image] = None       # Галерея
    published_at: Optional[datetime] = None
    views: int = 0                     # Счётчик просмотров
```

### FAQ

```python
@dataclass
class FAQ:
    question: str = ""
    answer: Union[str, list[str]] = ""  # Строка или массив абзацев
    category: str = ""                  # Категория
    show_in_admission: bool = False     # Показывать в приёмной кампании
    images: list[Image] = None
    documents: list[FAQDocument] = None
    document_file_ids: list[int] = None  # Ссылки на DocumentFile
```

### FAQDocument

```python
@dataclass
class FAQDocument:
    title: str = ""
    file_url: str = ""
    file_size: int = 0
```

### Document

```python
@dataclass
class Document:
    title: str = ""
    category: str = ""               # licenses, accreditations, other
    file_url: str = ""
    file_size: int = 0
    images: list[Image] = None
```

### GalleryImage

```python
@dataclass
class GalleryImage:
    url: str = ""
    thumbnail: Optional[str] = None
    alt: str = ""
    category: str = ""               # college, events, etc.
    caption: str = ""
    date_taken: Optional[str] = None  # ISO date string
```

### TestQuestion

```python
@dataclass
class TestQuestion:
    text: str = ""
    options: list[str] = None           # Варианты ответов
    answer_scores: list[dict] = None    # Баллы: [{код_специальности: балл}]
    image_url: Optional[str] = None
    documents: list[dict] = None
```

### TestAnswer

```python
@dataclass
class TestAnswer:
    question_id: int = 0
    selected: int = 0                   # Индекс выбранного варианта
```

### TestResult

```python
@dataclass
class TestResult:
    recommendation: str = ""
    motivation: str = ""
    recommended_specialties: list[dict] = None  # [{code, name, score}]
```

### AboutInfo

```python
@dataclass
class AboutInfo:
    title: str = ""
    description: list[str] = None
    images: list[Image] = None
```

### AdmissionInfo

```python
@dataclass
class AdmissionInfo:
    year: int = 0
    specialties_admission: list[dict] = None
    submission_methods: list[dict] = None
    important_dates: list[dict] = None
```

### SubmissionMethod

```python
@dataclass
class SubmissionMethod:
    title: str = ""
    description: str = ""
    link: str = ""
```

### ImportantDate

```python
@dataclass
class ImportantDate:
    title: str = ""
    date: str = ""                      # ISO date string
    description: str = ""
```

### DocumentFile

```python
@dataclass
class DocumentFile:
    title: str = ""
    file_url: str = ""
    file_size: int = 0
    category: str = ""
```

### User

```python
@dataclass
class User:
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_superuser: bool = False
```

---

## Pydantic схемы (Presentation Layer)

Схемы определены в `app/presentation/schemas.py` и используются для валидации HTTP-запросов/ответов.

### Общие схемы

#### ImageSchema

```python
class ImageSchema(BaseModel):
    url: str
    alt: str = ""
    caption: str = ""
    
    model_config = ConfigDict(from_attributes=True)
```

#### ImageWithThumbnailSchema

```python
class ImageWithThumbnailSchema(ImageSchema):
    thumbnail: Optional[str] = None
```

#### PaginationSchema

```python
class PaginationSchema(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
```

---

### About

#### AboutResponse

```python
class AboutResponse(BaseModel):
    title: str
    description: list[str]
    images: list[ImageSchema]
```

#### AboutUpdateSchema

```python
class AboutUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[list[str]] = None
    images: Optional[list[ImageSchema]] = None
```

---

### Admission

#### AdmissionResponse

```python
class AdmissionResponse(BaseModel):
    year: int
    specialties_admission: list[dict]
    submission_methods: list[dict]
    important_dates: list[dict]
```

#### AdmissionCreateSchema

```python
class AdmissionCreateSchema(BaseModel):
    year: int
    specialties_admission: list[dict]
    submission_methods: list[dict]
    important_dates: list[dict]
```

#### AdmissionListResponseSchema

```python
class AdmissionListResponseSchema(BaseModel):
    items: list[AdmissionResponse]
    total: int
```

---

### Specialty

#### SpecialtyListItemSchema

```python
class SpecialtyListItemSchema(BaseModel):
    id: int
    code: str
    name: str
    short_description: str
    
    model_config = ConfigDict(from_attributes=True)
```

#### SpecialtyEducationOptionSchema

```python
class SpecialtyEducationOptionSchema(BaseModel):
    id: Optional[int] = None
    education_level: str
    duration: str
    budget_places: int
    paid_places: int
```

#### SpecialtyDetailResponse

```python
class SpecialtyDetailResponse(BaseModel):
    id: int
    code: str
    name: str
    short_description: str
    description: list[str]
    exams: list[str]
    images: list[ImageSchema]
    documents: list[ImageSchema]
    education_options: list[SpecialtyEducationOptionSchema]
    facts_preview: list[FactTitleSchema]
```

#### SpecialtiesResponse

```python
class SpecialtiesResponse(BaseModel):
    items: list[SpecialtyListItemSchema]
    total: int
    page: int
    limit: int
    pages: int
```

---

### Fact

#### FactTitleSchema

```python
class FactTitleSchema(BaseModel):
    id: int
    title: str
    
    model_config = ConfigDict(from_attributes=True)
```

#### FactDetailResponse

```python
class FactDetailResponse(BaseModel):
    id: int
    specialty_code: str
    title: str
    description: list[str]
    images: list[ImageSchema]
```

---

### News

#### NewsListItemSchema

```python
class NewsListItemSchema(BaseModel):
    id: int
    title: str
    slug: str
    preview_text: str
    preview_image: Optional[ImageSchema] = None
    published_at: datetime
    views: int
    
    model_config = ConfigDict(from_attributes=True)
```

#### NewsListResponse

```python
class NewsListResponse(BaseModel):
    items: list[NewsListItemSchema]
    total: int
    page: int
    limit: int
    pages: int
```

#### NewsDetailResponse

```python
class NewsDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    preview_text: str
    content: list[str]
    preview_image: Optional[ImageSchema] = None
    gallery: list[ImageSchema]
    published_at: datetime
    views: int
```

---

### FAQ

#### FAQDocumentSchema

```python
class FAQDocumentSchema(BaseModel):
    title: str
    file_url: str
    file_size: int
```

#### FAQItemSchema

```python
class FAQItemSchema(BaseModel):
    id: int
    question: str
    answer: Union[str, list[str]]
    category: Optional[str] = None
    show_in_admission: bool
    images: list[ImageSchema]
    documents: list[FAQDocumentSchema]
```

#### FAQItemCreateSchema

```python
class FAQItemCreateSchema(BaseModel):
    question: str
    answer: Union[str, list[str]]
    category: Optional[str] = None
    show_in_admission: bool = False
    images: list[ImageSchema] = []
    documents: list[FAQDocumentSchema] = []
    document_file_ids: list[int] = []
```

#### FAQItemUpdateSchema

```python
class FAQItemUpdateSchema(BaseModel):
    question: Optional[str] = None
    answer: Optional[Union[str, list[str]]] = None
    category: Optional[str] = None
    show_in_admission: Optional[bool] = None
    images: Optional[list[ImageSchema]] = None
    documents: Optional[list[FAQDocumentSchema]] = None
    document_file_ids: Optional[list[int]] = None
```

---

### Document

#### DocumentItemSchema

```python
class DocumentItemSchema(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    file_url: str
    file_size: int
    images: list[ImageSchema]
```

#### DocumentItemCreateSchema

```python
class DocumentItemCreateSchema(BaseModel):
    title: str
    category: Optional[str] = None
    file_url: str
    file_size: int
    images: list[ImageSchema] = []
```

---

### Gallery

#### GalleryItemDetailSchema

```python
class GalleryItemDetailSchema(BaseModel):
    id: int
    url: str
    thumbnail: Optional[str] = None
    alt: str
    category: Optional[str] = None
    caption: str
    date_taken: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
```

#### GalleryItemCreateSchema

```python
class GalleryItemCreateSchema(BaseModel):
    url: str
    thumbnail: Optional[str] = None
    alt: str = ""
    category: str = ""
    caption: str = ""
    date_taken: Optional[str] = None
```

---

### DocumentFile

#### DocumentFileSchema

```python
class DocumentFileSchema(BaseModel):
    id: int
    title: str
    file_url: str
    file_size: int
    category: Optional[str] = None
```

#### DocumentFileCreateSchema

```python
class DocumentFileCreateSchema(BaseModel):
    title: str
    file_url: str
    file_size: int
    category: Optional[str] = None
```

---

### Test

#### TestQuestionSchema

```python
class TestQuestionSchema(BaseModel):
    id: int
    text: str
    options: list[str]
    answer_scores: list[dict]
    image_url: Optional[str] = None
    documents: list[dict] = []
```

#### TestAnswerSchema

```python
class TestAnswerSchema(BaseModel):
    question_id: int
    selected: int
```

#### TestRequest

```python
class TestRequest(BaseModel):
    answers: list[TestAnswerSchema]
    
    @model_validator(mode='after')
    def validate_answer_count(self) -> 'TestRequest':
        if len(self.answers) != 10:
            raise ValueError(f'Необходимо ровно 10 ответов, получено: {len(self.answers)}')
        return self
```

#### TestResultResponse

```python
class TestResultResponse(BaseModel):
    recommendation: str
    motivation: str
    recommended_specialties: list[dict]
```

---

### Auth

#### TokenSchema

```python
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

#### TokenRefreshSchema

```python
class TokenRefreshSchema(BaseModel):
    refresh_token: str
```

#### UserCreateSchema

```python
class UserCreateSchema(BaseModel):
    email: str
    username: str = Field(..., min_length=3, max_length=50)
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Неверный формат email')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        valid, errors = validate_password(v)
        if not valid:
            raise ValueError(f'Пароль не соответствует требованиям: {", ".join(errors)}')
        return v
```

#### UserUpdateSchema

```python
class UserUpdateSchema(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None
```

#### UserResponseSchema

```python
class UserResponseSchema(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    
    model_config = ConfigDict(from_attributes=True)
```

#### UsersListResponseSchema

```python
class UsersListResponseSchema(BaseModel):
    items: list[UserResponseSchema]
    total: int
    page: int
    limit: int
    pages: int
```

#### LoginSchema

```python
class LoginSchema(BaseModel):
    username: str
    password: str
```

---

### Errors

#### ErrorResponse

```python
class ErrorResponse(BaseModel):
    detail: str
    status_code: Optional[int] = None
```

---

## Диаграмма связей моделей

```
┌──────────────┐       ┌──────────────────────────┐
│  Specialty   │ 1───►N│ SpecialtyEducationOption │
└──────┬───────┘       └──────────────────────────┘
       │
       │ code (FK)
       │
  ┌────┴────┐
  │         │
  ▼         ▼
┌─────┐  ┌─────────────────┐
│Fact │  │InterestingFact  │
└─────┘  └─────────────────┘

┌──────────┐     ┌─────────────────┐
│   News   │     │GalleryImage     │
│          │     └─────────────────┘
└──────────┘

┌──────────┐     ┌─────────────────┐
│   FAQ    │────►│ FAQDocument     │
│          │     │DocumentFile (FK)│
└──────────┘     └─────────────────┘

┌──────────┐
│ Document │
└──────────┘

┌──────────────┐     ┌─────────────────┐
│TestQuestion  │     │  TestAnswer     │
│(answer_scores│◄────│(question_id,    │
│ с кодами     │     │ selected)       │
│ специальн.)  │     └─────────────────┘
└──────────────┘

┌──────────┐     ┌─────────────────┐
│   User   │ 1──►N│RefreshToken     │
└──────────┘     └─────────────────┘

┌──────────┐
│ AboutInfo│
└──────────┘

┌──────────────┐
│AdmissionInfo │
└──────────────┘
```

---

## Конвертация ORM → Domain → Schema

Поток данных при запросе:

```
ORM Model (SQLAlchemy)
      │
      │ Repository._to_domain()
      ▼
Domain Model (dataclass)
      │
      │ Pydantic model_validate() / from_attributes
      ▼
Pydantic Schema (response)
      │
      │ JSON serialization
      ▼
HTTP Response (JSON)
```

Пример:

```python
# ORM → Domain
def _to_domain(self, model: SpecialtyModel) -> Specialty:
    return Specialty(
        id=model.id,
        code=model.code,
        name=model.name,
        short_description=model.short_description,
        description=model.description or [],
        exams=model.exams or [],
        images=[Image(**img) for img in (model.images or [])],
        education_options=[
            SpecialtyEducationOption(**eo.__dict__) 
            for eo in model.education_options
        ]
    )

# Domain → Schema → JSON
@router.get("/specialties/{code}")
async def get_specialty(code: str) -> SpecialtyDetailResponse:
    specialty = await use_case.execute(code)  # Domain model
    return SpecialtyDetailResponse.model_validate(specialty)  # Schema
```
