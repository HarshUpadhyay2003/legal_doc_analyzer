import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Send, Copy, ThumbsUp, ThumbsDown, Clock, CheckCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

const BASE_API_URL = 'http://localhost:5000';

interface Document {
  id: number;
  title: string;
}

interface PreviousQuestion {
  id: number;
  question: string;
  answer: string;
  created_at?: string; // Add this
  score?: number;
}

export const QAPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previousQuestions, setPreviousQuestions] = useState<PreviousQuestion[]>([]);
  const [isLoadingPrevious, setIsLoadingPrevious] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true); // Add loading state

  useEffect(() => {
    const fetchDocuments = async () => {
      setError(null);
      setIsLoadingDocuments(true); // Set loading
      try {
        const token = localStorage.getItem('jwt_token');
        const response = await fetch(`${BASE_API_URL}/documents`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });
        if (!response.ok) {
          throw new Error('Failed to fetch documents.');
        }
        const docs = await response.json();
        setDocuments(docs.map((doc: any) => ({ id: doc.id, title: doc.title })));
      } catch (err: any) {
        setError(err.message || 'Error fetching documents.');
      } finally {
        setIsLoadingDocuments(false); // Done loading
      }
    };
    fetchDocuments();
  }, []);

  // Fetch previous questions when document is selected
  useEffect(() => {
    if (selectedDocId) {
      fetchPreviousQuestions(selectedDocId);
    } else {
      setPreviousQuestions([]);
    }
  }, [selectedDocId]);

  const fetchPreviousQuestions = async (docId: number) => {
    setIsLoadingPrevious(true);
    try {
      const token = localStorage.getItem('jwt_token');
      const response = await fetch(`${BASE_API_URL}/previous-questions/${docId}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setPreviousQuestions(data.questions || []);
        } else {
          console.error('Failed to fetch previous questions:', data.error);
          setPreviousQuestions([]);
        }
      } else {
        console.error('Error fetching previous questions:', response.status);
        setPreviousQuestions([]);
      }
    } catch (err) {
      console.error('Error fetching previous questions:', err);
      setPreviousQuestions([]);
    } finally {
      setIsLoadingPrevious(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnswer(null);
    setError(null);
    if (!question.trim() || !selectedDocId) return;
    setIsLoading(true);
    try {
      const token = localStorage.getItem('jwt_token');
      const response = await fetch(`${BASE_API_URL}/ask-question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ document_id: selectedDocId, question }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to get answer.');
      }
      setAnswer(data.answer);
      
      // Refresh the previous questions list to include the new question
      if (selectedDocId) {
        fetchPreviousQuestions(selectedDocId);
      }
      
      setQuestion(''); // Clear the question input
    } catch (err: any) {
      setError(err.message || 'Error getting answer.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatTimestamp = (timestamp: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return isNaN(date.getTime()) ? '' : date.toLocaleString();
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Question & Answer</h1>
        <p className="text-muted-foreground">Ask questions about your legal documents and get AI-powered answers</p>
      </div>

      {/* Document Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Document</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingDocuments ? (
            <div className="text-gray-500">Loading documents...</div>
          ) : (
          <select
            className="w-full border rounded p-2 mb-2 bg-white text-black dark:bg-gray-800 dark:text-white dark:border-gray-600"
            value={selectedDocId ?? ''}
            onChange={e => setSelectedDocId(Number(e.target.value) || null)}
              disabled={isLoadingDocuments || documents.length === 0}
          >
            <option value="">-- Select a document --</option>
            {documents.map(doc => (
              <option key={doc.id} value={doc.id}>{doc.title}</option>
            ))}
          </select>
          )}
        </CardContent>
      </Card>

      {/* Question Input */}
      <Card>
        <CardHeader>
          <CardTitle>Ask a Question</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="Type your question here... (e.g., What are the termination clauses in my contract?)"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={4}
              className="resize-none"
              disabled={!selectedDocId}
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                {question.length}/500 characters
              </span>
              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setQuestion('')}
                  disabled={!question.trim()}
                >
                  Clear
                </Button>
                <Button
                  type="submit"
                  disabled={!question.trim() || isLoading || !selectedDocId}
                  className="bg-accent hover:bg-accent/90"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Ask Question
                    </>
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Previous Questions Section */}
      {selectedDocId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Previous Questions
              {isLoadingPrevious && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-accent"></div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {previousQuestions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No previous questions for this document.</p>
                <p className="text-sm">Ask your first question above!</p>
              </div>
            ) : (
              <Accordion type="single" collapsible className="w-full">
                {previousQuestions.map((prevQ, index) => (
                  <AccordionItem key={prevQ.id} value={`item-${index}`}>
                    <AccordionTrigger className="text-left hover:no-underline">
                      <div className="flex items-center justify-between w-full pr-4">
                        <div className="flex-1 text-left">
                          <p className="font-medium text-foreground">{prevQ.question}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Clock className="h-3 w-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">
                              {formatTimestamp(prevQ.created_at)}
                            </span>
                            {prevQ.score !== undefined && (
                              <Badge variant="secondary" className="text-xs">
                                Score: {(prevQ.score * 100).toFixed(0)}%
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="pt-4 pb-2">
                        <div className="flex items-start space-x-3">
                          <div className="bg-accent/10 p-2 rounded-lg">
                            <MessageSquare className="h-4 w-4 text-accent" />
                          </div>
                          <div className="flex-1">
                            <p className="text-foreground">{prevQ.answer}</p>
                            <div className="flex items-center space-x-2 mt-2">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => handleCopy(prevQ.answer)}
                              >
                                <Copy className="h-3 w-3 mr-1" />
                                Copy
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            )}
          </CardContent>
        </Card>
      )}

      {/* Current Answer Display */}
      {answer && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Answer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-start space-x-3">
              <div className="bg-accent/10 p-2 rounded-lg">
                <MessageSquare className="h-4 w-4 text-accent" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-foreground">{answer}</p>
                <div className="flex items-center space-x-2 mt-2">
                  <Button variant="ghost" size="sm" onClick={() => handleCopy(answer)}>
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <div className="text-red-600 font-medium">{error}</div>
      )}
    </div>
  );
};
