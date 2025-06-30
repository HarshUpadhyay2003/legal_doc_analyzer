import { useCallback, useEffect } from 'react';
import { useSummary } from '@/contexts/SummaryContext';
import { toast } from '@/hooks/use-toast';

const BASE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

interface Document {
  id: number;
  title: string;
  upload_time: string;
  status: string;
  size: string;
  type: string;
  file_path?: string;
}

export function useSummaryGeneration() {
  const {
    startSummary,
    completeSummary,
    failSummary,
    getSummary,
    isSummaryLoading,
    hasActiveRequest,
    state,
  } = useSummary();

  const getAuthHeader = () => {
    const token = localStorage.getItem('jwt_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // Cleanup effect to abort active requests when component unmounts
  useEffect(() => {
    return () => {
      // Abort all active requests when the component unmounts
      Object.values(state.activeRequests).forEach(controller => {
        if (controller) {
          controller.abort();
        }
      });
    };
  }, [state.activeRequests]);

  const generateSummary = useCallback(async (doc: Document): Promise<string | null> => {
    const docId = doc.id;
    
    // Check if we already have a summary for this document
    const existingSummary = getSummary(docId);
    if (existingSummary?.content) {
      return existingSummary.content;
    }

    // Check if there's already an active request for this document
    if (hasActiveRequest(docId)) {
      console.log(`Summary generation already in progress for document ${docId}`);
      return null;
    }

    // Create abort controller for this request
    const controller = new AbortController();
    
    try {
      // Start the summary generation
      startSummary(docId, doc.title, controller);

      const response = await fetch(`${BASE_API_URL}/documents/summary/${docId}`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Complete the summary generation
      completeSummary(docId, data.summary);
      
      return data.summary;
      
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log(`Summary generation cancelled for document ${docId}`);
        return null;
      }
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      failSummary(docId, errorMessage);
      
      toast({
        title: 'Summary Error',
        description: errorMessage,
        variant: 'destructive',
      });
      
      return null;
    }
  }, [startSummary, completeSummary, failSummary, getSummary, hasActiveRequest]);

  const cancelSummaryGeneration = useCallback((docId: number) => {
    const controller = state.activeRequests[docId];
    if (controller) {
      controller.abort();
      console.log(`Cancelling summary generation for document ${docId}`);
    }
  }, [state.activeRequests]);

  return {
    generateSummary,
    cancelSummaryGeneration,
    getSummary,
    isSummaryLoading,
    hasActiveRequest,
  };
} 