import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Alert,
  Snackbar,
} from '@mui/material';
import FileUploader from '../../components/common/FileUploader';
import api from '../../services/api';

const UploadTextbook: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    
    // Try to extract title from filename
    if (!title) {
      const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
      setTitle(fileName);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a PDF file to upload.');
      return;
    }
    
    if (!title) {
      setError('Please enter a title for the textbook.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      
      if (author) {
        formData.append('author', author);
      }
      
      if (description) {
        formData.append('description', description);
      }
      
      // Upload textbook
      await api.post('/api/v1/content/upload_textbook', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setSuccess(true);
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/teacher');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload textbook. Please try again.');
      console.error('Error uploading textbook:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" className="page-container">
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Upload Textbook
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload a PDF textbook to generate educational content such as slides and quizzes.
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} noValidate className="form-container">
          <Box className="form-field">
            <FileUploader
              onFileSelect={handleFileSelect}
              accept=".pdf,application/pdf"
              label="Drag and drop a PDF file here, or click to select a file"
              isLoading={loading}
            />
          </Box>
          
          <Box className="form-field">
            <TextField
              required
              fullWidth
              id="title"
              label="Title"
              name="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={loading}
            />
          </Box>
          
          <Box className="form-field">
            <TextField
              fullWidth
              id="author"
              label="Author"
              name="author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              disabled={loading}
            />
          </Box>
          
          <Box className="form-field">
            <TextField
              fullWidth
              id="description"
              label="Description"
              name="description"
              multiline
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={loading}
            />
          </Box>
          
          <Box className="form-actions">
            <Button
              type="button"
              variant="outlined"
              onClick={() => navigate('/teacher')}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !selectedFile || !title}
            >
              {loading ? 'Uploading...' : 'Upload Textbook'}
            </Button>
          </Box>
        </Box>
      </Paper>
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={() => setSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccess(false)} severity="success" sx={{ width: '100%' }}>
          Textbook uploaded successfully! Redirecting...
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UploadTextbook; 