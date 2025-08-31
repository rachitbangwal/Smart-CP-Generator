"""
FastAPI application with real document processing
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import the real document processor
from document_processor import DocumentProcessor

# Create required directories
BASE_DIR = Path(__file__).parent

UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

IMAGES_DIR = STATIC_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Create templates directory
templates = Jinja2Templates(directory="templates")

# In-memory storage for demo (replace with database in production)
templates_storage: Dict[str, Dict[str, Any]] = {}
recaps_storage: Dict[str, Dict[str, Any]] = {}
documents_storage: Dict[str, Dict[str, Any]] = {}

# Initialize document processor
doc_processor = DocumentProcessor()

app = FastAPI(
    title="Smart Charter Party Generator",
    description="Automate creation of Charter Party contracts from recap documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static files with check_dir=False to allow symlinks and cache busting
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), check_dir=False), name="static")

# Create Request model
class GenerateRequest(BaseModel):
    template_id: str
    recap_id: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request):
    """Serve the generate page"""
    return templates.TemplateResponse("generate.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Smart Charter Party Generator"}

@app.get("/debug/image/{image_name}")
async def serve_image(image_name: str):
    """Debug endpoint to serve images directly"""
    image_path = STATIC_DIR / "images" / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image {image_name} not found")
    return FileResponse(image_path)

@app.post("/api/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    """Upload Charter Party template"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Validate file type
    allowed_types = [".pdf", ".doc", ".docx"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF, DOC, or DOCX files.")
    
    # Generate unique ID
    template_id = str(uuid.uuid4())
    
    # Save file
    file_path = UPLOADS_DIR / f"template_{template_id}{file_ext}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store metadata
    templates_storage[template_id] = {
        "id": template_id,
        "filename": file.filename,
        "path": str(file_path),
        "size": len(content),
        "uploaded_at": time.time()
    }
    
    return {"id": template_id, "filename": file.filename, "size": len(content)}

@app.post("/api/recaps/upload")
async def upload_recap(file: UploadFile = File(...)):
    """Upload recap document"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Validate file type
    allowed_types = [".pdf", ".doc", ".docx"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF, DOC, or DOCX files.")
    
    # Generate unique ID
    recap_id = str(uuid.uuid4())
    
    # Save file
    file_path = UPLOADS_DIR / f"recap_{recap_id}{file_ext}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store metadata
    recaps_storage[recap_id] = {
        "id": recap_id,
        "filename": file.filename,
        "path": str(file_path),
        "size": len(content),
        "uploaded_at": time.time()
    }
    
    return {"id": recap_id, "filename": file.filename, "size": len(content)}

@app.post("/api/generate")
async def generate_charter_party(request: GenerateRequest):
    """Generate Charter Party from template and recap using real document processing"""
    # Validate inputs
    if request.template_id not in templates_storage:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if request.recap_id not in recaps_storage:
        raise HTTPException(status_code=404, detail="Recap document not found")
    
    template_info = templates_storage[request.template_id]
    recap_info = recaps_storage[request.recap_id]
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    try:
        # Use real document processor
        output_path = OUTPUTS_DIR / f"generated_{document_id}.docx"
        
        print(f"Processing template: {template_info['path']}")
        print(f"Processing recap: {recap_info['path']}")
        
        try:
            # Process documents using real NLP and document manipulation
            processed_path, change_report = doc_processor.generate_charter_party(
                template_path=template_info["path"],
                recap_path=recap_info["path"],
                output_path=str(output_path)
            )
        except Exception as e:
            import traceback
            print("Document processing error:")
            print(traceback.format_exc())
            raise
        
        # Add timestamp to change report
        change_report["generation_summary"]["generated_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save change report
        report_path = OUTPUTS_DIR / f"report_{document_id}.json"
        with open(report_path, "w") as f:
            json.dump(change_report, f, indent=2)
        
        # Store document metadata
        documents_storage[document_id] = {
            "id": document_id,
            "template_id": request.template_id,
            "recap_id": request.recap_id,
            "output_path": processed_path,
            "report_path": str(report_path),
            "generated_at": time.time(),
            "status": "completed"
        }
        
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Charter Party generated successfully with real document processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/api/download/{document_id}")
async def download_document(document_id: str):
    """Download generated Charter Party document"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document_info = documents_storage[document_id]
    output_path = document_info["output_path"]
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=output_path,
        filename=f"generated_charter_party_{document_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/report/{document_id}")
async def download_report(document_id: str):
    """Download change report"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document_info = documents_storage[document_id]
    report_path = document_info["report_path"]
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=report_path,
        filename=f"change_report_{document_id}.json",
        media_type="application/json"
    )

@app.get("/api/status/{document_id}")
async def get_document_status(document_id: str):
    """Get document generation status"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return documents_storage[document_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
