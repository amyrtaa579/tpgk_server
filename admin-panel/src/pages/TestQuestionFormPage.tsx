import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col, Badge } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import DocumentUploader from '../components/DocumentUploader';

interface Specialty {
  id: number;
  code: string;
  name: string;
}

export default function TestQuestionFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [formData, setFormData] = useState({
    text: '',
    options: [''] as string[],
    answer_scores: [] as { answer: string; specialties: string[] }[],
    image_url: '',
    documents: [] as string[],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [showDocumentUploader, setShowDocumentUploader] = useState(false);
  const [activeAnswerForScoring, setActiveAnswerForScoring] = useState<string | null>(null);

  useEffect(() => {
    loadSpecialties();
    if (isEdit) {
      loadQuestion();
    }
  }, [id]);

  const loadSpecialties = async () => {
    try {
      const response = await apiService.getSpecialties(1, 100);
      setSpecialties(response.items || []);
    } catch (err) {
      console.error('Failed to load specialties:', err);
    }
  };

  const loadQuestion = async () => {
    try {
      const question = await apiService.getTestQuestionById(Number(id));
      setFormData({
        text: question.text,
        options: question.options || [''],
        answer_scores: question.answer_scores || [],
        image_url: question.image_url || '',
        documents: question.documents?.map((d) => d.url) || [],
      });
    } catch (err) {
      setError('Не удалось загрузить вопрос: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    // Фильтруем пустые варианты
    const filteredOptions = formData.options.filter(opt => opt.trim() !== '');

    if (filteredOptions.length < 2) {
      setError('Должно быть как минимум 2 варианта ответа');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = { 
        text: formData.text,
        options: filteredOptions,
        answer_scores: formData.answer_scores,
        image_url: formData.image_url,
        documents: formData.documents,
      };
      if (isEdit) {
        await apiService.updateTestQuestion(Number(id), payload);
      } else {
        await apiService.createTestQuestion(payload);
      }
      navigate('/test-questions');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...formData.options];
    newOptions[index] = value;
    setFormData({ ...formData, options: newOptions });
    
    // Обновляем answer_scores при изменении текста ответа
    const oldAnswer = formData.options[index];
    if (oldAnswer && oldAnswer.trim()) {
      const newAnswerScores = formData.answer_scores.map(score => 
        score.answer === oldAnswer ? { ...score, answer: value } : score
      );
      setFormData({ ...formData, options: newOptions, answer_scores: newAnswerScores });
    } else {
      setFormData({ ...formData, options: newOptions });
    }
  };

  const handleAddOption = () => {
    setFormData({ ...formData, options: [...formData.options, ''] });
  };

  const handleRemoveOption = (index: number) => {
    if (formData.options.length <= 2) {
      alert('Должно быть как минимум 2 варианта ответа');
      return;
    }
    const removedOption = formData.options[index];
    const newOptions = formData.options.filter((_, i) => i !== index);
    const newAnswerScores = formData.answer_scores.filter(s => s.answer !== removedOption);
    setFormData({ ...formData, options: newOptions, answer_scores: newAnswerScores });
  };

  const handleImageSelect = (imageUrl: string) => {
    setFormData({ ...formData, image_url: imageUrl });
    setShowImagePicker(false);
  };

  const handleRemoveImage = () => {
    setFormData({ ...formData, image_url: '' });
  };

  const handleDocumentSelect = (documentUrl: string) => {
    setFormData({ ...formData, documents: [...formData.documents, documentUrl] });
    setShowDocumentUploader(false);
  };

  const handleRemoveDocument = (index: number) => {
    setFormData({ ...formData, documents: formData.documents.filter((_, i) => i !== index) });
  };

  // Управление answer_scores
  const handleToggleSpecialty = (answer: string, specialtyCode: string) => {
    const existingScore = formData.answer_scores.find(s => s.answer === answer);
    let newAnswerScores;

    if (existingScore) {
      const hasSpecialty = existingScore.specialties.includes(specialtyCode);
      if (hasSpecialty) {
        // Удаляем специальность
        newAnswerScores = formData.answer_scores.map(s =>
          s.answer === answer
            ? { ...s, specialties: s.specialties.filter(sp => sp !== specialtyCode) }
            : s
        ).filter(s => s.specialties.length > 0);
      } else {
        // Добавляем специальность
        newAnswerScores = formData.answer_scores.map(s =>
          s.answer === answer
            ? { ...s, specialties: [...s.specialties, specialtyCode] }
            : s
        );
      }
    } else {
      // Создаём новую запись
      newAnswerScores = [...formData.answer_scores, { answer, specialties: [specialtyCode] }];
    }

    setFormData({ ...formData, answer_scores: newAnswerScores });
  };

  const getSpecialtiesForAnswer = (answer: string): string[] => {
    const score = formData.answer_scores.find(s => s.answer === answer);
    return score ? score.specialties : [];
  };

  // Получение цвета для специальности по индексу
  const getSpecialtyColor = (index: number): string => {
    const colors = ['primary', 'success', 'danger', 'info', 'warning', 'secondary', 'dark', 'info'];
    return colors[index % colors.length];
  };

  // Получение стиля для бейджа специальности
  const getBadgeStyle = (isSelected: boolean, color: string) => {
    if (isSelected) {
      // Для выбранных: цветной фон, белый текст
      return {
        bg: color,
        text: 'light' as const,
        border: '2px solid transparent',
      };
    } else {
      // Для невыбранных: светлый фон, тёмный текст, цветная рамка
      return {
        bg: 'light' as const,
        text: 'dark' as const,
        border: `2px solid var(--bs-${color})`,
      };
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
        <h2>{isEdit ? 'Редактирование вопроса' : 'Новый вопрос теста'}</h2>
        <Button variant="secondary" as={Link as any} to="/test-questions">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-primary text-white">
          <Card.Title className="mb-0">📝 Основная информация</Card.Title>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Текст вопроса *</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.text}
                onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                required
                placeholder="Введите текст вопроса"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Варианты ответов *</Form.Label>
              {formData.options.map((option, index) => (
                <Row key={index} className="mb-2 align-items-center">
                  <Col md={10}>
                    <Form.Control
                      type="text"
                      value={option}
                      onChange={(e) => handleOptionChange(index, e.target.value)}
                      placeholder={`Вариант ${index + 1}`}
                    />
                  </Col>
                  <Col md={2}>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleRemoveOption(index)}
                      disabled={formData.options.length <= 2}
                    >
                      Удалить
                    </Button>
                  </Col>
                </Row>
              ))}
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={handleAddOption}
              >
                + Добавить вариант
              </Button>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Изображение (необязательно)</Form.Label>
              {formData.image_url ? (
                <div className="mb-2">
                  <div className="position-relative d-inline-block">
                    <img
                      src={formData.image_url}
                      alt="Question"
                      style={{ maxWidth: '300px', maxHeight: '200px', borderRadius: '4px' }}
                    />
                    <Button
                      variant="danger"
                      size="sm"
                      className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                      onClick={handleRemoveImage}
                    >
                      ×
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setShowImagePicker(true)}
                >
                  Выбрать изображение
                </Button>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Документы (необязательно)</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setShowDocumentUploader(true)}
                >
                  Добавить документ
                </Button>
              </div>
              <div className="mt-2">
                {formData.documents.map((docUrl: string, index: number) => (
                  <div key={index} className="d-inline-block me-2 position-relative">
                    <div
                      className="d-flex align-items-center justify-content-center bg-light border rounded"
                      style={{ width: '100px', height: '100px', borderRadius: '4px' }}
                    >
                      <span style={{ fontSize: '24px' }}>📄</span>
                    </div>
                    <div className="text-center" style={{ fontSize: '12px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      Документ {index + 1}
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                      onClick={() => handleRemoveDocument(index)}
                    >
                      ×
                    </Button>
                  </div>
                ))}
              </div>
            </Form.Group>

            <div className="d-flex gap-2">
              <Button variant="success" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link as any} to="/test-questions">
                Отмена
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      {/* Секция управления баллами */}
      <Card className="shadow-sm">
        <Card.Header className="bg-success text-white">
          <Card.Title className="mb-0">🎯 Баллы за ответы (какие специальности получает за каждый ответ)</Card.Title>
        </Card.Header>
        <Card.Body>
          <Alert variant="info" className="mb-3">
            <strong>Как это работает:</strong> Для каждого варианта ответа выберите специальности, которые получат баллы при выборе этого ответа.
          </Alert>

          {formData.options.filter(opt => opt.trim()).length === 0 ? (
            <Alert variant="warning">
              Сначала добавьте варианты ответов выше, затем настройте баллы.
            </Alert>
          ) : specialties.length === 0 ? (
            <Alert variant="info">
              Загрузка специальностей...
            </Alert>
          ) : (
            <Row>
              {formData.options.filter(opt => opt.trim()).map((option, idx) => {
                const answerText = option.trim();
                const selectedSpecialties = getSpecialtiesForAnswer(answerText);

                return (
                  <Col md={6} key={idx} className="mb-4">
                    <Card className={`border-${activeAnswerForScoring === answerText ? 'primary' : 'secondary'}`}>
                      <Card.Header className="d-flex justify-content-between align-items-center">
                        <strong>Ответ {idx + 1}:</strong>
                        <span className="text-muted">{answerText}</span>
                      </Card.Header>
                      <Card.Body>
                        <div className="d-flex flex-wrap gap-2">
                          {specialties.map((spec, specIdx) => {
                            const isSelected = selectedSpecialties.includes(spec.code);
                            const color = getSpecialtyColor(specIdx);
                            const badgeStyle = getBadgeStyle(isSelected, color);
                            
                            return (
                              <Badge
                                key={spec.code}
                                bg={badgeStyle.bg}
                                text={badgeStyle.text}
                                style={{
                                  cursor: 'pointer',
                                  padding: '8px 12px',
                                  fontSize: '14px',
                                  border: badgeStyle.border,
                                  transition: 'all 0.2s',
                                }}
                                onClick={() => handleToggleSpecialty(answerText, spec.code)}
                              >
                                {isSelected ? '✓ ' : ''}{spec.code} - {spec.name}
                              </Badge>
                            );
                          })}
                        </div>
                        {selectedSpecialties.length === 0 && (
                          <small className="text-muted mt-2 d-block">
                            ⚠️ Ни одна специальность не выбрана
                          </small>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                );
              })}
            </Row>
          )}
        </Card.Body>
      </Card>

      <MinioImagePicker
        show={showImagePicker}
        onHide={() => setShowImagePicker(false)}
        onSelect={handleImageSelect}
        hideMinioTab={true}
      />

      <DocumentUploader
        show={showDocumentUploader}
        onHide={() => setShowDocumentUploader(false)}
        onSelect={handleDocumentSelect}
      />
    </div>
  );
}
