import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';

export default function GalleryFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    url: '',
    thumbnail: '',
    alt: '',
    category: 'common',
    caption: '',
    date_taken: new Date().toISOString().split('T')[0],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);

  useEffect(() => {
    if (isEdit) {
      loadImage();
    }
  }, [id]);

  const loadImage = async () => {
    try {
      const image = await apiService.getGalleryImage(Number(id));
      setFormData({
        url: image.url,
        thumbnail: image.thumbnail || image.url,
        alt: image.alt,
        category: image.category,
        caption: image.caption || '',
        date_taken: image.date_taken ? image.date_taken.split('T')[0] : new Date().toISOString().split('T')[0],
      });
    } catch {
      setError('Не удалось загрузить изображение');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const imageData = {
        url: formData.url,
        thumbnail: formData.thumbnail || formData.url,
        alt: formData.alt,
        category: formData.category,
        caption: formData.caption || null,
        date_taken: formData.date_taken ? new Date(formData.date_taken).toISOString() : null,
      };

      if (isEdit) {
        await apiService.updateGalleryImage(Number(id), imageData);
      } else {
        await apiService.createGalleryImage(imageData);
      }
      navigate('/gallery');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    setFormData({
      ...formData,
      url: imageUrl,
      thumbnail: imageUrl,
      alt: imageUrl.split('/').pop() || 'Изображение',
    });
    setShowImagePicker(false);
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
        <h2>{isEdit ? 'Редактирование изображения' : 'Добавить изображение в галерею'}</h2>
        <Button variant="secondary" as={Link as any} to="/gallery">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>URL изображения *</Form.Label>
              <div className="d-flex gap-2 mb-2">
                <Form.Control
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  placeholder="https://..."
                  readOnly
                />
                <Button
                  variant="outline-primary"
                  onClick={() => setShowImagePicker(true)}
                >
                  Выбрать изображение
                </Button>
              </div>
              <Form.Text className="text-muted">
                Загрузите файл через кнопку "Выбрать изображение" или вставьте URL
              </Form.Text>
              {formData.url && (
                <div className="mt-2">
                  <img
                    src={formData.url}
                    alt="Preview"
                    style={{ maxWidth: '300px', maxHeight: '200px', borderRadius: '4px' }}
                  />
                </div>
              )}
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>URL превью</Form.Label>
                  <Form.Control
                    type="url"
                    value={formData.thumbnail}
                    onChange={(e) => setFormData({ ...formData, thumbnail: e.target.value })}
                    placeholder="https://..."
                  />
                  <Form.Text className="text-muted">
                    Если не указано, используется основное изображение
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Категория *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    required
                    placeholder="common"
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Alt текст *</Form.Label>
              <Form.Control
                type="text"
                value={formData.alt}
                onChange={(e) => setFormData({ ...formData, alt: e.target.value })}
                required
                placeholder="Описание изображения"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Caption (подпись)</Form.Label>
              <Form.Control
                type="text"
                value={formData.caption}
                onChange={(e) => setFormData({ ...formData, caption: e.target.value })}
                placeholder="Подпись к изображению"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Дата съёмки</Form.Label>
              <Form.Control
                type="date"
                value={formData.date_taken}
                onChange={(e) => setFormData({ ...formData, date_taken: e.target.value })}
              />
            </Form.Group>

            <div className="d-flex gap-2">
              <Button variant="primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link as any} to="/gallery">
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
        hideGalleryTab={true}
      />
    </div>
  );
}
