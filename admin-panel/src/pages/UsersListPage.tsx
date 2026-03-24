import { useState, useEffect } from 'react';
import { Table, Button, Card, Spinner, Alert, Badge, Modal, Form } from 'react-bootstrap';
import { apiService } from '../services/api';
import type { User } from '../types';

export default function UsersListPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editData, setEditData] = useState({
    email: '',
    username: '',
    is_active: true,
    is_superuser: false,
  });

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getUsers(1, 100);
      setUsers(response.items);
    } catch {
      setError('Не удалось загрузить пользователей');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleDelete = async (userId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
      return;
    }

    try {
      await apiService.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Ошибка при удалении');
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setEditData({
      email: user.email,
      username: user.username,
      is_active: user.is_active,
      is_superuser: user.is_superuser,
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!editingUser) return;

    try {
      await apiService.updateUser(editingUser.id, editData);
      await loadUsers();
      setShowEditModal(false);
      setEditingUser(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Ошибка при сохранении');
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
        <h2>Пользователи</h2>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm">
        <Card.Body>
          {users.length === 0 ? (
            <p className="text-muted text-center">Пользователи не найдены</p>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Имя пользователя</th>
                  <th>Роль</th>
                  <th>Статус</th>
                  <th>Дата регистрации</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.email}</td>
                    <td>{user.username}</td>
                    <td>
                      {user.is_superuser ? (
                        <Badge bg="danger">Суперпользователь</Badge>
                      ) : (
                        <Badge bg="primary">Пользователь</Badge>
                      )}
                    </td>
                    <td>
                      {user.is_active ? (
                        <Badge bg="success">Активен</Badge>
                      ) : (
                        <Badge bg="secondary">Не активен</Badge>
                      )}
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString('ru-RU')}</td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        onClick={() => handleEdit(user)}
                      >
                        Редактировать
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(user.id)}
                      >
                        Удалить
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Edit Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Редактирование пользователя</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={editData.email}
                onChange={(e) => setEditData({ ...editData, email: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Имя пользователя</Form.Label>
              <Form.Control
                type="text"
                value={editData.username}
                onChange={(e) => setEditData({ ...editData, username: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="active-switch"
                label="Активен"
                checked={editData.is_active}
                onChange={(e) => setEditData({ ...editData, is_active: e.target.checked })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="superuser-switch"
                label="Суперпользователь"
                checked={editData.is_superuser}
                onChange={(e) => setEditData({ ...editData, is_superuser: e.target.checked })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Отмена
          </Button>
          <Button variant="primary" onClick={handleSaveEdit}>
            Сохранить
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
