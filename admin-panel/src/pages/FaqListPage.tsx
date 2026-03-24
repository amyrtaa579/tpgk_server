import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { FAQ } from '../types';

export default function FaqListPage() {
  const [faqItems, setFaqItems] = useState<FAQ[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFaq = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getFaq();
      setFaqItems(response);
    } catch {
      setError('Не удалось загрузить FAQ');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFaq();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      return;
    }

    try {
      await apiService.deleteFaq(id);
      setFaqItems((prev) => prev.filter((item) => item.id !== id));
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
        <h2>Часто задаваемые вопросы (FAQ)</h2>
        <Button variant="success" as={Link} to="/faq/new">
          + Новый вопрос
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {faqItems.length === 0 ? (
            <p className="text-muted text-center">Вопросы не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Вопрос</th>
                  <th>Категория</th>
                  <th>Показывать в приёмной</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {faqItems.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.question}</td>
                    <td>
                      <Badge bg="secondary">{item.category}</Badge>
                    </td>
                    <td>
                      {item.show_in_admission ? (
                        <Badge bg="success">Да</Badge>
                      ) : (
                        <Badge bg="secondary">Нет</Badge>
                      )}
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link}
                        to={`/faq/${item.id}/edit`}
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
