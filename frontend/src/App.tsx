import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import { useState, useEffect } from 'react';
import { DocumentsPage } from './components/documents/DocumentsPage';
import { Dashboard } from './components/dashboard/Dashboard';
import { QAPage } from './components/qa/QAPage';
import { SearchPage } from './components/search/SearchPage';
import { SettingsPage } from './components/settings/SettingsPage';

const queryClient = new QueryClient();

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
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={
                <Index 
                  isAuthenticated={isAuthenticated} 
                  onLoginSuccess={handleLogin} 
                  onLogout={handleLogout} 
                />
              }
            >
              {isAuthenticated && (
                <>
                  <Route index element={<Dashboard />} />
                  <Route path="documents" element={<DocumentsPage />} />
                  <Route path="question-answering" element={<QAPage />} />
                  <Route path="search" element={<SearchPage />} />
                  <Route path="settings" element={<SettingsPage />} />
                </>
              )}
            </Route>
            {!isAuthenticated && <Route path="/*" element={<Navigate to="/" replace />} />}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
