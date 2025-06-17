import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, ListItem, ListItemText, Typography } from '@mui/material';

const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    setError(''); // Clear previous errors

    try {
      // Step 1: Upload file
      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: formData
      });

      if (!uploadResponse.ok) {
        const err = await uploadResponse.json();
        setError(err.error || 'Upload failed');
        return;
      }

      const uploadData = await uploadResponse.json();
      setError('');
      // Add document to the list immediately with loading state
      setDocuments(prev => [{
        id: uploadData.document_id,
        title: uploadData.title,
        summary: 'Processing...',
        upload_time: new Date().toISOString(),
        status: 'processing'
      }, ...prev]);

      // Step 2: Process document
      const processResponse = await fetch(`/api/process-document/${uploadData.document_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        }
      });

      if (!processResponse.ok) {
        const err = await processResponse.json();
        setError(err.error || 'Processing failed');
        return;
      }

      setError('');
      // Update document in the list with processed content
      setDocuments(prev => prev.map(doc => 
        doc.id === uploadData.document_id 
          ? { ...doc, status: 'completed' }
          : doc
      ));

      // Refresh the documents list to get the full content
      fetchDocuments();

    } catch (error) {
      console.error('Error:', error);
      setError('Failed to upload or process document');
    }
  };

  const fetchDocuments = async () => {
    // Implementation of fetchDocuments function
  };

  return (
    <div>
      {error && (
        <Box sx={{ color: 'red', mb: 2 }}>{error}</Box>
      )}
      {/* ... rest of the component content ... */}
    </div>
  );
};

export default DocumentsPage; 