"""Resume Parser Manager - Orchestrates resume extraction process"""
import asyncio
import sys
import os
import random
import string

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.agents.resume_parser_agent import ResumeParserAgent
from backend.app.agents.data_aggregation_agent import DataAggregationAgent


class ResumeParserManager:
    """Manages resume parsing workflow"""
    
    def __init__(self):
        """Initialize manager with agents"""
        self.resume_parser = ResumeParserAgent()
        self.aggregation_agent = DataAggregationAgent()
    
    def _generate_id_from_name(self, name: str) -> str:
        """Generate ID from name initials"""
        if not name:
            return "USER001"
        
        # Split name and get initials
        parts = name.strip().split()
        initials = ''.join([part[0].upper() for part in parts if part])
        
        # Add random 3-digit number
        random_num = random.randint(100, 999)
        
        return f"{initials}{random_num}"
    
    def _generate_password(self, length: int = 8) -> str:
        """Generate a simple password"""
        # Mix of uppercase, lowercase, and digits
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        password = ''.join(random.choices(chars, k=length))
        return password
    
    async def process_resume(self, resume_file_path: str) -> dict:
        """Main workflow: Resume Extraction - Returns name, ID, password, and skills only"""
        
        print("=" * 50)
        print("Starting Resume Extraction")
        print("=" * 50)
        
        # Step 1: Parse resume
        print("\n[Step 1] Parsing resume...")
        resume_data = self.resume_parser.parse_resume(resume_file_path)
        print(f"✓ Resume parsed. Name: {resume_data.get('name')}")
        
        # Step 2: Aggregate data (no scraping - just use resume data)
        print("\n[Step 2] Aggregating profile data...")
        unified_profile = self.aggregation_agent.aggregate_profile(
            resume_data,
            {},  # No LinkedIn data
            {}   # No GitHub data
        )
        
        # Step 3: Generate ID and password
        print("\n[Step 3] Generating credentials...")
        name = unified_profile.get('personal_info', {}).get('name', 'Unknown')
        user_id = self._generate_id_from_name(name)
        password = self._generate_password()
        skills = unified_profile.get('skills', [])
        
        print(f"✓ Generated ID: {user_id}")
        print(f"✓ Generated Password: {password}")
        print(f"✓ Extracted {len(skills)} skills")
        
        print("\n" + "=" * 50)
        print("✓ Extraction Complete!")
        print("=" * 50)
        
        # Return simplified output
        return {
            "name": name,
            "id": user_id,
            "password": password,
            "skills": skills
        }
