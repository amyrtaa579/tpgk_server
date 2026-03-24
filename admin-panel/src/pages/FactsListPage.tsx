import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { FactListItem } from '../types';

export default function FactsListPage() {
  const [facts, setFacts] = useState<FactListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFacts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getFacts(1, 100);
      setFacts(response.items);
    } catch {
      setError('Не удалось загрузить факты');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFacts();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот факт?')) {
      return;
    }

    try {
      await apiService.deleteFact(id);
      setFacts((prev) => prev.filter((f) => f.id !== id));
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
        <h2>Интересные факты</h2>
        <Button variant="info" as={Link} to="/facts/new">
          + Новый факт
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {facts.length === 0 ? (
            <p className="text-muted text-center">Факты не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Код специальности</th>
                  <th>Заголовок</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {facts.map((fact) => (
                  <tr key={fact.id}>
                    <td>{fact.id}</td>
                    <td>
                      <code>{fact.specialty_code}</code>
                    </td>
                    <td>{fact.title}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link}
                        to={`/facts/${fact.id}/edit`}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(fact.id)}
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
