from pydantic import BaseModel, Field
from typing import Optional

class GradeCreate(BaseModel):
    student_name: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    marks_obtained: float
    total_marks: float
    semester: str

class GradeResponse(BaseModel):
    id: int
    student_name: str
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str

class StudyTipsRequest(BaseModel):
    id: int

class OverallAnalysisResponse(BaseModel):
    total_students: int
    average_score: float
    top_subject: str
    weak_subject: str
    recommendations: str