import { useState } from 'react';
import { Box, Paper, Tabs, Tab, Button } from '@mui/material';
import { saveAs } from 'file-saver';

interface DocumentPreviewProps {
  docxData: string;
}

export function DocumentPreview({ docxData }: DocumentPreviewProps) {
  const handleDownload = () => {
    const buffer = Buffer.from(docxData, 'base64');
    const blob = new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });
    saveAs(blob, 'charter-party.docx');
  };

  return (
    <Paper sx={{ mt: 3, p: 2 }}>
      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleDownload}
        >
          Download DOCX
        </Button>
      </Box>
    </Paper>
  );
}
