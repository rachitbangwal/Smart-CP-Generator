declare module 'pdfjs-dist' {
  export const GlobalWorkerOptions: {
    workerSrc: string;
  };

  export const version: string;

  export interface PDFDocumentProxy {
    numPages: number;
    getPage(pageNumber: number): Promise<PDFPageProxy>;
  }

  export interface PDFPageProxy {
    getTextContent(): Promise<PDFTextContent>;
  }

  export interface PDFTextContent {
    items: Array<{
      str: string;
      dir: string;
      transform: number[];
      width: number;
      height: number;
      fontName: string;
    }>;
  }

  export function getDocument(data: { data: Buffer }): PDFDocumentLoadingTask;

  export interface PDFDocumentLoadingTask {
    promise: Promise<PDFDocumentProxy>;
  }
}
