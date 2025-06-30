import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import NotFound from "./pages/NotFound";
import { useState, useEffect } from 'react';
import { DocumentsPage } from './components/documents/DocumentsPage';
import { Dashboard } from './components/dashboard/Dashboard';
import { QAPage } from './components/qa/QAPage';
import { SearchPage } from './components/search/SearchPage';
import { SettingsPage } from './components/settings/SettingsPage';
import { SummaryProvider } from './contexts/SummaryContext';
import { SummaryStatusNotifier } from './components/documents/SummaryStatusNotifier';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { ThemeProvider } from './contexts/ThemeContext';
import { MainLayout } from './components/layout/MainLayout';
import Welcome from './pages/Welcome';

const queryClient = new QueryClient();

// Auth wrapper component to handle navigation between login and register
const AuthWrapper = ({ onLoginSuccess, initialForm }: { onLoginSuccess: (token: string) => void, initialForm: 'login' | 'register' }) => {
  const navigate = useNavigate();
  const [currentForm, setCurrentForm] = useState<'login' | 'register'>(initialForm);

  const handleSwitchToRegister = () => {
    setCurrentForm('register');
    navigate('/');
  };

  const handleSwitchToLogin = () => {
    setCurrentForm('login');
    navigate('/login');
  };

  const handleRegisterSuccess = () => {
    setCurrentForm('login');
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <div className="w-full max-w-md">
        {currentForm === 'register' ? (
          <RegisterForm 
            onSwitchToLogin={handleSwitchToLogin}
            onRegisterSuccess={handleRegisterSuccess}
          />
        ) : (
          <LoginForm 
            onSwitchToRegister={handleSwitchToRegister}
            onLoginSuccess={onLoginSuccess}
          />
        )}
      </div>
    </div>
  );
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status on mount and when localStorage changes
    const checkAuth = () => {
      const token = localStorage.getItem('jwt_token');
      setIsAuthenticated(!!token);
      setIsLoading(false);
    };

    checkAuth();
    // Listen for storage events (in case token is modified in another tab)
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  const handleLogin = (token: string) => {
    localStorage.setItem('jwt_token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <SummaryProvider>
        <SummaryStatusNotifier />
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {!isAuthenticated ? (
                <>
                  <Route path="/" element={<Welcome />} />
                  <Route path="/login" element={<AuthWrapper onLoginSuccess={handleLogin} initialForm="login" />} />
                  <Route path="/register" element={<AuthWrapper onLoginSuccess={handleLogin} initialForm="register" />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </>
              ) : (
                <>
                  <Route path="/" element={
                    <MainLayout currentPage="dashboard" onNavigate={(page) => window.location.href = `/${page === 'dashboard' ? '' : page}`} onLogout={handleLogout}>
                      <Dashboard />
                    </MainLayout>
                  } />
                  <Route path="/documents" element={
                    <MainLayout currentPage="documents" onNavigate={(page) => window.location.href = `/${page === 'dashboard' ? '' : page}`} onLogout={handleLogout}>
                      <DocumentsPage />
                    </MainLayout>
                  } />
                  <Route path="/question-answering" element={
                    <MainLayout currentPage="question-answering" onNavigate={(page) => window.location.href = `/${page === 'dashboard' ? '' : page}`} onLogout={handleLogout}>
                      <QAPage />
                    </MainLayout>
                  } />
                  <Route path="/search" element={
                    <MainLayout currentPage="search" onNavigate={(page) => window.location.href = `/${page === 'dashboard' ? '' : page}`} onLogout={handleLogout}>
                      <SearchPage />
                    </MainLayout>
                  } />
                  <Route path="/settings" element={
                    <MainLayout currentPage="settings" onNavigate={(page) => window.location.href = `/${page === 'dashboard' ? '' : page}`} onLogout={handleLogout}>
                      <SettingsPage />
                    </MainLayout>
                  } />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </>
              )}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </SummaryProvider>
    </QueryClientProvider>
  );
};

export default App;
