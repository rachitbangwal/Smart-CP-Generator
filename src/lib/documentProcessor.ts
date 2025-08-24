import { Buffer } from 'buffer';
import mammoth from 'mammoth';
import { Document, Paragraph, TextRun, Packer } from 'docx';
import { CPDocument } from '../types';

class DocumentProcessingError extends Error {
  documentType: string;
  details?: string;

  constructor({ message, documentType, details }: { message: string; documentType: string; details?: string }) {
    super(message);
    this.documentType = documentType;
    this.details = details;
    this.name = 'DocumentProcessingError';
  }
}

export async function processFixtureRecap(file: Buffer): Promise<string> {
  try {
    const result = await mammoth.extractRawText({ buffer: file });
    return result.value;
  } catch (error) {
    throw new DocumentProcessingError({
      message: 'Failed to process fixture recap',
      documentType: 'fixture',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

export async function processBaseCP(file: Buffer): Promise<Document> {
  try {
    const result = await mammoth.extractRawText({ buffer: file });
    // Convert to docx Document object for manipulation
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            children: [
              new TextRun(result.value)
            ],
          }),
        ],
      }],
    });
    return doc;
  } catch (error) {
    throw new DocumentProcessingError({
      message: 'Failed to process base CP',
      documentType: 'baseCP',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

export async function processNegotiatedClauses(file: Buffer): Promise<string[]> {
  try {
    const result = await mammoth.extractRawText({ buffer: file });
    // Split into individual clauses based on numbering or formatting
    return result.value.split(/\n(?=\d+\.)/);
  } catch (error) {
    throw new DocumentProcessingError({
      message: 'Failed to process negotiated clauses',
      documentType: 'clauses',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

export async function mergeDocuments(
  baseCP: Document,
  fixtureRecap: string,
  negotiatedClauses: string[]
): Promise<Buffer> {
  try {
    // Create a new document with all the content
    const mergedDoc = new Document({
      sections: [{
        properties: {},
        children: [
          // Fixture Recap Section
          new Paragraph({
            children: [new TextRun('FIXTURE RECAP')],
            heading: 'Heading1',
          }),
          new Paragraph({
            children: [new TextRun(fixtureRecap)],
          }),
          // Separator
          new Paragraph({
            children: [new TextRun('BASE CHARTER PARTY')],
            heading: 'Heading1',
          }),
          // Base CP Content as a new paragraph
          new Paragraph({
            children: [new TextRun(await baseCPToText(baseCP))],
          }),
          // Additional Clauses Section
          new Paragraph({
            children: [new TextRun('ADDITIONAL CLAUSES')],
            heading: 'Heading1',
          }),
          ...negotiatedClauses.map(
            clause =>
              new Paragraph({
                children: [new TextRun(clause)],
              })
          ),
        ],
      }],
    });

    return await Packer.toBuffer(mergedDoc);
  } catch (error) {
    throw new Error(
      `Failed to merge documents: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// Helper function to extract text from a Document
async function baseCPToText(doc: Document): Promise<string> {
  const buffer = await Packer.toBuffer(doc);
  const result = await mammoth.extractRawText({ buffer });
  return result.value;
}


