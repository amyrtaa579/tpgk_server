"""API роутеры для админ-панели."""

from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, Body, Query, Security
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes

from app.infrastructure.database import get_db_session
from app.infrastructure.repositories import (
    UserRepository,
    SpecialtyRepository,
    NewsRepository,
    FactRepository,
    FAQRepository,
    DocumentRepository,
    GalleryRepository,
    AboutRepository,
    TestQuestionRepository,
)
from app.application.auth_use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
    LogoutUserUseCase,
    GetCurrentUserUseCase,
    GetAllUsersUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
)
from app.application.dependencies import get_current_user, get_current_superuser, get_current_user_id
from app.presentation.schemas import (
    TokenSchema,
    TokenRefreshSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    UsersListResponseSchema,
    LoginSchema,
    GalleryItemCreateSchema,
    GalleryItemUpdateSchema,
    FAQItemSchema,
    FAQItemCreateSchema,
    FAQItemUpdateSchema,
    DocumentItemSchema,
    DocumentItemCreateSchema,
    DocumentItemUpdateSchema,
    AboutResponse,
    AboutUpdateSchema,
    TestQuestionSchema,
    TestQuestionCreateSchema,
    TestQuestionUpdateSchema,
)
from app.infrastructure.minio_service import (
    upload_file_from_bytes,
    delete_file,
    generate_unique_filename,
    get_file_extension,
    get_minio_client,
)
from app.core.config import get_settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.infrastructure.models import SpecialtyModel, NewsModel, InterestingFactModel
from sqlalchemy import select, delete

settings = get_settings()


def create_auth_router() -> APIRouter:
    """Создать роутер для аутентификации."""
    router = APIRouter(prefix="/auth", tags=["Auth"])

    @router.post("/register", response_model=UserResponseSchema, summary="Регистрация")
    async def register(
        user_data: UserCreateSchema,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Регистрация нового пользователя."""
        repository = UserRepository(session)
        use_case = RegisterUserUseCase(repository)
        user = await use_case.execute(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
        )
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
        }

    @router.post("/login", response_model=TokenSchema, summary="Вход")
    async def login(
        credentials: LoginSchema,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Вход в систему."""
        repository = UserRepository(session)
        use_case = LoginUserUseCase(repository)
        user, access_token, refresh_token = await use_case.execute(
            username=credentials.username,
            password=credentials.password,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @router.post("/login/oauth", include_in_schema=False)
    async def login_oauth(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Вход для OAuth2 (Swagger UI)."""
        repository = UserRepository(session)
        use_case = LoginUserUseCase(repository)
        user, access_token, refresh_token = await use_case.execute(
            username=form_data.username,
            password=form_data.password,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    @router.post("/refresh", response_model=TokenSchema, summary="Обновление токена")
    async def refresh_token(
        token_data: TokenRefreshSchema,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Обновление access токена."""
        repository = UserRepository(session)
        use_case = RefreshTokenUseCase(repository)
        new_access, new_refresh = await use_case.execute(token_data.refresh_token)
        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    @router.post("/logout", summary="Выход")
    async def logout(
        token_data: TokenRefreshSchema,
        session: AsyncSession = Depends(get_db_session),
    ):
        """Выход из системы."""
        repository = UserRepository(session)
        use_case = LogoutUserUseCase(repository)
        await use_case.execute(token_data.refresh_token)
        return {"message": "Выход выполнен успешно"}

    @router.get("/me", response_model=UserResponseSchema, summary="Текущий пользователь")
    async def get_me(current_user: dict = Depends(get_current_user)):
        """Получение информации о текущем пользователе."""
        return current_user

    return router


def create_admin_users_router() -> APIRouter:
    """Создать роутер для управления пользователями (только для суперпользователей)."""
    router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

    @router.get("", response_model=UsersListResponseSchema, summary="Список пользователей")
    async def get_all_users(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["users:read"]),
    ):
        """Получение всех пользователей (только для суперпользователей)."""
        repository = UserRepository(session)
        use_case = GetAllUsersUseCase(repository)
        result = await use_case.execute(page=page, limit=limit)
        return result

    @router.get("/{user_id}", response_model=UserResponseSchema, summary="Пользователь по ID")
    async def get_user(
        user_id: int,
        current_user: dict = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["users:read"]),
    ):
        """Получение пользователя по ID."""
        repository = UserRepository(session)
        use_case = GetCurrentUserUseCase(repository)
        user = await use_case.execute(user_id)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
        }

    @router.patch("/{user_id}", response_model=UserResponseSchema, summary="Обновление пользователя")
    async def update_user(
        user_id: int,
        updates: UserUpdateSchema,
        current_user: dict = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["users:write"]),
    ):
        """Обновление пользователя."""
        repository = UserRepository(session)
        use_case = UpdateUserUseCase(repository)
        
        update_data = updates.model_dump(exclude_unset=True)
        user = await use_case.execute(user_id, update_data)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
        }

    @router.delete("/{user_id}", summary="Удаление пользователя")
    async def delete_user(
        user_id: int,
        current_user: dict = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Удаление пользователя."""
        repository = UserRepository(session)
        use_case = DeleteUserUseCase(repository)
        await use_case.execute(user_id)
        return {"message": "Пользователь удалён"}

    return router


def create_admin_specialties_router() -> APIRouter:
    """Создать роутер для управления специальностями."""
    router = APIRouter(prefix="/admin/specialties", tags=["Admin - Specialties"])

    @router.get("", summary="Список специальностей")
    async def get_specialties(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["specialties:read"]),
    ):
        """Получение всех специальностей."""
        repository = SpecialtyRepository(session)
        specialties, total = await repository.get_all(page=page, limit=limit)

        items = [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "is_popular": s.is_popular,
            }
            for s in specialties
        ]

        return {"total": total, "page": page, "limit": limit, "items": items}

    @router.post("", summary="Создание специальности")
    async def create_specialty(
        code: str = Form(...),
        name: str = Form(...),
        short_description: str = Form(""),
        description: str = Form("[]"),  # JSON string
        duration: str = Form(""),
        budget_places: int = Form(0),
        paid_places: int = Form(0),
        qualification: str = Form(""),
        exams: str = Form("[]"),  # JSON string
        images: str = Form("[]"),  # JSON string
        is_popular: bool = Form(False),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["specialties:write"]),
    ):
        """Создание новой специальности."""
        import json
        
        specialty = SpecialtyModel(
            code=code,
            name=name,
            short_description=short_description,
            description=json.loads(description),
            duration=duration,
            budget_places=budget_places,
            paid_places=paid_places,
            qualification=qualification,
            exams=json.loads(exams),
            images=json.loads(images),
            is_popular=is_popular,
        )
        
        session.add(specialty)
        await session.commit()
        await session.refresh(specialty)
        
        return {"id": specialty.id, "code": specialty.code, "name": specialty.name}

    @router.get("/{specialty_id}", summary="Специальность по ID")
    async def get_specialty(
        specialty_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение специальности по ID."""
        result = await session.execute(
            select(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
        )
        specialty = result.scalar_one_or_none()
        
        if not specialty:
            raise NotFoundException("Специальность не найдена")
        
        return specialty

    @router.put("/{specialty_id}", summary="Обновление специальности")
    async def update_specialty(
        specialty_id: int,
        code: str = Form(...),
        name: str = Form(...),
        short_description: str = Form(""),
        description: str = Form("[]"),
        duration: str = Form(""),
        budget_places: int = Form(0),
        paid_places: int = Form(0),
        qualification: str = Form(""),
        exams: str = Form("[]"),
        images: str = Form("[]"),
        is_popular: bool = Form(False),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Обновление специальности."""
        import json
        
        result = await session.execute(
            select(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
        )
        specialty = result.scalar_one_or_none()
        
        if not specialty:
            raise NotFoundException("Специальность не найдена")
        
        specialty.code = code
        specialty.name = name
        specialty.short_description = short_description
        specialty.description = json.loads(description)
        specialty.duration = duration
        specialty.budget_places = budget_places
        specialty.paid_places = paid_places
        specialty.qualification = qualification
        specialty.exams = json.loads(exams)
        specialty.images = json.loads(images)
        specialty.is_popular = is_popular
        
        await session.commit()
        await session.refresh(specialty)
        
        return {"id": specialty.id, "code": specialty.code, "name": specialty.name}

    @router.delete("/{specialty_id}", summary="Удаление специальности")
    async def delete_specialty(
        specialty_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Удаление специальности."""
        await session.execute(
            delete(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
        )
        await session.commit()
        
        return {"message": "Специальность удалена"}

    return router


def create_admin_news_router() -> APIRouter:
    """Создать роутер для управления новостями."""
    router = APIRouter(prefix="/admin/news", tags=["Admin - News"])

    @router.get("", summary="Список новостей")
    async def get_news(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение всех новостей."""
        repository = NewsRepository(session)
        news_list, total = await repository.get_all(page=page, limit=limit)
        
        items = [
            {
                "id": n.id,
                "title": n.title,
                "slug": n.slug,
                "published_at": n.published_at.isoformat(),
            }
            for n in news_list
        ]
        
        return {"total": total, "page": page, "limit": limit, "items": items}

    @router.post("", summary="Создание новости")
    async def create_news(
        title: str = Form(...),
        slug: str = Form(...),
        preview_text: str = Form(""),
        content: str = Form("[]"),  # JSON string
        preview_image: Optional[str] = Form(None),
        gallery: str = Form("[]"),  # JSON string
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Создание новой новости."""
        import json
        from datetime import datetime
        
        news = NewsModel(
            title=title,
            slug=slug,
            preview_text=preview_text,
            content=json.loads(content),
            preview_image=preview_image,
            gallery=json.loads(gallery),
            published_at=datetime.utcnow(),
            views=0,
        )
        
        session.add(news)
        await session.commit()
        await session.refresh(news)
        
        return {"id": news.id, "title": news.title, "slug": news.slug}

    @router.get("/{news_id}", summary="Новость по ID")
    async def get_news_by_id(
        news_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение новости по ID."""
        result = await session.execute(
            select(NewsModel).where(NewsModel.id == news_id)
        )
        news = result.scalar_one_or_none()
        
        if not news:
            raise NotFoundException("Новость не найдена")
        
        return news

    @router.put("/{news_id}", summary="Обновление новости")
    async def update_news(
        news_id: int,
        title: str = Form(...),
        slug: str = Form(...),
        preview_text: str = Form(""),
        content: str = Form("[]"),
        preview_image: Optional[str] = Form(None),
        gallery: str = Form("[]"),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Обновление новости."""
        import json
        
        result = await session.execute(
            select(NewsModel).where(NewsModel.id == news_id)
        )
        news = result.scalar_one_or_none()
        
        if not news:
            raise NotFoundException("Новость не найдена")
        
        news.title = title
        news.slug = slug
        news.preview_text = preview_text
        news.content = json.loads(content)
        news.preview_image = preview_image
        news.gallery = json.loads(gallery)
        
        await session.commit()
        await session.refresh(news)
        
        return {"id": news.id, "title": news.title, "slug": news.slug}

    @router.delete("/{news_id}", summary="Удаление новости")
    async def delete_news(
        news_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Удаление новости."""
        await session.execute(
            delete(NewsModel).where(NewsModel.id == news_id)
        )
        await session.commit()
        
        return {"message": "Новость удалена"}

    return router


def create_admin_facts_router() -> APIRouter:
    """Создать роутер для управления фактами."""
    router = APIRouter(prefix="/admin/facts", tags=["Admin - Facts"])

    @router.get("", summary="Список фактов")
    async def get_facts(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение всех фактов."""
        repository = FactRepository(session)
        # Получаем все факты (простая реализация)
        result = await session.execute(select(InterestingFactModel))
        facts = result.scalars().all()
        
        items = [
            {
                "id": f.id,
                "specialty_code": f.specialty_code,
                "title": f.title,
            }
            for f in facts
        ]
        
        return {"total": len(items), "page": page, "limit": limit, "items": items}

    @router.post("", summary="Создание факта")
    async def create_fact(
        specialty_code: str = Form(...),
        title: str = Form(...),
        description: str = Form("[]"),
        images: str = Form("[]"),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Создание нового факта."""
        import json

        fact = InterestingFactModel(
            specialty_code=specialty_code,
            title=title,
            description=json.loads(description),
            images=json.loads(images),
        )

        session.add(fact)
        await session.commit()
        await session.refresh(fact)

        return {"id": fact.id, "title": fact.title}

    @router.get("/{fact_id}", summary="Факт по ID")
    async def get_fact(
        fact_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Получение факта по ID."""
        result = await session.execute(
            select(InterestingFactModel).where(InterestingFactModel.id == fact_id)
        )
        fact = result.scalar_one_or_none()
        
        if not fact:
            raise NotFoundException("Факт не найден")

        return {
            "id": fact.id,
            "specialty_code": fact.specialty_code,
            "title": fact.title,
            "description": fact.description,
            "images": fact.images,
        }

    @router.put("/{fact_id}", summary="Редактирование факта")
    async def update_fact(
        fact_id: int,
        specialty_code: str = Form(...),
        title: str = Form(...),
        description: str = Form("[]"),
        images: str = Form("[]"),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Редактирование факта."""
        import json

        result = await session.execute(
            select(InterestingFactModel).where(InterestingFactModel.id == fact_id)
        )
        fact = result.scalar_one_or_none()
        
        if not fact:
            raise NotFoundException("Факт не найден")

        fact.specialty_code = specialty_code
        fact.title = title
        fact.description = json.loads(description)
        fact.images = json.loads(images)

        await session.commit()
        await session.refresh(fact)

        return {"id": fact.id, "title": fact.title}

    @router.delete("/{fact_id}", summary="Удаление факта")
    async def delete_fact(
        fact_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        """Удаление факта."""
        await session.execute(
            delete(InterestingFactModel).where(InterestingFactModel.id == fact_id)
        )
        await session.commit()
        
        return {"message": "Факт удалён"}

    return router


def create_admin_upload_router() -> APIRouter:
    """Создать роутер для загрузки файлов."""
    router = APIRouter(prefix="/admin/upload", tags=["Admin - Upload"])

    @router.post("/image", summary="Загрузка изображения")
    async def upload_image(
        file: UploadFile = File(...),
        category: str = Form("common"),
        current_user: dict = Depends(get_current_user),
    ):
        """Загрузка изображения в MinIO."""
        # Проверка типа файла
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise BadRequestException("Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP")
        
        # Чтение файла
        file_data = await file.read()
        
        # Генерация уникального имени
        unique_filename = generate_unique_filename(file.filename)
        object_name = f"images/{category}/{unique_filename}"
        
        # Загрузка
        file_url = upload_file_from_bytes(
            bucket=settings.minio_bucket,
            file_data=file_data,
            object_name=object_name,
            content_type=file.content_type,
        )
        
        return {
            "url": file_url,
            "filename": file.filename,
            "size": len(file_data),
            "content_type": file.content_type,
        }

    @router.post("/document", summary="Загрузка документа")
    async def upload_document(
        file: UploadFile = File(...),
        category: str = Form("common"),
        current_user: dict = Depends(get_current_user),
    ):
        """Загрузка документа в MinIO."""
        # Проверка типа файла
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
        ]
        if file.content_type not in allowed_types:
            raise BadRequestException("Недопустимый тип файла")
        
        # Чтение файла
        file_data = await file.read()
        
        # Генерация уникального имени
        unique_filename = generate_unique_filename(file.filename)
        object_name = f"documents/{category}/{unique_filename}"
        
        # Загрузка
        file_url = upload_file_from_bytes(
            bucket=settings.minio_bucket,
            file_data=file_data,
            object_name=object_name,
            content_type=file.content_type,
        )

        return {
            "url": file_url,
            "filename": file.filename,
            "size": len(file_data),
            "content_type": file.content_type,
        }

    @router.get("/minio/list", summary="Список файлов в MinIO")
    async def list_minio_files(
        prefix: Optional[str] = Query(None, description="Префикс для фильтрации (например, images/)"),
        current_user: dict = Depends(get_current_user),
    ):
        """Получение списка файлов в MinIO."""
        client = get_minio_client()
        
        try:
            # Получаем список объектов
            objects = client.list_objects(
                settings.minio_bucket,
                prefix=prefix or "images/",
                recursive=True
            )
            
            # Фильтруем только изображения
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            files = []
            for obj in objects:
                object_name = obj.object_name
                # Проверяем расширение
                if any(object_name.lower().endswith(ext) for ext in image_extensions):
                    files.append({
                        "key": object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    })
            
            return {"objects": files, "total": len(files)}
        except Exception as e:
            raise BadRequestException(f"Ошибка получения списка файлов: {str(e)}")

    return router


def create_admin_gallery_router() -> APIRouter:
    """Создать роутер для управления галереей."""
    router = APIRouter(prefix="/admin/gallery", tags=["Admin - Gallery"])

    @router.get("", summary="Список изображений галереи")
    async def get_gallery(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение всех изображений галереи."""
        repository = GalleryRepository(session)
        images = await repository.get_all(category=category)
        return {"total": len(images), "items": images}

    @router.post("", summary="Добавление изображения в галерею")
    async def add_gallery_image(
        image_data: GalleryItemCreateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Добавление изображения в галерею."""
        from app.infrastructure.models import GalleryImageModel
        from datetime import datetime, timezone

        # Обрабатываем date_taken: если есть timezone, убираем его для совместимости с БД
        date_taken = None
        if image_data.date_taken:
            if image_data.date_taken.tzinfo is not None:
                date_taken = image_data.date_taken.replace(tzinfo=None)
            else:
                date_taken = image_data.date_taken

        image = GalleryImageModel(
            url=image_data.url,
            thumbnail=image_data.thumbnail,
            alt=image_data.alt,
            category=image_data.category,
            caption=image_data.caption,
            date_taken=date_taken or datetime.now(timezone.utc).replace(tzinfo=None),
        )

        session.add(image)
        await session.commit()
        await session.refresh(image)

        return {
            "id": image.id,
            "url": image.url,
            "thumbnail": image.thumbnail,
            "alt": image.alt,
            "category": image.category,
            "caption": image.caption,
        }

    @router.get("/{image_id}", summary="Изображение по ID")
    async def get_gallery_image(
        image_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение изображения по ID."""
        from sqlalchemy import select
        from app.infrastructure.models import GalleryImageModel

        result = await session.execute(
            select(GalleryImageModel).where(GalleryImageModel.id == image_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise NotFoundException("Изображение не найдено")

        return image

    @router.put("/{image_id}", summary="Обновление изображения")
    async def update_gallery_image(
        image_id: int,
        image_data: GalleryItemUpdateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Обновление изображения в галерее."""
        from sqlalchemy import select
        from app.infrastructure.models import GalleryImageModel

        result = await session.execute(
            select(GalleryImageModel).where(GalleryImageModel.id == image_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise NotFoundException("Изображение не найдено")

        update_data = image_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(image, field, value)

        await session.commit()
        await session.refresh(image)

        return image

    @router.delete("/{image_id}", summary="Удаление изображения")
    async def delete_gallery_image(
        image_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Удаление изображения из галереи."""
        from sqlalchemy import select, delete
        from app.infrastructure.models import GalleryImageModel

        result = await session.execute(
            select(GalleryImageModel).where(GalleryImageModel.id == image_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise NotFoundException("Изображение не найдено")

        await session.execute(
            delete(GalleryImageModel).where(GalleryImageModel.id == image_id)
        )
        await session.commit()

        return {"message": "Изображение удалено"}

    return router


def create_admin_faq_router() -> APIRouter:
    """Создать роутер для управления FAQ."""
    router = APIRouter(prefix="/admin/faq", tags=["Admin - FAQ"])

    @router.get("", response_model=list[FAQItemSchema], summary="Список FAQ")
    async def get_faq_list(
        category: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение списка FAQ."""
        repository = FAQRepository(session)
        faq_items = await repository.get_all(category=category)
        return faq_items

    @router.get("/{faq_id}", response_model=FAQItemSchema, summary="FAQ по ID")
    async def get_faq_item(
        faq_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение FAQ по ID."""
        repository = FAQRepository(session)
        faq_item = await repository.get_by_id(faq_id)
        if not faq_item:
            raise NotFoundException("FAQ не найден")
        return faq_item

    @router.post("", response_model=FAQItemSchema, summary="Создание FAQ")
    async def create_faq_item(
        faq_data: FAQItemCreateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Создание элемента FAQ."""
        repository = FAQRepository(session)
        faq_item = await repository.create(
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
            show_in_admission=faq_data.show_in_admission,
            images=[img.model_dump() for img in faq_data.images],
            documents=[doc.model_dump() for doc in faq_data.documents],
        )
        return faq_item

    @router.put("/{faq_id}", response_model=FAQItemSchema, summary="Обновление FAQ")
    async def update_faq_item(
        faq_id: int,
        faq_data: FAQItemUpdateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Обновление элемента FAQ."""
        repository = FAQRepository(session)
        update_data = faq_data.model_dump(exclude_unset=True)
        faq_item = await repository.update(faq_id, **update_data)
        return faq_item

    @router.delete("/{faq_id}", summary="Удаление FAQ")
    async def delete_faq_item(
        faq_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Удаление элемента FAQ."""
        repository = FAQRepository(session)
        deleted = await repository.delete(faq_id)
        if not deleted:
            raise NotFoundException("FAQ не найден")
        return {"message": "FAQ удалён"}

    return router


def create_admin_documents_router() -> APIRouter:
    """Создать роутер для управления документами."""
    router = APIRouter(prefix="/admin/documents", tags=["Admin - Documents"])

    @router.get("", response_model=list[DocumentItemSchema], summary="Список документов")
    async def get_document_list(
        category: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение списка документов."""
        repository = DocumentRepository(session)
        documents = await repository.get_all(category=category)
        return documents

    @router.get("/{doc_id}", response_model=DocumentItemSchema, summary="Документ по ID")
    async def get_document_item(
        doc_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение документа по ID."""
        repository = DocumentRepository(session)
        document = await repository.get_by_id(doc_id)
        if not document:
            raise NotFoundException("Документ не найден")
        return document

    @router.post("", response_model=DocumentItemSchema, summary="Создание документа")
    async def create_document_item(
        doc_data: DocumentItemCreateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Создание документа."""
        repository = DocumentRepository(session)
        document = await repository.create(
            title=doc_data.title,
            category=doc_data.category,
            file_url=doc_data.file_url,
            file_size=doc_data.file_size,
            images=[img.model_dump() for img in doc_data.images],
        )
        return document

    @router.put("/{doc_id}", response_model=DocumentItemSchema, summary="Обновление документа")
    async def update_document_item(
        doc_id: int,
        doc_data: DocumentItemUpdateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Обновление документа."""
        repository = DocumentRepository(session)
        update_data = doc_data.model_dump(exclude_unset=True)
        document = await repository.update(doc_id, **update_data)
        return document

    @router.delete("/{doc_id}", summary="Удаление документа")
    async def delete_document_item(
        doc_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Удаление документа."""
        repository = DocumentRepository(session)
        deleted = await repository.delete(doc_id)
        if not deleted:
            raise NotFoundException("Документ не найден")
        return {"message": "Документ удалён"}

    return router


def create_admin_about_router() -> APIRouter:
    """Создать роутер для управления информацией о колледже."""
    router = APIRouter(prefix="/admin/about", tags=["Admin - About"])

    @router.get("", response_model=AboutResponse, summary="Информация о колледже")
    async def get_about_info(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение информации о колледже."""
        repository = AboutRepository(session)
        about_info = await repository.get_info()
        return about_info

    @router.put("", response_model=AboutResponse, summary="Обновление информации о колледже")
    async def update_about_info(
        about_data: AboutUpdateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Обновление информации о колледже."""
        repository = AboutRepository(session)
        update_data = about_data.model_dump(exclude_unset=True)
        about_info = await repository.update(**update_data)
        return about_info

    return router


def create_admin_test_router() -> APIRouter:
    """Создать роутер для управления вопросами теста."""
    router = APIRouter(prefix="/admin/test/questions", tags=["Admin - Test Questions"])

    @router.get("", response_model=list[TestQuestionSchema], summary="Список вопросов теста")
    async def get_test_questions(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение списка вопросов теста."""
        repository = TestQuestionRepository(session)
        questions = await repository.get_all()
        return questions

    @router.get("/{question_id}", response_model=TestQuestionSchema, summary="Вопрос теста по ID")
    async def get_test_question(
        question_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:read"]),
    ):
        """Получение вопроса теста по ID."""
        repository = TestQuestionRepository(session)
        question = await repository.get_by_id(question_id)
        if not question:
            raise NotFoundException("Вопрос теста не найден")
        return question

    @router.post("", response_model=TestQuestionSchema, summary="Создание вопроса теста")
    async def create_test_question(
        question_data: TestQuestionCreateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Создание вопроса теста."""
        repository = TestQuestionRepository(session)
        question = await repository.create(
            text=question_data.text,
            options=question_data.options,
            image_url=question_data.image_url,
            documents=[doc.model_dump() for doc in question_data.documents],
        )
        return question

    @router.put("/{question_id}", response_model=TestQuestionSchema, summary="Обновление вопроса теста")
    async def update_test_question(
        question_id: int,
        question_data: TestQuestionUpdateSchema,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Обновление вопроса теста."""
        repository = TestQuestionRepository(session)
        update_data = question_data.model_dump(exclude_unset=True)
        question = await repository.update(question_id, **update_data)
        return question

    @router.delete("/{question_id}", summary="Удаление вопроса теста")
    async def delete_test_question(
        question_id: int,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
        _scopes: None = Security(get_current_user_id, scopes=["news:write"]),
    ):
        """Удаление вопроса теста."""
        repository = TestQuestionRepository(session)
        deleted = await repository.delete(question_id)
        if not deleted:
            raise NotFoundException("Вопрос теста не найден")
        return {"message": "Вопрос теста удалён"}

    return router
