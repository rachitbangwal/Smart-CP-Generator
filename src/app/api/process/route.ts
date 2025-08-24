import { NextRequest, NextResponse } from 'next/server';
import {
  processFixtureRecap,
  processBaseCP,
  processNegotiatedClauses,
  mergeDocuments
} from '@/lib/documentProcessor';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const fixture = formData.get('fixture') as File;
    const baseCP = formData.get('baseCP') as File;
    const clauses = formData.get('clauses') as File;
    
    if (!fixture || !baseCP || !clauses) {
      return NextResponse.json(
        { error: 'Missing required files' },
        { status: 400 }
      );
    }

    // Convert files to buffers and get MIME types
    const fixtureBuffer = Buffer.from(await fixture.arrayBuffer());
    const baseCPBuffer = Buffer.from(await baseCP.arrayBuffer());
    const clausesBuffer = Buffer.from(await clauses.arrayBuffer());

    // Process individual documents with their MIME types
    const [fixtureText, baseCPDoc, clausesList] = await Promise.all([
      processFixtureRecap(fixtureBuffer, fixture.type),
      processBaseCP(baseCPBuffer, baseCP.type),
      processNegotiatedClauses(clausesBuffer, clauses.type),
    ]);

    // Merge documents
    const mergedDocxBuffer = await mergeDocuments(baseCPDoc, fixtureText, clausesList);
    
    return NextResponse.json({
      docx: Buffer.from(mergedDocxBuffer).toString('base64'),
    });
  } catch (error) {
    console.error('Error processing documents:', error);
    return NextResponse.json(
      { error: 'Failed to process documents' },
      { status: 500 }
    );
  }
}
