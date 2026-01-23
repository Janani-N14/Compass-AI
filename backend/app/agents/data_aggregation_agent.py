"""Data Aggregation Agent - Merges factual data from resume only (no scraping)"""
import re
from typing import Dict, List


class DataAggregationAgent:
    def __init__(self):
        """Initialize data aggregation agent (no LLM needed for simple merging)"""
        pass
    
    def aggregate_profile(self, resume_data: Dict, linkedin_data: Dict = None, github_data: Dict = None) -> Dict:
        """Merge all data sources into unified profile - FACTUAL DATA ONLY"""
        
        # Use resume data as primary source (no scraping)
        linkedin_data = linkedin_data or {}
        github_data = github_data or {}
        
        # Get skills from resume
        skills = resume_data.get("skills", []) or []
        
        # Get experience from resume
        experience = resume_data.get("experience", []) or []
        
        # Get education from resume
        education = resume_data.get("education", []) or []
        
        # Get projects from resume
        projects = resume_data.get("projects", []) or []
        
        # Get achievements from resume
        achievements = resume_data.get("achievements", []) or []
        
        # Build unified profile - FACTUAL DATA ONLY
        unified_profile = {
            "personal_info": {
                "name": resume_data.get("name"),
                "email": resume_data.get("email"),
                "phone": resume_data.get("phone"),
                "location": None,  # Not in resume
                "bio": None  # Will be set from summary if available
            },
            "skills": sorted(list(set(skills))) if skills else [],
            "experience": experience,
            "education": education,
            "projects": projects,
            "achievements": achievements,
            "academic_info": {
                "gpa": resume_data.get("gpa"),
                "interests": resume_data.get("interests", []) or []
            }
        }
        
        # Set bio from raw text summary if available
        raw_text = resume_data.get("raw_text", "")
        if raw_text:
            # Try to extract summary section
            summary_match = re.search(r'Summary\s+(.*?)(?=\n\n|\nSkills|\nExperience|\nEducation|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
            if summary_match:
                unified_profile["personal_info"]["bio"] = summary_match.group(1).strip()[:300]
            else:
                # Use first 200 chars as bio
                unified_profile["personal_info"]["bio"] = raw_text[:200].strip()
        
        # Remove None/empty values from personal_info
        unified_profile["personal_info"] = {
            k: v for k, v in unified_profile["personal_info"].items() 
            if v is not None and v != ""
        }
        
        # Remove any analysis/advisory fields that might have been added
        # Only keep factual extraction data
        fields_to_remove = [
            "career_goal",
            "comprehensive_analysis",
            "profile_analysis",
            "market_intelligence",
            "career_path",
            "skill_level",
            "strengths",
            "weaknesses",
            "career_readiness",
            "recommended_careers",
            "skill_gaps"
        ]
        
        for field in fields_to_remove:
            unified_profile.pop(field, None)
            if "personal_info" in unified_profile:
                unified_profile["personal_info"].pop(field, None)
            if "academic_info" in unified_profile:
                unified_profile["academic_info"].pop(field, None)
        
        return unified_profile
