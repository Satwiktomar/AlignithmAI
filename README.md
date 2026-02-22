# ⚡ Alignithm.AI

**AI-powered resume and career intelligence platform.** Alignithm.AI helps you optimize your resume, score your fit against job descriptions, generate cover letters, analyze skill gaps, simulate recruiter reviews, and manage your career portfolio — all powered by Gemini AI.

---

## Features

| Feature | Description |
|---------|-------------|
| 📄 **Smart Resume Parsing** | Upload PDF/DOCX/TXT — AI extracts all structured data |
| 🎯 **Match Scoring** | ATS-style scoring across skill, keyword, experience, and ATS dimensions |
| ✍️ **Cover Letter Generator** | Tone-aware, human-sounding letters grounded in your actual resume |
| 📊 **Skill Gap Analysis** | Identifies missing skills and generates a phased learning roadmap |
| 🤖 **Recruiter Simulation** | Honest AI recruiter feedback with shortlist decision |
| 🗂️ **Project Ranker** | Ranks your projects by relevance to the target job |
| 🔖 **Resume Versions** | Save and compare tailored resume snapshots per job |
| 💼 **Job Analyzer** | Paste or scrape any job posting for structured parsing |

---

## Architecture

```
alignithm-ai/
├── backend/          FastAPI REST API + SQLite DB
│   ├── app/
│   │   ├── api/routes/     auth, resume, jobs, match, coverletter, projects, advanced
│   │   ├── models/         SQLAlchemy ORM models
│   │   ├── schemas/        Pydantic schemas
│   │   ├── services/       gemini, parser, scraper, auth
│   │   └── prompts/        All Gemini prompt templates
│   └── requirements.txt
│
├── ml/               FastAPI ML microservice (semantic similarity + ATS scoring)
│   ├── embedding_engine.py     Sentence-Transformers embeddings
│   ├── ats_scorer.py           Keyword coverage + ATS formatting checks
│   ├── skill_taxonomy.py       Skill normalization and overlap detection
│   ├── routes/                 similarity, ats, taxonomy endpoints
│   └── requirements.txt
│
└── frontend/         Streamlit UI
    ├── app.py                  Main app + sidebar navigation
    ├── pages_custom/           dashboard, resume, jobs, match, coverletter,
    │                           skillgap, recruiter, projects, versions
    └── utils/                  auth.py (login page + API helper), styles.py (CSS)
```

---

## Setup

### Prerequisites
- Python 3.11+
- A [Google AI Studio](https://ai.google.dev) API key with access to `gemini-2.5-flash`

### 1. Clone
```bash
git clone https://github.com/Satwiktomar/AlignithmAI.git
cd AlignithmAI
```

### 2. Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=sqlite:///./rolefit.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

Run migrations and start:
```bash
alembic upgrade head
uvicorn app.main:app --port 8000 --reload
```

### 3. ML Service
```bash
cd ml
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

> ⚠️ `sentence-transformers` will download ~90MB model on first run.

### 4. Frontend
```bash
cd frontend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| Backend API | FastAPI, SQLAlchemy, SQLite, passlib (JWT auth) |
| AI Engine | Google Gemini 2.5 Flash |
| ML Service | FastAPI, Sentence-Transformers (all-MiniLM-L6-v2), scikit-learn |
| Frontend | Streamlit, custom CSS (Inter font, dark theme) |
| Auth | JWT (python-jose), bcrypt 4.0.1 |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key |
| `GEMINI_MODEL` | ✅ | Default: `gemini-2.5-flash` |
| `DATABASE_URL` | ✅ | SQLite path or PostgreSQL URL |
| `SECRET_KEY` | ✅ | JWT signing key (change in production) |
| `ALGORITHM` | ✅ | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | — | Default: `10080` (7 days) |
| `ML_SERVICE_URL` | — | Default: `http://localhost:8001` |

---

## Notes

- **URL scraping**: LinkedIn, Indeed, and Greenhouse block bots. Use "Paste text" mode for those sites.
- **Resume parsing**: Supports PDF, DOCX, TXT up to ~12,000 characters.
- **Gemini model**: Only `gemini-2.5-flash` is confirmed working on the free API tier at this time. `gemini-1.5-flash` and `gemini-2.0-flash` may not be available depending on your API key region/tier.

---

## License

MIT
