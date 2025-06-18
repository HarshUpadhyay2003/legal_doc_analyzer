import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Outlet } from 'react-router-dom';
import { Toaster } from "@/components/ui/toaster";
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { MainLayout } from '@/components/layout/MainLayout';
import { ThemeProvider } from '@/contexts/ThemeContext';

interface IndexProps {
  isAuthenticated: boolean;
  onLoginSuccess: (token: string) => void;
  onLogout: () => void;
}

const Index: React.FC<IndexProps> = ({ isAuthenticated, onLoginSuccess, onLogout }) => {
  const [showRegister, setShowRegister] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Get current page from pathname
  const getCurrentPage = (pathname: string) => {
    if (pathname === '/') return 'dashboard';
    return pathname.substring(1); // Remove leading slash
  };

  const handleNavigate = (page: string) => {
    navigate(`/${page === 'dashboard' ? '' : page}`);
  };

  if (!isAuthenticated) {
    return (
      <ThemeProvider>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            {showRegister ? (
              <RegisterForm 
                onSwitchToLogin={() => setShowRegister(false)}
                onRegisterSuccess={() => setShowRegister(false)}
              />
            ) : (
              <LoginForm 
                onSwitchToRegister={() => setShowRegister(true)}
                onLoginSuccess={onLoginSuccess}
              />
            )}
          </div>
          <Toaster />
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <MainLayout 
        currentPage={getCurrentPage(location.pathname)} 
        onNavigate={handleNavigate} 
        onLogout={onLogout}
      >
        <Outlet />
        <Toaster />
      </MainLayout>
    </ThemeProvider>
  );
};

export default Index;
