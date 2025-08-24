import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography } from '@mui/material';

interface FileUploadProps {
  onFileAccepted: (file: File) => void;
  documentType: 'fixture' | 'baseCP' | 'clauses';
  accept?: Record<string, string[]>;
}

export function FileUpload({ onFileAccepted, documentType, accept }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0]);
      }
    },
    [onFileAccepted]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles: 1,
  });

  const getDocumentTypeName = (type: string) => {
    switch (type) {
      case 'fixture':
        return 'Fixture Recap';
      case 'baseCP':
        return 'Base Charter Party';
      case 'clauses':
        return 'Negotiated Clauses';
      default:
        return type;
    }
  };

  return (
    <Paper
      {...getRootProps()}
      sx={{
        p: 3,
        textAlign: 'center',
        cursor: 'pointer',
        bgcolor: isDragActive ? 'action.hover' : 'background.paper',
        borderStyle: 'dashed',
        borderWidth: 2,
        borderColor: isDragActive ? 'primary.main' : 'divider',
      }}
    >
      <input {...getInputProps()} />
      <Typography variant="h6" gutterBottom>
        {getDocumentTypeName(documentType)}
      </Typography>
      <Typography color="textSecondary">
        {isDragActive
          ? 'Drop the file here'
          : 'Drag and drop a file here, or click to select'}
      </Typography>
    </Paper>
  );
}
