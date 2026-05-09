# 🎯 Resume Screening AI — Search Relevance Edition

> **AI-powered recruitment platform** with hybrid vector search, cross-encoder reranking, and Groq LLaMA 3 analysis. Built for scale — not just a keyword matcher.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=flat-square&logo=streamlit)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Local-purple?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🚀 What Makes This Different

Most resume screeners just run every resume through an LLM and hope for the best. This system uses a **proper Search Relevance pipeline** — the same architecture used in production recommendation engines:

```
JD Input
   │
   ▼
Query Transformation (Groq expands vague JD into rich search concept)
   │
   ▼
Hybrid Search (ChromaDB vector similarity + metadata hard filters)
   │
   ▼
Cross-Encoder Reranking (FlashRank reads JD + resume TOGETHER)
   │
   ▼
LLM Deep Analysis (Groq scores only top 5 — not all resumes)
   │
   ▼
Ranked Results ✅
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗄️ **Persistent Vector Store** | ChromaDB stores resume embeddings locally — upload once, search forever |
| 🔀 **Hybrid Search** | Vector similarity + metadata filters (experience years, skills) |
| 🧠 **Query Transformation** | Groq expands "Senior Dev" into 200-word semantic concept before searching |
| 🎯 **Cross-Encoder Reranking** | FlashRank re-reads JD + resume together — fixes semantic drift |
| ⚡ **Groq LLaMA 3** | Ultra-fast inference on top-5 candidates only |
| 📊 **Transparent Scoring** | 0-100 score, matched skills, missing skills, SHORTLIST/MAYBE/REJECT |
| 🖥️ **Beautiful UI** | Glassmorphism Streamlit frontend with real-time status |

---

## 🧠 What is Semantic Drift (and how we fix it)

**The Problem:** When you use an LLM to *both* retrieve *and* rank resumes, it hallucinates relevance. A resume mentioning "Python" tangentially ranks high for a Python job because the model "vibes" with it.

**The Fix:** Separate retrieval from ranking.

| Step | Tool | Why |
|---|---|---|
| Retrieve | ChromaDB (bi-encoder) | Fast — finds semantically similar resumes |
| Hard filter | Metadata WHERE clause | Blocks candidates below experience threshold |
| Rerank | FlashRank (cross-encoder) | Reads JD + resume *together* — no drift |
| Analyze | Groq LLaMA 3 | Deep analysis on top 5 only |

---

## 🛠️ Tech Stack

```
Backend      FastAPI + Uvicorn
Frontend     Streamlit
Vector DB    ChromaDB (local, persistent)
Embeddings   SentenceTransformer (all-MiniLM-L6-v2) — free, runs on CPU
Reranker     FlashRank (ms-marco-MiniLM-L-12-v2) — free, local
LLM          Groq API → LLaMA 3.3 70B Versatile
File Parse   pdfplumber + python-docx
```

---

## 📁 Project Structure

```
Resume-screening-ai/
├── backend/
│   ├── backend.py          # FastAPI app — full search relevance pipeline
│   ├── .env                # GROQ_API_KEY goes here
│   ├── chroma_db/          # Auto-created — persistent vector store
│   └── uploads/resumes/    # Auto-created — uploaded resume files
├── frontend/
│   └── app.py              # Streamlit UI
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/engrrabdulkhaliq001/Resume-screening-ai.git
cd Resume-screening-ai
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn groq python-dotenv pdfplumber python-docx \
            chromadb sentence-transformers flashrank streamlit requests
```

> **First run:** SentenceTransformer (~80MB) and FlashRank (~150MB) models download automatically and cache locally. Free forever after.

### 3. Set your Groq API key

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_key_here
```

Get a free key at: [console.groq.com](https://console.groq.com)

### 4. Start the backend

```bash
cd backend
python -m uvicorn backend:fapp --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the frontend (new terminal)

```bash
cd frontend
streamlit run app.py
```

Open: [http://localhost:8501](http://localhost:8501)

---

## 🔄 How to Use

1. **Upload Job Description** — Fill in title, description, required skills, experience level
2. **Upload Resumes** — PDF, DOCX, DOC, or TXT (bulk upload supported)
3. **Click Score & Rank** — Pipeline runs automatically
4. **View Results** — Ranked table with scores, matched/missing skills, and detailed breakdown

> **Note:** Resumes are stored in ChromaDB permanently. You only need to upload them once — even after server restart they remain indexed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Server status + indexed resume count |
| `POST` | `/upload-jd` | Upload job description |
| `POST` | `/upload-resume` | Upload + index a resume into ChromaDB |
| `GET` | `/ranked-candidates` | Run full pipeline — returns ranked results |
| `GET` | `/collection-info` | Debug: see what's in ChromaDB |
| `DELETE` | `/clear` | Clear all resumes and JD |

### Example: Upload JD

```bash
curl -X POST http://localhost:8000/upload-jd \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We need a Python developer with FastAPI and ML experience.",
    "skills_required": ["python", "fastapi", "docker"],
    "experience_years": 3,
    "education": "bachelors"
  }'
```

### Example: Ranked Results Response

```json
{
  "job_title": "Senior Python Developer",
  "expanded_query": "We are seeking an experienced Python engineer...",
  "total_indexed": 12,
  "retrieved_by_search": 12,
  "sent_to_llm": 3,
  "shortlisted": 1,
  "maybe": 2,
  "rejected": 0,
  "ranked_candidates": [
    {
      "candidate_name": "Abdul Khaliq",
      "matched_skills": ["python", "fastapi", "docker"],
      "missing_skills": ["kubernetes", "aws"],
      "experience_years": 2,
      "education": "bachelors",
      "final_score": 78,
      "recommendation": "SHORTLIST",
      "summary": "Strong Python and FastAPI skills...",
      "rerank_score": 0.8921,
      "vector_distance": 0.1823
    }
  ]
}
```

---

## 🎯 Scoring Logic

| Score | Recommendation | Meaning |
|---|---|---|
| ≥ 75 | ✅ SHORTLIST | Strong match — move to interview |
| 50–74 | ⚠️ MAYBE | Partial match — review manually |
| < 50 | ❌ REJECT | Poor match |

---

## 🔧 Configuration

Edit these constants in `backend/backend.py`:

```python
GROQ_MODEL    = "llama-3.3-70b-versatile"   # Groq model
EMBED_MODEL   = "all-MiniLM-L6-v2"          # Embedding model (local)
HYBRID_FETCH  = 20                           # Candidates retrieved by vector search
RERANK_TOP_N  = 5                            # Candidates sent to Groq after reranking
```

---

## 🌐 Deployment

### Backend — Railway

```bash
# Set environment variable in Railway dashboard:
GROQ_API_KEY=your_key_here
```

> Note: ChromaDB stores data locally. For production, replace with a hosted vector DB like Pinecone or Weaviate.

### Frontend — Streamlit Cloud

Add to `secrets.toml`:
```toml
API_URL = "https://your-railway-backend-url.up.railway.app"
```

---

## 📈 Why This Architecture Matters (for Upwork clients)

This is not a simple "send resume to ChatGPT" script. This is a **Search Relevance System**:

- **Bi-encoder + Cross-encoder pipeline** — industry standard for retrieval-augmented systems
- **Persistent vector store** — scales to thousands of resumes without re-processing
- **Metadata hard filters** — enforces non-negotiable requirements before LLM sees candidates
- **Query expansion** — handles vague job titles by enriching them semantically
- **Cost-efficient** — Groq only analyzes top 5, not all resumes

The same architecture powers recommendation systems at LinkedIn, Indeed, and similar platforms.

---

## 👤 Author

**Abdul Khaliq**
- 🌐 Portfolio: [myportfolio-abdulkhaliq.vercel.app](https://myportfolio-abdulkhaliq.vercel.app)
- 💻 GitHub: [@engrrabdulkhaliq001](https://github.com/engrrabdulkhaliq001)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ using FastAPI, ChromaDB, SentenceTransformers, FlashRank, and Groq LLaMA 3*
