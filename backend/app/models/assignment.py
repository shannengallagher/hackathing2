from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class AssignmentType(str, Enum):
    HOMEWORK = "homework"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PAPER = "paper"
    READING = "reading"
    PRESENTATION = "presentation"
    LAB = "lab"
    DISCUSSION = "discussion"
    PARTICIPATION = "participation"
    ATTENDANCE = "attendance"
    OTHER = "other"


class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    assignment_type: AssignmentType = AssignmentType.OTHER
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0, le=100)
    weight_percentage: Optional[float] = None
    course_name: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    """Model for partial updates - all fields optional"""
    title: Optional[str] = None
    description: Optional[str] = None
    assignment_type: Optional[AssignmentType] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0, le=100)
    weight_percentage: Optional[float] = None
    course_name: Optional[str] = None


class Assignment(AssignmentBase):
    id: int
    syllabus_id: int
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_text_snippet: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SyllabusBase(BaseModel):
    filename: str
    course_name: Optional[str] = None
    instructor: Optional[str] = None
    semester: Optional[str] = None


class SyllabusCreate(SyllabusBase):
    raw_text: Optional[str] = None


class Syllabus(SyllabusBase):
    id: int
    upload_date: datetime
    processing_status: str = "pending"
    raw_text: Optional[str] = None
    assignments: List[Assignment] = []

    class Config:
        from_attributes = True


class ExtractionResult(BaseModel):
    syllabus_id: int
    assignments: List[Assignment]
    course_info: dict
    extraction_confidence: float
    warnings: List[str] = []
