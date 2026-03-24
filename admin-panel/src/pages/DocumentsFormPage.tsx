import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import type { Image, Document } from '../types';

export default function DocumentFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    title: '',
    category: 'general',
    file_url: '',
    file_size: undefined as number | undefined,
    images: [] as Image[],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);

  useEffect(() => {
    if (isEdit) {
      loadDocument();
    }
  }, [id]);

  const loadDocument = async () => {
    try {
      const doc = await apiService.getDocumentById(Number(id));
      setFormData({
        title: doc.title,
        category: doc.category,
        file_url: doc.file_url,
        file_size: doc.file_size || undefined,
        images: doc.images || [],
      });
    } catch (err) {
      setError('Не удалось загрузить документ: ' + (err instanceof Error ? err.message : 'Неизвестная ошибка'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingFile(true);
    setError(null);

    try {
      const response = await apiService.uploadDocument(file, formData.category);
      setFormData({
        ...formData,
        file_url: response.url,
        file_size: response.size,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при загрузке файла');
    } finally {
      setUploadingFile(false);
      e.target.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (isEdit) {
        await apiService.updateDocument(Number(id), formData);
      } else {
        await apiService.createDocument(formData);
      }
      navigate('/documents');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    const newImage: Image = { url: imageUrl, alt: 'Изображение документа' };
    setFormData({ ...formData, images: [...formData.images, newImage] });
    setShowImagePicker(false);
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
        <h2>{isEdit ? 'Редактирование документа' : 'Новый документ'}</h2>
        <Button variant="secondary" as={Link} to="/documents">
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
                  <Form.Label>Название *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    placeholder="Название документа"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Категория *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    required
                    placeholder="general"
                  />
                  <Form.Text className="text-muted">
                    Например: general, admission, studies
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Файл *</Form.Label>
              {formData.file_url ? (
                <div className="mb-2">
                  <Alert variant="success" className="mb-2">
                    ✓ Файл загружен: {formData.file_url}
                  </Alert>
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => setFormData({ ...formData, file_url: '', file_size: undefined })}
                  >
                    Удалить файл
                  </Button>
                </div>
              ) : (
                <>
                  <Form.Control
                    type="file"
                    onChange={handleFileUpload}
                    disabled={uploadingFile}
                  />
                  {uploadingFile && (
                    <Spinner animation="border" size="sm" className="ms-2" />
                  )}
                  <Form.Text className="text-muted">
                    Загрузите файл документа (PDF, DOC, DOCX)
                  </Form.Text>
                </>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Изображения</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setShowImagePicker(true)}
                >
                  Выбрать изображение
                </Button>
              </div>
              <div className="mt-2">
                {formData.images.map((img: Image, index: number) => (
                  <div key={index} className="d-inline-block me-2 position-relative">
                    <img
                      src={img.url}
                      alt={img.alt || ''}
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
              <Button variant="success" type="submit" disabled={isSubmitting || !formData.file_url}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link} to="/documents">
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
