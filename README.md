# Smart CP Generator

A web-based platform that automates the creation of Charter Party (CP) contracts by merging multiple input documents into a standardized format.

## Features

- Upload and process three types of documents:
  - Fixture Recap
  - Base Charter Party
  - Negotiated Clauses
- Automatic document merging with proper formatting
- Generate output in both DOCX and PDF formats
- Modern, responsive user interface
- Real-time document processing status

## Technical Stack

- **Frontend**: Next.js with TypeScript and Material-UI
- **Document Processing**: 
  - mammoth.js (DOCX processing)
  - docx (DOCX generation)
  - pdf-lib (PDF generation)
- **File Handling**: react-dropzone
- **Styling**: Material-UI components and Tailwind CSS

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

4. **Start Production Server**
   ```bash
   npm start
   ```

## Usage

1. Upload the required documents:
   - Fixture Recap (DOCX/DOC)
   - Base Charter Party (DOCX/DOC)
   - Negotiated Clauses (DOCX/DOC)

2. Click "Generate Charter Party" to process the documents

3. Download the merged document in either DOCX or PDF format

## Project Structure

```
src/
├── app/
│   ├── api/
│   │   └── process/
│   │       └── route.ts    # API endpoint for document processing
│   ├── layout.tsx          # Root layout component
│   └── page.tsx           # Main page component
├── components/
│   ├── DocumentGenerator.tsx  # Main document upload and processing
│   ├── DocumentPreview.tsx    # Generated document preview/download
│   └── FileUpload.tsx        # File upload component
├── lib/
│   └── documentProcessor.ts   # Document processing utilities
└── types/
    └── index.ts              # TypeScript type definitions
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
