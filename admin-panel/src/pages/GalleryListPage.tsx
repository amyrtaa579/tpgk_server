import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert, Badge, Form, Image as BSImage, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { GalleryImage } from '../types';

interface MinioObject {
  key: string;
  size: number;
  last_modified: string | null;
}

export default function GalleryListPage() {
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [minioObjects, setMinioObjects] = useState<MinioObject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'gallery' | 'minio'>('gallery');

  const loadGalleryImages = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getGallery(categoryFilter === 'all' ? undefined : categoryFilter);
      setImages(response.items);
    } catch {
      setError('Не удалось загрузить изображения');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMinioFiles = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/admin/upload/minio/list', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMinioObjects(data.objects || []);
      } else {
        setError('Не удалось загрузить файлы из MinIO');
      }
    } catch {
      setError('Не удалось загрузить файлы из MinIO');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'gallery') {
      loadGalleryImages();
    } else {
      loadMinioFiles();
    }
  }, [categoryFilter, activeTab]);

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить это изображение?')) {
      return;
    }

    try {
      await apiService.deleteGalleryImage(id);
      setImages((prev) => prev.filter((img) => img.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Ошибка при удалении');
    }
  };

  const categories = ['all', ...Array.from(new Set(images.map((img) => img.category)))];
  const minioCategories = ['all', ...Array.from(new Set(minioObjects.map((obj) => {
    const parts = obj.key.split('/');
    return parts.length > 1 ? parts[1] : 'other';
  })))];

  const filteredMinioObjects = minioObjects.filter(obj => {
    if (categoryFilter === 'all') return true;
    const parts = obj.key.split('/');
    const objCategory = parts.length > 1 ? parts[1] : 'other';
    return objCategory === categoryFilter;
  });

  const getMinioUrl = (key: string) => {
    return `https://minio.anmicius.ru/anmicius-media/${key}`;
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
        <h2>Галерея изображений</h2>
        <Button variant="warning" as={Link} to="/gallery/new">
          + Добавить изображение
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Nav variant="tabs" activeKey={activeTab} onSelect={(k) => setActiveTab(k as 'gallery' | 'minio')}>
            <Nav.Item>
              <Nav.Link eventKey="gallery">
                📁 Галерея ({images.length})
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="minio">
                ☁️ Файлы в MinIO ({minioObjects.length})
              </Nav.Link>
            </Nav.Item>
          </Nav>

          <Form.Group className="mt-3">
            <Form.Label>Фильтр по категории</Form.Label>
            <Form.Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              {(activeTab === 'gallery' ? categories : minioCategories).map((cat) => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'Все категории' : cat}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Card.Body>
      </Card>

      <Card className="shadow-sm">
        <Card.Body>
          {activeTab === 'gallery' ? (
            <>
              {images.length === 0 ? (
                <p className="text-muted text-center">Изображения не найдены</p>
              ) : (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Изображение</th>
                      <th>Alt</th>
                      <th>Категория</th>
                      <th>Caption</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {images.map((img) => (
                      <tr key={img.id}>
                        <td>
                          <BSImage
                            src={img.thumbnail || img.url}
                            alt={img.alt}
                            style={{ width: '80px', height: '60px', objectFit: 'cover', borderRadius: '4px' }}
                          />
                        </td>
                        <td style={{ maxWidth: '200px' }} className="text-truncate">{img.alt}</td>
                        <td>
                          <Badge bg="secondary">{img.category}</Badge>
                        </td>
                        <td style={{ maxWidth: '200px' }} className="text-truncate">
                          {img.caption || '—'}
                        </td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-2"
                            as={Link}
                            to={`/gallery/${img.id}/edit`}
                          >
                            Редактировать
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDelete(img.id)}
                          >
                            Удалить
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </>
          ) : (
            <>
              {minioObjects.length === 0 ? (
                <p className="text-muted text-center">
                  Файлы не найдены. Загрузите изображения через форму создания специальности, новости или галереи.
                </p>
              ) : (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Превью</th>
                      <th>Путь в MinIO</th>
                      <th>Категория</th>
                      <th>Размер</th>
                      <th>Дата загрузки</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredMinioObjects.map((obj, index) => (
                      <tr key={index}>
                        <td>
                          <BSImage
                            src={getMinioUrl(obj.key)}
                            alt={obj.key}
                            style={{ width: '80px', height: '60px', objectFit: 'cover', borderRadius: '4px' }}
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="60"%3E%3Crect fill="%23ddd" width="80" height="60"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                            }}
                          />
                        </td>
                        <td style={{ maxWidth: '400px' }} className="text-truncate">
                          {obj.key}
                        </td>
                        <td>
                          <Badge bg="info">
                            {(() => {
                              const parts = obj.key.split('/');
                              return parts.length > 1 ? parts[1] : 'other';
                            })()}
                          </Badge>
                        </td>
                        <td>{(obj.size / 1024).toFixed(1)} KB</td>
                        <td>
                          {obj.last_modified ? new Date(obj.last_modified).toLocaleDateString('ru-RU') : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
