import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Send, Copy, ThumbsUp, ThumbsDown, Clock, CheckCircle } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';

const mockQuestions = [
  {
    id: 1,
    question: "What are the key terms in the employment contract?",
    answer: "The key terms in the employment contract include: 1) Job title and responsibilities, 2) Compensation and benefits, 3) Working hours and schedule, 4) Termination conditions, 5) Confidentiality clauses, and 6) Non-compete agreements.",
    confidence: 92,
    timestamp: "2024-01-15 10:30 AM",
    sources: ["Employment_Contract_2024.pdf", "HR_Policy_Manual.pdf"]
  },
  {
    id: 2,
    question: "What are the liability limitations in our service agreement?",
    answer: "The service agreement limits liability to the total amount paid under the contract in the preceding 12 months. It excludes liability for indirect, incidental, or consequential damages.",
    confidence: 88,
    timestamp: "2024-01-14 2:15 PM",
    sources: ["Service_Agreement_v2.pdf"]
  }
];

export const QAPage: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setQuestion('');
    }, 2000);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Question & Answer</h1>
        <p className="text-muted-foreground">Ask questions about your legal documents and get AI-powered answers</p>
      </div>

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
                  disabled={!question.trim() || isLoading}
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

      {/* Question History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {mockQuestions.map((qa) => (
            <div key={qa.id} className="border rounded-lg p-4 space-y-4">
              {/* Question */}
              <div className="flex items-start space-x-3">
                <div className="bg-accent/10 p-2 rounded-lg">
                  <MessageSquare className="h-4 w-4 text-accent" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-foreground">{qa.question}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                    <span className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {qa.timestamp}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      {qa.confidence}% confidence
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Answer */}
              <div className="bg-accent/5 rounded-lg p-4">
                <p className="text-foreground leading-relaxed">{qa.answer}</p>
              </div>

              {/* Sources */}
              <div>
                <p className="text-sm font-medium text-foreground mb-2">Sources:</p>
                <div className="flex flex-wrap gap-2">
                  {qa.sources.map((source, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(qa.answer)}
                >
                  <Copy className="h-3 w-3 mr-1" />
                  Copy
                </Button>
                <Button variant="ghost" size="sm">
                  <ThumbsUp className="h-3 w-3 mr-1" />
                  Helpful
                </Button>
                <Button variant="ghost" size="sm">
                  <ThumbsDown className="h-3 w-3 mr-1" />
                  Not Helpful
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};
