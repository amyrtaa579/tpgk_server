import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col, Badge, InputGroup } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import TextArrayEditor from '../components/TextArrayEditor';
import type { Image } from '../types';

export default function SpecialtyFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    code: '',
    name: '',
    short_description: '',
    description: [] as string[],
    duration: '',
    budget_places: 0,
    paid_places: 0,
    qualification: '',
    exams: [] as string[],
    images: [] as Image[],
    is_popular: false,
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [newExam, setNewExam] = useState('');

  useEffect(() => {
    if (isEdit) {
      loadSpecialty();
    }
  }, [id]);

  const loadSpecialty = async () => {
    try {
      const specialty = await apiService.getSpecialtyById(Number(id));
      setFormData({
        code: specialty.code,
        name: specialty.name,
        short_description: specialty.short_description,
        description: specialty.description,
        duration: specialty.duration,
        budget_places: specialty.budget_places,
        paid_places: specialty.paid_places,
        qualification: specialty.qualification,
        exams: specialty.exams,
        images: specialty.images || [],
        is_popular: specialty.is_popular,
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
      const formFormData = new FormData();
      formFormData.append('code', formData.code);
      formFormData.append('name', formData.name);
      formFormData.append('short_description', formData.short_description);
      formFormData.append('description', JSON.stringify(formData.description));
      formFormData.append('duration', formData.duration);
      formFormData.append('budget_places', formData.budget_places.toString());
      formFormData.append('paid_places', formData.paid_places.toString());
      formFormData.append('qualification', formData.qualification);
      formFormData.append('exams', JSON.stringify(formData.exams));
      formFormData.append('images', JSON.stringify(formData.images));
      formFormData.append('is_popular', formData.is_popular.toString());

      if (isEdit) {
        await apiService.updateSpecialty(Number(id), formFormData);
      } else {
        await apiService.createSpecialty(formFormData);
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
  };

  const handleRemoveImage = (index: number) => {
    setFormData({ ...formData, images: formData.images.filter((_, i) => i !== index) });
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
        <Button variant="secondary" as={Link} to="/specialties">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
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
                    placeholder="09.02.07"
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
                    placeholder="Информационные системы и программирование"
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
                placeholder="Краткое описание специальности"
              />
            </Form.Group>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Срок обучения</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.duration}
                    onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                    placeholder="3 года 10 месяцев"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Бюджетных мест</Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.budget_places}
                    onChange={(e) => setFormData({ ...formData, budget_places: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Платных мест</Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.paid_places}
                    onChange={(e) => setFormData({ ...formData, paid_places: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Квалификация</Form.Label>
              <Form.Control
                type="text"
                value={formData.qualification}
                onChange={(e) => setFormData({ ...formData, qualification: e.target.value })}
                placeholder="Техник-программист"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Экзамены</Form.Label>
              <div className="mb-2">
                {formData.exams.map((exam, index) => (
                  <Badge key={index} bg="primary" className="me-1 mb-1">
                    {exam}
                    <button
                      type="button"
                      className="btn-close btn-close-white ms-2"
                      style={{ fontSize: '8px' }}
                      onClick={() => handleRemoveExam(index)}
                    />
                  </Badge>
                ))}
              </div>
              <InputGroup>
                <Form.Control
                  type="text"
                  value={newExam}
                  onChange={(e) => setNewExam(e.target.value)}
                  placeholder="Добавить экзамен"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddExam())}
                />
                <Button variant="outline-primary" onClick={handleAddExam}>
                  Добавить
                </Button>
              </InputGroup>
            </Form.Group>

            <TextArrayEditor
              value={formData.description}
              onChange={(desc) => setFormData({ ...formData, description: desc })}
              label="Полное описание"
              placeholder="Добавить пункт описания"
              addButtonText="Добавить пункт"
            />

            <Form.Group className="mb-3">
              <Form.Label>Изображения</Form.Label>
              <div className="mb-2">
                <Button variant="outline-primary" size="sm" onClick={() => setShowImagePicker(true)}>
                  Выбрать изображение
                </Button>
              </div>
              <Form.Text className="text-muted d-block mb-2">
                Нажмите "Выбрать изображение" для загрузки или выбора из галереи/MinIO
              </Form.Text>
              <div className="mt-2">
                {formData.images.map((img: Image, index: number) => (
                  <div key={index} className="d-inline-block me-2 position-relative">
                    <img
                      src={img.url}
                      alt={img.alt}
                      style={{ width: '100px', height: '100px', objectFit: 'cover', borderRadius: '4px' }}
                    />
                    <Button
                      variant="danger"
                      size="sm"
                      className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                      onClick={() => handleRemoveImage(index)}
                    >
                      ×
                    </Button>
                  </div>
                ))}
              </div>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="popular-switch"
                label="Популярная специальность"
                checked={formData.is_popular}
                onChange={(e) => setFormData({ ...formData, is_popular: e.target.checked })}
              />
            </Form.Group>

            <div className="d-flex gap-2">
              <Button variant="primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link} to="/specialties">
                Отмена
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      <MinioImagePicker
        show={showImagePicker}
        onHide={() => setShowImagePicker(false)}
        onSelect={handleImageSelect}
        hideMinioTab={true}
      />
    </div>
  );
}
