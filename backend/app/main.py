"""Backend entrypoint - API server for resume extraction"""
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if __name__ == "__main__":
    print("=" * 60)
    print("Resume Extraction System API")
    print("=" * 60)
    print("\nServer will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("\nEndpoint: POST /api/upload-resume")
    print("Output: {name, id, password, skills}")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "backend.app.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
