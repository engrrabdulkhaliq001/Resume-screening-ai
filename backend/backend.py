"""
backend.py - FastAPI + Groq
Run: uvicorn backend:fapp --host 0.0.0.0 --port 8000
"""
import re, uuid, shutil, json, os
import backend
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()  # .env file se GROQ_API_KEY load karega

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

GROQ_MODEL = "llama-3.3-70b-versatile"
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

fapp = FastAPI()
fapp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stored_resumes: dict = {}
stored_jd: dict = {}

# API key environment variable se aayegi — kabhi hardcode mat karo
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not set!")

client = Groq(api_key=GROQ_API_KEY)


# ── File Parser ───────────────────────────────────────────
def parse_file(path: str) -> dict:
    fp = Path(path)
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
    name = (
        lines[0]
        if lines and 2 <= len(lines[0].split()) <= 4 and "@" not in lines[0]
        else "Unknown"
    )
    email_m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    email = email_m.group(0) if email_m else ""
    return {"name": name, "email": email, "full_text": text[:3000]}


# ── Groq Scoring ──────────────────────────────────────────
def groq_score(resume_text: str, jd_text: str) -> dict:
    prompt = f"""You are an expert AI HR assistant.

JOB DESCRIPTION:
{jd_text[:1500]}

CANDIDATE RESUME:
{resume_text[:2000]}

Return ONLY valid JSON (no extra text):
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

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600,
    )
    raw = re.sub(r"```json|```", "", resp.choices[0].message.content).strip()
    try:
        return json.loads(raw)
    except:
        return {"error": "parse_failed"}


# ── Endpoints ─────────────────────────────────────────────
class JDModel(BaseModel):
    title: str
    description: str
    skills_required: Optional[List[str]] = []
    experience_years: Optional[int] = None
    education: Optional[str] = "not specified"


@fapp.get("/")
def root():
    return {
        "status": "running",
        "resumes_uploaded": len(stored_resumes),
        "jd_title": stored_jd.get("title", "None"),
        "model": GROQ_MODEL,
    }


@fapp.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(400, f"Unsupported: {ext}")
    rid = str(uuid.uuid4())[:8]
    sp = UPLOAD_DIR / f"{rid}_{file.filename}"
    with open(sp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    parsed = parse_file(str(sp))
    parsed.update({"resume_id": rid, "filename": file.filename})
    stored_resumes[rid] = parsed
    return {
        "resume_id": rid,
        "filename": file.filename,
        "parsed": {"name": parsed.get("name", ""), "email": parsed.get("email", "")},
    }


@fapp.post("/upload-jd")
async def upload_jd(jd: JDModel):
    global stored_jd
    stored_jd = jd.model_dump()
    stored_jd["jd_id"] = str(uuid.uuid4())[:8]
    return {"jd_id": stored_jd["jd_id"], "title": jd.title}


@fapp.get("/ranked-candidates")
def ranked():
    if not stored_resumes:
        raise HTTPException(404, "No resumes uploaded")
    if not stored_jd:
        raise HTTPException(404, "No JD uploaded")
    jd_text = f"{stored_jd.get('title','')}\n{stored_jd.get('description','')}\nRequired: {', '.join(stored_jd.get('skills_required',[]))}"
    results = []
    for rid, resume in stored_resumes.items():
        scored = groq_score(resume.get("full_text", ""), jd_text)
        if not scored.get("error"):
            scored["resume_id"] = rid
            scored["filename"] = resume.get("filename", "")
            scored["candidate_name"] = scored.get("candidate_name") or resume.get("name", "Unknown")
            results.append(scored)
    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    return {
        "job_title": stored_jd.get("title", ""),
        "total_candidates": len(results),
        "shortlisted": sum(1 for r in results if r["recommendation"] == "SHORTLIST"),
        "maybe": sum(1 for r in results if r["recommendation"] == "MAYBE"),
        "rejected": sum(1 for r in results if r["recommendation"] == "REJECT"),
        "ranked_candidates": results,
    }


@fapp.delete("/clear")
def clear():
    stored_resumes.clear()
    stored_jd.clear()
    return {"message": "Cleared"}