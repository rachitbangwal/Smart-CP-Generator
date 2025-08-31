# Smart Charter Party Generator

A Python-based application that automates the creation of Charter Party (CP) contracts by parsing recap documents and negotiation notes, then intelligently mapping and filling base CP templates while preserving formatting and providing change tracking.

## Features

- **Input Processing**: Accept base CP templates in DOCX format (SHELLTIME)
- **Template Management**: Convert base CP templates to structured format with field identification
- **Intelligence Engine**: Use NLP for intelligent term extraction from recap documents
- **Document Generation**: Fill template fields while maintaining original formatting
- **Web Interface & API**: FastAPI backend with REST endpoints

## Technical Stack

- **Backend**: Python 3.9+, FastAPI
- **NLP**: spaCy
- **Document Processing**: python-docx, PyPDF2, pdfplumber, pdf2docx
- **Database**: SQLite for templates and mappings
- **Deployment**: Podman containerization

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd smart-cp-generator
```

2. **Quick Start:**
```bash
./start.sh
```

**Manual Setup:**

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model (optional, for full NLP features):
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Quick Start (Simple API)
```bash
python simple_app.py
```

Access the application at:
- **API**: http://localhost:8001
- **Health Check**: http://localhost:8001/health
- **API Documentation**: http://localhost:8001/docs (for full app)

## Current Status

⚠️ **Known Issues:**
- Partially Working
- currently unable to replace clauses from fixture recap to Base CP
- replacement of items not Working properly.
- SQLAlchemy compatibility issue with Python 3.13 (simple API works)

## Development Status

The project includes a **complete, production-ready codebase** with:

- ~~**Smart recap parsing** with regex and NLP extraction~~
- ~~**Template field detection** using pattern matching~~
- ~~**Format** maintaining base cp format~~
- ~~**Semantic term mapping** with TF-IDF similarity~~
- ~~**Document generation** with change tracking~~
- **Document Updation** updating clauses according to recap 
- **Multiple output formats** (DOCX, HTML, text)
- **Comprehensive logging** and error handling

## Project Structure

```
smart-cp-generator/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── models/                 # Data models
│   ├── parsers/               # Recap and document parsers
│   ├── preprocessors/         # Template processing
│   ├── generators/            # CP generation engine
│   ├── templates/             # Base CP templates
│   └── utils/                 # Helper functions
├── tests/                     # Comprehensive test suite
├── data/                      # Sample templates and recaps
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints

- `POST /api/upload-template` - Upload base CP template
- `POST /api/upload-recap` - Upload recap document
- `POST /api/generate-cp` - Generate filled charter party
- `GET /api/templates` - List available templates
- `GET /api/download/{file_id}` - Download generated document

## Development

Run tests:
```bash
pytest tests/ -v
```

Run with development server:
```bash
uvicorn src.main:app --reload --log-level debug
```
