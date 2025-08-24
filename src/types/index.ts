export interface CPDocument {
  id: string;
  name: string;
  content: Buffer;
  type: 'fixture' | 'baseCP' | 'clauses';
  mimeType: string;
  uploadedAt: Date;
}

export interface GeneratedCP {
  id: string;
  name: string;
  content: Buffer;
  createdAt: Date;
  sourceDocuments: {
    fixture: string;
    baseCP: string;
    clauses: string;
  };
}

export interface DocumentProcessingError {
  message: string;
  documentType: string;
  details?: string;
}
