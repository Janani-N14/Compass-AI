"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel
from typing import List


class ResumeExtractionResponse(BaseModel):
    """Response model for resume extraction"""
    name: str
    id: str
    password: str
    skills: List[str]


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
