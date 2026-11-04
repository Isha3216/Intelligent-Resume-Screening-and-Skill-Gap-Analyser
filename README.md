Intelligent Resume Screening & Skill Gap Analyzer

An Automated Applicant Tracking System (ATS) and Skill Gap Analyzer designed to evaluate candidate resumes against target job descriptions.
The system leverages Natural Language Processing (NLP) and Machine Learning vectorization to calculate contextual similarity match scores and pinpoint missing technical competencies.

Key Features

Multi-Format Ingestion:** Extracts text cleanly from candidate resumes in both **PDF** (`pdfplumber`) and **DOCX** (`python-docx`) formats.
NLP Skill Extraction:** Utilizes `spaCy` and `PhraseMatcher` against a multi-domain technical dictionary covering AI, Data Science, Web Development, Databases, DevOps, and Core Computer Science.
Hybrid ATS Match Scoring:** Combines a **75% weighted skill keyword overlap ratio** with a **25% TF-IDF Cosine Similarity score** for balanced, realistic evaluation metrics.
Automated Skill Gap Analysis:** Performs set-difference analysis between candidate skills and required job qualifications to output clear skill gap badges.
Interactive Sample Selectors:** Allows 1-click testing using pre-loaded resume (`sample_resumes/`) and job description (`sample_jds/`) dropdown menus.
Exportable Summary Reports:** Generates downloadable plain-text (`.txt`) audit reports detailing match scores, detected skills, and missing qualifications.
Custom Editorial UI:** Styled with a custom warm oatmeal (`#DED5C6`) and charcoal black (`#1E1E1C`) theme built in Streamlit.

 Tech Stack

Frontend / Dashboard:** [Streamlit](https://streamlit.io/)
NLP & Text Processing:** [spaCy](https://spacy.io/) (`en_core_web_sm`, `PhraseMatcher`)
Machine Learning & Vectorization:** [Scikit-learn](https://scikit-learn.org/) (`TfidfVectorizer`, `cosine_similarity`)
Document Parsers:** `pdfplumber`, `python-docx`
Programming Language:** Python 3.10+

Project Structure

├── sample_resumes/        # Pre-loaded PDF & DOCX test resumes (git-ignored)
├── sample_jds/            # Pre-loaded TXT job description files
├── analyzer.py            # Modular backend logic (parsing, spaCy matching, hybrid similarity engine)
├── app.py                 # Streamlit UI dashboard and custom CSS theme
├── requirements.txt       # Project dependencies
├── .gitignore             # Excludes venv, cache files, and private sample resumes
└── README.md              # Project documentation
