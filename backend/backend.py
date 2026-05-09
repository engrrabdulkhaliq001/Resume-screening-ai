"""
backend.py — Resume Screening AI: Search Relevance Edition
"""

import re, uuid, shutil, json, os
import numpy as np
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from flashrank import Ranker, RerankRequest

# ═══════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════
GROQ_MODEL     = "llama-3.3-70b-versatile"
EMBED_MODEL    = "all-MiniLM-L6-v2"
CHROMA_PATH    = "./chroma_db"
UPLOAD_DIR     = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

HYBRID_FETCH   = 20
RERANK_TOP_N   = 5

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not set!")

groq_client   = Groq(api_key=GROQ_API_KEY)
embedder      = SentenceTransformer(EMBED_MODEL)
reranker      = Ranker()

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection    = chroma_client.get_or_create_collection(
    name="resumes",
    metadata={"hnsw:space": "cosine"},
)

fapp = FastAPI(title="Resume Screening AI — Search Relevance Edition")
fapp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stored_jd: dict = {}


# ═══════════════════════════════════════════════════════════
# NUMPY CONVERTER — fixes all serialization errors
# ═══════════════════════════════════════════════════════════

def convert_numpy(obj):
    """Recursively convert all numpy types to native Python types."""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def parse_file(path: str) -> dict:
    fp   = Path(path)
    text = ""
    try:
        if fp.suffix.lower() == ".pdf":
            import pdfplumber
            with pdfplumber.open(fp) as pdf:
                for pg in pdf.pages:
                    t = pg.extract_text()
                    if t:
                        text += t + "\n"
        elif fp.suffix.lower() in [".docx", ".doc"]:
            from docx import Document
            for p in Document(fp).paragraphs:
                text += p.text + "\n"
        else:
            text = fp.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        text = str(e)

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name  = (
        lines[0]
        if lines and 2 <= len(lines[0].split()) <= 4 and "@" not in lines[0]
        else "Unknown"
    )
    email_m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    email   = email_m.group(0) if email_m else ""

    exp_match = re.search(
        r"(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)",
        text, re.IGNORECASE
    )
    experience_years = int(exp_match.group(1)) if exp_match else 0

    SKILL_KEYWORDS = [
        "python", "javascript", "typescript", "java", "c++", "golang", "rust",
        "react", "nextjs", "vue", "angular", "fastapi", "django", "flask",
        "langchain", "langgraph", "llm", "rag", "openai", "groq", "huggingface",
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "pytorch", "tensorflow", "scikit-learn", "xgboost",
        "machine learning", "deep learning", "nlp", "computer vision",
    ]
    text_lower   = text.lower()
    found_skills = [s for s in SKILL_KEYWORDS if s in text_lower]

    return {
        "name":             name,
        "email":            email,
        "full_text":        text[:3500],
        "experience_years": experience_years,
        "skills":           found_skills,
    }


def embed_text(text: str) -> list:
    return embedder.encode(text, normalize_embeddings=True).tolist()


# ═══════════════════════════════════════════════════════════
# PIPELINE STEP 1 — INDEXING
# ═══════════════════════════════════════════════════════════

def index_resume(resume_id: str, parsed: dict, filename: str):
    doc_text  = parsed["full_text"]
    embedding = embed_text(doc_text)

    metadata = {
        "name":             parsed.get("name", "Unknown"),
        "email":            parsed.get("email", ""),
        "filename":         filename,
        "experience_years": int(parsed.get("experience_years", 0)),
        "skills_csv":       ",".join(parsed.get("skills", [])),
    }

    collection.upsert(
        ids=[resume_id],
        documents=[doc_text],
        embeddings=[embedding],
        metadatas=[metadata],
    )


# ═══════════════════════════════════════════════════════════
# PIPELINE STEP 2 — QUERY TRANSFORMATION
# ═══════════════════════════════════════════════════════════

def transform_query(jd_text: str) -> str:
    prompt = f"""You are a search query expert for a resume retrieval system.

Given this job description, write a rich, dense search concept (150-200 words) that:
1. Expands technical synonyms (e.g. "ML" -> "machine learning, deep learning, AI")
2. Lists related tools and frameworks the ideal candidate likely knows
3. Describes the seniority level and years of experience expected
4. Mentions soft skills and domain context
5. Uses natural paragraph prose - NOT bullet points

Job Description:
{jd_text[:1500]}

Output ONLY the expanded search concept. No preamble, no headers."""

    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════
# PIPELINE STEP 3 — HYBRID SEARCH
# ═══════════════════════════════════════════════════════════

def hybrid_search(
    query_text: str,
    n_results: int = HYBRID_FETCH,
    min_exp_years: int = 0,
    required_skills: List[str] = None,
) -> list:
    query_embedding = embed_text(query_text)

    query_kwargs = dict(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count() or 1),
        include=["documents", "metadatas", "distances"],
    )

    results = collection.query(**query_kwargs)

    candidates = []
    for i, rid in enumerate(results["ids"][0]):
        candidates.append({
            "resume_id": rid,
            "document":  results["documents"][0][i],
            "metadata":  results["metadatas"][0][i],
            "distance":  float(results["distances"][0][i]),
        })
    return candidates


# ═══════════════════════════════════════════════════════════
# PIPELINE STEP 4 — RERANKING
# ═══════════════════════════════════════════════════════════

def rerank_candidates(query: str, candidates: list, top_n: int = RERANK_TOP_N) -> list:
    if not candidates:
        return []

    passages = [
        {"id": c["resume_id"], "text": c["document"][:1500]}
        for c in candidates
    ]
    request = RerankRequest(query=query, passages=passages)
    results = reranker.rerank(request)

    lookup = {c["resume_id"]: c for c in candidates}

    reranked = []
    for r in results[:top_n]:
        rid  = r["id"]
        base = lookup.get(rid, {}).copy()
        base["rerank_score"] = float(r["score"])
        reranked.append(base)

    return reranked


# ═══════════════════════════════════════════════════════════
# PIPELINE STEP 5 — FINAL LLM ANALYSIS
# ═══════════════════════════════════════════════════════════

def groq_score(resume_text: str, jd_text: str) -> dict:
    prompt = f"""You are an expert AI HR assistant.

JOB DESCRIPTION:
{jd_text[:1500]}

CANDIDATE RESUME:
{resume_text[:2000]}

Return ONLY valid JSON (no extra text, no markdown):
{{
  "candidate_name": "name from resume",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "experience_years": 0,
  "education": "bachelors/masters/phd/diploma/not specified",
  "final_score": 0,
  "recommendation": "SHORTLIST/MAYBE/REJECT",
  "summary": "3-line explanation"
}}
Rules: final_score 0-100. SHORTLIST>=75, MAYBE>=50, else REJECT."""

    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600,
    )
    raw = re.sub(r"```json|```", "", resp.choices[0].message.content).strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "parse_failed", "raw": raw[:200]}


# ═══════════════════════════════════════════════════════════
# API MODELS
# ═══════════════════════════════════════════════════════════

class JDModel(BaseModel):
    title:            str
    description:      str
    skills_required:  Optional[List[str]] = []
    experience_years: Optional[int]       = None
    education:        Optional[str]       = "not specified"


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@fapp.get("/")
def root():
    return convert_numpy({
        "status":          "running",
        "resumes_indexed": collection.count(),
        "jd_title":        stored_jd.get("title", "None"),
        "model":           GROQ_MODEL,
        "embed_model":     EMBED_MODEL,
        "chroma_path":     CHROMA_PATH,
    })


@fapp.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    rid = str(uuid.uuid4())[:8]
    sp  = UPLOAD_DIR / f"{rid}_{file.filename}"

    with open(sp, "wb") as f:
        shutil.copyfileobj(file.file, f)

    parsed = parse_file(str(sp))
    index_resume(rid, parsed, file.filename)

    return convert_numpy({
        "resume_id": rid,
        "filename":  file.filename,
        "indexed":   True,
        "parsed":    {
            "name":             parsed.get("name", ""),
            "email":            parsed.get("email", ""),
            "experience_years": parsed.get("experience_years", 0),
            "skills_detected":  parsed.get("skills", []),
        },
    })


@fapp.post("/upload-jd")
async def upload_jd(jd: JDModel):
    global stored_jd
    stored_jd = jd.model_dump()
    stored_jd["jd_id"] = str(uuid.uuid4())[:8]
    return {"jd_id": stored_jd["jd_id"], "title": jd.title}


@fapp.get("/ranked-candidates")
def ranked():
    if collection.count() == 0:
        raise HTTPException(404, "No resumes indexed yet. Upload resumes first.")
    if not stored_jd:
        raise HTTPException(404, "No JD uploaded. POST to /upload-jd first.")

    jd_text = (
        f"{stored_jd.get('title', '')}\n"
        f"{stored_jd.get('description', '')}\n"
        f"Required skills: {', '.join(stored_jd.get('skills_required', []))}"
    )

    expanded_query = transform_query(jd_text)

    candidates = hybrid_search(
        query_text      = expanded_query,
        n_results       = HYBRID_FETCH,
        min_exp_years   = 0,
        required_skills = [],
    )

    if not candidates:
        return convert_numpy({
            "job_title":         stored_jd.get("title", ""),
            "total_candidates":  0,
            "message":           "No candidates found.",
            "ranked_candidates": [],
        })

    top_candidates = rerank_candidates(expanded_query, candidates, top_n=RERANK_TOP_N)

    results = []
    for cand in top_candidates:
        scored = groq_score(cand.get("document", ""), jd_text)
        if True:  # temporarily show all results
            meta = cand.get("metadata", {})
            scored.update({
                "resume_id":       cand["resume_id"],
                "filename":        meta.get("filename", ""),
                "candidate_name":  scored.get("candidate_name") or meta.get("name", "Unknown"),
                "rerank_score":    round(float(cand.get("rerank_score", 0)), 4),
                "vector_distance": round(float(cand.get("distance", 1)), 4),
            })
            results.append(scored)

    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    response = {
        "job_title":           stored_jd.get("title", ""),
        "expanded_query":      expanded_query[:300] + "...",
        "total_indexed":       collection.count(),
        "retrieved_by_search": len(candidates),
        "sent_to_llm":         len(results),
        "shortlisted":         sum(1 for r in results if r.get("recommendation") == "SHORTLIST"),
            "maybe":           sum(1 for r in results if r.get("recommendation") == "MAYBE"),
"rejected":            sum(1 for r in results if r.get("recommendation") == "REJECT"),
        "ranked_candidates":   results,
    }

    return convert_numpy(response)


@fapp.delete("/clear")
def clear():
    global stored_jd, collection
    chroma_client.delete_collection("resumes")
    collection = chroma_client.get_or_create_collection(
        name="resumes",
        metadata={"hnsw:space": "cosine"},
    )
    stored_jd = {}
    return {"message": "ChromaDB collection cleared and JD reset."}


@fapp.get("/collection-info")
def collection_info():
    count = collection.count()
    if count == 0:
        return {"count": 0, "items": []}
    peek = collection.peek(limit=5)
    return convert_numpy({
        "count":           count,
        "sample_ids":      peek["ids"],
        "sample_metadata": peek["metadatas"],
    })