import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, FileText, Eye, Download, Clock } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const mockSearchResults = [
  {
    id: 1,
    title: "Employment Contract - Section 4.2",
    document: "Employment_Contract_2024.pdf",
    snippet: "The employee shall be entitled to twenty (20) days of paid vacation leave per calendar year, which shall accrue at the rate of 1.67 days per month...",
    relevance: 95,
    lastModified: "2024-01-15",
    type: "Contract"
  },
  {
    id: 2,
    title: "Termination Clause - Paragraph 8",
    document: "Service_Agreement_v2.pdf",
    snippet: "Either party may terminate this agreement with thirty (30) days written notice. Upon termination, all obligations shall cease except for those specifically...",
    relevance: 89,
    lastModified: "2024-01-14",
    type: "Agreement"
  },
  {
    id: 3,
    title: "Confidentiality Terms - Article 7",
    document: "NDA_Template.pdf",
    snippet: "The receiving party agrees to maintain in confidence all proprietary information disclosed by the disclosing party and shall not use such information...",
    relevance: 82,
    lastModified: "2024-01-13",
    type: "NDA"
  }
];

export const SearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [documentType, setDocumentType] = useState('');
  const [dateRange, setDateRange] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    
    setIsSearching(true);
    // Simulate search
    setTimeout(() => {
      setIsSearching(false);
    }, 1500);
  };

  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm) return text;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Search Documents</h1>
        <p className="text-muted-foreground">Find specific information across all your legal documents</p>
      </div>

      {/* Search Form */}
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

            {/* Advanced Filters */}
            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-accent/5 rounded-lg">
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
                      <SelectItem value="patent">Patent</SelectItem>
                      <SelectItem value="brief">Brief</SelectItem>
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
                <div className="flex items-end">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setDocumentType('');
                      setDateRange('');
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

      {/* Search Results */}
      {searchTerm && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
            <p className="text-sm text-muted-foreground">
              Found {mockSearchResults.length} results for "{searchTerm}"
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockSearchResults.map((result) => (
              <div key={result.id} className="border rounded-lg p-4 hover:bg-accent/5 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">{result.title}</h3>
                    <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                      <span className="flex items-center">
                        <FileText className="h-3 w-3 mr-1" />
                        {result.document}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {result.lastModified}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {result.relevance}% match
                      </Badge>
                    </div>
                  </div>
                  <Badge variant="outline">{result.type}</Badge>
                </div>
                
                <p 
                  className="text-foreground text-sm leading-relaxed mb-3"
                  dangerouslySetInnerHTML={{ 
                    __html: highlightText(result.snippet, searchTerm) 
                  }}
                />
                
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Eye className="h-3 w-3 mr-1" />
                    View Document
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
