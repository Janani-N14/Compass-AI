"""LLM Prompts for Resume Extraction (Optional)"""

RESUME_EXTRACTION_PROMPT = """Extract ALL information from this resume text. Be thorough and extract everything. Return ONLY valid JSON, no other text.

Resume Text:
{resume_text}

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
