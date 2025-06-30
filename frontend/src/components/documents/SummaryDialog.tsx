import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, Copy, Minus, X, Maximize2 } from 'lucide-react';
import { useSummary } from '@/contexts/SummaryContext';
import { useSummaryGeneration } from '@/hooks/useSummaryGeneration';
import { toast } from '@/hooks/use-toast';

interface Document {
  id: number;
  title: string;
  upload_time: string;
  status: string;
  size: string;
  type: string;
  file_path?: string;
}

interface SummaryDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  isMinimized: boolean;
  onMinimizeChange: (minimized: boolean) => void;
  selectedDocument: Document | null;
}

export const SummaryDialog: React.FC<SummaryDialogProps> = ({
  isOpen,
  onOpenChange,
  isMinimized,
  onMinimizeChange,
  selectedDocument,
}) => {
  const { generateSummary, getSummary, isSummaryLoading } = useSummaryGeneration();
  const [localSummary, setLocalSummary] = useState<string | null>(null);

  // Get summary data from global state
  const summaryData = selectedDocument ? getSummary(selectedDocument.id) : null;
  const isLoading = selectedDocument ? isSummaryLoading(selectedDocument.id) : false;

  // Update local summary when global state changes
  useEffect(() => {
    if (summaryData?.content) {
      setLocalSummary(summaryData.content);
    }
  }, [summaryData]);

  // Generate summary when dialog opens and no summary exists
  useEffect(() => {
    if (isOpen && selectedDocument && !summaryData?.content && !isLoading) {
      generateSummary(selectedDocument);
    }
  }, [isOpen, selectedDocument, summaryData, isLoading, generateSummary]);

  const handleCopySummary = () => {
    if (localSummary) {
      navigator.clipboard.writeText(localSummary);
      toast({
        title: 'Copied',
        description: 'Summary copied to clipboard.',
      });
    }
  };

  const handleMaximize = () => {
    onMinimizeChange(false);
  };

  const handleMinimize = () => {
    onMinimizeChange(true);
  };

  const handleClose = () => {
    onOpenChange(false);
  };

  // Show minimized notification if summary is ready
  useEffect(() => {
    if (isMinimized && summaryData?.content && !summaryData.content.includes('Generating')) {
      toast({
        title: 'Summary Ready',
        description: `Summary for ${selectedDocument?.title} is ready. Click to view.`,
        action: (
          <Button
            variant="outline"
            onClick={handleMaximize}
          >
            View
          </Button>
        ),
      });
    }
  }, [isMinimized, summaryData, selectedDocument]);

  // Don't render the dialog if it's minimized
  if (isMinimized) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <div className="flex items-center w-full">
          <DialogTitle className="flex-1">
            Summary for {selectedDocument?.title}
          </DialogTitle>
          <div className="flex flex-row gap-1 items-center">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 p-0"
              onClick={handleMinimize}
              title="Minimize"
            >
              <Minus className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 p-0"
              onClick={handleClose}
              title="Close"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <div className="mt-4 min-h-[120px] flex flex-col gap-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center gap-4 py-8">
              <Loader2 className="h-10 w-10 animate-spin text-blue-600 mb-2" />
              <span className="text-lg font-semibold text-blue-700">Generating summary...</span>
              <span className="text-gray-500 text-sm">
                This may take a few moments for large documents.
              </span>
            </div>
          ) : summaryData?.error ? (
            <div className="flex flex-col items-center justify-center gap-4 py-8">
              <span className="text-red-600 font-semibold">Error generating summary</span>
              <span className="text-gray-500 text-sm">{summaryData.error}</span>
              <Button 
                onClick={() => selectedDocument && generateSummary(selectedDocument)}
                variant="outline"
              >
                Retry
              </Button>
            </div>
          ) : localSummary ? (
            <div className="relative bg-gray-100 rounded p-4 max-h-96 overflow-auto">
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 z-10"
                onClick={handleCopySummary}
                title="Copy summary"
              >
                <Copy className="h-4 w-4" />
              </Button>
              <pre className="whitespace-pre-wrap break-words text-gray-800 pr-8">
                {localSummary}
              </pre>
            </div>
          ) : (
            <span className="text-gray-500">No summary available.</span>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}; 