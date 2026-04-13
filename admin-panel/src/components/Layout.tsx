import React, { useState } from 'react';
import { Navbar, Nav, Button } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const menuItems = [
  { path: '/', label: 'Главная', icon: '🏠' },
  { path: '/specialties', label: 'Специальности', icon: '📚' },
  { path: '/news', label: 'Новости', icon: '📰' },
  { path: '/facts', label: 'Факты', icon: '💡' },
  { path: '/admission', label: 'Приёмная кампания', icon: '🎓' },
  { path: '/faq', label: 'FAQ', icon: '❓' },
  { path: '/documents', label: 'Документы', icon: '📄' },
  { path: '/about', label: 'О колледже', icon: 'ℹ️' },
  { path: '/test-questions', label: 'Тесты', icon: '📝' },
  { path: '/gallery', label: 'Галерея', icon: '🖼️' },
  { path: '/users', label: 'Пользователи', icon: '👥' },
];

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="d-flex" style={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <div
        className="bg-dark text-white"
        style={{
          width: '250px',
          minWidth: '250px',
          transition: 'transform 0.3s ease',
          position: 'fixed',
          height: '100vh',
          overflowY: 'auto',
          zIndex: 1000,
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-250px)',
        }}
      >
        <div className="p-3 border-bottom border-secondary">
          <h4 className="mb-0">Anmicius Admin</h4>
          <small className="text-muted">Панель управления</small>
        </div>
        <Nav className="flex-column p-2">
          {menuItems.map((item) => (
            <Nav.Link
              key={item.path}
              as={Link as any}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              active={location.pathname === item.path}
              style={{
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                borderRadius: '4px',
                marginBottom: '4px',
              }}
            >
              <span className="me-2">{item.icon}</span>
              {item.label}
            </Nav.Link>
          ))}
        </Nav>
      </div>

      {/* Main content */}
      <div
        style={{
          flex: 1,
          marginLeft: sidebarOpen ? '250px' : '0',
          transition: 'margin-left 0.3s ease',
          width: '100%',
        }}
      >
        {/* Top navbar */}
        <Navbar bg="light" expand="lg" className="border-bottom px-3">
          <Button
            variant="outline-secondary"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="me-3"
          >
            ☰
          </Button>

          <Navbar.Brand as={Link as any} to="/">
            Anmicius API
          </Navbar.Brand>

          <Navbar.Toggle aria-controls="navbar-nav" />
          <Navbar.Collapse id="navbar-nav" className="justify-content-end">
            <Nav className="align-items-center">
              {user && (
                <>
                  <span className="me-3 text-muted">
                    👤 {user.username}
                  </span>
                  <Button variant="outline-danger" size="sm" onClick={handleLogout}>
                    Выйти
                  </Button>
                </>
              )}
            </Nav>
          </Navbar.Collapse>
        </Navbar>

        {/* Page content */}
        <main className="p-4" style={{ minHeight: 'calc(100vh - 56px)' }}>
          {children}
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 999,
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
