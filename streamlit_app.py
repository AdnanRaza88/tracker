import streamlit as st
import requests
import pandas as pd
from datetime import date

st.set_page_config(page_title="GradePulse", layout="wide")

# Custom CSS for Neumorphic Light UI
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background: #e6f0ff;
        color: #1e3a8a;
        border-radius: 12px;
        border: none;
        box-shadow: 5px 5px 10px #d1d5db, -5px -5px 10px #ffffff;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 3px 3px 6px #d1d5db, -3px -3px 6px #ffffff;
        transform: translateY(-2px);
    }
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 8px 8px 16px #d1d5db, -8px -8px 16px #ffffff;
        margin-bottom: 20px;
    }
    h1 {
        color: #1e40af;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 GradePulse - Student Grade Tracker")
st.markdown("### Professional Academic Performance Management")

BASE_URL = st.text_input("Backend API URL", "http://localhost:8000", help="Change after Railway deployment")

if st.button("Refresh Data"):
    st.rerun()

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Add Grade", "All Records", "AI Tools"])

# Dashboard
if page == "Dashboard":
    try:
        grades = requests.get(f"{BASE_URL}/grades").json()
        if grades:
            df = pd.DataFrame(grades)
            st.subheader("Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                avg = (df['marks_obtained'] / df['total_marks'] * 100).mean()
                st.metric("Class Average", f"{avg:.1f}%")
            with col3:
                st.metric("Students", df['student_name'].nunique())
            
            st.subheader("Recent Grades")
            st.dataframe(df.tail(10), use_container_width=True)
    except:
        st.info("Start backend or check API URL")

# Add Grade
elif page == "Add Grade":
    with st.form("add_grade"):
        st.subheader("Add New Grade Record")
        student_name = st.text_input("Student Name")
        subject = st.text_input("Subject")
        marks_obtained = st.number_input("Marks Obtained", min_value=0.0, step=0.1)
        total_marks = st.number_input("Total Marks", min_value=1.0, value=100.0, step=0.1)
        semester = st.text_input("Semester", "Fall-2026")
        
        if st.form_submit_button("Save Grade"):
            if student_name and subject:
                data = {
                    "student_name": student_name,
                    "subject": subject,
                    "marks_obtained": marks_obtained,
                    "total_marks": total_marks,
                    "semester": semester
                }
                try:
                    resp = requests.post(f"{BASE_URL}/grades", json=data)
                    if resp.status_code == 200:
                        st.success("Grade added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add")
                except:
                    st.error("Cannot connect to backend")

# All Records
elif page == "All Records":
    try:
        grades = requests.get(f"{BASE_URL}/grades").json()
        if grades:
            df = pd.DataFrame(grades)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            with col1:
                delete_id = st.number_input("Delete by ID", min_value=1, step=1)
                if st.button("Delete Record"):
                    try:
                        requests.delete(f"{BASE_URL}/grades/{delete_id}")
                        st.success("Deleted")
                        st.rerun()
                    except:
                        st.error("Error")
            with col2:
                update_id = st.number_input("Update ID", min_value=1, step=1)
                # Update form simplified
    except:
        st.warning("No data or backend not running")

# AI Tools
elif page == "AI Tools":
    st.subheader("AI Powered Insights")
    tab1, tab2 = st.tabs(["Study Tips", "Class Analysis"])
    
    with tab1:
        grade_id = st.number_input("Enter Grade ID for Tips", min_value=1, step=1)
        if st.button("Get Personalized Study Tips"):
            try:
                resp = requests.post(f"{BASE_URL}/grades/{grade_id}/study-tips")
                if resp.status_code == 200:
                    st.markdown(f"<div class='card'>{resp.text}</div>", unsafe_allow_html=True)
                else:
                    st.error("Record not found")
            except:
                st.error("Backend error")
    
    with tab2:
        if st.button("Generate Overall Class Analysis"):
            try:
                resp = requests.post(f"{BASE_URL}/grades/overall-analysis")
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Class Average: {data['average_score']}%")
                    st.info(f"Strongest: {data['top_subject']} | Weakest: {data['weak_subject']}")
                    st.markdown(f"<div class='card'>{data['recommendations']}</div>", unsafe_allow_html=True)
            except:
                st.error("Error generating analysis")

st.caption("Made for Level 2 Assignment | Clean & Professional")