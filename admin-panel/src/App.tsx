import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SpecialtiesListPage from './pages/SpecialtiesListPage';
import SpecialtyFormPage from './pages/SpecialtyFormPage';
import NewsListPage from './pages/NewsListPage';
import NewsFormPage from './pages/NewsFormPage';
import FactsListPage from './pages/FactsListPage';
import FactFormPage from './pages/FactFormPage';
import GalleryListPage from './pages/GalleryListPage';
import GalleryFormPage from './pages/GalleryFormPage';
import UsersListPage from './pages/UsersListPage';
import FaqListPage from './pages/FaqListPage';
import FaqFormPage from './pages/FaqFormPage';
import DocumentsListPage from './pages/DocumentsListPage';
import DocumentsFormPage from './pages/DocumentsFormPage';
import AboutPage from './pages/AboutPage';
import TestQuestionsListPage from './pages/TestQuestionsListPage';
import TestQuestionFormPage from './pages/TestQuestionFormPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Specialties */}
          <Route
            path="/specialties"
            element={
              <ProtectedRoute>
                <Layout>
                  <SpecialtiesListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/specialties/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <SpecialtyFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/specialties/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <SpecialtyFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* News */}
          <Route
            path="/news"
            element={
              <ProtectedRoute>
                <Layout>
                  <NewsListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/news/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <NewsFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/news/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <NewsFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Facts */}
          <Route
            path="/facts"
            element={
              <ProtectedRoute>
                <Layout>
                  <FactsListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/facts/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <FactFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/facts/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <FactFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Gallery */}
          <Route
            path="/gallery"
            element={
              <ProtectedRoute>
                <Layout>
                  <GalleryListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/gallery/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <GalleryFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/gallery/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <GalleryFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Users (superuser only) */}
          <Route
            path="/users"
            element={
              <ProtectedRoute requireSuperuser>
                <Layout>
                  <UsersListPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* FAQ */}
          <Route
            path="/faq"
            element={
              <ProtectedRoute>
                <Layout>
                  <FaqListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/faq/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <FaqFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/faq/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <FaqFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Documents */}
          <Route
            path="/documents"
            element={
              <ProtectedRoute>
                <Layout>
                  <DocumentsListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <DocumentsFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <DocumentsFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* About */}
          <Route
            path="/about"
            element={
              <ProtectedRoute>
                <Layout>
                  <AboutPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Test Questions */}
          <Route
            path="/test-questions"
            element={
              <ProtectedRoute>
                <Layout>
                  <TestQuestionsListPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test-questions/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <TestQuestionFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test-questions/:id/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <TestQuestionFormPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
