import os
import streamlit as st
from analyzer import process_resume_screening, generate_report_text

st.set_page_config(page_title="Resume Screening & Skill Gap Analyzer", layout="wide")

st.title("Intelligent Resume Screening & Skill Gap Analyzer")
st.write("Upload a candidate resume or choose a pre-loaded sample to analyze contextual fit against job requirements.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Candidate Resume")
    
    input_mode = st.radio(
        "Choose Resume Source:", 
        ["Upload File (PDF/DOCX)", "Use Pre-loaded Sample Resume"]
    )
    
    uploaded_resume = None
    
    if input_mode == "Upload File (PDF/DOCX)":
        uploaded_resume = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
    else:
        sample_dir = "sample_resumes"
        if os.path.exists(sample_dir) and os.listdir(sample_dir):
            sample_files = [f for f in os.listdir(sample_dir) if f.endswith(('.pdf', '.docx'))]
            if sample_files:
                selected_sample = st.selectbox("Select a Sample Resume:", sample_files)
                sample_path = os.path.join(sample_dir, selected_sample)
                uploaded_resume = open(sample_path, "rb")
                st.info(f"Loaded: `{selected_sample}`")
            else:
                st.error("No .pdf or .docx files found in `sample_resumes/` folder.")
        else:
            st.error("The `sample_resumes/` folder was not found.")

with col2:
    st.subheader("2. Job Description (JD)")
    job_description = st.text_area("Paste job requirements here", height=180)

if st.button("Run Screening Analysis", type="primary"):
    if not uploaded_resume:
        st.warning("Please upload or select a resume before proceeding.")
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

            # Export Report Download Button
            st.divider()
            file_display_name = os.path.basename(uploaded_resume.name)
            report_data = generate_report_text(results, file_display_name)
            
            st.download_button(
                label="📥 Download Summary Report (.txt)",
                data=report_data,
                file_name=f"Screening_Report_{file_display_name.split('.')[0]}.txt",
                mime="text/plain"
            )