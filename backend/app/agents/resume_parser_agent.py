"""Resume Parser Agent - Extracts data from resumes and finds LinkedIn/GitHub URLs"""
import re
import json
import os
from typing import Dict, List, Optional
import PyPDF2
import docx
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.services.llm_service import LLMService
from backend.app.config import config


class ResumeParserAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.linkedin_pattern = re.compile(
            r'(?:linkedin\.com/in/|linkedin\.com/pub/)[\w-]+|linkedin\.com/profile/view\?id=[\w-]+',
            re.IGNORECASE
        )
        self.github_pattern = re.compile(
            r'github\.com/[\w-]+',
            re.IGNORECASE
        )
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        )
    
    def parse_resume(self, file_path: str) -> Dict:
        """Extract text and URLs from resume"""
        try:
            text = self._extract_text(file_path)
            
            # Extract URLs using regex
            linkedin_url = self._extract_linkedin(text)
            github_url = self._extract_github(text)
            email = self._extract_email(text)
            phone = self._extract_phone(text)
            
            # Clean email - remove common prefixes
            if email:
                email = self._clean_email(email)
            
            # Use LLM to extract structured data
            structured_data = self._extract_with_llm(text)
            
            # Clean email from structured data too
            if structured_data.get("email"):
                structured_data["email"] = self._clean_email(structured_data["email"])
            
            return {
                "raw_text": text,
                "linkedin_url": linkedin_url,
                "github_url": github_url,
                "email": email or structured_data.get("email"),
                "phone": phone or structured_data.get("phone"),
                "name": structured_data.get("name"),
                "skills": structured_data.get("skills", []),
                "experience": structured_data.get("experience", []),
                "education": structured_data.get("education", []),
                "projects": structured_data.get("projects", []),
                "achievements": structured_data.get("achievements", []),
                "gpa": structured_data.get("gpa"),
                "interests": structured_data.get("interests", []),
                "career_goal": structured_data.get("career_goal")
            }
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return {
                "raw_text": "",
                "linkedin_url": None,
                "github_url": None,
                "email": None,
                "phone": None,
                "name": None,
                "skills": [],
                "experience": [],
                "education": [],
                "projects": [],
                "achievements": [],
                "gpa": None,
                "interests": [],
                "career_goal": None
            }
    
    def _clean_email(self, email: str) -> str:
        """Clean email by removing common prefixes and fixing common issues"""
        # Remove common prefixes that might be attached
        prefixes_to_remove = ["pe", "envel", "email", "mail", "e-", "e_"]
        
        # Check if email starts with a prefix followed by the actual email
        for prefix in prefixes_to_remove:
            if email.lower().startswith(prefix):
                # Try to find the actual email part
                remaining = email[len(prefix):]
                # Check if remaining part looks like an email
                if re.match(r'^[a-z0-9._%+-]+@', remaining, re.IGNORECASE):
                    email = remaining
                    break
        
        # Remove any non-email characters at the start
        email = re.sub(r'^[^a-z0-9]+', '', email, flags=re.IGNORECASE)
        
        # Final validation - ensure it's a valid email format
        if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
            return email
        
        return email
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX"""
        if file_path.endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.endswith(('.docx', '.doc')):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL from text"""
        matches = self.linkedin_pattern.findall(text)
        if matches:
            url = matches[0]
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL from text"""
        matches = self.github_pattern.findall(text)
        if matches:
            url = matches[0]
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        matches = self.email_pattern.findall(text)
        if matches:
            return matches[0]
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        matches = self.phone_pattern.findall(text)
        return matches[0] if matches else None
    
    def _extract_with_llm(self, text: str) -> Dict:
        """Use LLM to extract structured data with improved prompt"""
        prompt = f"""Extract ALL information from this resume text. Be thorough and extract everything. Return ONLY valid JSON, no other text.

Resume Text:
{text[:4000]}

Extract and return as JSON with ALL fields:
{{
    "name": "Full name exactly as written",
    "email": "Email address if found (clean format)",
    "phone": "Phone number if found",
    "skills": ["skill1", "skill2", ...],  // Extract ALL skills mentioned
    "experience": [
        {{
            "title": "Job title",
            "company": "Company name",
            "duration": "Time period (e.g., 2025 – Present)",
            "description": "Complete job description with all bullet points"
        }}
    ],  // Extract ALL work experience
    "education": [
        {{
            "degree": "Degree name (e.g., B.Tech, Bachelor's)",
            "institution": "Institution/University name",
            "year": "Graduation year or date range (e.g., 2023 – 2027)",
            "gpa": "GPA if mentioned (e.g., 9.06)"
        }}
    ],  // Extract ALL education entries
    "projects": [
        {{
            "name": "Project name",
            "description": "Complete project description with all details",
            "technologies": ["tech1", "tech2", ...]  // All technologies used
        }}
    ],  // Extract ALL projects mentioned
    "achievements": [
        "Achievement 1",
        "Achievement 2",
        ...
    ],  // Extract ALL achievements, awards, honors
    "gpa": "Overall GPA if mentioned separately (e.g., 9.06)",
    "interests": ["interest1", "interest2"],  // If mentioned
    "career_goal": "Career goal or objective if mentioned in summary"
}}

IMPORTANT:
- Extract EVERYTHING - don't miss any projects, education, or achievements
- For education, include degree, institution, year/date range, and GPA
- For projects, include ALL projects mentioned
- For achievements, extract all awards, honors, hackathon wins, etc.
- Return complete descriptions, not summaries"""
        
        try:
            completion = self.llm_service.create_completion(prompt, temperature=0)
            response_text = self.llm_service.get_response_text(completion)
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {}
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse LLM JSON response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
        return {}
