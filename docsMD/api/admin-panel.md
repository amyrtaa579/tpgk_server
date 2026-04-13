# Админ-панель

Админ-панель — это **React-приложение** для управления контентом API через веб-интерфейс. Предоставляет CRUD-операции для всех сущностей: специальности, новости, FAQ, документы, пользователи и т.д.

## Обзор

| Параметр | Значение |
|----------|----------|
| **Фреймворк** | React 18 + TypeScript |
| **UI библиотека** | React Bootstrap 5.3.2 |
| **Роутинг** | React Router 6.20 |
| **HTTP клиент** | Axios 1.6.2 |
| **Сборщик** | Vite 5.0.8 |
| **Загрузка файлов** | react-dropzone 14.2.3 |
| **Директория** | `admin-panel/` |

---

## Архитектура

```
admin-panel/
├── src/
│   ├── components/       # Переиспользуемые компоненты
│   ├── context/          # React Context (auth, etc.)
│   ├── hooks/            # Кастомные хуки
│   ├── pages/            # Страницы (роуты)
│   ├── services/         # API сервисы (Axios)
│   ├── types/            # TypeScript типы
│   ├── App.tsx           # Главный компонент (роутинг)
│   └── main.tsx          # Точка входа
├── dist/                 # Собранный билд (static files)
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### Структура страниц

```
src/pages/
├── Login.tsx             # Страница входа
├── Dashboard.tsx         # Главная панель
├── Specialties/
│   ├── SpecialtiesList.tsx      # Список специальностей
│   ├── SpecialtyCreate.tsx      # Создание специальности
│   └── SpecialtyEdit.tsx        # Редактирование
├── News/
│   ├── NewsList.tsx             # Список новостей
│   ├── NewsCreate.tsx           # Создание новости
│   └── NewsEdit.tsx             # Редактирование
├── Facts/                # Факты о специальностях
├── FAQ/                  # Управление FAQ
├── Documents/            # Документы
├── Gallery/              # Фотогалерея
├── Users/                # Управление пользователями
├── Cache/                # Управление кэшем
└── Settings/             # Настройки
```

---

## Запуск (Development)

### Предварительные требования

- Node.js 18+
- npm 9+

### Установка и запуск

```bash
# Перейти в директорию админ-панели
cd admin-panel

# Установить зависимости
npm install

# Запустить dev-сервер
npm run dev
```

Админ-панель доступна по адресу: `http://localhost:5173`

### Сборка для Production

```bash
# Собрать билд
npm run build

# Предпросмотр билда
npm run preview
```

**Результат:** Директория `dist/` — готовые статические файлы для Nginx.

---

## Интеграция с API

### Базовый URL

По умолчанию админ-панель подключается к API по адресу `http://localhost:8000`.

Для изменения — настройте в `services/api.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});
```

### Аутентификация

**Вход через админ-панель:**

1. Перейти на `/login`
2. Ввести username и password
3. JWT-токен сохраняется в `localStorage`
4. Все последующие запросы включают токен автоматически

**Axios interceptor:**

```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Автоматическое обновление при 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Попытка refresh токена
      // Или редирект на /login
    }
    return Promise.reject(error);
  }
);
```

---

## Основные функции

### 1. Управление специальностями

- **Список** с пагинацией и поиском
- **Создание** новой специальности (form-data с JSON-полями)
- **Редактирование** существующей
- **Удаление** с подтверждением
- **Загрузка изображений** через drag-and-drop

### 2. Управление новостями

- **Редактор контента** с поддержкой абзацев
- **Превью изображения**
- **Галерея** новости
- **Slug** генерируется автоматически из заголовка

### 3. Управление фактами

- **Привязка** к специальности (по коду)
- **Множество изображений**
- **Форматирование** описания (массив абзацев)

### 4. Фотогалерея

- **Drag-and-drop** загрузка
- **Превью** изображений
- **Категории** для фильтрации
- **Метаданные**: caption, date_taken, alt

### 5. Управление пользователями (только суперпользователь)

- **Список** всех пользователей
- **Редактирование**: email, password, is_active, is_superuser
- **Удаление** с подтверждением

### 6. Управление кэшем

- **Статистика** Redis (количество ключей, память)
- **Очистка** всего кэша
- **Очистка** по группам

---

## Компоненты

### Компонент загрузки файлов

```tsx
import { useDropzone } from 'react-dropzone';

interface FileUploaderProps {
  onUpload: (url: string) => void;
  category: string;
  accept?: Record<string, string[]>;
  maxSize?: number;
}

const FileUploader: React.FC<FileUploaderProps> = ({ 
  onUpload, 
  category, 
  accept, 
  maxSize 
}) => {
  const { getRootProps, getInputProps } = useDropzone({
    accept,
    maxSize,
    onDrop: async (acceptedFiles) => {
      // Загрузка файла в MinIO через API
      const formData = new FormData();
      formData.append('file', acceptedFiles[0]);
      
      const response = await api.post(
        `/admin/upload/image?category=${category}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      onUpload(response.data.url);
    }
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      <p>Перетащите файл сюда или нажмите для выбора</p>
    </div>
  );
};
```

### Компонент пагинации

```tsx
interface PaginationProps {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ page, pages, onPageChange }) => {
  return (
    <div className="d-flex justify-content-center">
      <button 
        disabled={page <= 1} 
        onClick={() => onPageChange(page - 1)}
      >
        Назад
      </button>
      <span>Страница {page} из {pages}</span>
      <button 
        disabled={page >= pages} 
        onClick={() => onPageChange(page + 1)}
      >
        Вперёд
      </button>
    </div>
  );
};
```

---

## Развёртывание

### Через Docker Compose (Production)

Админ-панель раздаётся через **Nginx** как статические файлы.

**Конфигурация Nginx:**

```nginx
# Админ-панель
server {
    listen 443 ssl http2;
    server_name admin.anmicius.ru;

    ssl_certificate /etc/letsencrypt/live/admin.anmicius.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.anmicius.ru/privkey.pem;

    root /admin-panel/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # SPA routing
    }

    # API proxy для запросов с того же домена
    location /api/ {
        proxy_pass http://api:8000;
    }

    location /auth/ {
        proxy_pass http://api:8000;
    }

    location /admin/ {
        proxy_pass http://api:8000;
    }
}
```

### Сборка и деплой

```bash
# 1. Собрать админ-панель
cd admin-panel
npm run build

# 2. Файлы будут в dist/
# dist/ уже примонтирован в nginx через docker-compose

# 3. Перезапустить nginx
docker-compose restart nginx
```

**docker-compose.yml:**
```yaml
nginx:
  volumes:
    - ./admin-panel/dist:/admin-panel/dist:ro  # Read-only
```

---

## TypeScript типы

### Основные типы

```typescript
// types/specialty.ts
export interface Specialty {
  id: number;
  code: string;
  name: string;
  short_description: string;
  description: string[];
  exams: string[];
  images: Image[];
  education_options: EducationOption[];
  is_popular: boolean;
}

export interface SpecialtyCreate {
  code: string;
  name: string;
  short_description: string;
  description?: string[];
  exams?: string[];
  images?: Image[];
  education_options?: EducationOption[];
}

// types/user.ts
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

// types/auth.ts
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
```

---

## Сервисы API

### AuthService

```typescript
// services/auth.ts
export const AuthService = {
  async login(username: string, password: string): Promise<AuthTokens> {
    const response = await api.post('/auth/login', { username, password });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    return response.data;
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    await api.post('/auth/logout', { refresh_token: refreshToken });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
```

### SpecialtyService

```typescript
// services/specialty.ts
export const SpecialtyService = {
  async getAll(page = 1, limit = 10): Promise<PaginatedResponse<Specialty>> {
    const response = await api.get(`/admin/specialties?page=${page}&limit=${limit}`);
    return response.data;
  },

  async create(data: SpecialtyCreate): Promise<Specialty> {
    const formData = new FormData();
    formData.append('code', data.code);
    formData.append('name', data.name);
    formData.append('short_description', data.short_description);
    formData.append('description', JSON.stringify(data.description || []));
    // ...
    
    const response = await api.post('/admin/specialties', formData);
    return response.data;
  },

  async update(id: number, data: SpecialtyUpdate): Promise<Specialty> {
    // Аналогично create
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/admin/specialties/${id}`);
  }
};
```

---

## Безопасность

### Защита от XSS

- **React** автоматически экранирует данные
- **dangerouslySetInnerHTML** не используется
- **CSP заголовки** в Nginx

### Защита от CSRF

- **JWT в localStorage** (не в cookies)
- **CORS** настроен на конкретные origins

### Проверка авторизации

```typescript
// ProtectedRoute компонент
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Использование
<Route 
  path="/admin/specialties" 
  element={
    <ProtectedRoute>
      <SpecialtiesList />
    </ProtectedRoute>
  } 
/>
```

---

## Troubleshooting

### Админ-панель не загружается

**Причина:** Билд не собран или Nginx не видит файлы.

**Решение:**
```bash
# Собрать билд
cd admin-panel && npm run build

# Проверить монтирование
docker-compose exec nginx ls -la /admin-panel/dist
```

### 401 при запросах к API

**Причина:** Токен истёк или не сохранён.

**Решение:** 
- Войти заново через `/login`
- Проверить `localStorage` в DevTools

### CORS ошибка

**Причина:** API не настроен на домен админ-панели.

**Решение:** Добавить origin в `.env`:
```bash
CORS_ORIGINS=https://anmicius.ru,https://admin.anmicius.ru
```

---

## Связанные документы

- [Админ-эндпоинты](./admin-endpoints.md) — API endpoints для админки
- [Аутентификация](./authentication.md) — JWT и scopes
- [Развёртывание](./deployment.md) — Nginx конфигурация
