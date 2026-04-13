import { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import MinioImagePicker from '../components/MinioImagePicker';
import MinioDocumentPicker from '../components/MinioDocumentPicker';
import TextArrayEditor from '../components/TextArrayEditor';
import type { Image, FAQ } from '../types';

export default function FaqFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    question: '',
    answer: [] as string[],
    category: 'general',
    show_in_admission: false,
    images: [] as Image[],
    documents: [] as Image[],
    document_file_ids: [] as number[],
  });

  const [isLoading, setIsLoading] = useState(isEdit);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [showDocumentPicker, setShowDocumentPicker] = useState(false);

  useEffect(() => {
    if (isEdit) {
      loadFaq();
    }
  }, [id]);

  const loadFaq = async () => {
    try {
      const faq = await apiService.getFaqById(Number(id));
      setFormData({
        question: faq.question,
        answer: Array.isArray(faq.answer) ? faq.answer : [faq.answer],
        category: faq.category,
        show_in_admission: faq.show_in_admission,
        images: faq.images || [],
        documents: faq.documents || [],
        document_file_ids: faq.document_file_ids || [],
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

    try {
      const payload = {
        ...formData,
        answer: formData.answer.length === 1 ? formData.answer[0] : formData.answer,
      };

      if (isEdit) {
        await apiService.updateFaq(Number(id), payload);
      } else {
        await apiService.createFaq(payload);
      }
      navigate('/faq');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    const newImage: Image = { url: imageUrl, alt: 'Изображение FAQ' };
    setFormData({ ...formData, images: [...formData.images, newImage] });
    setShowImagePicker(false);
  };

  const handleRemoveImage = (index: number) => {
    setFormData({ ...formData, images: formData.images.filter((_, i) => i !== index) });
  };

  const handleDocumentSelect = (documentUrl: string, title: string, docId?: number) => {
    if (docId) {
      // Документ из галереи — добавляем ID
      if (!formData.document_file_ids.includes(docId)) {
        setFormData({ ...formData, document_file_ids: [...formData.document_file_ids, docId] });
      }
    } else {
      // Прямая загрузка — добавляем как документ
      const newDoc: Image = { url: documentUrl, alt: title };
      setFormData({ ...formData, documents: [...formData.documents, newDoc] });
    }
    setShowDocumentPicker(false);
  };

  const handleRemoveDocument = (index: number, type: 'document' | 'file') => {
    if (type === 'document') {
      setFormData({ ...formData, documents: formData.documents.filter((_, i) => i !== index) });
    } else {
      setFormData({ ...formData, document_file_ids: formData.document_file_ids.filter((_, i) => i !== index) });
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
        <h2>{isEdit ? 'Редактирование вопроса' : 'Новый вопрос'}</h2>
        <Button variant="secondary" as={Link as any} to="/faq">
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
                  <Form.Label>Вопрос *</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={formData.question}
                    onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                    required
                    placeholder="Введите вопрос"
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
              <Form.Label>Ответ *</Form.Label>
              <TextArrayEditor
                value={formData.answer}
                onChange={(answer) => setFormData({ ...formData, answer })}
                label=""
                placeholder="Добавить абзац ответа"
                addButtonText="Добавить абзац"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Показывать в приёмной комиссии"
                checked={formData.show_in_admission}
                onChange={(e) => setFormData({ ...formData, show_in_admission: e.target.checked })}
              />
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

            <Form.Group className="mb-3">
              <Form.Label>Документы</Form.Label>
              <div className="mb-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setShowDocumentPicker(true)}
                >
                  Добавить документ
                </Button>
                <Form.Text className="text-muted d-block mt-1">
                  Можно загрузить файл или выбрать из галереи документов
                </Form.Text>
              </div>

              {/* Загруженные документы (прямая загрузка) */}
              {formData.documents.length > 0 && (
                <div className="mb-3">
                  <Form.Label className="text-muted small">Загруженные файлы:</Form.Label>
                  <div>
                    {formData.documents.map((doc: Image, index: number) => (
                      <div key={`doc-${index}`} className="d-inline-block me-2 position-relative mb-2">
                        <div
                          className="d-flex align-items-center justify-content-center bg-light border rounded"
                          style={{ width: '100px', height: '100px', borderRadius: '4px' }}
                        >
                          <span style={{ fontSize: '24px' }}>📄</span>
                        </div>
                        <div className="text-center" style={{ fontSize: '12px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {doc.alt}
                        </div>
                        <Button
                          variant="danger"
                          size="sm"
                          className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                          onClick={() => handleRemoveDocument(index, 'document')}
                        >
                          ×
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Документы из галереи */}
              {formData.document_file_ids.length > 0 && (
                <div>
                  <Form.Label className="text-muted small">Из галереи документов:</Form.Label>
                  <div>
                    {formData.document_file_ids.map((fileId: number, index: number) => (
                      <div key={`file-${index}`} className="d-inline-block me-2 position-relative mb-2">
                        <div
                          className="d-flex align-items-center justify-content-center bg-info bg-opacity-10 border border-info border-opacity-25 rounded"
                          style={{ width: '100px', height: '100px', borderRadius: '4px' }}
                        >
                          <span style={{ fontSize: '24px' }}>📎</span>
                        </div>
                        <div className="text-center" style={{ fontSize: '12px', maxWidth: '100px' }}>
                          ID: {fileId}
                        </div>
                        <Button
                          variant="danger"
                          size="sm"
                          className="position-absolute top-0 start-100 translate-middle rounded-circle p-1"
                          onClick={() => handleRemoveDocument(index, 'file')}
                        >
                          ×
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Form.Group>

            <div className="d-flex gap-2">
              <Button variant="success" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Сохранение...' : 'Сохранить'}
              </Button>
              <Button variant="secondary" as={Link as any} to="/faq">
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

      <MinioDocumentPicker
        show={showDocumentPicker}
        onHide={() => setShowDocumentPicker(false)}
        onSelect={handleDocumentSelect}
      />
    </div>
  );
}
