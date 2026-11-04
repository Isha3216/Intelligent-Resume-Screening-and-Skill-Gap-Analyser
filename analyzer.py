import pdfplumber
import docx
import spacy
from spacy.matcher import PhraseMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy NLP model with auto-download fallback
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Expanded Technical Skill Dictionary organized by domain
SKILLS_DB = [
    # Programming Languages
    "python", "java", "c++", "c", "c#", "r", "javascript", "typescript", 
    "go", "rust", "php", "ruby", "kotlin", "swift", "sql", "html", "css",

    # Artificial Intelligence, Data Science & ML
    "machine learning", "deep learning", "data science", "nlp", 
    "natural language processing", "computer vision", "opencv", "scikit-learn", 
    "tensorflow", "pytorch", "keras", "pandas", "numpy", "scipy", "matplotlib", 
    "seaborn", "rag", "retrieval-augmented generation", "tf-idf", "yolo", 
    "mediapipe", "reinforcement learning", "bert", "transformers",

    # Web Development & Frameworks
    "react", "react.js", "node.js", "express.js", "express", "angular", 
    "vue.js", "django", "flask", "fastapi", "bootstrap", "tailwind", 
    "tailwind css", "rest api", "graphql", "next.js",

    # Databases & Storage
    "mongodb", "mysql", "postgresql", "postgres", "sqlite", "oracle", 
    "redis", "firebase", "cassandra", "dynamodb",

    # Cloud, DevOps & Tools
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "git", 
    "github", "vs code", "linux", "unix", "ci/cd", "jenkins", "terraform",

    # Core Computer Science & Concepts
    "data structures", "algorithms", "object-oriented programming", "oop", 
    "system design", "cryptography", "software engineering", "agile", "scrum"
]

# Initialize PhraseMatcher with skill patterns
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in SKILLS_DB]
matcher.add("SKILLS", patterns)


def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts raw text lines from uploaded PDF resume using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def extract_text_from_docx(uploaded_file) -> str:
    """Extracts raw text lines from uploaded DOCX resume using python-docx."""
    doc = docx.Document(uploaded_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])
    return text


def extract_text_from_file(uploaded_file) -> str:
    """Routes uploaded file to the appropriate parser based on file extension."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")


def preprocess_and_extract_skills(text: str):
    """
    Cleans raw text (lemmatization & stop-word removal) 
    and extracts candidate skills matching the technical dictionary.
    """
    doc = nlp(text)
    
    # Lemmatization and stop-word elimination
    clean_tokens = [
        token.lemma_.lower() 
        for token in doc 
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    clean_text = " ".join(clean_tokens)
    
    # Extract matched skills
    matches = matcher(doc)
    extracted_skills = set([doc[start:end].text.lower() for match_id, start, end in matches])
    
    return clean_text, extracted_skills


def calculate_similarity(candidate_skills: set, required_skills: set, resume_text: str, jd_text: str) -> float:
    """
    Computes a hybrid match score:
    - 75% weight on skill keyword overlap ratio.
    - 25% weight on full-text TF-IDF cosine similarity.
    """
    # 1. Calculate Skill Overlap Score (75% Weight)
    if not required_skills:
        skill_score = 100.0
    else:
        matched_skills = candidate_skills.intersection(required_skills)
        skill_score = (len(matched_skills) / len(required_skills)) * 100.0

    # 2. Calculate Text Cosine Similarity Score (25% Weight)
    text_score = 0.0
    if resume_text.strip() and jd_text.strip():
        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([resume_text, jd_text])
            similarity_matrix = cosine_similarity(vectors)
            text_score = similarity_matrix[0][1] * 100.0
        except Exception:
            text_score = skill_score

    # 3. Combine into weighted hybrid score
    final_score = (0.75 * skill_score) + (0.25 * text_score)
    return round(final_score, 2)


def generate_report_text(results: dict, filename: str) -> str:
    """Generates a plain-text report summarizing screening results."""
    report = "==================================================\n"
    report += " RESUME SCREENING & SKILL GAP ANALYSIS REPORT\n"
    report += "==================================================\n\n"
    report += f"Candidate File: {filename}\n"
    report += f"Contextual Match Score: {results['match_score']}%\n\n"
    
    report += f"--------------------------------------------------\n"
    report += f"EXTRACTED CANDIDATE SKILLS ({len(results['candidate_skills'])}):\n"
    report += f"--------------------------------------------------\n"
    candidate_str = ", ".join(sorted(results['candidate_skills'])).title() if results['candidate_skills'] else "None detected"
    report += f"{candidate_str}\n\n"
    
    report += f"--------------------------------------------------\n"
    report += f"REQUIRED JOB SKILLS ({len(results['required_skills'])}):\n"
    report += f"--------------------------------------------------\n"
    required_str = ", ".join(sorted(results['required_skills'])).title() if results['required_skills'] else "None detected"
    report += f"{required_str}\n\n"
    
    report += f"--------------------------------------------------\n"
    report += f"IDENTIFIED SKILL GAPS ({len(results['missing_skills'])}):\n"
    report += f"--------------------------------------------------\n"
    missing_str = ", ".join(sorted(results['missing_skills'])).title() if results['missing_skills'] else "No gaps identified"
    report += f"{missing_str}\n\n"
    
    report += "==================================================\n"
    return report


def process_resume_screening(uploaded_file, jd_text: str):
    """Main pipeline orchestrator."""
    # 1. Document Ingestion (PDF or DOCX)
    resume_raw_text = extract_text_from_file(uploaded_file)
    
    # 2. Preprocessing & Skill Extraction
    resume_clean_text, candidate_skills = preprocess_and_extract_skills(resume_raw_text)
    jd_clean_text, required_skills = preprocess_and_extract_skills(jd_text)
    
    # 3. Hybrid Match Score Calculation
    match_score = calculate_similarity(candidate_skills, required_skills, resume_clean_text, jd_clean_text)
    
    # 4. Skill Gap Analysis (Set Difference)
    missing_skills = required_skills - candidate_skills
    
    return {
        "match_score": match_score,
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
        "missing_skills": missing_skills
    }