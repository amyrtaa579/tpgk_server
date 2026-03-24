import { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Form, Row, Col, Card, Spinner, Alert, Nav, Badge } from 'react-bootstrap';
import { apiService } from '../services/api';
import type { GalleryImage, UploadResponse } from '../types';

interface MinioImagePickerProps {
  show: boolean;
  onHide: () => void;
  onSelect: (imageUrl: string) => void;
  category?: string;
  hideGalleryTab?: boolean; // Скрыть вкладку "Галерея" (для страницы создания галереи)
  hideMinioTab?: boolean; // Скрыть вкладку "Файлы MinIO" (для специальностей, новостей, фактов)
}

interface MinioObject {
  key: string;
  size: number;
  last_modified: string | null;
}

export default function MinioImagePicker({
  show,
  onHide,
  onSelect,
  category,
  hideGalleryTab = false,
  hideMinioTab = false,
}: MinioImagePickerProps) {
  const [galleryImages, setGalleryImages] = useState<GalleryImage[]>([]);
  const [minioObjects, setMinioObjects] = useState<MinioObject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>(category || 'all');
  const [categories, setCategories] = useState<string[]>(['all']);
  const [viewMode, setViewMode] = useState<'upload' | 'gallery' | 'minio'>('upload');
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const [uploadCategory, setUploadCategory] = useState(category || 'common');

  const loadGalleryImages = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getGallery(filterCategory === 'all' ? undefined : filterCategory);
      const items = response.items || [];
      setGalleryImages(items);
      setMinioObjects([]);

      const uniqueCategories = Array.from(new Set(items.map(img => img.category)));
      setCategories(['all', ...uniqueCategories]);
    } catch (err) {
      setError('Не удалось загрузить изображения');
    } finally {
      setIsLoading(false);
    }
  }, [filterCategory]);

  const loadMinioImages = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Требуется авторизация');
        setIsLoading(false);
        return;
      }

      const response = await fetch('/api/v1/admin/upload/minio/list', {
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

            const retryResponse = await fetch('/api/v1/admin/upload/minio/list', {
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
      setError('Не удалось загрузить изображения из MinIO');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const processMinioResponse = (data: { objects?: MinioObject[] }) => {
    const objects = (data.objects || []) as MinioObject[];
    setMinioObjects(objects);
    setGalleryImages([]);
    setUploadedUrl(null);

    const uniqueCategories = Array.from(
      new Set(
        objects
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
        loadGalleryImages();
      } else if (viewMode === 'minio' && !hideMinioTab) {
        loadMinioImages();
      } else {
        setGalleryImages([]);
        setMinioObjects([]);
        setCategories(['all']);
        setIsLoading(false);
      }
    }
  }, [show, viewMode, loadGalleryImages, loadMinioImages, hideGalleryTab, hideMinioTab]);

  const handleSelect = () => {
    if (selectedImage) {
      onSelect(selectedImage);
      onHide();
      setSelectedImage(null);
    } else if (uploadedUrl) {
      onSelect(uploadedUrl);
      onHide();
      setUploadedUrl(null);
    }
  };

  const handleImageClick = (imageUrl: string) => {
    setSelectedImage(imageUrl);
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

      const response = await fetch('/api/v1/admin/upload/image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data: UploadResponse = await response.json();
        setUploadedUrl(data.url);
        setSelectedImage(data.url);
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

  const filteredGalleryImages = galleryImages.filter(img => {
    if (filterCategory === 'all') return true;
    return img.category === filterCategory;
  });

  const filteredMinioObjects = minioObjects.filter(obj => {
    if (filterCategory === 'all') return true;
    const parts = obj.key.split('/');
    const objCategory = parts.length > 1 ? parts[1] : 'other';
    return objCategory === filterCategory;
  });

  return (
    <Modal show={show} onHide={onHide} size="xl" centered>
      <Modal.Header closeButton>
        <Modal.Title>Выбор изображения</Modal.Title>
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
                🖼️ Галерея ({galleryImages.length})
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
                if (files.length > 0 && files[0].type.startsWith('image/')) {
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
                accept="image/*"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
                id="upload-input"
              />
              <label htmlFor="upload-input" style={{ cursor: 'pointer' }}>
                <div className="mb-2">
                  <span style={{ fontSize: '48px' }}>📁</span>
                </div>
                <p className="mb-2">Перетащите файл сюда или нажмите для выбора</p>
                <Button variant="outline-primary" size="sm" as="span">
                  Выбрать файл
                </Button>
              </label>
            </div>

            {uploadedUrl && (
              <Card className="mt-3 bg-light">
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <img
                        src={uploadedUrl}
                        alt="Uploaded"
                        className="img-fluid rounded"
                        style={{ maxHeight: '200px', objectFit: 'contain' }}
                      />
                    </Col>
                    <Col md={8}>
                      <h6>Загруженное изображение</h6>
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
            ) : galleryImages.length === 0 ? (
              <Alert variant="info">
                Нет изображений в галерее. Добавьте изображения через раздел "Галерея" или загрузите файл.
              </Alert>
            ) : (
              <Row xs={2} md={3} lg={4} className="g-3">
                {filteredGalleryImages.map((img, index) => {
                  const imageUrl = img.url;
                  const isSelected = selectedImage === imageUrl;

                  return (
                    <Col key={index}>
                      <Card
                        className={`h-100 cursor-pointer ${
                          isSelected ? 'border-primary border-2' : ''
                        }`}
                        onClick={() => handleImageClick(imageUrl)}
                      >
                        <Card.Img
                          variant="top"
                          src={imageUrl}
                          alt={img.alt}
                          style={{ height: '150px', objectFit: 'cover' }}
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="150" height="150"%3E%3Crect fill="%23ddd" width="150" height="150"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                          }}
                        />
                        <Card.Body className="p-2">
                          <Card.Text className="small text-truncate mb-1">
                            {img.caption || img.alt || 'Без названия'}
                          </Card.Text>
                          <Badge bg="secondary">{img.category}</Badge>
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
                Нет файлов в MinIO. Загрузите изображения через вкладку "Загрузить файл".
              </Alert>
            ) : (
              <>
                <Row xs={2} md={3} lg={4} className="g-3">
                  {filteredMinioObjects.map((obj, index) => {
                    const imageUrl = getMinioUrl(obj.key);
                    const isSelected = selectedImage === imageUrl;

                    return (
                      <Col key={index}>
                        <Card
                          className={`h-100 cursor-pointer ${
                            isSelected ? 'border-primary border-2' : ''
                          }`}
                          onClick={() => handleImageClick(imageUrl)}
                        >
                          <Card.Img
                            variant="top"
                            src={imageUrl}
                            alt={obj.key}
                            style={{ height: '150px', objectFit: 'cover' }}
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="150" height="150"%3E%3Crect fill="%23ddd" width="150" height="150"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                            }}
                          />
                          <Card.Body className="p-2">
                            <Card.Text className="small text-truncate mb-1">
                              {obj.key.split('/').pop()}
                            </Card.Text>
                            <Badge bg="info">
                              {(() => {
                                const parts = obj.key.split('/');
                                return parts.length > 1 ? parts[1] : 'other';
                              })()}
                            </Badge>
                            <span className="ms-1 text-muted small">
                              ({(obj.size / 1024).toFixed(1)} KB)
                            </span>
                          </Card.Body>
                        </Card>
                      </Col>
                    );
                  })}
                </Row>
              </>
            )}
          </>
        )}

        {selectedImage && (
          <Card className="mt-3 bg-light">
            <Card.Body>
              <Row>
                <Col md={4}>
                  <img
                    src={selectedImage}
                    alt="Selected"
                    className="img-fluid rounded"
                    style={{ maxHeight: '200px', objectFit: 'contain' }}
                  />
                </Col>
                <Col md={8}>
                  <h6>Выбранное изображение</h6>
                  <p className="mb-1">
                    <strong>URL:</strong>{' '}
                    <small className="text-muted text-break">{selectedImage}</small>
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
          disabled={!selectedImage && !uploadedUrl}
        >
          Выбрать
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
