// Types for the admin panel

export interface Image {
  url: string;
  alt: string;
  caption?: string | null;
  thumbnail?: string | null;
}

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

// Specialty
export interface Specialty {
  id: number;
  code: string;
  name: string;
  short_description: string;
  description: string[];
  duration: string;
  budget_places: number;
  paid_places: number;
  qualification: string;
  exams: string[];
  images: Image[];
  is_popular: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SpecialtyListItem {
  id: number;
  code: string;
  name: string;
  is_popular: boolean;
}

export interface SpecialtyCreate {
  code: string;
  name: string;
  short_description?: string;
  description?: string[];
  duration?: string;
  budget_places?: number;
  paid_places?: number;
  qualification?: string;
  exams?: string[];
  images?: Image[];
  is_popular?: boolean;
}

// Interesting Fact
export interface InterestingFact {
  id: number;
  specialty_code: string;
  title: string;
  description: string[];
  images: Image[];
  created_at?: string;
  updated_at?: string;
}

export interface FactListItem {
  id: number;
  specialty_code: string;
  title: string;
}

export interface FactCreate {
  specialty_code: string;
  title: string;
  description?: string[];
  images?: Image[];
}

// News
export interface News {
  id: number;
  title: string;
  slug: string;
  preview_text: string;
  content: string[];
  preview_image?: string | null;
  gallery: Image[];
  published_at: string;
  views: number;
  created_at?: string;
  updated_at?: string;
}

export interface NewsListItem {
  id: number;
  title: string;
  slug: string;
  published_at: string;
}

export interface NewsCreate {
  title: string;
  slug: string;
  preview_text?: string;
  content?: string[];
  preview_image?: string | null;
  gallery?: Image[];
}

// FAQ
export interface FAQ {
  id: number;
  question: string;
  answer: string | string[];
  category: string;
  show_in_admission: boolean;
  images: Image[];
  documents: Image[];
  created_at?: string;
  updated_at?: string;
}

export interface FAQCreate {
  question: string;
  answer: string | string[];
  category: string;
  show_in_admission?: boolean;
  images?: Image[];
  documents?: Image[];
}

// Document
export interface Document {
  id: number;
  title: string;
  category: string;
  file_url: string;
  file_size?: number | null;
  images: Image[];
  created_at?: string;
  updated_at?: string;
}

export interface DocumentCreate {
  title: string;
  category: string;
  file_url: string;
  file_size?: number | null;
  images?: Image[];
}

// Test Question
export interface TestQuestion {
  id: number;
  text: string;
  options: string[];
  image_url?: string | null;
  documents: Image[];
  created_at?: string;
  updated_at?: string;
}

// Gallery Image
export interface GalleryImage {
  id: number;
  url: string;
  thumbnail: string;
  alt: string;
  category: string;
  caption?: string | null;
  date_taken?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface GalleryImageCreate {
  url: string;
  thumbnail: string;
  alt: string;
  category: string;
  caption?: string | null;
  date_taken?: string | null;
}

export interface GalleryImageUpdate {
  url?: string;
  thumbnail?: string;
  alt?: string;
  category?: string;
  caption?: string | null;
  date_taken?: string | null;
}

// Upload
export interface UploadResponse {
  url: string;
  filename: string;
  size: number;
  content_type: string;
}

// Pagination
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  items: T[];
}

// API Error
export interface ApiError {
  detail: string;
  status_code?: number;
}
