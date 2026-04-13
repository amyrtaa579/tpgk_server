import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { TestQuestion } from '../types';

export default function TestQuestionsListPage() {
  const [questions, setQuestions] = useState<TestQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getTestQuestions();
      setQuestions(response);
    } catch {
      setError('Не удалось загрузить вопросы теста');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      return;
    }

    try {
      await apiService.deleteTestQuestion(id);
      setQuestions((prev) => prev.filter((q) => q.id !== id));
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
        <h2>Вопросы теста профориентации</h2>
        <Button variant="success" as={Link as any} to="/test-questions/new">
          + Новый вопрос
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {questions.length === 0 ? (
            <p className="text-muted text-center">Вопросы не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Текст вопроса</th>
                  <th>Варианты ответов</th>
                  <th>Изображение</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {questions.map((q) => (
                  <tr key={q.id}>
                    <td>{q.id}</td>
                    <td style={{ maxWidth: '300px' }}>{q.text}</td>
                    <td>
                      <small className="text-muted">
                        {q.options?.length || 0} вариантов
                      </small>
                    </td>
                    <td>
                      {q.image_url ? (
                        <img
                          src={q.image_url}
                          alt="Question"
                          style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '4px' }}
                        />
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        as={Link as any}
                        to={`/test-questions/${q.id}/edit`}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(q.id)}
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
