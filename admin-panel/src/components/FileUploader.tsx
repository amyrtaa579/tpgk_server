import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, Alert, Spinner, Form, Badge } from 'react-bootstrap';
import { apiService } from '../services/api';
import type { UploadResponse } from '../types';

interface FileUploaderProps {
  onUpload: (url: string) => void;
  accept?: Record<string, string[]>;
  category?: string;
  uploadType: 'image' | 'document';
  multiple?: boolean;
  saveToGallery?: boolean;
  onSaveToGallery?: (saved: boolean) => void;
}

export default function FileUploader({
  onUpload,
  accept,
  category = 'common',
  uploadType,
  multiple = false,
  saveToGallery = false,
  onSaveToGallery,
}: FileUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadResponse[]>([]);
  const [saveToGalleryState, setSaveToGalleryState] = useState(saveToGallery);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    setError(null);

    try {
      const uploadPromises = acceptedFiles.map(async (file) => {
        // Сначала загружаем файл в MinIO
        const uploadResult = uploadType === 'image'
          ? await apiService.uploadImage(file, category)
          : await apiService.uploadDocument(file, category);

        // Если нужно, сохраняем в галерею
        if (saveToGalleryState && uploadType === 'image') {
          try {
            await apiService.createGalleryImage({
              url: uploadResult.url,
              thumbnail: uploadResult.url,
              alt: file.name.split('.')[0] || 'Изображение',
              category: category,
              caption: file.name,
              date_taken: new Date().toISOString(),
            });
          } catch (galleryError) {
            console.error('Ошибка сохранения в галерею:', galleryError);
            // Не прерываем загрузку, если ошибка только с галереей
          }
        }

        return uploadResult;
      });

      const results = await Promise.all(uploadPromises);
      setUploadedFiles((prev) => [...prev, ...results]);

      if (results.length > 0 && !multiple) {
        onUpload(results[0].url);
      } else if (multiple) {
        results.forEach((result) => onUpload(result.url));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setIsUploading(false);
    }
  }, [onUpload, category, uploadType, multiple, saveToGalleryState]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
  });

  const handleSaveToGalleryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setSaveToGalleryState(checked);
    onSaveToGallery?.(checked);
  };

  return (
    <div>
      <div
        {...getRootProps()}
        style={{
          border: '2px dashed #ccc',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? '#e3f2fd' : '#fafafa',
          transition: 'background-color 0.2s',
        }}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <div>
            <Spinner animation="border" variant="primary" size="sm" />
            <p className="mt-2 mb-0">Загрузка...</p>
          </div>
        ) : isDragActive ? (
          <p>Перетащите файлы сюда...</p>
        ) : (
          <div>
            <p className="mb-2">
              Перетащите файлы сюда или нажмите для выбора
            </p>
            <Button variant="outline-primary" size="sm">
              Выбрать файлы
            </Button>
          </div>
        )}
      </div>

      {uploadType === 'image' && (
        <Form.Group className="mt-2">
          <Form.Check
            type="checkbox"
            id="save-to-gallery"
            label="Сохранить в галерею (добавить в каталог изображений)"
            checked={saveToGalleryState}
            onChange={handleSaveToGalleryChange}
          />
        </Form.Group>
      )}

      {error && <Alert variant="danger" className="mt-2">{error}</Alert>}

      {uploadedFiles.length > 0 && (
        <div className="mt-3">
          <h6>Загруженные файлы:</h6>
          <ul className="list-group">
            {uploadedFiles.map((file, index) => (
              <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                <span>{file.filename}</span>
                <Badge bg="success">{(file.size / 1024).toFixed(1)} KB</Badge>
              </li>
            ))}
          </ul>
          {saveToGalleryState && uploadType === 'image' && (
            <Alert variant="success" className="mt-2 mb-0">
              ✓ Файлы также сохранены в галерее
            </Alert>
          )}
        </div>
      )}
    </div>
  );
}
