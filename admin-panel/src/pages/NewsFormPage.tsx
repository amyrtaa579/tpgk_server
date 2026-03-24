import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import TextArrayEditor from '../components/TextArrayEditor';
import type { Image } from '../types';

export default function NewsFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    preview_text: '',
    content: [] as string[],
    preview_image: '',
    gallery: [] as Image[],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [imagePickerTarget, setImagePickerTarget] = useState<'preview' | 'gallery'>('preview');

  useEffect(() => {
    if (isEdit) {
      loadNews();
    }
  }, [id]);

  const loadNews = async () => {
    try {
      const news = await apiService.getNewsById(Number(id));
      setFormData({
        title: news.title,
        slug: news.slug,
        preview_text: news.preview_text,
        content: news.content,
        preview_image: news.preview_image || '',
        gallery: news.gallery || [],
      });
    } catch (err) {
      setError('Не удалось загрузить новость: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
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
      formFormData.append('title', formData.title);
      formFormData.append('slug', formData.slug);
      formFormData.append('preview_text', formData.preview_text);
      formFormData.append('content', JSON.stringify(formData.content));
      formFormData.append('preview_image', formData.preview_image);
      formFormData.append('gallery', JSON.stringify(formData.gallery));

      if (isEdit) {
        await apiService.updateNews(Number(id), formFormData);
      } else {
        await apiService.createNews(formFormData);
      }
      navigate('/news');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    if (imagePickerTarget === 'preview') {
      setFormData({ ...formData, preview_image: imageUrl });
    } else {
      const newImage: Image = { url: imageUrl, alt: 'Изображение галереи', thumbnail: imageUrl };
      setFormData({ ...formData, gallery: [...formData.gallery, newImage] });
    }
    setShowImagePicker(false);
  };

  const handleRemoveGalleryImage = (index: number) => {
    setFormData({ ...formData, gallery: formData.gallery.filter((_, i) => i !== index) });
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
        <h2>{isEdit ? 'Редактирование новости' : 'Новая новость'}</h2>
        <Button variant="secondary" as={Link} to="/news">
          Назад к списку
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Заголовок *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    placeholder="Заголовок новости"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Slug *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.slug}
                    onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                    required
                    placeholder="novost-1"
                  />
                  <Form.Text className="text-muted">
                    URL-адрес новости (латиница)
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Текст для превью</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.preview_text}
                onChange={(e) => setFormData({ ...formData, preview_text: e.target.value })}
                placeholder="Краткое описание новости"
              />
            </Form.Group>

            <TextArrayEditor
              value={formData.content}
              onChange={(content) => setFormData({ ...formData, content })}
              label="Содержимое новости"
              placeholder="Добавить абзац"
              addButtonText="Добавить абзац"
            />

            <Form.Group className="mb-3">
              <Form.Label>Изображение превью</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  className="me-2"
                  onClick={() => {
                    setImagePickerTarget('preview');
                    setShowImagePicker(true);
                  }}
                >
                  Выбрать изображение
                </Button>
              </div>
              <Form.Text className="text-muted d-block mb-2">
                Нажмите "Выбрать изображение" для загрузки или выбора из галереи/MinIO
              </Form.Text>
              {formData.preview_image && (
                <div className="mt-2 position-relative d-inline-block">
                  <img
                    src={formData.preview_image}
                    alt="Preview"
                    style={{ width: '200px', height: '150px', objectFit: 'cover', borderRadius: '4px' }}
                  />
                  <Button
                    variant="danger"
                    size="sm"
                    className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                    onClick={() => setFormData({ ...formData, preview_image: '' })}
                  >
                    ×
                  </Button>
                </div>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Галерея</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  className="me-2"
                  onClick={() => {
                    setImagePickerTarget('gallery');
                    setShowImagePicker(true);
                  }}
                >
                  Выбрать изображение
                </Button>
              </div>
              <Form.Text className="text-muted d-block mb-2">
                Нажмите "Выбрать изображение" для загрузки или выбора из галереи/MinIO
              </Form.Text>
              <div className="mt-2">
                {formData.gallery.map((img: Image, index: number) => (
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
                      onClick={() => handleRemoveGalleryImage(index)}
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
              <Button variant="secondary" as={Link} to="/news">
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
