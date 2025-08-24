import { useState } from 'react';
import { Box, Button, Container, Typography, CircularProgress } from '@mui/material';
import { FileUpload } from './FileUpload';
import { DocumentPreview } from './DocumentPreview';

interface DocumentState {
  fixture: File | null;
  baseCP: File | null;
  clauses: File | null;
}

interface GeneratedDocuments {
  docx: string;
}

export function DocumentGenerator() {
  const [documents, setDocuments] = useState<DocumentState>({
    fixture: null,
    baseCP: null,
    clauses: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [generatedDocs, setGeneratedDocs] = useState<GeneratedDocuments | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = (type: keyof DocumentState) => (file: File) => {
    setDocuments((prev) => ({ ...prev, [type]: file }));
    setGeneratedDocs(null);
    setError(null);
  };

  const handleGenerate = async () => {
    if (!documents.fixture || !documents.baseCP || !documents.clauses) {
      setError('Please upload all required documents');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('fixture', documents.fixture);
      formData.append('baseCP', documents.baseCP);
      formData.append('clauses', documents.clauses);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process documents');
      }

      const result = await response.json();
      setGeneratedDocs(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const acceptedFormats = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/msword': ['.doc'],
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Smart CP Generator
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center">
          Upload your documents to generate a merged Charter Party contract
        </Typography>

        <Box display="grid" gridTemplateColumns="repeat(12, 1fr)" gap={3} sx={{ mt: 2 }}>
          <Box gridColumn={{ xs: 'span 12', md: 'span 4' }}>
            <FileUpload
              documentType="fixture"
              onFileAccepted={handleFileUpload('fixture')}
              accept={acceptedFormats}
            />
          </Box>
          <Box gridColumn={{ xs: 'span 12', md: 'span 4' }}>
            <FileUpload
              documentType="baseCP"
              onFileAccepted={handleFileUpload('baseCP')}
              accept={acceptedFormats}
            />
          </Box>
          <Box gridColumn={{ xs: 'span 12', md: 'span 4' }}>
            <FileUpload
              documentType="clauses"
              onFileAccepted={handleFileUpload('clauses')}
              accept={acceptedFormats}
            />
          </Box>
        </Box>

        {error && (
          <Typography color="error" align="center" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleGenerate}
            disabled={!documents.fixture || !documents.baseCP || !documents.clauses || isLoading}
          >
            {isLoading ? (
              <>
                <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                Processing...
              </>
            ) : (
              'Generate Charter Party'
            )}
          </Button>
        </Box>

        {generatedDocs && (
          <DocumentPreview
            docxData={generatedDocs.docx}
          />
        )}
      </Box>
    </Container>
  );
}
