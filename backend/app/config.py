"""Configuration for Resume Parser - Constants, mappings, env loading"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for Resume Parser"""
    
    # LLM Configuration - Groq only
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    
    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "temp")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    
    # Scraping Settings
    SCRAPING_DELAY: float = float(os.getenv("SCRAPING_DELAY", "2.0"))  # Delay between requests (seconds)
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required in .env file")

config = Config()
