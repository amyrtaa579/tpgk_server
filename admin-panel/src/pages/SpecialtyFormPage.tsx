import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col, Badge, InputGroup } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService, fixMinioUrls } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import MinioDocumentPicker from '../components/MinioDocumentPicker';
import TextArrayEditor from '../components/TextArrayEditor';
import type { Image } from '../types';

interface EducationOption {
  id?: number;
  education_level: string;
  duration: string;
  budget_places: number;
  paid_places: number;
}

export default function SpecialtyFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    code: '',
    name: '',
    short_description: '',
    description: [] as string[],
    exams: [] as string[],
    images: [] as Image[],
    documents: [] as Image[],
    education_options: [] as EducationOption[],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [showDocumentPicker, setShowDocumentPicker] = useState(false);
  const [newExam, setNewExam] = useState('');

  useEffect(() => {
    if (isEdit) {
      loadSpecialty();
    }
  }, [id]);

  const loadSpecialty = async () => {
    try {
      const specialty = await apiService.getSpecialtyById(Number(id));
      
      // Преобразуем description из строки в массив, если нужно
      let description = specialty.description || [];
      if (typeof description === 'string') {
        try {
          description = JSON.parse(description);
        } catch {
          description = [];
        }
      }
      
      // Преобразуем exams из строки в массив, если нужно
      let exams = specialty.exams || [];
      if (typeof exams === 'string') {
        try {
          exams = JSON.parse(exams);
        } catch {
          exams = [];
        }
      }
      
      setFormData({
        code: specialty.code,
        name: specialty.name,
        short_description: specialty.short_description || '',
        description: description,
        exams: exams,
        images: fixMinioUrls(specialty.images || []),
        documents: fixMinioUrls(specialty.documents || []),
        education_options: specialty.education_options || [],
      });
    } catch (err) {
      setError('Не удалось загрузить специальность: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        ...formData,
        description: JSON.stringify(formData.description),
        exams: JSON.stringify(formData.exams),
        images: JSON.stringify(formData.images),
        documents: JSON.stringify(formData.documents),
        education_options: JSON.stringify(formData.education_options),
      };

      if (isEdit) {
        await apiService.updateSpecialty(Number(id), payload);
      } else {
        await apiService.createSpecialty(payload);
      }
      navigate('/specialties');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddExam = () => {
    if (newExam.trim()) {
      setFormData({ ...formData, exams: [...formData.exams, newExam.trim()] });
      setNewExam('');
    }
  };

  const handleRemoveExam = (index: number) => {
    setFormData({ ...formData, exams: formData.exams.filter((_, i) => i !== index) });
  };

  const handleImageSelect = (imageUrl: string) => {
    const newImage: Image = { url: imageUrl, alt: 'Изображение специальности' };
    setFormData({ ...formData, images: [...formData.images, newImage] });
    setShowImagePicker(false);
  };

  const handleDocumentSelect = (documentUrl: string, title: string) => {
    const newDoc: Image = { url: documentUrl, alt: title };
    setFormData({ ...formData, documents: [...formData.documents, newDoc] });
    setShowDocumentPicker(false);
  };

  const handleRemoveImage = (index: number) => {
    setFormData({ ...formData, images: formData.images.filter((_, i) => i !== index) });
  };

  const handleRemoveDocument = (index: number) => {
    setFormData({ ...formData, documents: formData.documents.filter((_, i) => i !== index) });
  };

  // Управление уровнями образования
  const handleAddEducationOption = () => {
    setFormData({
      ...formData,
      education_options: [
        ...formData.education_options,
        { education_level: 'Основное общее', duration: '', budget_places: 0, paid_places: 0 },
      ],
    });
  };

  const handleRemoveEducationOption = (index: number) => {
    setFormData({
      ...formData,
      education_options: formData.education_options.filter((_, i) => i !== index),
    });
  };

  const handleUpdateEducationOption = (index: number, field: keyof EducationOption, value: any) => {
    const newOptions = [...formData.education_options];
    newOptions[index] = { ...newOptions[index], [field]: value };
    setFormData({ ...formData, education_options: newOptions });
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
        <h2>{isEdit ? 'Редактирование специальности' : 'Новая специальность'}</h2>
        <Button variant="secondary" as={Link as any} to="/specialties">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-primary text-white">
          <Card.Title className="mb-0">📚 Основная информация</Card.Title>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Код специальности *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    required
                    placeholder="15.02.19"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Название *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    placeholder="Сварочное производство"
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Краткое описание</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={formData.short_description}
                onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                placeholder="Краткая информация о специальности"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Полное описание (список)</Form.Label>
              <TextArrayEditor
                value={formData.description}
                onChange={(items) => setFormData({ ...formData, description: items })}
                placeholder="Добавьте пункт описания"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Экзамены</Form.Label>
              <InputGroup className="mb-2">
                <Form.Control
                  type="text"
                  value={newExam}
                  onChange={(e) => setNewExam(e.target.value)}
                  placeholder="Введите экзамен"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddExam())}
                />
                <Button variant="outline-primary" onClick={handleAddExam}>
                  Добавить
                </Button>
              </InputGroup>
              <div className="d-flex flex-wrap gap-2">
                {formData.exams.map((exam, index) => (
                  <Badge key={index} bg="primary" className="px-3 py-2">
                    {exam}
                    <button
                      type="button"
                      className="btn-close btn-close-white ms-2"
                      aria-label="Remove"
                      onClick={() => handleRemoveExam(index)}
                      style={{ fontSize: '10px' }}
                    />
                  </Badge>
                ))}
              </div>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Изображения</Form.Label>
              <div className="mb-2">
                <Button variant="outline-primary" size="sm" onClick={() => setShowImagePicker(true)}>
                  Добавить изображение
                </Button>
              </div>
              <Row>
                {formData.images.map((img, index) => (
                  <Col key={index} xs={4} md={3} className="mb-2">
                    <div className="position-relative">
                      <img
                        src={img.url}
                        alt={img.alt}
                        className="img-fluid rounded"
                        style={{ width: '100%', height: '150px', objectFit: 'cover' }}
                      />
                      <Button
                        variant="danger"
                        size="sm"
                        className="position-absolute top-0 end-0 m-1 rounded-circle p-1"
                        onClick={() => handleRemoveImage(index)}
                      >
                        ×
                      </Button>
                    </div>
                  </Col>
                ))}
              </Row>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Документы</Form.Label>
              <div className="mb-2">
                <Button variant="outline-primary" size="sm" onClick={() => setShowDocumentPicker(true)}>
                  Добавить документ
                </Button>
              </div>
              <Row>
                {formData.documents.map((doc, index) => (
                  <Col key={index} xs={4} md={3} className="mb-2">
                    <div className="position-relative">
                      <div
                        className="d-flex align-items-center justify-content-center bg-light border rounded"
                        style={{ height: '150px' }}
                      >
                        <span style={{ fontSize: '48px' }}>📄</span>
                      </div>
                      <div className="text-center mt-1" style={{ fontSize: '12px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {doc.alt}
                      </div>
                      <Button
                        variant="danger"
                        size="sm"
                        className="position-absolute top-0 end-0 m-1 rounded-circle p-1"
                        onClick={() => handleRemoveDocument(index)}
                      >
                        ×
                      </Button>
                    </div>
                  </Col>
                ))}
              </Row>
            </Form.Group>

            <div className="d-flex gap-2">
              <Button variant="success" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link as any} to="/specialties">
                Отмена
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      {/* Уровни образования */}
      <Card className="shadow-sm">
        <Card.Header className="bg-success text-white">
          <Card.Title className="mb-0">🎓 Уровни образования</Card.Title>
        </Card.Header>
        <Card.Body>
          <Alert variant="info" className="mb-3">
            <strong>Информация:</strong> Добавьте один или два уровня образования (Основное общее и/или Среднее общее).
            Для каждого уровня укажите срок обучения и количество мест.
          </Alert>

          {formData.education_options.map((option, index) => (
            <Card key={index} className="mb-3 border-secondary">
              <Card.Header className="d-flex justify-content-between align-items-center">
                <strong>Уровень {index + 1}</strong>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => handleRemoveEducationOption(index)}
                  disabled={formData.education_options.length <= 1}
                >
                  Удалить
                </Button>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Уровень образования *</Form.Label>
                      <Form.Select
                        value={option.education_level}
                        onChange={(e) => handleUpdateEducationOption(index, 'education_level', e.target.value)}
                      >
                        <option value="Основное общее">Основное общее (9 классов)</option>
                        <option value="Среднее общее">Среднее общее (11 классов)</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Срок обучения *</Form.Label>
                      <Form.Control
                        type="text"
                        value={option.duration}
                        onChange={(e) => handleUpdateEducationOption(index, 'duration', e.target.value)}
                        placeholder="3 г. 10 мес."
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Бюджетных мест</Form.Label>
                      <Form.Control
                        type="number"
                        value={option.budget_places}
                        onChange={(e) => handleUpdateEducationOption(index, 'budget_places', parseInt(e.target.value) || 0)}
                        min="0"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Платных мест</Form.Label>
                      <Form.Control
                        type="number"
                        value={option.paid_places}
                        onChange={(e) => handleUpdateEducationOption(index, 'paid_places', parseInt(e.target.value) || 0)}
                        min="0"
                      />
                    </Form.Group>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          ))}

          <Button variant="outline-success" onClick={handleAddEducationOption}>
            + Добавить уровень образования
          </Button>
        </Card.Body>
      </Card>

      <MinioImagePicker
        show={showImagePicker}
        onHide={() => setShowImagePicker(false)}
        onSelect={handleImageSelect}
        hideMinioTab={true}
      />

      <MinioDocumentPicker
        show={showDocumentPicker}
        onHide={() => setShowDocumentPicker(false)}
        onSelect={handleDocumentSelect}
      />
    </div>
  );
}
