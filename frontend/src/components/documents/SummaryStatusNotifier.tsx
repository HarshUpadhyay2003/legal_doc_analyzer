import { useEffect, useRef } from 'react';
import { useSummary } from '@/contexts/SummaryContext';
import { toast } from '@/hooks/use-toast';

export function SummaryStatusNotifier() {
  const { state } = useSummary();
  const prevSummaries = useRef<{ [docId: number]: boolean }>({});

  useEffect(() => {
    Object.entries(state.summaries).forEach(([docId, summaryData]) => {
      const wasLoading = prevSummaries.current[docId];
      if (wasLoading && !summaryData.isLoading && summaryData.content) {
        toast({
          title: 'Summary Generation Complete',
          description: `Summary for "${summaryData.documentTitle}" is ready.`,
        });
      }
      prevSummaries.current[docId] = summaryData.isLoading;
    });
  }, [state.summaries]);

  return null;
} 