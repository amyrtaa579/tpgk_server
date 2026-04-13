import { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Form, Row, Col, Card, Spinner, Alert, Nav, Badge } from 'react-bootstrap';
import { apiService } from '../services/api';

interface MinioDocumentPickerProps {
  show: boolean;
  onHide: () => void;
  onSelect: (documentUrl: string, title: string, docId?: number) => void;
  category?: string;
  hideGalleryTab?: boolean;
  hideMinioTab?: boolean;
}

interface DocumentFile {
  id: number;
  title: string;
  file_url: string;
  file_size?: number | null;
  category: string;
  created_at?: string;
  updated_at?: string;
}

interface MinioObject {
  key: string;
  size: number;
  last_modified: string | null;
}

export default function MinioDocumentPicker({
  show,
  onHide,
  onSelect,
  category,
  hideGalleryTab = false,
  hideMinioTab = false,
}: MinioDocumentPickerProps) {
  const [documentFiles, setDocumentFiles] = useState<DocumentFile[]>([]);
  const [minioObjects, setMinioObjects] = useState<MinioObject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<number | undefined>(undefined);
  const [filterCategory, setFilterCategory] = useState<string>(category || 'all');
  const [categories, setCategories] = useState<string[]>(['all']);
  const [viewMode, setViewMode] = useState<'upload' | 'gallery' | 'minio'>('upload');
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const [uploadedTitle, setUploadedTitle] = useState<string>('');
  const [uploadCategory, setUploadCategory] = useState(category || 'common');

  const loadDocumentFiles = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getDocuments();
      const items = response || [];
      
      // Фильтруем по категории если нужно
      const filtered = filterCategory === 'all' 
        ? items 
        : items.filter((doc: any) => doc.category === filterCategory);
      
      setDocumentFiles(filtered);
      setMinioObjects([]);

      const uniqueCategories = Array.from(new Set(items.map((doc: any) => doc.category)));
      setCategories(['all', ...uniqueCategories]);
    } catch (err) {
      setError('Не удалось загрузить документы');
    } finally {
      setIsLoading(false);
    }
  }, [filterCategory]);

  const loadMinioDocuments = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Требуется авторизация');
        setIsLoading(false);
        return;
      }

      const response = await fetch('/api/v1/admin/upload/minio/list?prefix=documents/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const refreshResponse = await fetch('/api/v1/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });

          if (refreshResponse.ok) {
            const { access_token } = await refreshResponse.json();
            localStorage.setItem('access_token', access_token);

            const retryResponse = await fetch('/api/v1/admin/upload/minio/list?prefix=documents/', {
              headers: {
                'Authorization': `Bearer ${access_token}`,
                'Content-Type': 'application/json',
              },
            });

            if (retryResponse.ok) {
              const data = await retryResponse.json();
              processMinioResponse(data);
              return;
            }
          }
        }

        setError('Сессия истекла. Пожалуйста, войдите снова');
        setIsLoading(false);
        return;
      }

      if (response.ok) {
        const data = await response.json();
        processMinioResponse(data);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(`Ошибка: ${errorData.detail || 'Не удалось загрузить список файлов из MinIO'}`);
      }
    } catch (err) {
      setError('Не удалось загрузить документы из MinIO');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const processMinioResponse = (data: { objects?: MinioObject[] }) => {
    const objects = (data.objects || []) as MinioObject[];
    // Фильтруем только документы (pdf, doc, docx, xls, xlsx, txt)
    const documentExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.rtf', '.odt'];
    const filteredObjects = objects.filter(obj => {
      const ext = '.' + obj.key.split('.').pop()?.toLowerCase();
      return documentExtensions.includes(ext);
    });
    
    setMinioObjects(filteredObjects);
    setDocumentFiles([]);
    setUploadedUrl(null);

    const uniqueCategories = Array.from(
      new Set(
        filteredObjects
          .map((obj) => {
            const parts = obj.key.split('/');
            return parts.length > 1 ? parts[1] : 'other';
          })
      )
    );
    setCategories(['all', ...uniqueCategories]);
  };

  useEffect(() => {
    if (show) {
      setIsLoading(true);
      if (viewMode === 'gallery' && !hideGalleryTab) {
        loadDocumentFiles();
      } else if (viewMode === 'minio' && !hideMinioTab) {
        loadMinioDocuments();
      } else {
        setDocumentFiles([]);
        setMinioObjects([]);
        setCategories(['all']);
        setIsLoading(false);
      }
    }
  }, [show, viewMode, loadDocumentFiles, loadMinioDocuments, hideGalleryTab, hideMinioTab]);

  const handleSelect = () => {
    if (selectedDocument && selectedTitle) {
      onSelect(selectedDocument, selectedTitle, selectedDocId);
      onHide();
      setSelectedDocument(null);
      setSelectedTitle(null);
      setSelectedDocId(undefined);
    } else if (uploadedUrl) {
      onSelect(uploadedUrl, uploadedTitle || uploadedUrl.split('/').pop() || 'Документ');
      onHide();
      setUploadedUrl(null);
      setUploadedTitle('');
    }
  };

  const handleDocumentClick = (fileUrl: string, title: string, docId?: number) => {
    setSelectedDocument(fileUrl);
    setSelectedTitle(title);
    setSelectedDocId(docId);
  };

  const getMinioUrl = (key: string) => {
    return `https://minio.anmicius.ru/anmicius-media/${key}`;
  };

  const handleUpload = async (file: File) => {
    try {
      setError(null);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Требуется авторизация');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', uploadCategory);

      const response = await fetch('/api/v1/admin/upload/document', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadedUrl(data.url);
        setSelectedDocument(data.url);
        setUploadedTitle(file.name.replace(/\.[^/.]+$/, '')); // Убираем расширение
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(`Ошибка загрузки: ${errorData.detail || 'Не удалось загрузить файл'}`);
      }
    } catch (err) {
      setError('Ошибка при загрузке файла');
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files[0]);
    }
  };

  const filteredDocumentFiles = documentFiles.filter(doc => {
    if (filterCategory === 'all') return true;
    return doc.category === filterCategory;
  });

  const filteredMinioObjects = minioObjects.filter(obj => {
    if (filterCategory === 'all') return true;
    const parts = obj.key.split('/');
    const objCategory = parts.length > 1 ? parts[1] : 'other';
    return objCategory === filterCategory;
  });

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return '📄';
      case 'doc':
      case 'docx': return '📝';
      case 'xls':
      case 'xlsx': return '📊';
      case 'txt': return '📃';
      default: return '📁';
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="xl" centered>
      <Modal.Header closeButton>
        <Modal.Title>Выбор документа</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Nav variant="tabs" activeKey={viewMode} onSelect={(k) => setViewMode(k as 'upload' | 'gallery' | 'minio')}>
          <Nav.Item>
            <Nav.Link eventKey="upload">
              📤 Загрузить файл
            </Nav.Link>
          </Nav.Item>
          {!hideGalleryTab && (
            <Nav.Item>
              <Nav.Link eventKey="gallery">
                🗂️ Галерея документов ({documentFiles.length})
              </Nav.Link>
            </Nav.Item>
          )}
          {!hideMinioTab && (
            <Nav.Item>
              <Nav.Link eventKey="minio">
                ☁️ Файлы MinIO ({minioObjects.length})
              </Nav.Link>
            </Nav.Item>
          )}
        </Nav>

        {viewMode === 'upload' ? (
          <div className="mt-4">
            <Form.Group className="mb-3">
              <Form.Label>Категория</Form.Label>
              <Form.Select
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
              >
                <option value="common">common</option>
                <option value="specialties">specialties</option>
                <option value="news">news</option>
                <option value="events">events</option>
                <option value="students">students</option>
              </Form.Select>
            </Form.Group>

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const files = Array.from(e.dataTransfer.files);
                if (files.length > 0) {
                  handleUpload(files[0]);
                }
              }}
              style={{
                border: '2px dashed #ccc',
                borderRadius: '8px',
                padding: '40px',
                textAlign: 'center',
                backgroundColor: '#fafafa',
                cursor: 'pointer',
              }}
            >
              <input
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.rtf,.odt"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
                id="upload-input"
              />
              <label htmlFor="upload-input" style={{ cursor: 'pointer' }}>
                <div className="mb-2">
                  <span style={{ fontSize: '48px' }}>📁</span>
                </div>
                <p className="mb-2">Перетащите файл сюда или нажмите для выбора</p>
                <p className="text-muted small">PDF, DOC, DOCX, XLS, XLSX, TXT</p>
                <Button variant="outline-primary" size="sm" as="span">
                  Выбрать файл
                </Button>
              </label>
            </div>

            {uploadedUrl && (
              <Card className="mt-3 bg-light">
                <Card.Body>
                  <Row>
                    <Col md={4} className="d-flex align-items-center justify-content-center">
                      <span style={{ fontSize: '64px' }}>{getFileIcon(uploadedUrl)}</span>
                    </Col>
                    <Col md={8}>
                      <h6>Загруженный документ</h6>
                      <p className="mb-1">
                        <strong>Название:</strong> {uploadedTitle}
                      </p>
                      <p className="mb-1">
                        <strong>URL:</strong>{' '}
                        <small className="text-muted text-break">{uploadedUrl}</small>
                      </p>
                      <Badge bg="success">✓ Готово к выбору</Badge>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            )}

            {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
          </div>
        ) : viewMode === 'gallery' && !hideGalleryTab ? (
          <>
            <div className="mt-4">
              <Form.Group className="mb-3">
                <Form.Label>Фильтр по категории</Form.Label>
                <Form.Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? 'Все категории' : cat}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            {isLoading ? (
              <div className="text-center py-5">
                <Spinner animation="border" variant="primary" />
                <p className="mt-2 text-muted">Загрузка...</p>
              </div>
            ) : documentFiles.length === 0 ? (
              <Alert variant="info">
                Нет документов в галерее. Добавьте документы или загрузите файл.
              </Alert>
            ) : (
              <Row xs={1} md={2} lg={3} className="g-3">
                {filteredDocumentFiles.map((doc, index) => {
                  const isSelected = selectedDocument === doc.file_url;

                  return (
                    <Col key={index}>
                      <Card
                        className={`h-100 cursor-pointer ${
                          isSelected ? 'border-primary border-2' : ''
                        }`}
                        onClick={() => handleDocumentClick(doc.file_url, doc.title, doc.id)}
                      >
                        <Card.Body className="p-3">
                          <div className="d-flex align-items-center mb-2">
                            <span style={{ fontSize: '32px', marginRight: '12px' }}>
                              {getFileIcon(doc.title)}
                            </span>
                            <div className="text-truncate">
                              <Card.Title className="mb-0 text-truncate">{doc.title}</Card.Title>
                            </div>
                          </div>
                          <Badge bg="secondary">{doc.category}</Badge>
                          {doc.file_size && (
                            <span className="text-muted small ms-2">
                              ({(doc.file_size / 1024).toFixed(1)} KB)
                            </span>
                          )}
                        </Card.Body>
                      </Card>
                    </Col>
                  );
                })}
              </Row>
            )}
          </>
        ) : (
          <>
            <div className="mt-4">
              <Form.Group className="mb-3">
                <Form.Label>Фильтр по категории</Form.Label>
                <Form.Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? 'Все категории' : cat}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            {isLoading ? (
              <div className="text-center py-5">
                <Spinner animation="border" variant="primary" />
                <p className="mt-2 text-muted">Загрузка...</p>
              </div>
            ) : minioObjects.length === 0 ? (
              <Alert variant="info">
                Нет файлов в MinIO. Загрузите документы через вкладку "Загрузить файл".
              </Alert>
            ) : (
              <Row xs={1} md={2} lg={3} className="g-3">
                {filteredMinioObjects.map((obj, index) => {
                  const fileUrl = getMinioUrl(obj.key);
                  const fileName = obj.key.split('/').pop() || obj.key;
                  const isSelected = selectedDocument === fileUrl;

                  return (
                    <Col key={index}>
                      <Card
                        className={`h-100 cursor-pointer ${
                          isSelected ? 'border-primary border-2' : ''
                        }`}
                        onClick={() => handleDocumentClick(fileUrl, fileName.replace(/\.[^/.]+$/, ''))}
                      >
                        <Card.Body className="p-3">
                          <div className="d-flex align-items-center mb-2">
                            <span style={{ fontSize: '32px', marginRight: '12px' }}>
                              {getFileIcon(fileName)}
                            </span>
                            <div className="text-truncate">
                              <Card.Title className="mb-0 text-truncate">{fileName}</Card.Title>
                            </div>
                          </div>
                          <Badge bg="info">
                            {(() => {
                              const parts = obj.key.split('/');
                              return parts.length > 1 ? parts[1] : 'other';
                            })()}
                          </Badge>
                          <span className="text-muted small ms-2">
                            ({(obj.size / 1024).toFixed(1)} KB)
                          </span>
                        </Card.Body>
                      </Card>
                    </Col>
                  );
                })}
              </Row>
            )}
          </>
        )}

        {selectedDocument && (
          <Card className="mt-3 bg-light">
            <Card.Body>
              <Row>
                <Col md={4} className="d-flex align-items-center justify-content-center">
                  <span style={{ fontSize: '64px' }}>{getFileIcon(selectedDocument)}</span>
                </Col>
                <Col md={8}>
                  <h6>Выбранный документ</h6>
                  <p className="mb-1">
                    <strong>Название:</strong> {selectedTitle}
                  </p>
                  <p className="mb-1">
                    <strong>URL:</strong>{' '}
                    <small className="text-muted text-break">{selectedDocument}</small>
                  </p>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Отмена
        </Button>
        <Button
          variant="primary"
          onClick={handleSelect}
          disabled={!selectedDocument && !uploadedUrl}
        >
          Выбрать
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
