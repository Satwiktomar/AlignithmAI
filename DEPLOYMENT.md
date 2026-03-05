# AlignithmAI — Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AlignithmAI                              │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Frontend    │──▶│   Backend    │──▶│  ML Service   │       │
│  │  (Streamlit)  │   │  (FastAPI)   │   │  (FastAPI)    │       │
│  │  Port: 8501   │   │  Port: 8000  │   │  Port: 8001   │      │
│  └──────────────┘   └──────┬───────┘   └──────────────┘        │
│                            │                                    │
│                     ┌──────▼───────┐   ┌──────────────┐        │
│                     │   Database   │   │   Ollama      │        │
│                     │ SQLite/PG    │   │   (local AI)  │        │
│                     │              │   │  Port: 11434  │        │
│                     └──────────────┘   └──────────────┘        │
│                                                                 │
│              ┌────────────────────────────┐                     │
│              │   Gemini API (Cloud AI)    │                     │
│              │   Per-user API key         │                     │
│              └────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

### `backend/` — FastAPI REST API (Port 8000)
| File / Dir | Purpose |
|---|---|
| `app/main.py` | FastAPI app, CORS, middleware, route registration |
| `app/database.py` | SQLAlchemy engine (SQLite dev / PostgreSQL prod) |
| `app/models/__init__.py` | ORM models: User, Resume, Job, MatchScore, CoverLetter, Project, CachedRoadmap |
| `app/api/routes/auth.py` | JWT auth (register, login, /me) |
| `app/api/routes/resume.py` | Resume CRUD, PDF/DOCX parsing |
| `app/api/routes/jobs.py` | Job description CRUD |
| `app/api/routes/match.py` | Resume ↔ JD matching via Gemini |
| `app/api/routes/advanced.py` | Skill gap, recruiter sim, roadmap builder (with caching), tone/bias detection, industry mode |
| `app/api/routes/coverletter.py` | Cover letter generation |
| `app/api/routes/projects.py` | Project management CRUD |
| `app/services/gemini.py` | Gemini API client with retry + fallback to local Ollama |
| `app/services/ollama_service.py` | Ollama local model client (Mistral) |
| `app/services/auth.py` | Password hashing, JWT tokens, API key encryption |
| `app/services/parser.py` | Resume text extraction (PDF/DOCX) |
| `app/services/scraper.py` | Job URL scraping |
| `app/prompts/__init__.py` | All AI prompts (resume parse, JD parse, match, skill gap, roadmap, etc.) |
| `app/limiter.py` | Rate limiter (slowapi) |
| `Dockerfile` | Python 3.11-slim + gcc + libpq-dev |
| `requirements.txt` | FastAPI, SQLAlchemy, google-genai, httpx, python-jose, etc. |
| `.env.example` | Template for environment variables |

### `ml/` — ML Microservice (Port 8001)
| File / Dir | Purpose |
|---|---|
| `main.py` | FastAPI app, model warmup on startup |
| `embedding_engine.py` | Sentence-transformers embedding + cosine similarity + caching |
| `ats_scorer.py` | Rule-based ATS scoring (keyword coverage, formatting, quantification) |
| `skill_taxonomy.py` | Skill normalization + taxonomy mapping (1000+ skills) |
| `section_detector.py` | Resume section header detection |
| `action_verb_analyzer.py` | Action verb analysis + strong verb suggestions |
| `routes/similarity.py` | `/similarity` and `/rank-projects` endpoints |
| `routes/ats.py` | `/ats-score` and `/ats-enhanced` endpoints |
| `routes/taxonomy.py` | `/normalize-skills` endpoint |
| `__init__.py` | Unified API surface for all ML functions |
| `Dockerfile` | Python 3.11-slim |
| `requirements.txt` | FastAPI, sentence-transformers, scikit-learn, numpy |

### `frontend/` — Streamlit UI (Port 8501)
| File / Dir | Purpose |
|---|---|
| `app.py` | Main Streamlit app, navigation, auth check, Ollama toggle |
| `pages_custom/dashboard.py` | Dashboard with stats |
| `pages_custom/resume.py` | Resume upload + viewing |
| `pages_custom/jobs.py` | Job description management |
| `pages_custom/match.py` | Resume ↔ JD match analysis |
| `pages_custom/coverletter.py` | Cover letter generation |
| `pages_custom/skillgap.py` | Skill gap analysis with flowchart |
| `pages_custom/roadmap.py` | Roadmap builder with caching |
| `pages_custom/recruiter.py` | Recruiter simulation |
| `pages_custom/projects.py` | Project management |
| `pages_custom/versions.py` | Resume versioning |
| `pages_custom/profile.py` | Settings / API key config |
| `utils/auth.py` | API helper (requests wrapper with auth headers) |
| `utils/styles.py` | Dark theme CSS + page header component |
| `Dockerfile` | Python 3.11-slim + Streamlit |
| `requirements.txt` | Streamlit, requests, altair |

---

## Environment Variables

### Backend (`backend/.env`)
```env
# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///./rolefit.db
# DATABASE_URL=postgresql://user:pass@host:5432/rolefit

# Auth
SECRET_KEY=<random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI — Gemini (users provide their own API key via Settings)
GEMINI_MODEL=gemini-2.0-flash
GEMINI_FALLBACK_MODEL=gemini-2.0-flash-lite

# AI — Local (Ollama)
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

# ML Service
ML_SERVICE_URL=http://localhost:8001

# CORS
ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

# Environment
ENVIRONMENT=development
```

### Frontend (`frontend/.env`)
```env
API_URL=http://localhost:8000/api
```
> Note: the frontend reads `API_URL` via `os.getenv("API_URL", "http://localhost:8000/api")` in `utils/auth.py`.

### ML Service
```env
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- (Optional) Ollama for local AI — [https://ollama.com](https://ollama.com)
- (Optional) PostgreSQL for production-like DB

### Step 1: Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# Create .env from template
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Run
uvicorn app.main:app --reload --port 8000
```
The SQLite database `rolefit.db` is auto-created on first startup.

### Step 2: ML Service
```bash
cd ml
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload --port 8001
```
> First startup downloads the sentence-transformers model (~90MB). This is a one-time download.

### Step 3: Frontend
```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
streamlit run app.py --server.port 8501
```

### Step 4: Local AI (Optional)
```bash
# Install Ollama from https://ollama.com
ollama serve                  # Start the Ollama server
ollama pull mistral           # Download the Mistral model (~4GB)
```
Then toggle "🖥️ Local AI" ON in the Streamlit sidebar.

---

## Docker Compose Deployment

```bash
# From project root
docker-compose up --build -d
```

This starts 4 services:
- `backend` on port 8000
- `ml` on port 8001
- `frontend` on port 8501
- `db` (PostgreSQL 16) on port 5432

Access the app at `http://localhost:8501`.

> **Note:** Ollama runs on the host, not in Docker. The backend accesses it via `http://host.docker.internal:11434`.

---

## Render Deployment

The project includes `render.yaml` for one-click deploy on [Render](https://render.com):

1. Push the repo to GitHub
2. In Render dashboard → **New Blueprint Instance** → connect your repo
3. Render auto-detects `render.yaml` and creates:
   - `rolefit-backend` (Python web service)
   - `rolefit-ml` (Python web service)
   - `rolefit-frontend` (Python web service)
   - `rolefit-db` (PostgreSQL free tier)
4. Set `ALLOWED_ORIGINS` on the backend to your frontend URL
5. The `SECRET_KEY` is auto-generated by Render

> **Important:** On Render free tier, services spin down after 15min of inactivity. First request after idle takes ~30s.

---

## Database

| Mode | Engine | Config |
|---|---|---|
| Development | SQLite | `DATABASE_URL=sqlite:///./rolefit.db` (auto-created) |
| Production | PostgreSQL | `DATABASE_URL=postgresql://user:pass@host:5432/dbname` |

Tables are auto-created via `Base.metadata.create_all()` on startup. Models:
- `users` — auth, API key storage, preferences
- `resumes` — uploaded resumes with parsed JSON
- `resume_versions` — versioned resume snapshots
- `job_descriptions` — parsed JDs
- `match_scores` — Resume ↔ JD match results
- `cover_letters` — generated cover letters
- `projects` — user projects
- `cached_roadmaps` — cached roadmap generations (NEW)

---

## AI Architecture

### Cloud AI (Gemini)
- Users provide their own Gemini API key via Settings
- Key is encrypted (AES) before storage in DB
- Primary model: `gemini-2.0-flash`, fallback: `gemini-2.0-flash-lite`
- Automatic retry with exponential backoff on quota errors
- Falls back to local Ollama if both Gemini models are exhausted

### Local AI (Ollama)
- Runs on the host machine
- Default model: `mistral`
- Toggle-able per user in the sidebar
- Used as fallback when no API key is configured or Gemini quota is exhausted

---

## Key API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |
| POST | `/api/resume/upload` | Upload resume (PDF/DOCX) |
| POST | `/api/jobs/` | Add job description |
| POST | `/api/match/analyze` | Match resume ↔ JD |
| POST | `/api/coverletter/generate` | Generate cover letter |
| POST | `/api/advanced/skillgap` | Skill gap analysis |
| POST | `/api/advanced/roadmap-builder` | Generate/cache roadmap |
| GET | `/api/advanced/cached-roadmaps` | List cached roadmaps |
| DELETE | `/api/advanced/cached-roadmaps/{id}` | Delete cached roadmap |
| POST | `/api/advanced/recruiter-sim` | Recruiter simulation |
| POST | `/api/advanced/tone-detect` | AI tone detection |
| POST | `/api/advanced/bias-detect` | Bias/redundancy detection |
| POST | `/api/advanced/industry-mode` | Industry-specific calibration |
| GET | `/api/advanced/dashboard-stats` | Dashboard statistics |
| GET | `/health` | Health check |

---

## LLM Deployment Prompt

> **Copy-paste the section below to give to another LLM for deployment help:**

---

```
I need help deploying a 3-service Python web application called AlignithmAI. Here is the full system description:

## Architecture
- 3 independent Python services, each with its own Dockerfile, requirements.txt, and venv
- All services communicate over HTTP REST

## Service 1: Backend (FastAPI) — Port 8000
- Entry point: backend/app/main.py
- Start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
- Database: SQLite (dev) or PostgreSQL (prod) via SQLAlchemy ORM
- Tables auto-created on startup via Base.metadata.create_all()
- Auth: JWT tokens with python-jose, passwords hashed with passlib/bcrypt
- AI: Google Gemini API (per-user API keys encrypted with AES) with fallback to local Ollama
- Rate limiting: slowapi
- Dependencies: fastapi, uvicorn, sqlalchemy, alembic, google-genai, httpx, python-jose, passlib, bcrypt, cryptography, slowapi, psycopg2-binary, python-dotenv, pypdf2, python-docx, aiofiles
- Key env vars: DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, GEMINI_MODEL, OLLAMA_MODEL, OLLAMA_BASE_URL, ML_SERVICE_URL, ALLOWED_ORIGINS, ENVIRONMENT
- Dockerfile: python:3.11-slim with gcc and libpq-dev

## Service 2: ML Service (FastAPI) — Port 8001
- Entry point: ml/main.py
- Start command: uvicorn main:app --host 0.0.0.0 --port 8001
- Purpose: Embedding-based semantic similarity (sentence-transformers), ATS scoring, skill taxonomy normalization
- Downloads sentence-transformers model on first startup (~90MB)
- No database needed
- Dependencies: fastapi, uvicorn, pydantic, python-dotenv, scikit-learn, numpy, sentence-transformers
- Key env vars: ALLOWED_ORIGINS
- Dockerfile: python:3.11-slim

## Service 3: Frontend (Streamlit) — Port 8501
- Entry point: frontend/app.py
- Start command: streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
- Communicates with backend via HTTP (API_URL env var)
- Dependencies: streamlit, requests, altair, and other Streamlit dependencies
- Key env vars: API_URL (default: http://localhost:8000/api)
- Dockerfile: python:3.11-slim

## Database
- Dev: SQLite (auto-created rolefit.db)
- Prod: PostgreSQL 16
- Tables: users, resumes, resume_versions, job_descriptions, match_scores, cover_letters, projects, cached_roadmaps

## Optional: Ollama (Local AI)
- Not containerized — runs on the host
- Install from https://ollama.com
- Start: ollama serve
- Pull model: ollama pull mistral
- Backend connects to it at OLLAMA_BASE_URL (default http://localhost:11434)
- In Docker, use http://host.docker.internal:11434

## Docker Compose
- docker-compose.yml exists in the project root
- Services: backend, ml, frontend, db (postgres:16-alpine)
- Volume: pgdata for PostgreSQL data persistence

## Render.com
- render.yaml exists for blueprint deployment
- 3 web services + 1 PostgreSQL database
- SECRET_KEY auto-generated
- DATABASE_URL injected from Render's managed PostgreSQL

## Important Notes
- Users must provide their own Gemini API key via the Settings page (free at aistudio.google.com)
- The SECRET_KEY in .env must be changed from the default in production
- ALLOWED_ORIGINS must be updated to match the actual frontend URL in production
- Backend health check: GET /health
- Frontend health check: GET /_stcore/health
- ML health check: GET /health
```

---
