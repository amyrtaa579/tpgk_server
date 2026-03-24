import { useState, useEffect } from 'react';
import { Card, Row, Col, Spinner, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    specialties: 0,
    news: 0,
    facts: 0,
    galleryImages: 0,
    users: 0,
    faq: 0,
    documents: 0,
    testQuestions: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [specialties, news, facts, gallery, users, faq, documents, testQuestions] = await Promise.all([
          apiService.getSpecialties(1, 1).catch(() => ({ total: 0 })),
          apiService.getNews(1, 1).catch(() => ({ total: 0 })),
          apiService.getFacts(1, 1).catch(() => ({ total: 0 })),
          apiService.getGallery().catch(() => ({ total: 0 })),
          apiService.getUsers(1, 1).catch(() => ({ total: 0 })),
          apiService.getFaq().catch(() => []),
          apiService.getDocuments().catch(() => []),
          apiService.getTestQuestions().catch(() => []),
        ]);

        setStats({
          specialties: specialties.total || 0,
          news: news.total || 0,
          facts: facts.total || 0,
          galleryImages: gallery.total || 0,
          users: users.total || 0,
          faq: Array.isArray(faq) ? faq.length : 0,
          documents: Array.isArray(documents) ? documents.length : 0,
          testQuestions: Array.isArray(testQuestions) ? testQuestions.length : 0,
        });
      } catch {
        setError('Не удалось загрузить статистику');
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  const statCards = [
    {
      title: 'Специальности',
      value: stats.specialties,
      icon: '📚',
      link: '/specialties',
      color: 'primary',
    },
    {
      title: 'Новости',
      value: stats.news,
      icon: '📰',
      link: '/news',
      color: 'success',
    },
    {
      title: 'Интересные факты',
      value: stats.facts,
      icon: '💡',
      link: '/facts',
      color: 'info',
    },
    {
      title: 'FAQ',
      value: stats.faq,
      icon: '❓',
      link: '/faq',
      color: 'secondary',
    },
    {
      title: 'Документы',
      value: stats.documents,
      icon: '📄',
      link: '/documents',
      color: 'dark',
    },
    {
      title: 'О колледже',
      value: '1',
      icon: 'ℹ️',
      link: '/about',
      color: 'primary',
    },
    {
      title: 'Тесты',
      value: stats.testQuestions,
      icon: '📝',
      link: '/test-questions',
      color: 'warning',
    },
    {
      title: 'Изображения в галерее',
      value: stats.galleryImages,
      icon: '🖼️',
      link: '/gallery',
      color: 'warning',
    },
    ...(user?.is_superuser
      ? [
          {
            title: 'Пользователи',
            value: stats.users,
            icon: '👥',
            link: '/users',
            color: 'danger',
          },
        ]
      : []),
  ];

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
        <Spinner animation="border" variant="primary" />
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Панель управления</h2>
        <div>
          <span className="text-muted">
            👋 Добро пожаловать, <strong>{user?.username}</strong>
          </span>
          {user?.is_superuser && (
            <span className="badge bg-danger ms-2">Суперпользователь</span>
          )}
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Row className="g-4">
        {statCards.map((stat) => (
          <Col xs={12} sm={6} md={4} lg={2} key={stat.title}>
            <Card className="h-100 shadow-sm">
              <Card.Body className="text-center">
                <div className="display-4 mb-2">{stat.icon}</div>
                <h3 className={`text-${stat.color}`}>{stat.value}</h3>
                <p className="text-muted mb-3">{stat.title}</p>
                <Button variant={`outline-${stat.color}`} size="sm" as={Link} to={stat.link}>
                  Управление
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="mt-4">
        <Col>
          <Card className="shadow-sm">
            <Card.Header>
              <h5 className="mb-0">Быстрые действия</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-flex flex-wrap gap-2">
                <Button variant="primary" as={Link} to="/specialties/new">
                  + Новая специальность
                </Button>
                <Button variant="success" as={Link} to="/news/new">
                  + Новая новость
                </Button>
                <Button variant="info" as={Link} to="/facts/new">
                  + Новый факт
                </Button>
                <Button variant="secondary" as={Link} to="/faq/new">
                  + Новый вопрос FAQ
                </Button>
                <Button variant="dark" as={Link} to="/documents/new">
                  + Новый документ
                </Button>
                <Button variant="warning" as={Link} to="/test-questions/new">
                  + Новый вопрос теста
                </Button>
                <Button variant="warning" as={Link} to="/gallery/new">
                  + Изображение в галерею
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        <Col>
          <Card className="shadow-sm">
            <Card.Header>
              <h5 className="mb-0">О системе</h5>
            </Card.Header>
            <Card.Body>
              <p className="mb-2">
                <strong>API:</strong> Anmicius API v1
              </p>
              <p className="mb-0">
                <strong>Версия панели:</strong> 1.0.0
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
