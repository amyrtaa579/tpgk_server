import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  AuthTokens,
  LoginCredentials,
  User,
  Specialty,
  SpecialtyListItem,
  FactListItem,
  News,
  NewsListItem,
  GalleryImage,
  UploadResponse,
  PaginatedResponse,
  FAQ,
  FAQCreate,
  Document,
  DocumentCreate,
  TestQuestion,
  Image,
} from '../types';

const API_BASE_URL = '/api/v1';

export class ApiError extends Error {
  status_code?: number;
  detail: string;

  constructor(message: string, status_code?: number) {
    super(message);
    this.name = 'ApiError';
    this.status_code = status_code;
    this.detail = message;
  }
}

class ApiService {
  private client: AxiosInstance;
  private refreshTokenPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for adding auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for handling auth errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.refreshTokenPromise) {
            try {
              const newToken = await this.refreshTokenPromise;
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            } catch {
              this.logout();
              return Promise.reject(error);
            }
          }

          originalRequest._retry = true;

          const refreshToken = localStorage.getItem('refresh_token');
          if (!refreshToken) {
            this.logout();
            return Promise.reject(error);
          }

          this.refreshTokenPromise = this.refreshAccessToken(refreshToken);

          try {
            const newToken = await this.refreshTokenPromise;
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            this.logout();
            return Promise.reject(refreshError);
          } finally {
            this.refreshTokenPromise = null;
          }
        }

        const errorMessage = error.response?.data?.detail || 'Произошла ошибка';
        const statusCode = error.response?.status;
        return Promise.reject(new ApiError(errorMessage, statusCode));
      }
    );
  }

  private async refreshAccessToken(refreshToken: string): Promise<string> {
    const response = await axios.post<{ access_token: string }>(
      `${API_BASE_URL}/auth/refresh`,
      { refresh_token: refreshToken }
    );
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return access_token;
  }

  // ============ Auth ============
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await this.client.post<AuthTokens>('/auth/login', credentials);
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await this.client.post('/auth/logout', { refresh_token: refreshToken });
      } catch {
        // Ignore logout errors
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // ============ Users (Admin) ============
  async getUsers(page: number = 1, limit: number = 10): Promise<PaginatedResponse<User>> {
    const response = await this.client.get<PaginatedResponse<User>>('/admin/users', {
      params: { page, limit },
    });
    return response.data;
  }

  async getUser(userId: number): Promise<User> {
    const response = await this.client.get<User>(`/admin/users/${userId}`);
    return response.data;
  }

  async createUser(userData: { email: string; username: string; password: string }): Promise<User> {
    const response = await this.client.post('/admin/users', userData);
    return response.data;
  }

  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response = await this.client.patch(`/admin/users/${userId}`, userData);
    return response.data;
  }

  async deleteUser(userId: number): Promise<void> {
    await this.client.delete(`/admin/users/${userId}`);
  }

  // ============ Specialties ============
  async getSpecialties(page: number = 1, limit: number = 100): Promise<PaginatedResponse<SpecialtyListItem>> {
    const response = await this.client.get<PaginatedResponse<SpecialtyListItem>>('/admin/specialties', {
      params: { page, limit },
    });
    return response.data;
  }

  async getSpecialtyById(id: number): Promise<Specialty> {
    const response = await this.client.get<Specialty>(`/admin/specialties/${id}`);
    return response.data;
  }

  async createSpecialty(formData: FormData): Promise<{ id: number; code: string; name: string }> {
    const response = await this.client.post('/admin/specialties', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async updateSpecialty(id: number, formData: FormData): Promise<{ id: number; code: string; name: string }> {
    const response = await this.client.put(`/admin/specialties/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteSpecialty(id: number): Promise<void> {
    await this.client.delete(`/admin/specialties/${id}`);
  }

  // ============ News ============
  async getNews(page: number = 1, limit: number = 100): Promise<PaginatedResponse<NewsListItem>> {
    const response = await this.client.get<PaginatedResponse<NewsListItem>>('/admin/news', {
      params: { page, limit },
    });
    return response.data;
  }

  async getNewsById(id: number): Promise<News> {
    const response = await this.client.get<News>(`/admin/news/${id}`);
    return response.data;
  }

  async createNews(formData: FormData): Promise<{ id: number; title: string; slug: string }> {
    const response = await this.client.post('/admin/news', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async updateNews(id: number, formData: FormData): Promise<{ id: number; title: string; slug: string }> {
    const response = await this.client.put(`/admin/news/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteNews(id: number): Promise<void> {
    await this.client.delete(`/admin/news/${id}`);
  }

  // ============ Facts ============
  async getFacts(page: number = 1, limit: number = 100): Promise<PaginatedResponse<FactListItem>> {
    const response = await this.client.get<PaginatedResponse<FactListItem>>('/admin/facts', {
      params: { page, limit },
    });
    return response.data;
  }

  async getFact(id: number): Promise<{ id: number; specialty_code: string; title: string; description: string[]; images: Image[] }> {
    const response = await this.client.get(`/admin/facts/${id}`);
    return response.data;
  }

  async createFact(formData: FormData): Promise<{ id: number; title: string }> {
    const response = await this.client.post('/admin/facts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async updateFact(id: number, formData: FormData): Promise<{ id: number; title: string }> {
    const response = await this.client.put(`/admin/facts/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteFact(id: number): Promise<void> {
    await this.client.delete(`/admin/facts/${id}`);
  }

  // ============ Gallery ============
  async getGallery(category?: string): Promise<PaginatedResponse<GalleryImage>> {
    const params = category ? { category } : {};
    const response = await this.client.get<PaginatedResponse<GalleryImage>>('/admin/gallery', { params });
    return response.data;
  }

  async getGalleryImage(id: number): Promise<GalleryImage> {
    const response = await this.client.get<GalleryImage>(`/admin/gallery/${id}`);
    return response.data;
  }

  async createGalleryImage(imageData: {
    url: string;
    thumbnail: string;
    alt: string;
    category: string;
    caption?: string | null;
    date_taken?: string | null;
  }): Promise<GalleryImage> {
    const response = await this.client.post('/admin/gallery', imageData);
    return response.data;
  }

  async updateGalleryImage(id: number, imageData: Partial<GalleryImage>): Promise<GalleryImage> {
    const response = await this.client.put(`/admin/gallery/${id}`, imageData);
    return response.data;
  }

  async deleteGalleryImage(id: number): Promise<void> {
    await this.client.delete(`/admin/gallery/${id}`);
  }

  // ============ Upload ============
  async uploadImage(file: File, category: string = 'common'): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const response = await this.client.post<UploadResponse>('/admin/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async uploadDocument(file: File, category: string = 'common'): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const response = await this.client.post<UploadResponse>('/admin/upload/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // ============ MinIO Images Browser ============
  async getMinioImages(category?: string): Promise<GalleryImage[]> {
    // Using gallery endpoint to get all images from MinIO
    const response = await this.getGallery(category);
    return response.items;
  }

  // ============ FAQ ============
  async getFaq(): Promise<FAQ[]> {
    const response = await this.client.get<FAQ[]>('/admin/faq');
    return response.data;
  }

  async getFaqById(id: number): Promise<FAQ> {
    const response = await this.client.get<FAQ>(`/admin/faq/${id}`);
    return response.data;
  }

  async createFaq(faqData: FAQCreate): Promise<FAQ> {
    const response = await this.client.post<FAQ>('/admin/faq', faqData);
    return response.data;
  }

  async updateFaq(id: number, faqData: Partial<FAQ>): Promise<FAQ> {
    const response = await this.client.put<FAQ>(`/admin/faq/${id}`, faqData);
    return response.data;
  }

  async deleteFaq(id: number): Promise<void> {
    await this.client.delete(`/admin/faq/${id}`);
  }

  // ============ Documents ============
  async getDocuments(): Promise<Document[]> {
    const response = await this.client.get<Document[]>('/admin/documents');
    return response.data;
  }

  async getDocumentById(id: number): Promise<Document> {
    const response = await this.client.get<Document>(`/admin/documents/${id}`);
    return response.data;
  }

  async createDocument(docData: DocumentCreate): Promise<Document> {
    const response = await this.client.post<Document>('/admin/documents', docData);
    return response.data;
  }

  async updateDocument(id: number, docData: Partial<Document>): Promise<Document> {
    const response = await this.client.put<Document>(`/admin/documents/${id}`, docData);
    return response.data;
  }

  async deleteDocument(id: number): Promise<void> {
    await this.client.delete(`/admin/documents/${id}`);
  }

  // ============ About ============
  async getAbout(): Promise<{ title: string; description: string[]; images: Image[] }> {
    const response = await this.client.get('/admin/about');
    return response.data;
  }

  async updateAbout(aboutData: { title: string; description: string[]; images?: Image[] }): Promise<void> {
    await this.client.put('/admin/about', aboutData);
  }

  // ============ Test Questions ============
  async getTestQuestions(): Promise<TestQuestion[]> {
    const response = await this.client.get<TestQuestion[]>('/admin/test/questions');
    return response.data;
  }

  async getTestQuestionById(id: number): Promise<TestQuestion> {
    const response = await this.client.get<TestQuestion>(`/admin/test/questions/${id}`);
    return response.data;
  }

  async createTestQuestion(questionData: { text: string; options: string[]; image_url?: string }): Promise<TestQuestion> {
    const response = await this.client.post<TestQuestion>('/admin/test/questions', questionData);
    return response.data;
  }

  async updateTestQuestion(id: number, questionData: Partial<TestQuestion>): Promise<TestQuestion> {
    const response = await this.client.put<TestQuestion>(`/admin/test/questions/${id}`, questionData);
    return response.data;
  }

  async deleteTestQuestion(id: number): Promise<void> {
    await this.client.delete(`/admin/test/questions/${id}`);
  }
}

export const apiService = new ApiService();
