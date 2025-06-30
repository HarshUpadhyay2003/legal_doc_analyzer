import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface SummaryState {
  summaries: { [docId: number]: SummaryData };
  activeRequests: { [docId: number]: AbortController };
}

interface SummaryData {
  content: string | null;
  isLoading: boolean;
  error: string | null;
  timestamp: number;
  documentTitle: string;
}

type SummaryAction =
  | { type: 'START_SUMMARY'; docId: number; documentTitle: string; controller: AbortController }
  | { type: 'COMPLETE_SUMMARY'; docId: number; content: string }
  | { type: 'FAIL_SUMMARY'; docId: number; error: string }
  | { type: 'CLEAR_SUMMARY'; docId: number }
  | { type: 'CLEAR_ALL_SUMMARIES' };

const initialState: SummaryState = {
  summaries: {},
  activeRequests: {},
};

function summaryReducer(state: SummaryState, action: SummaryAction): SummaryState {
  switch (action.type) {
    case 'START_SUMMARY':
      return {
        ...state,
        summaries: {
          ...state.summaries,
          [action.docId]: {
            content: null,
            isLoading: true,
            error: null,
            timestamp: Date.now(),
            documentTitle: action.documentTitle,
          },
        },
        activeRequests: {
          ...state.activeRequests,
          [action.docId]: action.controller,
        },
      };

    case 'COMPLETE_SUMMARY':
      return {
        ...state,
        summaries: {
          ...state.summaries,
          [action.docId]: {
            ...state.summaries[action.docId],
            content: action.content,
            isLoading: false,
            error: null,
          },
        },
        activeRequests: {
          ...state.activeRequests,
          [action.docId]: undefined as any,
        },
      };

    case 'FAIL_SUMMARY':
      return {
        ...state,
        summaries: {
          ...state.summaries,
          [action.docId]: {
            ...state.summaries[action.docId],
            isLoading: false,
            error: action.error,
          },
        },
        activeRequests: {
          ...state.activeRequests,
          [action.docId]: undefined as any,
        },
      };

    case 'CLEAR_SUMMARY':
      const newSummaries = { ...state.summaries };
      const newActiveRequests = { ...state.activeRequests };
      delete newSummaries[action.docId];
      delete newActiveRequests[action.docId];
      return {
        ...state,
        summaries: newSummaries,
        activeRequests: newActiveRequests,
      };

    case 'CLEAR_ALL_SUMMARIES':
      return {
        summaries: {},
        activeRequests: {},
      };

    default:
      return state;
  }
}

interface SummaryContextType {
  state: SummaryState;
  startSummary: (docId: number, documentTitle: string, controller: AbortController) => void;
  completeSummary: (docId: number, content: string) => void;
  failSummary: (docId: number, error: string) => void;
  clearSummary: (docId: number) => void;
  clearAllSummaries: () => void;
  getSummary: (docId: number) => SummaryData | null;
  isSummaryLoading: (docId: number) => boolean;
  hasActiveRequest: (docId: number) => boolean;
}

const SummaryContext = createContext<SummaryContextType | undefined>(undefined);

export function SummaryProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(summaryReducer, initialState);

  const startSummary = (docId: number, documentTitle: string, controller: AbortController) => {
    dispatch({ type: 'START_SUMMARY', docId, documentTitle, controller });
  };

  const completeSummary = (docId: number, content: string) => {
    dispatch({ type: 'COMPLETE_SUMMARY', docId, content });
  };

  const failSummary = (docId: number, error: string) => {
    dispatch({ type: 'FAIL_SUMMARY', docId, error });
  };

  const clearSummary = (docId: number) => {
    dispatch({ type: 'CLEAR_SUMMARY', docId });
  };

  const clearAllSummaries = () => {
    dispatch({ type: 'CLEAR_ALL_SUMMARIES' });
  };

  const getSummary = (docId: number): SummaryData | null => {
    return state.summaries[docId] || null;
  };

  const isSummaryLoading = (docId: number): boolean => {
    return state.summaries[docId]?.isLoading || false;
  };

  const hasActiveRequest = (docId: number): boolean => {
    return !!state.activeRequests[docId];
  };

  const value: SummaryContextType = {
    state,
    startSummary,
    completeSummary,
    failSummary,
    clearSummary,
    clearAllSummaries,
    getSummary,
    isSummaryLoading,
    hasActiveRequest,
  };

  return (
    <SummaryContext.Provider value={value}>
      {children}
    </SummaryContext.Provider>
  );
}

export function useSummary() {
  const context = useContext(SummaryContext);
  if (context === undefined) {
    throw new Error('useSummary must be used within a SummaryProvider');
  }
  return context;
} 