"""
Smart Charter Party Generator - Main FastAPI Application
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

import structlog
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .models.base import CPTemplate, RecapDocument, GeneratedCP
from .models.database import get_db, create_tables
from .parsers.recap_parser import RecapParser
from .parsers.template_parser import TemplateParser
from .preprocessors.template_preprocessor import TemplatePreprocessor
from .generators.cp_generator import CPGenerator
from .utils.file_manager import FileManager
from .utils.logger import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger()

# Create FastAPI app
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

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
file_manager = FileManager()
recap_parser = RecapParser()
template_parser = TemplateParser()
template_preprocessor = TemplatePreprocessor()
cp_generator = CPGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize database and components on startup"""
    logger.info("Starting Smart Charter Party Generator")
    create_tables()
    logger.info("Application started successfully")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Smart Charter Party Generator"}

@app.post("/api/upload-template")
async def upload_template(
    file: UploadFile = File(...),
    template_type: str = "GENCON",
    db = Depends(get_db)
):
    """Upload and process a base CP template"""
    try:
        logger.info(f"Uploading template: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are supported.")
        
        # Save uploaded file
        file_path = await file_manager.save_upload(file, "templates")
        
        # Parse and preprocess template
        parsed_template = await template_parser.parse(file_path)
        preprocessed_template = await template_preprocessor.process(parsed_template, template_type)
        
        # Save to database
        template = CPTemplate(
            name=file.filename,
            type=template_type,
            file_path=str(file_path),
            processed_data=preprocessed_template
        )
        
        template_id = template.save(db)
        
        logger.info(f"Template processed successfully: {template_id}")
        return {
            "template_id": template_id,
            "filename": file.filename,
            "type": template_type,
            "fields_detected": len(preprocessed_template.get("fields", [])),
            "status": "processed"
        }
        
    except Exception as e:
        logger.error(f"Error uploading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing template: {str(e)}")

@app.post("/api/upload-recap")
async def upload_recap(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """Upload and parse a recap document"""
    try:
        logger.info(f"Uploading recap: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT files are supported.")
        
        # Save uploaded file
        file_path = await file_manager.save_upload(file, "recaps")
        
        # Parse recap document
        parsed_recap = await recap_parser.parse(file_path)
        
        # Save to database
        recap = RecapDocument(
            name=file.filename,
            file_path=str(file_path),
            parsed_data=parsed_recap
        )
        
        recap_id = recap.save(db)
        
        logger.info(f"Recap processed successfully: {recap_id}")
        return {
            "recap_id": recap_id,
            "filename": file.filename,
            "terms_extracted": len(parsed_recap.get("terms", [])),
            "status": "processed"
        }
        
    except Exception as e:
        logger.error(f"Error uploading recap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing recap: {str(e)}")

@app.post("/api/generate-cp")
async def generate_charter_party(
    template_id: int,
    recap_id: int,
    output_format: str = "docx",
    db = Depends(get_db)
):
    """Generate a charter party from template and recap"""
    try:
        logger.info(f"Generating CP: template_id={template_id}, recap_id={recap_id}")
        
        # Retrieve template and recap from database
        template = CPTemplate.get_by_id(db, template_id)
        recap = RecapDocument.get_by_id(db, recap_id)
        
        if not template or not recap:
            raise HTTPException(status_code=404, detail="Template or recap not found")
        
        # Generate charter party
        generated_cp = await cp_generator.generate(
            template.processed_data,
            recap.parsed_data,
            output_format
        )
        
        # Save generated document
        output_path = await file_manager.save_generated_cp(generated_cp, output_format)
        
        # Save to database
        cp_record = GeneratedCP(
            template_id=template_id,
            recap_id=recap_id,
            output_path=str(output_path),
            changes_tracked=generated_cp.get("changes", []),
            format=output_format
        )
        
        cp_id = cp_record.save(db)
        
        logger.info(f"CP generated successfully: {cp_id}")
        return {
            "cp_id": cp_id,
            "output_path": str(output_path),
            "changes_count": len(generated_cp.get("changes", [])),
            "format": output_format,
            "status": "generated"
        }
        
    except Exception as e:
        logger.error(f"Error generating CP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating charter party: {str(e)}")

@app.get("/api/templates")
async def list_templates(db = Depends(get_db)):
    """List all available templates"""
    try:
        templates = CPTemplate.get_all(db)
        return [
            {
                "id": t.id,
                "name": t.name,
                "type": t.type,
                "created_at": t.created_at.isoformat(),
                "fields_count": len(t.processed_data.get("fields", []))
            }
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving templates")

@app.get("/api/recaps")
async def list_recaps(db = Depends(get_db)):
    """List all processed recap documents"""
    try:
        recaps = RecapDocument.get_all(db)
        return [
            {
                "id": r.id,
                "name": r.name,
                "created_at": r.created_at.isoformat(),
                "terms_count": len(r.parsed_data.get("terms", []))
            }
            for r in recaps
        ]
    except Exception as e:
        logger.error(f"Error listing recaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving recaps")

@app.get("/api/generated-cps")
async def list_generated_cps(db = Depends(get_db)):
    """List all generated charter parties"""
    try:
        cps = GeneratedCP.get_all(db)
        return [
            {
                "id": cp.id,
                "template_id": cp.template_id,
                "recap_id": cp.recap_id,
                "format": cp.format,
                "created_at": cp.created_at.isoformat(),
                "changes_count": len(cp.changes_tracked)
            }
            for cp in cps
        ]
    except Exception as e:
        logger.error(f"Error listing generated CPs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving generated charter parties")

@app.get("/api/download/{cp_id}")
async def download_charter_party(cp_id: int, db = Depends(get_db)):
    """Download a generated charter party"""
    try:
        cp = GeneratedCP.get_by_id(db, cp_id)
        if not cp:
            raise HTTPException(status_code=404, detail="Charter party not found")
        
        if not os.path.exists(cp.output_path):
            raise HTTPException(status_code=404, detail="Generated file not found")
        
        filename = f"charter_party_{cp_id}.{cp.format}"
        return FileResponse(
            path=cp.output_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading CP {cp_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading charter party")

@app.get("/api/cp-changes/{cp_id}")
async def get_cp_changes(cp_id: int, db = Depends(get_db)):
    """Get tracked changes for a generated charter party"""
    try:
        cp = GeneratedCP.get_by_id(db, cp_id)
        if not cp:
            raise HTTPException(status_code=404, detail="Charter party not found")
        
        return {
            "cp_id": cp_id,
            "changes": cp.changes_tracked,
            "total_changes": len(cp.changes_tracked)
        }
        
    except Exception as e:
        logger.error(f"Error getting changes for CP {cp_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving changes")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
