import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from "@/components/ui/toaster";
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { MainLayout } from '@/components/layout/MainLayout';
import { Dashboard } from '@/components/dashboard/Dashboard';
import { DocumentsPage } from '@/components/documents/DocumentsPage';
import { QAPage } from '@/components/qa/QAPage';
import { SearchPage } from '@/components/search/SearchPage';
import { SettingsPage } from '@/components/settings/SettingsPage';
import { ThemeProvider } from '@/contexts/ThemeContext';

interface IndexProps {
  isAuthenticated: boolean;
  onLoginSuccess: (token: string) => void;
  onLogout: () => void;
}

const Index: React.FC<IndexProps> = ({ isAuthenticated, onLoginSuccess, onLogout }) => {
  const [showRegister, setShowRegister] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      if (location.pathname === '/') {
        setCurrentPage('dashboard');
      } else if (location.pathname === '/documents') {
        setCurrentPage('documents');
      } else if (location.pathname === '/question-answering') {
        setCurrentPage('question-answering');
      } else if (location.pathname === '/search') {
        setCurrentPage('search');
      } else if (location.pathname === '/settings') {
        setCurrentPage('settings');
      }
    }
  }, [isAuthenticated, location.pathname]);

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
      <MainLayout currentPage={currentPage} onNavigate={setCurrentPage} onLogout={onLogout}>
        {currentPage === 'dashboard' && <Dashboard onNavigate={setCurrentPage} />}
        {currentPage === 'documents' && <DocumentsPage />}
        {currentPage === 'question-answering' && <QAPage />}
        {currentPage === 'search' && <SearchPage />}
        {currentPage === 'settings' && <SettingsPage />}
        <Toaster />
      </MainLayout>
    </ThemeProvider>
  );
};

export default Index;
