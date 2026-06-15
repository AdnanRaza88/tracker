from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Grade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str = Field(default_factory=lambda: date.today().isoformat())