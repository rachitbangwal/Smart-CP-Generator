'use client';

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { DocumentGenerator } from '@/components/DocumentGenerator';

const theme = createTheme({
  // You can customize the theme here
});

export default function Home() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DocumentGenerator />
    </ThemeProvider>
  );
}
