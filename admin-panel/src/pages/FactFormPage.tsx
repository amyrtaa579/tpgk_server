import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import TextArrayEditor from '../components/TextArrayEditor';
import type { Image } from '../types';

export default function FactFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    specialty_code: '',
    title: '',
    description: [] as string[],
    images: [] as Image[],
  });

  const [specialties, setSpecialties] = useState<{ id: number; code: string; name: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      await loadSpecialties();
      if (isEdit && id) {
        await loadFact(id);
      }
    };
    loadData();
  }, [isEdit, id]);

  const loadSpecialties = async () => {
    try {
      const response = await apiService.getSpecialties(1, 100);
      setSpecialties(response.items);
      if (response.items.length > 0 && !isEdit) {
        setFormData((prev) => ({ ...prev, specialty_code: response.items[0].code }));
      }
    } catch (err) {
      console.error('Ошибка загрузки специальностей:', err);
      setError('Не удалось загрузить список специальностей');
    }
  };

  const loadFact = async (factId: string) => {
    try {
      console.log('Загрузка факта ID:', factId);
      const response = await apiService.getFact(Number(factId));
      console.log('Факт загружен:', response);
      setFormData({
        specialty_code: response.specialty_code,
        title: response.title,
        description: response.description || [],
        images: response.images || [],
      });
    } catch (err) {
      console.error('Ошибка загрузки факта:', err);
      setError('Не удалось загрузить факт: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
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
      formFormData.append('specialty_code', formData.specialty_code);
      formFormData.append('title', formData.title);
      formFormData.append('description', JSON.stringify(formData.description));
      formFormData.append('images', JSON.stringify(formData.images));

      if (isEdit) {
        await apiService.updateFact(Number(id), formFormData);
      } else {
        await apiService.createFact(formFormData);
      }
      navigate('/facts');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    const newImage: Image = { url: imageUrl, alt: 'Изображение факта' };
    setFormData({ ...formData, images: [...formData.images, newImage] });
    setShowImagePicker(false);
  };

  const handleRemoveImage = (index: number) => {
    setFormData({ ...formData, images: formData.images.filter((_, i) => i !== index) });
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{isEdit ? 'Редактирование факта' : 'Новый интересный факт'}</h2>
        <Button variant="secondary" as={Link} to="/facts">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {isLoading ? (
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
          <Spinner animation="border" variant="primary" />
        </div>
      ) : (

      <Card className="shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Специальность *</Form.Label>
              <Form.Select
                value={formData.specialty_code}
                onChange={(e) => setFormData({ ...formData, specialty_code: e.target.value })}
                required
              >
                {specialties.map((spec) => (
                  <option key={spec.id} value={spec.code}>
                    {spec.code} — {spec.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Заголовок *</Form.Label>
              <Form.Control
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                placeholder="Заголовок факта"
              />
            </Form.Group>

            <TextArrayEditor
              value={formData.description}
              onChange={(desc) => setFormData({ ...formData, description: desc })}
              label="Описание факта"
              placeholder="Добавить пункт описания"
              addButtonText="Добавить пункт"
            />

            <Form.Group className="mb-3">
              <Form.Label>Изображения</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  className="me-2"
                  onClick={() => setShowImagePicker(true)}
                >
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

            <div className="d-flex gap-2">
              <Button variant="info" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link} to="/facts">
                Отмена
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
      )}

      <MinioImagePicker
        show={showImagePicker}
        onHide={() => setShowImagePicker(false)}
        onSelect={handleImageSelect}
        hideMinioTab={true}
      />
    </div>
  );
}
