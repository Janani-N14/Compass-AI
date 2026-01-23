"""FastAPI routes for Resume Extraction System"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.services.manager import ResumeParserManager
from backend.app.config import config
from backend.app.api.schemas import ResumeExtractionResponse, ErrorResponse

app = FastAPI(
    title="Resume Extraction System",
    description="Extract name, ID, password, and skills from resumes",
    version="2.0.0"
)



# Initialize manager
manager = ResumeParserManager()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Extraction System API",
        "version": "2.0.0",
        "status": "running",
        "output_format": {
            "name": "string",
            "id": "string (initials + 3-digit number)",
            "password": "string (auto-generated)",
            "skills": "array of strings"
        },
        "endpoints": {
            "upload_resume": "/api/upload-resume",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/upload-resume", response_model=ResumeExtractionResponse)
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume and extract name, ID, password, and skills
    
    Args:
        file: Resume file (PDF or DOCX format)
    
    Returns:
        ResumeExtractionResponse: Extracted data with name, id, password, and skills
    
    Raises:
        HTTPException: 400 for invalid file type or size, 500 for processing errors
    """
    
    # Validate file type
    if not file.filename.endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload PDF or DOCX file."
        )
    
    # Create temp directory if it doesn't exist
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(config.UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            if len(content) > config.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {config.MAX_FILE_SIZE / 1024 / 1024}MB"
                )
            f.write(content)
        
        # Process through manager - returns name, ID, password, skills
        result = await manager.process_resume(file_path)
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Return with schema validation
        return ResumeExtractionResponse(**result)
        
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
