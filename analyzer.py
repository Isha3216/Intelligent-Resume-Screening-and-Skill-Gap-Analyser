import pdfplumber
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

# Technical Skill Dictionary for PhraseMatcher
SKILLS_DB = [
    "python", "java", "c++", "c", "sql", "machine learning", "data science", 
    "react", "node.js", "mongodb", "aws", "docker", "git", "nlp", 
    "computer vision", "opencv", "scikit-learn", "pandas", "numpy", "r",
    "html", "css", "javascript", "express.js", "tailored", "deep learning"
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


def calculate_similarity(resume_text: str, jd_text: str) -> float:
    """Computes TF-IDF vector representations and Cosine Similarity percentage."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity_matrix = cosine_similarity(vectors)
    match_score = similarity_matrix[0][1] * 100
    return round(match_score, 2)


def process_resume_screening(uploaded_pdf, jd_text: str):
    """Main pipeline orchestrator."""
    # 1. Document Ingestion
    resume_raw_text = extract_text_from_pdf(uploaded_pdf)
    
    # 2. Preprocessing & Skill Extraction
    resume_clean_text, candidate_skills = preprocess_and_extract_skills(resume_raw_text)
    jd_clean_text, required_skills = preprocess_and_extract_skills(jd_text)
    
    # 3. Vectorization & Match Score Calculation
    match_score = calculate_similarity(resume_clean_text, jd_clean_text)
    
    # 4. Skill Gap Analysis (Set Difference)
    missing_skills = required_skills - candidate_skills
    
    return {
        "match_score": match_score,
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
        "missing_skills": missing_skills
    }