import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert, Badge, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { SpecialtyListItem } from '../types';

export default function SpecialtiesListPage() {
  const [specialties, setSpecialties] = useState<SpecialtyListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSpecialties = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getSpecialties(1, 100);
      setSpecialties(response.items);
    } catch {
      setError('Не удалось загрузить специальности');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSpecialties();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту специальность?')) {
      return;
    }

    try {
      await apiService.deleteSpecialty(id);
      setSpecialties((prev) => prev.filter((s) => s.id !== id));
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
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Специальности</h2>
        <Button variant="primary" as={Link as any} to="/specialties/new">
          + Новая специальность
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {specialties.length === 0 ? (
            <p className="text-muted text-center">Специальности не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Название</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {specialties.map((specialty) => (
                  <tr key={specialty.id}>
                    <td>
                      <code>{specialty.code}</code>
                    </td>
                    <td>{specialty.name}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link as any}
                        to={`/specialties/${specialty.id}/edit`}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(specialty.id)}
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
    </Container>
  );
}
