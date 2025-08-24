import PDFParser from 'pdf2json';

export async function extractTextFromPDF(buffer: Buffer): Promise<string> {
  return new Promise((resolve, reject) => {
    try {
      const pdfParser = new PDFParser();

      pdfParser.on('pdfParser_dataReady', (pdfData) => {
        try {
          const text = pdfData.Pages.map(page => 
            page.Texts.map(text => 
              decodeURIComponent(text.R[0].T)
            ).join(' ')
          ).join('\n');
          resolve(text);
        } catch (err) {
          reject(new Error(`Failed to process PDF data: ${err instanceof Error ? err.message : 'Unknown error'}`));
        }
      });

      pdfParser.on('pdfParser_dataError', (errData) => {
        reject(new Error(`PDF parsing error: ${errData.parserError}`));
      });

      pdfParser.parseBuffer(buffer);
    } catch (error) {
      reject(new Error(`Failed to extract text from PDF: ${error instanceof Error ? error.message : 'Unknown error'}`));
    }
  });
}
