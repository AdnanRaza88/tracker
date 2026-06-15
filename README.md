# GradePulse - Student Grade Tracker

Full FastAPI + SQLModel backend with Streamlit frontend for student academic performance tracking.

## Features
- CRUD operations for grades
- Groq AI powered study tips and class analysis
- Extra endpoint: Student-wise grades
- Beautiful neumorphic Streamlit UI

## Tech Stack
- FastAPI
- SQLModel + SQLite
- Pydantic
- Groq LLM
- Streamlit (Frontend)

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add GROQ_API_KEY
3. `uvicorn main:app --reload`
4. `streamlit run streamlit_app.py`

## Deployment
- Backend: Railway / Render
- Frontend: Streamlit Cloud