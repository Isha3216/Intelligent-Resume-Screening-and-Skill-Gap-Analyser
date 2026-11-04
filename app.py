import streamlit as st
from analyzer import process_resume_screening

st.set_page_config(page_title="Resume Screening & Skill Gap Analyzer", layout="wide")

st.title("Intelligent Resume Screening & Skill Gap Analyzer")
st.write("Upload a candidate resume in PDF format and provide a target job description to obtain contextual match analysis and skill gap reports.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Candidate Resume")
    uploaded_resume = st.file_uploader("Choose a PDF file", type=["pdf"])

with col2:
    st.subheader("2. Job Description (JD)")
    job_description = st.text_area("Paste job requirements here", height=180)

if st.button("Run Screening Analysis", type="primary"):
    if not uploaded_resume:
        st.warning("Please upload a PDF resume before proceeding.")
    elif not job_description.strip():
        st.warning("Please enter a job description before proceeding.")
    else:
        with st.spinner("Processing document text and computing similarity metrics..."):
            results = process_resume_screening(uploaded_resume, job_description)
            
            st.success("Analysis Complete!")
            
            st.metric(
                label="Contextual Match Score (Cosine Similarity)", 
                value=f"{results['match_score']}%"
            )
            
            st.divider()
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.subheader("Extracted Candidate Skills")
                if results['candidate_skills']:
                    st.write(", ".join(sorted(results['candidate_skills'])).title())
                else:
                    st.write("No matching technical skills detected from the precompiled dictionary.")

            with res_col2:
                st.subheader("Required Skills (from JD)")
                if results['required_skills']:
                    st.write(", ".join(sorted(results['required_skills'])).title())
                else:
                    st.write("No matching technical skills detected in the job description.")

            st.divider()
            st.subheader("Skill Gap Analysis")
            if results['missing_skills']:
                st.warning(f"**Missing Qualifications / Skills to Acquire:** {', '.join(sorted(results['missing_skills'])).title()}")
            else:
                st.info("No critical technical skill gaps identified based on the extracted job requirements!")