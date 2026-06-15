from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import os
from dotenv import load_dotenv
from groq import Groq

from models import Grade
from schemas import GradeCreate, GradeResponse, StudyTipsRequest, OverallAnalysisResponse
from database import get_session, create_db_and_tables

load_dotenv()

app = FastAPI(title="Student Grade Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/grades", response_model=GradeResponse)
def create_grade(grade: GradeCreate, session: Session = Depends(get_session)):
    db_grade = Grade(**grade.dict())
    session.add(db_grade)
    session.commit()
    session.refresh(db_grade)
    return db_grade

@app.get("/grades", response_model=List[GradeResponse])
def get_all_grades(session: Session = Depends(get_session)):
    grades = session.exec(select(Grade)).all()
    return grades

@app.get("/grades/{grade_id}", response_model=GradeResponse)
def get_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    return grade

@app.put("/grades/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, grade: GradeCreate, session: Session = Depends(get_session)):
    db_grade = session.get(Grade, grade_id)
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    for key, value in grade.dict().items():
        setattr(db_grade, key, value)
    session.add(db_grade)
    session.commit()
    session.refresh(db_grade)
    return db_grade

@app.delete("/grades/{grade_id}")
def delete_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    session.delete(grade)
    session.commit()
    return {"message": "Grade deleted successfully"}

@app.get("/grades/student/{student_name}", response_model=List[GradeResponse])
def get_student_grades(student_name: str, session: Session = Depends(get_session)):
    grades = session.exec(select(Grade).where(Grade.student_name == student_name)).all()
    if not grades:
        raise HTTPException(status_code=404, detail="No grades found for student")
    return grades

@app.post("/grades/{grade_id}/study-tips", response_model=str)
def get_study_tips(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    
    percentage = (grade.marks_obtained / grade.total_marks) * 100
    
    prompt = f"""You are a helpful teacher. Student {grade.student_name} scored {percentage:.1f}% in {grade.subject} in semester {grade.semester}.
    Give 3-4 personalized study tips and motivational advice in 2-3 paragraphs."""

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grades/overall-analysis", response_model=OverallAnalysisResponse)
def overall_analysis(session: Session = Depends(get_session)):
    grades = session.exec(select(Grade)).all()
    if not grades:
        raise HTTPException(status_code=400, detail="No grades available")
    
    total = len(grades)
    avg = sum(g.marks_obtained / g.total_marks * 100 for g in grades) / total
    
    subject_avg = {}
    for g in grades:
        perc = g.marks_obtained / g.total_marks * 100
        if g.subject not in subject_avg:
            subject_avg[g.subject] = []
        subject_avg[g.subject].append(perc)
    
    avg_per_subject = {s: sum(scores)/len(scores) for s, scores in subject_avg.items()}
    top_subject = max(avg_per_subject, key=avg_per_subject.get)
    weak_subject = min(avg_per_subject, key=avg_per_subject.get)
    
    prompt = f"Class overall average is {avg:.1f}%. Top subject: {top_subject}. Weak: {weak_subject}. Give short class performance summary and recommendations."
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        ai_text = completion.choices[0].message.content
    except:
        ai_text = "AI analysis temporarily unavailable."
    
    return OverallAnalysisResponse(
        total_students=total,
        average_score=round(avg, 1),
        top_subject=top_subject,
        weak_subject=weak_subject,
        recommendations=ai_text
    )