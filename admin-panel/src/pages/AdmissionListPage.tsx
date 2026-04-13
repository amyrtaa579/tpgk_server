import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { AdmissionListItem } from '../types';

export default function AdmissionListPage() {
  const [admissions, setAdmissions] = useState<AdmissionListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAdmissions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getAdmissionList();
      setAdmissions(response.items);
    } catch {
      setError('Не удалось загрузить данные о приёмных кампаниях');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAdmissions();
  }, []);

  const handleDelete = async (year: number) => {
    if (!confirm(`Вы уверены, что хотите удалить приёмную кампанию ${year} года?`)) {
      return;
    }

    try {
      await apiService.deleteAdmission(year);
      setAdmissions((prev) => prev.filter((item) => item.year !== year));
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
        <h2>Приёмные кампании</h2>
        <Button variant="success" as={Link as any} to="/admission/new">
          + Новая кампания
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {admissions.length === 0 ? (
            <p className="text-muted text-center">Приёмные кампании не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Год</th>
                  <th>Создано</th>
                  <th>Обновлено</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {admissions.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>
                      <Badge bg="primary">{item.year}</Badge>
                    </td>
                    <td>{new Date(item.created_at).toLocaleDateString('ru-RU')}</td>
                    <td>{new Date(item.updated_at).toLocaleDateString('ru-RU')}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link as any}
                        to={`/admission/${item.year}/edit`}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(item.year)}
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
