import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Upload, Search, FileText, MoreHorizontal, Eye, Download, Trash2, Loader2, Copy, Minus, X } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { toast } from '@/hooks/use-toast';
import { Calendar } from '@/components/ui/calendar';
import { format } from 'date-fns';

const BASE_API_URL = 'http://localhost:5000'; // Adjust if your backend is on a different URL/port

interface Document {
  id: number;
  title: string;
  upload_time: string;
  status: string;
  size: string;
  type: string;
  file_path?: string; // Add file_path from backend
}

function formatFileSize(bytes: number): string {
  if (!bytes || isNaN(bytes)) return 'N/A';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export const DocumentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isPdfLoading, setIsPdfLoading] = useState(false);
  const [isSummaryDialogOpen, setIsSummaryDialogOpen] = useState(false);
  const [isSummaryMinimized, setIsSummaryMinimized] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);
  const [summaryDoc, setSummaryDoc] = useState<Document | null>(null);
  const [summaryCache, setSummaryCache] = useState<{ [docId: number]: string }>({});
  const [isFilterDialogOpen, setIsFilterDialogOpen] = useState(false);
  const [filterType, setFilterType] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterName, setFilterName] = useState<string>('');
  const [filterDate, setFilterDate] = useState<Date | null>(null);
  const [recentOnly, setRecentOnly] = useState(false);
  const [recentDocs, setRecentDocs] = useState<number[]>([]); // store recently accessed doc IDs

  const getAuthHeader = () => {
    const token = localStorage.getItem('jwt_token');
    console.log('Retrieved JWT token from localStorage:', token);
    const header = token ? { 'Authorization': `Bearer ${token}` } : {};
    console.log('Constructed Authorization header:', header);
    return header;
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (!isViewDialogOpen && pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
      setPdfUrl(null);
    }
  }, [isViewDialogOpen, pdfUrl]);

  const fetchDocuments = async () => {
    setIsLoadingDocuments(true);
    try {
      const response = await fetch(`${BASE_API_URL}/documents`, {
        headers: getAuthHeader(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const formattedDocs: Document[] = data.map((doc: any) => ({
        id: doc.id,
        title: doc.title,
        upload_time: new Date(doc.upload_time).toLocaleDateString(),
        status: 'Processed',
        size: doc.size ? formatFileSize(doc.size) : 'N/A',
        type: doc.title.split('.').pop()?.toUpperCase() || 'Unknown',
        file_path: doc.file_path,
      }));
      setDocuments(formattedDocs);
    } catch (error) {
      console.error("Error fetching documents:", error);
      toast({
        title: "Error",
        description: "Failed to load documents. Please ensure you are logged in.",
        variant: "destructive",
      });
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${BASE_API_URL}/upload`);
      const authHeader = getAuthHeader();
      if (authHeader['Authorization']) {
        xhr.setRequestHeader('Authorization', authHeader['Authorization']);
      }

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentCompleted = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(percentCompleted);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          // Check for successful upload based on the actual response format
          if (response.status === "processing" || response.message === "File uploaded successfully") {
            toast({
              title: "Upload Successful",
              description: `${response.title} has been uploaded and is being processed.`, 
            });
            // Add a small delay to ensure server has processed the file
            setTimeout(() => {
              fetchDocuments();
            }, 1000);
          } else {
            toast({
              title: "Upload Failed",
              description: response.message || "An unknown error occurred.",
              variant: "destructive",
            });
          }
        } else {
          const errorResponse = JSON.parse(xhr.responseText);
          toast({
            title: "Upload Failed",
            description: errorResponse.message || `Server responded with status ${xhr.status}.`,
            variant: "destructive",
          });
        }
        setIsUploading(false);
      };

      xhr.onerror = () => {
        setIsUploading(false);
        toast({
          title: "Upload Error",
          description: "Network error or server unreachable.",
          variant: "destructive",
        });
      };

      xhr.send(formData);

    } catch (error) {
      setIsUploading(false);
      console.error("Error uploading file:", error);
      toast({
        title: "Upload Error",
        description: "An unexpected error occurred during upload.",
        variant: "destructive",
      });
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      'Processed': 'bg-green-100 text-green-800',
      'Processing': 'bg-yellow-100 text-yellow-800',
      'Failed': 'bg-red-100 text-red-800'
    };
    return variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800';
  };

  const handleViewDocument = useCallback(async (doc: Document) => {
    setSelectedDocument(doc);
    setIsViewDialogOpen(true);
    setIsPdfLoading(true);
    setPdfUrl(null);
    setRecentDocs((prev) => [doc.id, ...prev.filter(id => id !== doc.id)].slice(0, 10));

    const ext = doc.title.split('.').pop()?.toLowerCase();

    try {
      const token = localStorage.getItem('jwt_token');
      const response = await fetch(`${BASE_API_URL}/documents/view/${doc.title}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        toast({
          title: "View Failed",
          description: "Could not fetch document for preview.",
          variant: "destructive",
        });
        setPdfUrl(null);
        setIsPdfLoading(false);
        return;
      }

      const blob = await response.blob();

      if (ext === 'pdf') {
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      } else if (ext === 'doc' || ext === 'docx') {
        // Download the file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = doc.title;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        toast({
          title: "Download Started",
          description: "Preview not supported for DOC/DOCX. File downloaded.",
        });
        setPdfUrl(null);
        setIsViewDialogOpen(false); // Optionally close the dialog
      } else {
        setPdfUrl(null);
        toast({
          title: "Unsupported File",
          description: "This file type is not supported for preview or download.",
          variant: "destructive",
        });
      }
    } catch (err) {
      toast({
        title: "View Error",
        description: "An error occurred while fetching the document.",
        variant: "destructive",
      });
      setPdfUrl(null);
    } finally {
      setIsPdfLoading(false);
    }
  }, []);

  const handleDeleteDocument = (doc: Document) => {
    setSelectedDocument(doc);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (selectedDocument) {
      try {
        const response = await fetch(`${BASE_API_URL}/documents/${selectedDocument.id}`, {
          method: 'DELETE',
          headers: getAuthHeader(),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        toast({
          title: "Document Deleted",
          description: `${selectedDocument.title} has been successfully deleted.`, 
        });
        setDocuments(prevDocs => prevDocs.filter(doc => doc.id !== selectedDocument.id));
        setIsDeleteDialogOpen(false);
        setSelectedDocument(null);
      } catch (error) {
        console.error("Error deleting document:", error);
        toast({
          title: "Deletion Failed",
          description: `Failed to delete ${selectedDocument.title}. ${error instanceof Error ? error.message : String(error)}`,
          variant: "destructive",
        });
        setIsDeleteDialogOpen(false);
      }
    }
  };

  const handleDownload = async (doc: Document) => {
    if (!doc.title) {
      toast({
        title: "Download Failed",
        description: "Document title is missing.",
        variant: "destructive",
      });
      return;
    }
    
    try {
      const response = await fetch(`${BASE_API_URL}/documents/download/${doc.title}`, {
        headers: getAuthHeader(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.title; // Use the document title as the filename
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: "Download Started",
        description: `Downloading ${doc.title}...`,
      });
    } catch (error) {
      console.error("Error downloading document:", error);
      toast({
        title: "Download Failed",
        description: `Failed to download ${doc.title}. ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  };

  const handleViewSummary = async (doc: Document) => {
    setSummaryDoc(doc);
    setIsSummaryDialogOpen(true);
    setIsSummaryMinimized(false);
    setIsSummaryLoading(true);
    setSummary(null);
    if (summaryCache[doc.id]) {
      setSummary(summaryCache[doc.id]);
      setIsSummaryLoading(false);
      return;
    }
    try {
      const response = await fetch(`${BASE_API_URL}/documents/summary/${doc.id}`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSummary(data.summary);
      setSummaryCache((prev) => ({ ...prev, [doc.id]: data.summary }));
      // Notify user if minimized
      if (isSummaryMinimized) {
        toast({
          title: 'Summary Ready',
          description: `Summary for ${doc.title} is ready. Click to view.`,
          action: (
            <Button
              variant="outline"
              onClick={() => {
                setIsSummaryDialogOpen(true);
                setIsSummaryMinimized(false);
              }}
            >
              View
            </Button>
          ),
        });
      }
    } catch (error) {
      toast({
        title: 'Summary Error',
        description: error instanceof Error ? error.message : String(error),
        variant: 'destructive',
      });
      setSummary(null);
    } finally {
      setIsSummaryLoading(false);
    }
  };

  const handleCopySummary = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      toast({
        title: 'Copied',
        description: 'Summary copied to clipboard.',
      });
    }
  };

  const filteredDocuments = documents.filter(doc => {
    // Filter by name
    if (filterName && !doc.title.toLowerCase().includes(filterName.toLowerCase())) return false;
    // Filter by type
    if (filterType && doc.type.toLowerCase() !== filterType.toLowerCase()) return false;
    // Filter by status
    if (filterStatus && doc.status.toLowerCase() !== filterStatus.toLowerCase()) return false;
    // Filter by date
    if (filterDate && doc.upload_time !== format(filterDate, 'M/d/yyyy')) return false;
    // Filter by recent
    if (recentOnly && !recentDocs.includes(doc.id)) return false;
    // Also apply search term
    if (searchTerm && !doc.title.toLowerCase().includes(searchTerm.toLowerCase()) && !doc.type.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">Manage and analyze your legal documents</p>
        </div>
        <div className="flex items-center gap-4">
          {isUploading && (
            <div className="w-48">
              <Progress value={uploadProgress} className="h-2" />
              <p className="text-sm text-gray-600 mt-1">{uploadProgress}%</p>
            </div>
          )}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.doc,.docx"
          />
          <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleUploadClick}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={handleUploadClick}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Drag and drop your documents here
            </h3>
            <p className="text-gray-600 mb-4">
              or click to browse files. Supports only PDF files up to 10MB
            </p>
            <Button variant="outline">
              Browse Files
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button variant="outline" onClick={() => setIsFilterDialogOpen(true)}>Filter</Button>
          </div>

          {isLoadingDocuments ? (
            <div className="flex justify-center items-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <p className="ml-3 text-lg text-gray-600">Loading documents...</p>
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-gray-500">No documents found. Upload one to get started!</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="font-medium">{doc.title}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{doc.type}</Badge>
                    </TableCell>
                    <TableCell>{doc.upload_time}</TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(doc.status)}>
                        {doc.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{doc.size}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem onClick={() => handleViewDocument(doc)}>
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDownload(doc)}>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleViewSummary(doc)}>
                            <FileText className="h-4 w-4 mr-2" />
                            View Summary
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-red-600"
                            onClick={() => handleDeleteDocument(doc)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* View Document Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
          <div className="flex items-center w-full">
            <DialogTitle className="flex-1">{selectedDocument?.title}</DialogTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 p-0"
              onClick={() => setIsViewDialogOpen(false)}
              title="Close"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex-1 overflow-auto mt-4">
            {isPdfLoading ? (
              <div className="flex items-center justify-center h-full">
                <span className="text-gray-500">Loading document preview...</span>
              </div>
            ) : selectedDocument?.title && pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-full"
                title={selectedDocument.title}
              />
            ) : (
              <p>No document content available for preview.</p>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the document
              "{selectedDocument?.title}".
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Summary Dialog */}
      <Dialog open={isSummaryDialogOpen && !isSummaryMinimized} onOpenChange={setIsSummaryDialogOpen}>
        <DialogContent className="max-w-2xl" >
          <div className="flex items-center w-full">
            <DialogTitle className="flex-1">Summary for {summaryDoc?.title}</DialogTitle>
            <div className="flex flex-row gap-1 items-center">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 p-0"
                onClick={() => setIsSummaryMinimized(true)}
                title="Minimize"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 p-0"
                onClick={() => setIsSummaryDialogOpen(false)}
                title="Close"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="mt-4 min-h-[120px] flex flex-col gap-4">
            {isSummaryLoading ? (
              <div className="flex flex-col items-center justify-center gap-4 py-8">
                <Loader2 className="h-10 w-10 animate-spin text-blue-600 mb-2" />
                <span className="text-lg font-semibold text-blue-700">Generating summary...</span>
                <span className="text-gray-500 text-sm">This may take a few moments for large documents.</span>
              </div>
            ) : summary ? (
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
                <pre className="whitespace-pre-wrap break-words text-gray-800 pr-8">{summary}</pre>
              </div>
            ) : (
              <span className="text-gray-500">No summary available.</span>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Filter Dialog */}
      <Dialog open={isFilterDialogOpen} onOpenChange={setIsFilterDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Filter Documents</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <Input value={filterName} onChange={e => setFilterName(e.target.value)} placeholder="Document name" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <Input value={filterType} onChange={e => setFilterType(e.target.value)} placeholder="e.g. PDF, DOCX" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <Input value={filterStatus} onChange={e => setFilterStatus(e.target.value)} placeholder="e.g. Processed" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Upload Date</label>
              <Calendar selected={filterDate} onSelect={setFilterDate} />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" checked={recentOnly} onChange={e => setRecentOnly(e.target.checked)} id="recentOnly" />
              <label htmlFor="recentOnly" className="text-sm">Show only recently accessed</label>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => { setFilterType(''); setFilterStatus(''); setFilterName(''); setFilterDate(null); setRecentOnly(false); }}>Clear</Button>
              <Button onClick={() => setIsFilterDialogOpen(false)}>Apply</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};
