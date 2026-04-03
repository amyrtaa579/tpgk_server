import { useState, useEffect, useCallback } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col, InputGroup, Table, Badge, Modal } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { Admission, SpecialtyAdmission, SubmissionMethod, ImportantDate, SpecialtyListItem } from '../types';

export default function AdmissionFormPage() {
  const { year } = useParams<{ year: string }>();
  const navigate = useNavigate();
  const isEdit = !!year;
  const editYear = year ? parseInt(year, 10) : new Date().getFullYear();

  const [formData, setFormData] = useState<Admission>({
    year: editYear,
    specialties_admission: [],
    submission_methods: [],
    important_dates: [],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Справочник специальностей
  const [specialties, setSpecialties] = useState<SpecialtyListItem[]>([]);
  const [showSpecialtyPicker, setShowSpecialtyPicker] = useState(false);
  const [selectedSpecialtyCodes, setSelectedSpecialtyCodes] = useState<Set<string>>(new Set());

  // Состояния для добавления новых элементов вручную
  const [newSpecialty, setNewSpecialty] = useState<SpecialtyAdmission>({
    code: '',
    name: '',
    budget_places: 0,
    paid_places: 0,
    exams: [],
    duration: '',
  });

  const [newSubmissionMethod, setNewSubmissionMethod] = useState<SubmissionMethod>({
    title: '',
    description: '',
    link: null,
  });

  const [newImportantDate, setNewImportantDate] = useState<ImportantDate>({
    title: '',
    date: '',
    description: null,
  });

  const [examInput, setExamInput] = useState('');

  useEffect(() => {
    loadSpecialties();
    if (isEdit) {
      loadAdmission();
    } else {
      setFormData({ ...formData, year: editYear });
    }
  }, [year]);

  const loadSpecialties = async () => {
    try {
      const response = await apiService.getSpecialties(1, 100);
      setSpecialties(response.items || []);
    } catch (err) {
      console.error('Failed to load specialties:', err);
    }
  };

  const loadAdmission = async () => {
    try {
      const admission = await apiService.getAdmissionByYear(editYear);
      setFormData(admission);
    } catch (err) {
      // Если данных нет — это нормально, начинаем с пустой формы
      if ((err as any)?.status_code === 404) {
        setFormData({
          year: editYear,
          specialties_admission: [],
          submission_methods: [],
          important_dates: [],
        });
      } else {
        setError('Не удалось загрузить данные: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (isEdit) {
        await apiService.updateAdmission(editYear, formData);
      } else {
        await apiService.createAdmission(formData);
      }
      navigate('/admission');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  // === Выбор из справочника специальностей ===
  const handleAddFromDirectory = () => {
    const codesToAdd = Array.from(selectedSpecialtyCodes);
    if (codesToAdd.length === 0) {
      alert('Выберите хотя бы одну специальность');
      return;
    }

    const newEntries: SpecialtyAdmission[] = [];

    for (const code of codesToAdd) {
      const spec = specialties.find((s) => s.code === code);
      if (!spec) continue;

      // Если у специальности есть education_options — создаём отдельную запись для каждого
      if (spec.education_options && spec.education_options.length > 0) {
        for (const eo of spec.education_options) {
          // Пропускаем если уже добавлена такая же комбинация code + education_level
          const alreadyExists = formData.specialties_admission.some(
            (s) => s.code === code && s.education_level === eo.education_level
          );
          if (alreadyExists) continue;

          newEntries.push({
            code: spec.code,
            name: spec.name,
            education_level: eo.education_level,
            budget_places: eo.budget_places,
            paid_places: eo.paid_places,
            exams: spec.exams || [],
            duration: eo.duration,
          });
        }
      } else {
        // Fallback если education_options нет
        if (formData.specialties_admission.some((s) => s.code === code)) continue;

        newEntries.push({
          code: spec.code,
          name: spec.name,
          budget_places: 0,
          paid_places: 0,
          exams: spec.exams || [],
          duration: '',
        });
      }
    }

    if (newEntries.length === 0) {
      alert('Все выбранные специальности уже добавлены');
      return;
    }

    setFormData({
      ...formData,
      specialties_admission: [...formData.specialties_admission, ...newEntries],
    });

    setShowSpecialtyPicker(false);
    setSelectedSpecialtyCodes(new Set());
  };

  const toggleSpecialtySelection = (code: string) => {
    const newSet = new Set(selectedSpecialtyCodes);
    if (newSet.has(code)) {
      newSet.delete(code);
    } else {
      newSet.add(code);
    }
    setSelectedSpecialtyCodes(newSet);
  };

  const selectAllSpecialties = () => {
    const allCodes = specialties.map((s) => s.code);
    setSelectedSpecialtyCodes(new Set(allCodes));
  };

  const clearSelection = () => {
    setSelectedSpecialtyCodes(new Set());
  };

  // Handlers для специальностей (ручной ввод)
  const handleAddSpecialty = () => {
    if (!newSpecialty.code || !newSpecialty.name) {
      alert('Укажите код и название специальности');
      return;
    }
    setFormData({
      ...formData,
      specialties_admission: [...formData.specialties_admission, { ...newSpecialty }],
    });
    setNewSpecialty({ code: '', name: '', budget_places: 0, paid_places: 0, exams: [], duration: '' });
  };

  const handleRemoveSpecialty = (index: number) => {
    setFormData({
      ...formData,
      specialties_admission: formData.specialties_admission.filter((_, i) => i !== index),
    });
  };

  const handleAddExam = () => {
    if (examInput.trim()) {
      setNewSpecialty({ ...newSpecialty, exams: [...newSpecialty.exams, examInput.trim()] });
      setExamInput('');
    }
  };

  const handleRemoveExam = (examIndex: number) => {
    setNewSpecialty({ ...newSpecialty, exams: newSpecialty.exams.filter((_, i) => i !== examIndex) });
  };

  // Handlers для способов подачи
  const handleAddSubmissionMethod = () => {
    if (!newSubmissionMethod.title) {
      alert('Укажите название способа подачи');
      return;
    }
    setFormData({
      ...formData,
      submission_methods: [...formData.submission_methods, { ...newSubmissionMethod }],
    });
    setNewSubmissionMethod({ title: '', description: '', link: null });
  };

  const handleRemoveSubmissionMethod = (index: number) => {
    setFormData({
      ...formData,
      submission_methods: formData.submission_methods.filter((_, i) => i !== index),
    });
  };

  // Handlers для важных дат
  const handleAddImportantDate = () => {
    if (!newImportantDate.title || !newImportantDate.date) {
      alert('Укажите название и дату');
      return;
    }
    setFormData({
      ...formData,
      important_dates: [...formData.important_dates, { ...newImportantDate }],
    });
    setNewImportantDate({ title: '', date: '', description: null });
  };

  const handleRemoveImportantDate = (index: number) => {
    setFormData({
      ...formData,
      important_dates: formData.important_dates.filter((_, i) => i !== index),
    });
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
        <h2>{isEdit ? `Редактирование приёмной кампании ${editYear}` : 'Новая приёмная кампания'}</h2>
        <Button variant="secondary" as={Link as any} to="/admission">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Form onSubmit={handleSubmit}>
        {/* Год */}
        <Card className="mb-4 shadow-sm">
          <Card.Header>
            <Card.Title as="h5">Год приёма</Card.Title>
          </Card.Header>
          <Card.Body>
            <Form.Group>
              <Form.Label>Год поступления</Form.Label>
              <Form.Control
                type="number"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value, 10) })}
                disabled={isEdit}
                min={2020}
                max={2100}
              />
            </Form.Group>
          </Card.Body>
        </Card>

        {/* Специальности */}
        <Card className="mb-4 shadow-sm">
          <Card.Header className="d-flex justify-content-between align-items-center">
            <Card.Title as="h5" className="mb-0">
              Специальности
            </Card.Title>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={() => {
                setSelectedSpecialtyCodes(new Set());
                setShowSpecialtyPicker(true);
              }}
              disabled={specialties.length === 0}
            >
              📋 Добавить из справочника
            </Button>
          </Card.Header>
          <Card.Body>
            {formData.specialties_admission.length > 0 && (
              <Table responsive striped size="sm" className="mb-3">
                <thead>
                  <tr>
                    <th>Код</th>
                    <th>Название</th>
                    <th>Уровень образования</th>
                    <th>Бюджет</th>
                    <th>Платные</th>
                    <th>Экзамены</th>
                    <th>Длительность</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {formData.specialties_admission.map((spec, idx) => (
                    <tr key={idx}>
                      <td>
                        <Form.Control
                          size="sm"
                          value={spec.code}
                          onChange={(e) => {
                            const updated = [...formData.specialties_admission];
                            updated[idx] = { ...updated[idx], code: e.target.value };
                            setFormData({ ...formData, specialties_admission: updated });
                          }}
                        />
                      </td>
                      <td>
                        <Form.Control
                          size="sm"
                          value={spec.name}
                          onChange={(e) => {
                            const updated = [...formData.specialties_admission];
                            updated[idx] = { ...updated[idx], name: e.target.value };
                            setFormData({ ...formData, specialties_admission: updated });
                          }}
                        />
                      </td>
                      <td>
                        <small>{spec.education_level || '—'}</small>
                      </td>
                      <td style={{ width: 90 }}>
                        <Form.Control
                          type="number"
                          size="sm"
                          value={spec.budget_places}
                          onChange={(e) => {
                            const updated = [...formData.specialties_admission];
                            updated[idx] = { ...updated[idx], budget_places: parseInt(e.target.value, 10) || 0 };
                            setFormData({ ...formData, specialties_admission: updated });
                          }}
                        />
                      </td>
                      <td style={{ width: 90 }}>
                        <Form.Control
                          type="number"
                          size="sm"
                          value={spec.paid_places}
                          onChange={(e) => {
                            const updated = [...formData.specialties_admission];
                            updated[idx] = { ...updated[idx], paid_places: parseInt(e.target.value, 10) || 0 };
                            setFormData({ ...formData, specialties_admission: updated });
                          }}
                        />
                      </td>
                      <td>
                        <small>{spec.exams?.join(', ') || '—'}</small>
                      </td>
                      <td>
                        <Form.Control
                          size="sm"
                          value={spec.duration}
                          onChange={(e) => {
                            const updated = [...formData.specialties_admission];
                            updated[idx] = { ...updated[idx], duration: e.target.value };
                            setFormData({ ...formData, specialties_admission: updated });
                          }}
                        />
                      </td>
                      <td style={{ width: 90 }}>
                        <Button variant="outline-danger" size="sm" onClick={() => handleRemoveSpecialty(idx)}>
                          ×
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}

            {formData.specialties_admission.length === 0 && (
              <Alert variant="info" className="mb-3">
                Нет специальностей. Нажмите{' '}
                <strong>«📋 Добавить из справочника»</strong> чтобы выбрать из существующих, или добавьте вручную ниже.
              </Alert>
            )}

            {/* Ручное добавление */}
            <Card className="bg-light">
              <Card.Body>
                <h6>Добавить специальность вручную</h6>
                <Row>
                  <Col md={3}>
                    <Form.Control
                      placeholder="Код (напр. 15.02.19)"
                      value={newSpecialty.code}
                      onChange={(e) => setNewSpecialty({ ...newSpecialty, code: e.target.value })}
                    />
                  </Col>
                  <Col md={4}>
                    <Form.Control
                      placeholder="Название"
                      value={newSpecialty.name}
                      onChange={(e) => setNewSpecialty({ ...newSpecialty, name: e.target.value })}
                    />
                  </Col>
                  <Col md={2}>
                    <Form.Control
                      type="number"
                      placeholder="Бюджет"
                      value={newSpecialty.budget_places || ''}
                      onChange={(e) =>
                        setNewSpecialty({ ...newSpecialty, budget_places: parseInt(e.target.value, 10) || 0 })
                      }
                    />
                  </Col>
                  <Col md={2}>
                    <Form.Control
                      type="number"
                      placeholder="Платные"
                      value={newSpecialty.paid_places || ''}
                      onChange={(e) =>
                        setNewSpecialty({ ...newSpecialty, paid_places: parseInt(e.target.value, 10) || 0 })
                      }
                    />
                  </Col>
                </Row>
                <Row className="mt-2">
                  <Col md={3}>
                    <Form.Control
                      placeholder="Длительность (напр. 3 г. 10 мес.)"
                      value={newSpecialty.duration}
                      onChange={(e) => setNewSpecialty({ ...newSpecialty, duration: e.target.value })}
                    />
                  </Col>
                  <Col md={7}>
                    <InputGroup>
                      <Form.Control
                        placeholder="Экзамены (через запятую или по одному)"
                        value={examInput}
                        onChange={(e) => setExamInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddExam();
                          }
                        }}
                      />
                      <Button variant="outline-secondary" onClick={handleAddExam}>
                        + Экзамен
                      </Button>
                    </InputGroup>
                    {newSpecialty.exams.length > 0 && (
                      <div className="mt-1">
                        {newSpecialty.exams.map((exam, idx) => (
                          <Badge key={idx} bg="info" className="me-1 mb-1">
                            {exam}
                            <Button
                              variant="link"
                              size="sm"
                              className="ms-1 p-0 text-white"
                              onClick={() => handleRemoveExam(idx)}
                              style={{ textDecoration: 'none' }}
                            >
                              ×
                            </Button>
                          </Badge>
                        ))}
                      </div>
                    )}
                  </Col>
                  <Col md={2}>
                    <Button variant="outline-primary" onClick={handleAddSpecialty}>
                      + Добавить
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Card.Body>
        </Card>

        {/* Способы подачи документов */}
        <Card className="mb-4 shadow-sm">
          <Card.Header>
            <Card.Title as="h5">Способы подачи документов</Card.Title>
          </Card.Header>
          <Card.Body>
            {formData.submission_methods.length > 0 && (
              <Table responsive striped size="sm" className="mb-3">
                <thead>
                  <tr>
                    <th>Название</th>
                    <th>Описание</th>
                    <th>Ссылка</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {formData.submission_methods.map((method, idx) => (
                    <tr key={idx}>
                      <td>
                        <Form.Control
                          size="sm"
                          value={method.title}
                          onChange={(e) => {
                            const updated = [...formData.submission_methods];
                            updated[idx] = { ...updated[idx], title: e.target.value };
                            setFormData({ ...formData, submission_methods: updated });
                          }}
                        />
                      </td>
                      <td>
                        <Form.Control
                          size="sm"
                          value={method.description}
                          onChange={(e) => {
                            const updated = [...formData.submission_methods];
                            updated[idx] = { ...updated[idx], description: e.target.value };
                            setFormData({ ...formData, submission_methods: updated });
                          }}
                        />
                      </td>
                      <td>
                        <Form.Control
                          size="sm"
                          value={method.link || ''}
                          onChange={(e) => {
                            const updated = [...formData.submission_methods];
                            updated[idx] = { ...updated[idx], link: e.target.value || null };
                            setFormData({ ...formData, submission_methods: updated });
                          }}
                        />
                      </td>
                      <td style={{ width: 90 }}>
                        <Button variant="outline-danger" size="sm" onClick={() => handleRemoveSubmissionMethod(idx)}>
                          ×
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}

            <Card className="bg-light">
              <Card.Body>
                <h6>Добавить способ подачи</h6>
                <Row>
                  <Col md={3}>
                    <Form.Control
                      placeholder="Название"
                      value={newSubmissionMethod.title}
                      onChange={(e) => setNewSubmissionMethod({ ...newSubmissionMethod, title: e.target.value })}
                    />
                  </Col>
                  <Col md={5}>
                    <Form.Control
                      placeholder="Описание"
                      value={newSubmissionMethod.description}
                      onChange={(e) => setNewSubmissionMethod({ ...newSubmissionMethod, description: e.target.value })}
                    />
                  </Col>
                  <Col md={3}>
                    <Form.Control
                      placeholder="Ссылка (необязательно)"
                      value={newSubmissionMethod.link || ''}
                      onChange={(e) => setNewSubmissionMethod({ ...newSubmissionMethod, link: e.target.value || null })}
                    />
                  </Col>
                  <Col md={1}>
                    <Button variant="outline-primary" onClick={handleAddSubmissionMethod}>
                      +
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Card.Body>
        </Card>

        {/* Важные даты */}
        <Card className="mb-4 shadow-sm">
          <Card.Header>
            <Card.Title as="h5">Важные даты</Card.Title>
          </Card.Header>
          <Card.Body>
            {formData.important_dates.length > 0 && (
              <Table responsive striped size="sm" className="mb-3">
                <thead>
                  <tr>
                    <th>Событие</th>
                    <th>Дата</th>
                    <th>Описание</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {formData.important_dates.map((date, idx) => (
                    <tr key={idx}>
                      <td>
                        <Form.Control
                          size="sm"
                          value={date.title}
                          onChange={(e) => {
                            const updated = [...formData.important_dates];
                            updated[idx] = { ...updated[idx], title: e.target.value };
                            setFormData({ ...formData, important_dates: updated });
                          }}
                        />
                      </td>
                      <td>
                        <Form.Control
                          type="datetime-local"
                          size="sm"
                          value={typeof date.date === 'string' && date.date.includes('T')
                            ? date.date.slice(0, 16)
                            : date.date}
                          onChange={(e) => {
                            const updated = [...formData.important_dates];
                            updated[idx] = { ...updated[idx], date: e.target.value };
                            setFormData({ ...formData, important_dates: updated });
                          }}
                        />
                      </td>
                      <td>
                        <Form.Control
                          size="sm"
                          value={date.description || ''}
                          onChange={(e) => {
                            const updated = [...formData.important_dates];
                            updated[idx] = { ...updated[idx], description: e.target.value || null };
                            setFormData({ ...formData, important_dates: updated });
                          }}
                        />
                      </td>
                      <td style={{ width: 90 }}>
                        <Button variant="outline-danger" size="sm" onClick={() => handleRemoveImportantDate(idx)}>
                          ×
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}

            <Card className="bg-light">
              <Card.Body>
                <h6>Добавить дату</h6>
                <Row>
                  <Col md={4}>
                    <Form.Control
                      placeholder="Название события"
                      value={newImportantDate.title}
                      onChange={(e) => setNewImportantDate({ ...newImportantDate, title: e.target.value })}
                    />
                  </Col>
                  <Col md={3}>
                    <Form.Control
                      type="datetime-local"
                      value={newImportantDate.date}
                      onChange={(e) => setNewImportantDate({ ...newImportantDate, date: e.target.value })}
                    />
                  </Col>
                  <Col md={4}>
                    <Form.Control
                      placeholder="Описание (необязательно)"
                      value={newImportantDate.description || ''}
                      onChange={(e) => setNewImportantDate({ ...newImportantDate, description: e.target.value || null })}
                    />
                  </Col>
                  <Col md={1}>
                    <Button variant="outline-primary" onClick={handleAddImportantDate}>
                      +
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Card.Body>
        </Card>

        <div className="d-flex gap-2">
          <Button variant="primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? <Spinner animation="border" size="sm" /> : null}{' '}
            {isEdit ? 'Сохранить изменения' : 'Создать кампанию'}
          </Button>
          <Button variant="secondary" as={Link as any} to="/admission">
            Отмена
          </Button>
        </div>
      </Form>

      {/* Модальное окно выбора специальностей из справочника */}
      <Modal show={showSpecialtyPicker} onHide={() => setShowSpecialtyPicker(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>📋 Выбрать специальности из справочника</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="d-flex justify-content-between mb-3">
            <div>
              <Badge bg="primary">{selectedSpecialtyCodes.size} выбрано</Badge>
            </div>
            <div>
              <Button variant="outline-secondary" size="sm" className="me-2" onClick={selectAllSpecialties}>
                Выбрать все
              </Button>
              <Button variant="outline-secondary" size="sm" onClick={clearSelection}>
                Сбросить
              </Button>
            </div>
          </div>

          {specialties.length === 0 ? (
            <Alert variant="warning">Справочник специальностей пуст</Alert>
          ) : (
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {specialties.map((spec) => {
                const isSelected = selectedSpecialtyCodes.has(spec.code);
                const alreadyAdded = formData.specialties_admission.some((s) => s.code === spec.code);

                return (
                  <Card
                    key={spec.code}
                    className={`mb-2 ${alreadyAdded ? 'bg-light' : ''} ${isSelected ? 'border-primary' : ''}`}
                    style={{ cursor: alreadyAdded ? 'default' : 'pointer' }}
                    onClick={() => {
                      if (!alreadyAdded) {
                        toggleSpecialtySelection(spec.code);
                      }
                    }}
                  >
                    <Card.Body className="py-2 px-3">
                      <div className="d-flex align-items-center">
                        <Form.Check
                          type="checkbox"
                          checked={isSelected}
                          disabled={alreadyAdded}
                          onChange={() => toggleSpecialtySelection(spec.code)}
                          className="me-3"
                        />
                        <div className="flex-grow-1">
                          <strong>{spec.code}</strong> — {spec.name}
                          {alreadyAdded && (
                            <Badge bg="secondary" className="ms-2">
                              уже добавлена
                            </Badge>
                          )}
                          {spec.education_options && spec.education_options.length > 0 && (
                            <div className="text-muted small">
                              {spec.education_options.map((eo, idx) => (
                                <span key={idx} className="me-3">
                                  {eo.education_level}: бюджет {eo.budget_places}, платные {eo.paid_places}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                );
              })}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowSpecialtyPicker(false)}>
            Отмена
          </Button>
          <Button
            variant="primary"
            onClick={handleAddFromDirectory}
            disabled={selectedSpecialtyCodes.size === 0}
          >
            Добавить ({selectedSpecialtyCodes.size})
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
