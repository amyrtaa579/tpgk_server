import { useState } from 'react';
import { Modal, Button, Table, Spinner, Alert, Form } from 'react-bootstrap';
import { apiService } from '../services/api';
import type { Image } from '../types';

interface DocumentUploaderProps {
  show: boolean;
  onHide: () => void;
  onSelect: (documentUrl: string, title: string) => void;
}

interface UploadedDocument {
  url: string;
  title: string;
  filename: string;
  size: number;
}

export default function DocumentUploader({
  show,
  onHide,
  onSelect,
}: DocumentUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [documentTitle, setDocumentTitle] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('general');

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      // Загружаем документ в MinIO
      const uploadResult = await apiService.uploadDocument(file, selectedCategory);
      
      const newDoc: UploadedDocument = {
        url: uploadResult.url,
        title: documentTitle || file.name.split('.')[0],
        filename: uploadResult.filename,
        size: uploadResult.size,
      };
      
      setUploadedDocs([...uploadedDocs, newDoc]);
      setDocumentTitle('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setIsUploading(false);
      // Сбрасываем value input, чтобы можно было загрузить тот же файл снова
      e.target.value = '';
    }
  };

  const handleSelectDocument = (doc: UploadedDocument) => {
    onSelect(doc.url, doc.title);
    onHide();
  };

  const handleRemoveDocument = (index: number) => {
    setUploadedDocs(uploadedDocs.filter((_, i) => i !== index));
  };

  const handleClose = () => {
    setUploadedDocs([]);
    setDocumentTitle('');
    setError(null);
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Загрузка документов</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}

        <Form.Group className="mb-3">
          <Form.Label>Выберите файл документа</Form.Label>
          <Form.Control
            type="file"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf"
            onChange={handleFileSelect}
            disabled={isUploading}
          />
          <Form.Text className="text-muted">
            Поддерживаемые форматы: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF
          </Form.Text>
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Название документа (отобразится в списке)</Form.Label>
          <Form.Control
            type="text"
            value={documentTitle}
            onChange={(e) => setDocumentTitle(e.target.value)}
            placeholder="Введите название документа"
          />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Категория</Form.Label>
          <Form.Select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="general">Общее</option>
            <option value="admission">Приёмная комиссия</option>
            <option value="studies">Учеба</option>
            <option value="documents">Документы</option>
          </Form.Select>
        </Form.Group>

        {isUploading && (
          <div className="d-flex justify-content-center align-items-center py-3">
            <Spinner animation="border" variant="primary" />
            <span className="ms-2">Загрузка документа...</span>
          </div>
        )}

        {uploadedDocs.length > 0 && (
          <Table striped bordered hover size="sm" className="mt-3">
            <thead>
              <tr>
                <th>Название</th>
                <th>Файл</th>
                <th>Размер</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {uploadedDocs.map((doc, index) => (
                <tr key={index}>
                  <td>{doc.title}</td>
                  <td>
                    <a href={doc.url} target="_blank" rel="noopener noreferrer">
                      {doc.filename}
                    </a>
                  </td>
                  <td>{(doc.size / 1024).toFixed(1)} KB</td>
                  <td>
                    <Button
                      variant="success"
                      size="sm"
                      className="me-2"
                      onClick={() => handleSelectDocument(doc)}
                    >
                      Выбрать
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleRemoveDocument(index)}
                    >
                      Удалить
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Закрыть
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
