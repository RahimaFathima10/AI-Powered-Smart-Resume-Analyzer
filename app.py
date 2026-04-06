import streamlit as st
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Secure API Key Setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found! Please add it to your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Page Config
st.set_page_config(
    page_title="Smart Resume AI Analyzer",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    h1 { color: #0A66C2; text-align: center; }
    .candidate-name {
        font-size: 28px;
        font-weight: bold;
        color: #0A66C2;
        text-align: center;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Settings")
    theme_mode = st.toggle("Dark Mode", value=False)
    analysis_style = st.selectbox("Analysis Style", ["Detailed Analysis", "Short & Quick"])
    show_job_match = st.toggle("Show Job Match Score", value=True)
    temperature = st.slider("AI Creativity Level", 0.0, 1.0, 0.7, 0.1)
    st.markdown("---")
    st.caption("Made by Rahima Fathima")

# Main Title
st.markdown("<h1>AI Powered Smart Resume Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color:#555;'>Upload your resume and get instant professional AI feedback</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 2])
with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
with col2:
    job_description = st.text_area("Job Description (Optional)", height=150)

if uploaded_file and st.button("Analyze Resume", type="primary", use_container_width=True):
    with st.spinner("AI is analyzing your resume... This may take a few seconds"):
        try:
            # Save and extract text from PDF
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
           
            doc = fitz.open("temp.pdf")
            resume_text = ""
            for page in doc:
                resume_text += page.get_text()
            doc.close()

            model = genai.GenerativeModel('gemini-2.5-flash')

            style_instruction = "Give detailed analysis with explanations." if analysis_style == "Detailed Analysis" else "Give short and concise analysis."

            prompt = f"""
You are a senior HR recruiter and ATS expert.

First, extract the full name of the candidate from the resume.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description if job_description else "No job description provided."}

Respond **strictly** in this exact format only:

**CANDIDATE NAME**: [Full Name]

**OVERALL SCORE**: [number]/100
**ATS SCORE**: [number]/100
**JOB MATCH**: [number]%

**Key Strengths**:
- point 1
- point 2

**Areas to Improve**:
- point 1
- point 2

**Extracted Skills**:
- Technical: ...
- Soft: ...

**Missing Skills**:
- ...

**Actionable Suggestions**:
1. ...
2. ...
3. ...

Be professional, honest and encouraging. {style_instruction}
"""

            response = model.generate_content(
                prompt, 
                generation_config={"temperature": temperature}
            )
           
            analysis = response.text

            # ================ IMPROVED SCORE & NAME EXTRACTION ================

            # Candidate Name
            candidate_name = "Candidate"
            name_match = re.search(r'\*\*CANDIDATE NAME\*\*:\s*(.+)', analysis, re.IGNORECASE)
            if name_match:
                candidate_name = name_match.group(1).strip()
            st.markdown(f"<div class='candidate-name'>{candidate_name}</div>", unsafe_allow_html=True)

            # Overall Score
            overall = "75"
            overall_match = re.search(r'\*\*OVERALL SCORE\*\*:\s*(\d+)', analysis, re.IGNORECASE)
            if overall_match:
                overall = overall_match.group(1).strip()

            # ATS Score
            ats = "80"
            ats_match = re.search(r'\*\*ATS SCORE\*\*:\s*(\d+)', analysis, re.IGNORECASE)
            if ats_match:
                ats = ats_match.group(1).strip()

            # Job Match
            match = "70"
            match_match = re.search(r'\*\*JOB MATCH\*\*:\s*(\d+)', analysis, re.IGNORECASE)
            if match_match:
                match = match_match.group(1).strip()

            st.success("Analysis Complete!")

            # Score Cards
            st.markdown("### AI Evaluation Scores")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Overall Score", f"{overall}/100")
            with c2:
                st.metric("ATS Score", f"{ats}/100")
            with c3:
                if job_description and show_job_match:
                    st.metric("Job Match", f"{match}%")

            st.markdown("---")
            st.markdown(analysis)

            # Download Report
            report = f"Resume Analysis Report - {datetime.now().strftime('%d %B %Y')}\n\n{analysis}"
            st.download_button(
                label="Download Full Report",
                data=report,
                file_name=f"Resume_Analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("Something went wrong. Please check your API key or internet connection.")
            st.write(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>AI Resume Analyzer</p>", unsafe_allow_html=True)