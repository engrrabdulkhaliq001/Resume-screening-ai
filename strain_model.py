"""
Resume Screening AI - Scoring Engine (Step 6)
Scores a resume against a job description on a scale of 0-100
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ===================== SETUP =====================

MODEL_DIR = Path("models")

print("Loading BERT model...")
model = SentenceTransformer(str(MODEL_DIR / "sentence_bert"))
print("Model loaded!")

# List of technical skills to detect in resumes and job descriptions
SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql",
    "react", "angular", "vue", "nodejs", "django", "flask", "fastapi",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "keras", "opencv",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "postgresql", "mongodb", "mysql", "redis", "elasticsearch",
    "html", "css", "rest api", "graphql", "microservices",
    "data science", "data analysis", "computer vision",
    "agile", "scrum", "ci/cd", "jenkins", "github", "gitlab",
    "tableau", "power bi", "excel", "spark", "hadoop",
    "php", "ruby", "swift", "kotlin", "flutter",
]

# ===================== HELPERS =====================

def extract_skills(text):
    """Extract matching skills from raw text"""
    if not text:
        return []
    return [s for s in SKILLS if s in text.lower()]

def extract_exp_years(text):
    """Extract years of experience from text using regex patterns"""
    import re
    if not text:
        return None
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'experience\s*of\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yr[s]?\s*exp',
    ]
    for pat in patterns:
        match = re.search(pat, text.lower())
        if match:
            return int(match.group(1))
    return None


# ===================== SCORING ENGINE =====================

def score_resume(resume_data: dict, job_data: dict) -> dict:
    """
    Score a resume against a job description

    resume_data = {
        "name": "Ali Hassan",
        "skills": ["python", "sql"],
        "experience_years": 3,
        "education": "bachelors",
        "full_text": "..."
    }

    job_data = {
        "title": "Python Developer",
        "skills_required": ["python", "django", "sql"],
        "experience_years": 2,
        "description": "..."
    }
    """

    # 1. Semantic Similarity using BERT
    resume_text = resume_data.get("full_text", "") or resume_data.get("text", "")
    job_text    = job_data.get("description", "") or job_data.get("title", "")

    # Truncate to BERT max token limit
    resume_text = resume_text[:512] if resume_text else "no content"
    job_text    = job_text[:512]    if job_text    else "no content"

    resume_emb = model.encode([resume_text])
    job_emb    = model.encode([job_text])
    semantic   = float(cosine_similarity(resume_emb, job_emb)[0][0]) * 100

    # 2. Skills Match Score
    resume_skills = set(s.lower() for s in resume_data.get("skills", []))
    job_skills    = set(s.lower() for s in job_data.get("skills_required", []))

    # Fallback: extract skills from raw text if not provided
    if not resume_skills:
        resume_skills = set(extract_skills(resume_text))
    if not job_skills:
        job_skills = set(extract_skills(job_text))

    if job_skills:
        matched      = resume_skills & job_skills
        missing      = job_skills - resume_skills
        extra        = resume_skills - job_skills
        skills_score = (len(matched) / len(job_skills)) * 100
    else:
        matched      = set()
        missing      = set()
        extra        = resume_skills
        skills_score = semantic  # use semantic score as fallback

    # 3. Experience Match Score
    resume_exp = resume_data.get("experience_years") or extract_exp_years(resume_text)
    job_exp    = job_data.get("experience_years")    or extract_exp_years(job_text)

    if resume_exp is not None and job_exp is not None:
        if resume_exp >= job_exp:
            exp_score = 100
        elif resume_exp >= job_exp * 0.7:
            exp_score = 75
        else:
            exp_score = max(0, (resume_exp / job_exp) * 100)
        exp_detail = f"{resume_exp} yrs (required: {job_exp} yrs)"
    else:
        exp_score  = 50  # default when experience not specified
        exp_detail = "Not specified"

    # 4. Education Match Score
    # Higher number = higher degree level
    edu_hierarchy = {
        "phd": 4, "masters": 3, "bachelors": 2,
        "associate": 1, "diploma": 1, "not specified": 0
    }
    resume_edu     = resume_data.get("education", "not specified").lower()
    job_edu        = job_data.get("education", "not specified").lower()
    resume_edu_val = edu_hierarchy.get(resume_edu, 0)
    job_edu_val    = edu_hierarchy.get(job_edu, 0)

    if job_edu_val == 0:
        edu_score = 100  # no education requirement
    elif resume_edu_val >= job_edu_val:
        edu_score = 100  # meets or exceeds requirement
    elif resume_edu_val == job_edu_val - 1:
        edu_score = 70   # one level below requirement
    else:
        edu_score = 40   # significantly below requirement

    # Final Weighted Score
    final_score = (
        semantic     * 0.40 +  # 40% weight - semantic understanding
        skills_score * 0.35 +  # 35% weight - skills match
        exp_score    * 0.15 +  # 15% weight - experience
        edu_score    * 0.10    # 10% weight - education
    )

    # Recommendation based on final score
    if final_score >= 75:
        recommendation = "SHORTLIST"
        emoji = "v"
    elif final_score >= 50:
        recommendation = "MAYBE"
        emoji = "?"
    else:
        recommendation = "REJECT"
        emoji = "x"

    return {
        "candidate_name"   : resume_data.get("name", "Unknown"),
        "job_title"        : job_data.get("title", "Unknown"),
        "final_score"      : round(final_score, 2),
        "recommendation"   : recommendation,
        "emoji"            : emoji,
        "breakdown": {
            "semantic_similarity" : round(semantic, 2),
            "skills_match"        : round(skills_score, 2),
            "experience_match"    : round(exp_score, 2),
            "education_match"     : round(edu_score, 2),
        },
        "skills": {
            "matched" : sorted(list(matched)),
            "missing" : sorted(list(missing)),
            "extra"   : sorted(list(extra)),
        },
        "experience": exp_detail,
        "education" : resume_edu,
    }


def rank_candidates(resumes: list, job: dict) -> list:
    """Rank all candidates against a single job and return sorted results"""
    print(f"\nRanking {len(resumes)} candidates for: {job.get('title', 'Unknown Job')}")
    print("="*60)

    results = []
    for resume in resumes:
        score = score_resume(resume, job)
        results.append(score)
        print(f"  {score['emoji']} {score['candidate_name']:<20} Score: {score['final_score']:>6.2f} | {score['recommendation']}")

    # Sort by final score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)

    print(f"\nTop Candidates:")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r['candidate_name']} - {r['final_score']}/100 ({r['recommendation']})")

    return results


# ===================== TEST =====================

if __name__ == "__main__":

    # Sample job description for testing
    sample_job = {
        "title": "Python Developer",
        "description": "We need a Python developer with Django, REST API, and SQL experience. 3 years experience required.",
        "skills_required": ["python", "django", "sql", "rest api", "git"],
        "experience_years": 3,
        "education": "bachelors",
    }

    # Sample resumes for testing
    sample_resumes = [
        {
            "name": "Ali Hassan",
            "full_text": "Python developer with 4 years of experience in Django, REST API, PostgreSQL, Git. BS Computer Science.",
            "skills": ["python", "django", "sql", "rest api", "git", "postgresql"],
            "experience_years": 4,
            "education": "bachelors",
        },
        {
            "name": "Sara Khan",
            "full_text": "Frontend developer React, JavaScript, HTML, CSS. 2 years experience.",
            "skills": ["react", "javascript", "html", "css"],
            "experience_years": 2,
            "education": "bachelors",
        },
        {
            "name": "Ahmed Raza",
            "full_text": "Data scientist with Python, pandas, machine learning, tensorflow. 5 years experience. Masters degree.",
            "skills": ["python", "pandas", "machine learning", "tensorflow", "sql"],
            "experience_years": 5,
            "education": "masters",
        },
    ]

    print("=== Scoring Engine Test ===\n")

    # Test single resume scoring
    print("--- Single Resume Score ---")
    result = score_resume(sample_resumes[0], sample_job)
    print(json.dumps(result, indent=2))

    # Rank all candidates
    print("\n--- All Candidates Ranked ---")
    ranked = rank_candidates(sample_resumes, sample_job)

    # Save results
    output = Path("data/scoring_results.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved: {output}")