import { useState } from 'react';
import { Form, Button, InputGroup, Badge } from 'react-bootstrap';

interface TextArrayEditorProps {
  value: string[];
  onChange: (values: string[]) => void;
  label?: string;
  placeholder?: string;
  addButtonText?: string;
}

export default function TextArrayEditor({
  value,
  onChange,
  label = 'Текстовые элементы',
  placeholder = 'Введите текст',
  addButtonText = 'Добавить',
}: TextArrayEditorProps) {
  const [newItem, setNewItem] = useState('');

  const handleAdd = () => {
    if (newItem.trim()) {
      onChange([...value, newItem.trim()]);
      setNewItem('');
    }
  };

  const handleRemove = (index: number) => {
    const updated = value.filter((_, i) => i !== index);
    onChange(updated);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <Form.Group>
      {label && <Form.Label>{label}</Form.Label>}
      <InputGroup className="mb-2">
        <Form.Control
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
        />
        <Button variant="outline-primary" onClick={handleAdd}>
          {addButtonText}
        </Button>
      </InputGroup>
      <div className="mt-2">
        {value.length === 0 ? (
          <Form.Text className="text-muted">Элементы не добавлены</Form.Text>
        ) : (
          value.map((item, index) => (
            <Badge
              key={index}
              bg="primary"
              className="me-1 mb-1 p-2"
              style={{ fontSize: '0.9rem', fontWeight: 'normal' }}
            >
              {item}
              <button
                type="button"
                className="btn-close btn-close-white ms-2"
                style={{ fontSize: '10px', verticalAlign: 'middle' }}
                onClick={() => handleRemove(index)}
                aria-label="Удалить"
              />
            </Badge>
          ))
        )}
      </div>
    </Form.Group>
  );
}
