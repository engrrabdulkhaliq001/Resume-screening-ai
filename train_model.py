"""
Resume Screening AI - Model Training
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pickle

from sentence_transformers import SentenceTransformer

# ===================== SETUP =====================

DATA_PATH  = Path("data/cleaned/all_data_clean.json")
MODEL_DIR  = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Loading data...")
with open(DATA_PATH, encoding="utf-8") as f:
    all_data = json.load(f)

# Resumes aur Job Descriptions alag karo
resumes = [r for r in all_data if r.get("type") == "resume" or r.get("source") == "kaggle_resume"]
jobs    = [r for r in all_data if r.get("type") == "job_description" or r.get("source") in ["indeed", "linkedin", "kaggle_jd"]]

print(f"Resumes : {len(resumes)}")
print(f"Jobs    : {len(jobs)}")


# ===================== STEP 1: LOAD BERT MODEL =====================

print("\nLoading Sentence-BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast + accurate
print("Model loaded!")


# ===================== STEP 2: CREATE EMBEDDINGS =====================

def get_text(record):
    """Record se text nikalo"""
    parts = []
    for key in ["text", "description", "summary", "title"]:
        val = record.get(key, "")
        if val and isinstance(val, str):
            parts.append(val)
    return " ".join(parts)[:512]  # BERT max tokens


print("\nCreating Resume embeddings...")
resume_texts = [get_text(r) for r in resumes]
resume_texts = [t if t.strip() else "no content" for t in resume_texts]
resume_embeddings = model.encode(resume_texts, show_progress_bar=True, batch_size=32)
print(f"Resume embeddings shape: {resume_embeddings.shape}")

print("\nCreating Job embeddings...")
job_texts = [get_text(j) for j in jobs]
job_texts = [t if t.strip() else "no content" for t in job_texts]
job_embeddings = model.encode(job_texts, show_progress_bar=True, batch_size=32)
print(f"Job embeddings shape: {job_embeddings.shape}")


# ===================== STEP 3: SCORING FUNCTION =====================

def score_resume_against_job(resume, job, resume_emb, job_emb):
    """
    Resume ko Job ke against score karo
    Returns: 0-100 score with breakdown
    """

    # 1. Semantic Similarity (BERT)
    sim = cosine_similarity([resume_emb], [job_emb])[0][0]
    semantic_score = float(sim) * 100

    # 2. Skills Match
    resume_skills = set(s.lower() for s in resume.get("skills", resume.get("skills_required", [])))
    job_skills    = set(s.lower() for s in job.get("skills_required", []))

    if job_skills:
        matched_skills = resume_skills & job_skills
        skills_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        skills_score = semantic_score  # fallback

    # 3. Experience Match
    resume_exp = resume.get("experience_years")
    job_exp    = job.get("experience_years")

    if resume_exp is not None and job_exp is not None:
        if resume_exp >= job_exp:
            exp_score = 100
        elif resume_exp >= job_exp * 0.7:
            exp_score = 70
        else:
            exp_score = max(0, (resume_exp / job_exp) * 100)
    else:
        exp_score = 50  # unknown

    # 4. Title Match
    resume_title = get_text(resume).lower()
    job_title    = job.get("title", "").lower()
    title_words  = set(job_title.split())
    resume_words = set(resume_title.split())
    title_overlap = len(title_words & resume_words)
    title_score = min(100, (title_overlap / max(len(title_words), 1)) * 100)

    # Weighted Final Score
    final_score = (
        semantic_score * 0.40 +
        skills_score   * 0.35 +
        exp_score      * 0.15 +
        title_score    * 0.10
    )

    return {
        "final_score"     : round(final_score, 2),
        "semantic_score"  : round(semantic_score, 2),
        "skills_score"    : round(skills_score, 2),
        "experience_score": round(exp_score, 2),
        "title_score"     : round(title_score, 2),
        "matched_skills"  : list(resume_skills & job_skills) if job_skills else [],
        "missing_skills"  : list(job_skills - resume_skills) if job_skills else [],
    }


# ===================== STEP 4: TEST SCORING =====================

print("\n=== Testing Scoring System ===")

# Sample test — pehli 3 jobs ke against pehle 5 resumes score karo
test_results = []
for j_idx in range(min(3, len(jobs))):
    job = jobs[j_idx]
    job_results = {
        "job_title"  : job.get("title", "Unknown"),
        "job_company": job.get("company", ""),
        "candidates" : []
    }

    for r_idx in range(min(5, len(resumes))):
        resume = resumes[r_idx]
        score = score_resume_against_job(
            resume, job,
            resume_embeddings[r_idx],
            job_embeddings[j_idx]
        )
        score["resume_id"]       = resume.get("id", f"resume_{r_idx}")
        score["resume_category"] = resume.get("category", "")
        job_results["candidates"].append(score)

    # Score ke basis pe sort karo
    job_results["candidates"].sort(key=lambda x: x["final_score"], reverse=True)
    test_results.append(job_results)

    print(f"\nJob: {job_results['job_title']}")
    for c in job_results["candidates"]:
        print(f"  Score: {c['final_score']:>6.2f} | Skills: {c['skills_score']:>6.2f} | Semantic: {c['semantic_score']:>6.2f} | {c['resume_category']}")


# ===================== STEP 5: SAVE MODEL & DATA =====================

print("\n=== Saving Model & Embeddings ===")

# BERT model save
model.save(str(MODEL_DIR / "sentence_bert"))
print(f"BERT model saved: models/sentence_bert/")

# Embeddings save
np.save(MODEL_DIR / "resume_embeddings.npy", resume_embeddings)
np.save(MODEL_DIR / "job_embeddings.npy", job_embeddings)
print(f"Embeddings saved!")

# Resume + Job metadata save
with open(MODEL_DIR / "resumes_meta.json", "w", encoding="utf-8") as f:
    json.dump([{
        "id"      : r.get("id", ""),
        "category": r.get("category", ""),
        "skills"  : r.get("skills", r.get("skills_required", [])),
        "exp_years": r.get("experience_years"),
        "text_preview": get_text(r)[:200],
    } for r in resumes], f, indent=2)

with open(MODEL_DIR / "jobs_meta.json", "w", encoding="utf-8") as f:
    json.dump([{
        "id"      : j.get("id", ""),
        "title"   : j.get("title", ""),
        "company" : j.get("company", ""),
        "skills"  : j.get("skills_required", []),
        "exp_years": j.get("experience_years"),
        "source"  : j.get("source", ""),
    } for j in jobs], f, indent=2)

print("Metadata saved!")

# Test results save
with open(MODEL_DIR / "test_results.json", "w", encoding="utf-8") as f:
    json.dump(test_results, f, indent=2)

print(f"""
╔══════════════════════════════════════════╗
║         MODEL TRAINING COMPLETE!        ║
╠══════════════════════════════════════════╣
║  Resumes indexed  : {len(resumes):<6}               ║
║  Jobs indexed     : {len(jobs):<6}               ║
║  Embedding dim    : 384                  ║
║  Model            : all-MiniLM-L6-v2    ║
╚══════════════════════════════════════════╝

Saved in: models/
  - sentence_bert/       (BERT model)
  - resume_embeddings.npy
  - job_embeddings.npy
  - resumes_meta.json
  - jobs_meta.json
  - test_results.json
""")