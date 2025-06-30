import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, FileText, Eye, Download, Clock, MessageSquare } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const LOCAL_STORAGE_KEY = 'legal-doc-search-state';

export const SearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [documentType, setDocumentType] = useState('');
  const [dateRange, setDateRange] = useState('');
  const [searchIn, setSearchIn] = useState<'both' | 'filename' | 'content'>('both');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewDocId, setViewDocId] = useState<number | null>(null);
  const [viewQAId, setViewQAId] = useState<number | null>(null);

  // Restore state on mount
  useEffect(() => {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSearchTerm(parsed.searchTerm || '');
        setShowAdvanced(parsed.showAdvanced || false);
        setDocumentType(parsed.documentType || '');
        setDateRange(parsed.dateRange || '');
        setSearchIn(parsed.searchIn || 'both');
        setResults(parsed.results || null);
        setViewDocId(parsed.viewDocId || null);
        setViewQAId(parsed.viewQAId || null);
      } catch (e) {
        // Ignore parse errors
      }
    }
  }, []);

  // Persist state on any change
  useEffect(() => {
    localStorage.setItem(
      LOCAL_STORAGE_KEY,
      JSON.stringify({
        searchTerm,
        showAdvanced,
        documentType,
        dateRange,
        searchIn,
        results,
        viewDocId,
        viewQAId,
      })
    );
  }, [searchTerm, showAdvanced, documentType, dateRange, searchIn, results, viewDocId, viewQAId]);

  // When searchTerm changes, if it is cleared, also clear results and error
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setResults(null);
      setError(null);
    }
  }, [searchTerm]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    setIsSearching(true);
    setError(null);
    setResults(null);
    setViewDocId(null);
    setViewQAId(null);
    try {
      const token = localStorage.getItem('jwt_token');
      const res = await fetch(`http://localhost:5000/search?q=${encodeURIComponent(searchTerm)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Search failed');
      }
      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm) return text;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  };

  const filteredDocuments = results ? results.documents.filter((doc: any) => {
    let typeMatch = true;
    if (documentType) {
      typeMatch = (doc.type && doc.type.toLowerCase() === documentType) ||
        (doc.title && doc.title.toLowerCase().includes(documentType));
    }
    let searchMatch = true;
    const keyword = searchTerm.toLowerCase();
    if (searchIn === 'filename') {
      searchMatch = doc.title && doc.title.toLowerCase().includes(keyword);
    } else if (searchIn === 'content') {
      searchMatch = doc.summary && doc.summary.toLowerCase().includes(keyword);
    } else {
      searchMatch = (doc.title && doc.title.toLowerCase().includes(keyword)) || (doc.summary && doc.summary.toLowerCase().includes(keyword));
    }
    return typeMatch && searchMatch;
  }) : [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Search Documents</h1>
        <p className="text-muted-foreground">Find specific information across all your legal documents</p>
      </div>
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search for terms, clauses, or phrases..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button
                type="submit"
                disabled={!searchTerm.trim() || isSearching}
                className="bg-accent hover:bg-accent/90"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>
            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-accent/5 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Document Type
                  </label>
                  <Select value={documentType} onValueChange={setDocumentType}>
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="agreement">Agreement</SelectItem>
                      <SelectItem value="nda">NDA</SelectItem>
                      <SelectItem value="memo">Legal Memo</SelectItem>
                      <SelectItem value="policy">Policy</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Date Range
                  </label>
                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any time" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="today">Today</SelectItem>
                      <SelectItem value="week">This week</SelectItem>
                      <SelectItem value="month">This month</SelectItem>
                      <SelectItem value="year">This year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Search In
                  </label>
                  <Select value={searchIn} onValueChange={v => setSearchIn(v as any)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Both" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="both">Both</SelectItem>
                      <SelectItem value="filename">Filename</SelectItem>
                      <SelectItem value="content">Content</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setDocumentType('');
                      setDateRange('');
                      setSearchIn('both');
                    }}
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            )}
          </form>
        </CardContent>
      </Card>
      {error && (
        <div className="text-red-600 bg-red-50 border border-red-200 rounded p-4">
          {error}
        </div>
      )}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
            <p className="text-sm text-muted-foreground">
              Found {filteredDocuments.length} documents and {results.qa.length} Q&A for "{searchTerm}"
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {filteredDocuments.map((result: any) => (
              <div key={result.id} className="border rounded-lg p-4 hover:bg-accent/5 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1" dangerouslySetInnerHTML={{ __html: highlightText(result.title, searchTerm) }} />
                    <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                      <span className="flex items-center">
                        <FileText className="h-3 w-3 mr-1" />
                        {result.title}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {result.upload_time}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {Math.round(result.match_score * 100)}% match
                      </Badge>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setViewDocId(viewDocId === result.id ? null : result.id)}>
                    <Eye className="h-3 w-3 mr-1" />
                    {viewDocId === result.id ? 'Hide' : 'View'}
                  </Button>
                </div>
                <p className="text-foreground text-sm leading-relaxed mb-3" dangerouslySetInnerHTML={{ __html: highlightText(result.summary, searchTerm) }} />
                {viewDocId === result.id && (
                  <div className="bg-accent/10 p-3 rounded mt-2">
                    <strong>Full Summary:</strong>
                    <div className="whitespace-pre-line mt-1">{result.summary}</div>
                  </div>
                )}
              </div>
            ))}
            {results.qa.length > 0 && <hr className="my-4" />}
            {results.qa.map((qa: any) => (
              <div key={qa.id} className="border rounded-lg p-4 hover:bg-accent/5 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1 flex items-center">
                      <MessageSquare className="h-4 w-4 mr-2 text-blue-500" />
                      <span dangerouslySetInnerHTML={{ __html: highlightText(qa.question, searchTerm) }} />
                    </h3>
                    <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                      <span>Doc ID: {qa.document_id}</span>
                      <span>{qa.created_at}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setViewQAId(viewQAId === qa.id ? null : qa.id)}>
                    <Eye className="h-3 w-3 mr-1" />
                    {viewQAId === qa.id ? 'Hide' : 'View'}
                  </Button>
                </div>
                <p className="text-foreground text-sm leading-relaxed mb-3" dangerouslySetInnerHTML={{ __html: highlightText(qa.answer, searchTerm) }} />
                {viewQAId === qa.id && (
                  <div className="bg-accent/10 p-3 rounded mt-2">
                    <strong>Full Answer:</strong>
                    <div className="whitespace-pre-line mt-1">{qa.answer}</div>
                  </div>
                )}
              </div>
            ))}
            {filteredDocuments.length === 0 && results.qa.length === 0 && (
              <div className="text-muted-foreground text-center py-8">No results found.</div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
