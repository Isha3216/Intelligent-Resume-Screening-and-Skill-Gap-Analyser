import os
import streamlit as st
from analyzer import process_resume_screening, generate_report_text

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Resume Screening & Skill Gap Analyzer", layout="wide")

# --- CUSTOM CLASSY THEME STYLING (WARM BEIGE & CHARCOAL LABELS FIX) ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Background & Base Font */
    .stApp {
        background-color: #DED5C6 !important;
        color: #1E1E1C !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Headings with Classy Serif Font */
    h1, h2, h3, .serif-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #1E1E1C !important;
        letter-spacing: -0.02em !important;
    }

    /* Top Title Alignment & Styling */
    .main-header {
        text-align: center;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1E1E1C;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em !important;
        margin-bottom: 0.3rem !important;
    }
    .main-header p {
        font-size: 1rem;
        color: #383834 !important;
        font-style: italic;
    }

    /* Card Containers */
    div[data-testid="stColumn"] > div {
        background-color: #E6DFD3 !important;
        border: 1px solid #1E1E1C !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03) !important;
    }

    /* --- WIDGET LABELS & HELPER TEXT VISIBILITY FIX --- */
    label, 
    label p, 
    [data-testid="stWidgetLabel"], 
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stWidgetLabel"] *,
    .stMarkdown p {
        color: #1E1E1C !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* Text Inputs & Selectboxes */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #F0EAE1 !important;
        color: #1E1E1C !important;
        border: 1px solid #1E1E1C !important;
        border-radius: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* File Uploader Dropzone Styling */
    [data-testid="stFileUploader"] section {
        background-color: #F0EAE1 !important;
        border: 1px dashed #1E1E1C !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #1E1E1C !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #1E1E1C !important;
        color: #F0EAE1 !important;
        border: 1px solid #1E1E1C !important;
        border-radius: 20px !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #F0EAE1 !important;
    }

    /* Primary Action Button */
    div.stButton > button[kind="primary"] {
        background-color: #1E1E1C !important;
        color: #F0EAE1 !important;
        border: 1px solid #1E1E1C !important;
        border-radius: 30px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
        margin-top: 1rem !important;
    }
    div.stButton > button[kind="primary"] * {
        color: #F0EAE1 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #383834 !important;
        color: #FFFFFF !important;
        border-color: #383834 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15) !important;
    }
    div.stButton > button[kind="primary"]:hover * {
        color: #FFFFFF !important;
    }

    /* Download Button */
    div.stDownloadButton > button {
        background-color: #E6DFD3 !important;
        color: #1E1E1C !important;
        border: 1px solid #1E1E1C !important;
        border-radius: 30px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stDownloadButton > button * {
        color: #1E1E1C !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #1E1E1C !important;
    }
    div.stDownloadButton > button:hover * {
        color: #F0EAE1 !important;
    }

    /* Radio Buttons Options */
    div[data-testid="stRadio"] label p {
        color: #1E1E1C !important;
        font-weight: 500 !important;
    }

    /* Results Card */
    .results-card {
        background-color: #E6DFD3;
        border: 1px solid #1E1E1C;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1.5rem;
    }

    /* Circular Match Score Badge */
    .score-circle-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 1rem 0 1.5rem 0;
    }
    .score-circle {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 5px solid #1E1E1C;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #F0EAE1;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .score-text {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        color: #1E1E1C;
    }
    .score-label {
        margin-top: 0.6rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        color: #383834;
        text-transform: uppercase;
    }

    /* Skill Gap Banner */
    .gap-banner {
        background-color: #1E1E1C;
        color: #F0EAE1;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-top: 1.5rem;
        text-align: center;
    }
    .gap-banner h4 {
        color: #F0EAE1 !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.1rem !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- HTML BADGE RENDERER HELPER ---
def render_skill_badges(skills, bg_color="#F0EAE1", border_color="#1E1E1C", text_color="#1E1E1C"):
    if not skills:
        return "<p style='color: #666; font-style: italic; font-size: 0.9rem;'>No skills detected.</p>"
    
    badges_html = "".join([
        f"<span style='display: inline-block; background-color: {bg_color}; color: {text_color}; "
        f"border: 1px solid {border_color}; padding: 4px 12px; border-radius: 20px; "
        f"font-weight: 500; font-size: 0.85rem; margin: 3px 3px 3px 0px;'>{skill.title()}</span>"
        for skill in sorted(skills)
    ])
    return f"<div style='margin-top: 0.5rem;'>{badges_html}</div>"


# --- HEADER SECTION ---
st.markdown("""
<div class="main-header">
    <h1>Intelligent Resume Screening & Skill Gap Analyzer</h1>
    <p>Analyzing resumes & identifying missing competencies against job requirements.</p>
</div>
""", unsafe_allow_html=True)


# --- INPUT CARDS SECTION ---
col1, col2 = st.columns(2)

# BOX 1: RESUME INPUT
with col1:
    st.markdown("<h3 class='serif-title'>1. Candidate Resume</h3>", unsafe_allow_html=True)
    
    input_mode = st.radio(
        "Choose Resume Source:", 
        ["Upload File (PDF/DOCX)", "Use Pre-loaded Sample Resume"],
        key="resume_mode"
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

# BOX 2: JOB DESCRIPTION INPUT
with col2:
    st.markdown("<h3 class='serif-title'>2. Job Description (JD)</h3>", unsafe_allow_html=True)
    
    jd_mode = st.radio(
        "Choose JD Source:",
        ["Paste Custom Text", "Use Pre-loaded Sample JD"],
        key="jd_mode"
    )
    
    job_description = ""
    
    if jd_mode == "Paste Custom Text":
        job_description = st.text_area("Paste job requirements here", height=180)
    else:
        sample_jd_dir = "sample_jds"
        if os.path.exists(sample_jd_dir) and os.listdir(sample_jd_dir):
            jd_files = [f for f in os.listdir(sample_jd_dir) if f.endswith('.txt')]
            if jd_files:
                selected_jd_file = st.selectbox("Select a Sample JD:", jd_files)
                jd_path = os.path.join(sample_jd_dir, selected_jd_file)
                with open(jd_path, "r", encoding="utf-8") as f:
                    default_jd_text = f.read()
                job_description = st.text_area("Job Requirements (Editable)", value=default_jd_text, height=180)
            else:
                st.error("No .txt files found in `sample_jds/` folder.")
        else:
            st.error("The `sample_jds/` folder was not found.")


# --- ANALYSIS ACTION BUTTON ---
if st.button("Run Screening Analysis", type="primary"):
    if not uploaded_resume:
        st.warning("Please upload or select a resume before proceeding.")
    elif not job_description.strip():
        st.warning("Please enter or select a job description before proceeding.")
    else:
        with st.spinner("Processing document text and computing similarity metrics..."):
            results = process_resume_screening(uploaded_resume, job_description)
            
            # --- RESULTS DISPLAY ---
            st.markdown("<div class='results-card'>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align: center;' class='serif-title'>Analysis Results</h2>", unsafe_allow_html=True)
            
            # Match Score Circle
            st.markdown(f"""
            <div class="score-circle-container">
                <div class="score-circle">
                    <span class="score-text">{results['match_score']}%</span>
                </div>
                <span class="score-label">Contextual Match Score</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Extracted & Required Skills
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown("<h4 class='serif-title'>Extracted Candidate Skills</h4>", unsafe_allow_html=True)
                st.markdown(render_skill_badges(results['candidate_skills']), unsafe_allow_html=True)

            with res_col2:
                st.markdown("<h4 class='serif-title'>Required Skills (from JD)</h4>", unsafe_allow_html=True)
                st.markdown(render_skill_badges(results['required_skills']), unsafe_allow_html=True)

            # Skill Gap Banner
            if results['missing_skills']:
                missing_badges = render_skill_badges(
                    results['missing_skills'], 
                    bg_color="#E6DFD3", 
                    border_color="#F0EAE1", 
                    text_color="#1E1E1C"
                )
                st.markdown(f"""
                <div class="gap-banner">
                    <h4 class='serif-title'>⚠ Identified Skill Gaps</h4>
                    {missing_badges}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="gap-banner" style="background-color: #2D4A3E;">
                    <h4 class='serif-title' style="color: #F0EAE1 !important;">✓ Complete Skill Match</h4>
                    <p style="margin: 0; font-size: 0.9rem;">No critical technical skill gaps identified based on the extracted job requirements.</p>
                </div>
                """, unsafe_allow_html=True)

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
            
            st.markdown("</div>", unsafe_allow_html=True)