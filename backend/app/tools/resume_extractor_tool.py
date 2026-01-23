"""Resume Extractor Tool - Function for agentic tool calling"""
import sys
import os
import random
import string
from typing import Dict, Union, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.agents.resume_parser_agent import ResumeParserAgent
from backend.app.agents.data_aggregation_agent import DataAggregationAgent


def _generate_id_from_name(name: str) -> str:
    """Generate ID from name initials"""
    if not name:
        return "USER001"
    
    # Split name and get initials
    parts = name.strip().split()
    initials = ''.join([part[0].upper() for part in parts if part])
    
    # Add random 3-digit number
    random_num = random.randint(100, 999)
    
    return f"{initials}{random_num}"


def _generate_password(length: int = 8) -> str:
    """Generate a simple password"""
    # Mix of uppercase, lowercase, and digits
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    password = ''.join(random.choices(chars, k=length))
    return password


def extract_resume_data(
    resume_file_path: Optional[str] = None,
    resume_file_content: Optional[bytes] = None,
    save_temp_file: bool = True
) -> Dict:
    """
    Extract structured data from a resume file.
    
    This function can be used as a tool in agentic systems for resume extraction.
    
    Args:
        resume_file_path (str, optional): Path to the resume file (PDF or DOCX).
                                         Required if resume_file_content is not provided.
        resume_file_content (bytes, optional): Binary content of the resume file.
                                              Required if resume_file_path is not provided.
        save_temp_file (bool): If True and resume_file_content is provided, saves to temp file.
                              Default: True
    
    Returns:
        dict: Extracted resume data with the following structure:
            {
                "name": str,
                "id": str,  # Generated from initials + random number
                "password": str,  # Auto-generated password
                "skills": List[str]
            }
            
            Or if error:
            {
                "status": "error",
                "message": str
            }
    
    Raises:
        ValueError: If neither resume_file_path nor resume_file_content is provided.
        FileNotFoundError: If resume_file_path is provided but file doesn't exist.
        Exception: For other extraction errors.
    
    Example:
        >>> # Using file path
        >>> result = extract_resume_data(resume_file_path="path/to/resume.pdf")
        >>> print(f"Name: {result['name']}")
        >>> print(f"ID: {result['id']}")
        >>> print(f"Password: {result['password']}")
        >>> print(f"Skills: {result['skills']}")
        
        >>> # Using file content
        >>> with open("resume.pdf", "rb") as f:
        ...     content = f.read()
        >>> result = extract_resume_data(resume_file_content=content)
        >>> print(result["skills"])
    """
    
    # Initialize agents
    resume_parser = ResumeParserAgent()
    aggregation_agent = DataAggregationAgent()
    
    # Determine file path
    temp_file_path = None
    file_path_to_use = None
    
    if resume_file_path:
        # Use provided file path
        if not os.path.exists(resume_file_path):
            return {
                "status": "error",
                "message": f"Resume file not found: {resume_file_path}"
            }
        file_path_to_use = resume_file_path
    
    elif resume_file_content:
        # Save content to temporary file
        if save_temp_file:
            import tempfile
            # Determine file extension from content or default to PDF
            file_ext = ".pdf"  # Default
            if resume_file_content.startswith(b'%PDF'):
                file_ext = ".pdf"
            elif resume_file_content.startswith(b'PK'):
                file_ext = ".docx"
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_file.write(resume_file_content)
            temp_file.close()
            temp_file_path = temp_file.name
            file_path_to_use = temp_file_path
        else:
            return {
                "status": "error",
                "message": "save_temp_file must be True when using resume_file_content"
            }
    else:
        return {
            "status": "error",
            "message": "resume_file_path or resume_file_content must be provided"
        }
    
    try:
        # Step 1: Parse resume
        resume_data = resume_parser.parse_resume(file_path_to_use)
        
        # Step 2: Aggregate data
        unified_profile = aggregation_agent.aggregate_profile(
            resume_data,
            {},  # No LinkedIn data
            {}   # No GitHub data
        )
        
        # Step 3: Generate ID and password
        name = unified_profile.get('personal_info', {}).get('name', 'Unknown')
        user_id = _generate_id_from_name(name)
        password = _generate_password()
        skills = unified_profile.get('skills', [])
        
        # Clean up temp file if created
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors
        
        # Return simplified format
        return {
            "name": name,
            "id": user_id,
            "password": password,
            "skills": skills
        }
        
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
        
        return {
            "status": "error",
            "message": f"Error extracting resume: {str(e)}"
        }


# Tool definition for agentic frameworks
RESUME_EXTRACTOR_TOOL = {
    "name": "extract_resume_data",
    "description": "Extract name, ID, password, and skills from a resume file (PDF or DOCX)",
    "parameters": {
        "type": "object",
        "properties": {
            "resume_file_path": {
                "type": "string",
                "description": "Path to the resume file (PDF or DOCX)"
            },
            "resume_file_content": {
                "type": "string",
                "description": "Base64 encoded binary content of the resume file"
            },
            "save_temp_file": {
                "type": "boolean",
                "description": "Whether to save file content to temporary file (default: true)",
                "default": True
            }
        },
        "required": []
    },
    "function": extract_resume_data
}


# Async version for async agentic frameworks
async def extract_resume_data_async(
    resume_file_path: Optional[str] = None,
    resume_file_content: Optional[bytes] = None,
    save_temp_file: bool = True
) -> Dict:
    """
    Async version of extract_resume_data for async agentic frameworks.
    
    Same functionality as extract_resume_data but async-compatible.
    """
    import asyncio
    
    # Run sync function in executor
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        extract_resume_data,
        resume_file_path,
        resume_file_content,
        save_temp_file
    )
