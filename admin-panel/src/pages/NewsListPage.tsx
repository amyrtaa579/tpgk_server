import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { NewsListItem } from '../types';

export default function NewsListPage() {
  const [news, setNews] = useState<NewsListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNews = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getNews(1, 100);
      setNews(response.items);
    } catch {
      setError('Не удалось загрузить новости');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту новость?')) {
      return;
    }

    try {
      await apiService.deleteNews(id);
      setNews((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Ошибка при удалении');
    }
  };

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
        <h2>Новости</h2>
        <Button variant="success" as={Link as any} to="/news/new">
          + Новая новость
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {news.length === 0 ? (
            <p className="text-muted text-center">Новости не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Заголовок</th>
                  <th>Slug</th>
                  <th>Дата публикации</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {news.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.title}</td>
                    <td>
                      <code>{item.slug}</code>
                    </td>
                    <td>{new Date(item.published_at).toLocaleDateString('ru-RU')}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link as any}
                        to={`/news/${item.id}/edit`}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(item.id)}
                      >
                        Удалить
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
