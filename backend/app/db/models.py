from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class SyllabusDB(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))  # Path to stored file for reference
    course_name = Column(String(255))
    instructor = Column(String(255))
    semester = Column(String(100))
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(50), default="pending")
    raw_text = Column(Text)

    assignments = relationship("AssignmentDB", back_populates="syllabus", cascade="all, delete-orphan")


class AssignmentDB(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabi.id"))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    assignment_type = Column(String(50), default="other")
    due_date = Column(Date)
    due_time = Column(String(10))
    estimated_hours = Column(Float, default=1.0)
    weight_percentage = Column(Float)
    course_name = Column(String(255))
    confidence_score = Column(Float, default=0.0)
    raw_text_snippet = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    syllabus = relationship("SyllabusDB", back_populates="assignments")
