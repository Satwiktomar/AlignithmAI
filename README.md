# ⚡ Alignithm.AI

**AI-powered career intelligence platform.** Score your resume against any job description, generate tailored cover letters, identify skill gaps with visual roadmaps, simulate recruiter reviews, manage your project portfolio, and build learning paths — all powered by Google Gemini.

> **Live:** Deploy via [Render Blueprint](#-deploy-on-render) or [Docker Compose](#-docker-compose) in minutes.

---

## ✨ Features

### 📊 Dashboard
Real-time career activity overview. See counts of resumes, jobs analyzed, projects, and cover letters at a glance. View your recent match scores with job and resume labels, dates, and color-coded ratings.

---

### 📄 Smart Resume Parsing
Upload your resume in **PDF, DOCX, or TXT** format. Gemini AI extracts all structured data — name, contact info, skills (technical, soft, domain), work experience with action verbs, education, certifications, and projects. Parsed data is stored and used across all other features. Resumes can be deleted or re-uploaded at any time.

---

### 💼 Job Description Analyzer
Two input modes:
- **Paste text** — paste any job posting directly
- **URL scrape** — enter a job posting URL and the backend fetches and parses it automatically

Gemini extracts: job title, company name, required skills, preferred qualifications, experience level, responsibilities, and more. Structured data is saved and used for matching, cover letters, and skill gap analysis.

> **Note:** LinkedIn, Indeed, and Greenhouse block bot scraping. Use "Paste text" for those sites.

---

### 🎯 Match Scoring & Improvement Suggestions
Select any resume + job combination and get a **multi-dimensional match report**:

| Sub-Score | What it measures |
|-----------|-----------------|
| **Skill Match** | Semantic overlap between your skills and the JD's requirements (via ML embeddings) |
| **Keyword Coverage** | Exact and fuzzy keyword hits for ATS systems |
| **Experience Alignment** | Years and domain relevance |
| **ATS Compatibility** | Formatting, section structure, and parsability |

Each report includes:
- **Overall score** (weighted composite)
- **Matched skills** and **missing skills** lists
- **Strengths** and **areas to improve**
- **AI-generated improvement suggestions** — actionable tips to boost your score

---

### ✍️ Cover Letter Generator
Generate a tailored cover letter for any resume + job combination. Choose from **5 tones**:
- **Formal** — traditional, corporate
- **Semi-Formal** — professional but approachable
- **Startup** — energetic, casual
- **Direct** — concise, to-the-point
- **Corporate** — structured, enterprise-focused

Letters are grounded in your actual resume data and the target JD — no generic filler. All generated letters are saved and can be downloaded as `.txt`, viewed, or deleted from the "Saved Letters" tab.

---

### 📊 Skill Gap Analysis
Select a resume and a job to identify the **exact skills gap** between your profile and the role. The AI returns:

- **✅ Skills you already have** — matched against the JD
- **🎯 Skills to acquire** — what's missing
- **Gap severity rating** — Low / Medium / High / Critical

#### 🗺️ Visual Learning Roadmap
A **color-coded interactive flowchart** rendered in the browser:
- 🟢 **Green** = Must-learn (critical priority)
- 🟡 **Yellow** = Should-learn (medium)
- ⚪ **White** = Nice-to-know (low)
- Each skill shows: **timeline**, **estimated hours**, **category**, **proficiency target**
- **Prerequisites** branch above each skill — marked ✅ if you already have them
- **Resources** with clickable links per skill

Plus:
- **⚡ Quick Wins** — skills learnable in 1-2 weeks
- **🎯 Long-term Goals**
- **🏆 Recommended Certifications** — real, verifiable certs from known providers (with URLs, priority, and timeline)
- **📝 Resume Update Tips** — how to rewrite sections to close the gap

---

### 🗺️ Roadmap Builder (Standalone)
Generate a **comprehensive learning roadmap** for any topic — not tied to a specific resume or job. Enter:
- A **role** (e.g., "ML Engineer")
- A **technology** (e.g., "Kubernetes")
- A **framework** (e.g., "React")
- Or paste a **full job description**

The AI generates a **roadmapstyle branching tree** with:
- **Sections** (gold headers) → **Sub-topics** (amber labels) → **Skills** (color-coded boxes)
- Priority tags: must_learn / should_learn / nice_to_know
- Estimated hours per skill
- Hover tooltips with learning resources
- **Certifications**, **career progression path**, and **related roadmaps** to explore next

Roadmaps are **cached per user** — instant reload for previously generated topics. Force-regenerate with the "Generate New" button.

---

### 🤖 Recruiter Simulation
An **honest AI recruiter review** of your resume against a specific job. The AI acts as a hiring manager and returns:
- **Shortlist or reject** decision with reasoning
- **Strengths** the recruiter would notice
- **Red flags** or concerns
- **What would make you a stronger candidate**

No sugarcoating — designed to give you the reality check before you apply.

---

### 🗂️ Project Portfolio with GitHub Auto-Fill
Manage your projects with rich metadata:
- **Title**, **description**, **domain**, **skills used**, **key metrics**, **complexity level**, **GitHub URL**
- **Tags** for organization

#### ⚡ GitHub Auto-Fill
Paste a **public GitHub repository URL** and click "Auto Extract." The system:
1. Fetches repo metadata (description, languages, topics)
2. Reads the README for richer context
3. Scans manifests (`package.json`, `requirements.txt`, etc.) for framework detection
4. Runs **deep contribution analysis** — classifies your commits as features, fixes, improvements
5. Lists your PRs and issues
6. Pre-fills the entire project form

#### 📄 LaTeX Export (XYZ Formula)
Generate a **resume-ready LaTeX snippet** for any project using Google's XYZ formula:
> "Accomplished X, as measured by Y, by doing Z."

Copy-paste directly into your LaTeX resume template.

#### 🏆 Project Ranking
Select a job description and rank all your projects by **relevance score** — the AI tells you which projects to highlight and why.

---

### 🔖 Resume Versions
**Save snapshots** of your resume tailored to specific jobs:
- Attach a **version label** (e.g., "ML Engineer v2") and **notes** about what changed
- Optionally link to a target job
- Match score is preserved at save time

**Compare versions** side-by-side — see skills, name, title across different snapshots. Delete old versions when no longer needed.

---

### ⚙️ Settings & Account Management
- **Profile editing** — update your display name
- **Gemini API Key management** — keys are encrypted with AES-256 (Fernet) before storage, never logged or returned in any API response
- **Local model toggle** — prefer Ollama over Gemini when available
- **Account deletion** — permanent, requires typing "DELETE" to confirm. Cascades to all data.

---

### 🧠 ML Service (Under the Hood)
The ML microservice runs independently and provides:
- **Semantic similarity** via `all-MiniLM-L6-v2` embeddings (sentence-transformers)
- **ATS scoring** — keyword extraction, formatting checks, section analysis
- **Skill taxonomy** — normalized skill matching with synonym detection (e.g., "JS" = "JavaScript")
- **AI Tone Detection** — flags generic AI-sounding phrases in your text
- **Bias & Redundancy Detection** — catches vague bullets and repeated language
- **Industry Mode Calibration** — re-scores your resume for specific sectors (tech, finance, healthcare, research)

---

### 🖥️ Local AI Fallback (Ollama)
When Gemini API quota runs out or you're offline:
- Ollama serves local models (default: Mistral)
- Status shown in the sidebar — green when Ollama is reachable
- Fully functional for all AI features (parsing, matching, cover letters, etc.)

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  ML Service   │
│  (Streamlit) │     │  (FastAPI)   │     │  (FastAPI)    │
│  Port 8501   │     │  Port 8000   │     │  Port 8001    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐     ┌──────────────┐
                     │   Database   │     │   Ollama      │
                     │ SQLite / PG  │     │  (optional)   │
                     └──────────────┘     └──────────────┘
```

- **3 independent Python services** communicating over REST
- **Per-user Gemini API keys** — users bring their own (free at [aistudio.google.com](https://aistudio.google.com))
- **Zero server-side AI costs** — no shared API key needed
- **Automatic fallback** — Gemini → Gemini Lite → Ollama (local)

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- (Optional) [Ollama](https://ollama.com) for local AI

### 1. Clone & setup
```bash
git clone https://github.com/Satwiktomar/AlignithmAI.git
cd AlignithmAI
```

### 2. Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate      # Windows
# source venv/bin/activate                         # Linux/Mac
pip install -r requirements.txt
copy .env.example .env                             # then edit .env
uvicorn app.main:app --reload --port 8000
```

### 3. ML Service
```bash
cd ml
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
> First startup downloads the sentence-transformers model (~90 MB). One-time only.

### 4. Frontend
```bash
cd frontend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open **http://localhost:8501** → register → add your Gemini API key in Settings.

---

## 🐳 Docker Compose

```bash
docker compose up --build -d
```

Starts 4 containers: **backend**, **ml**, **frontend**, **postgres**. Access at `http://localhost:8501`.

> Ollama runs on the host — the backend reaches it at `http://host.docker.internal:11434`.

---

## ☁️ Deploy on Render

The repo includes `render.yaml` for **one-click Blueprint deployment**:

1. Push to GitHub
2. Render Dashboard → **New Blueprint Instance** → connect your repo
3. Render auto-creates: `rolefit-backend`, `rolefit-ml`, `rolefit-frontend`, `rolefit-db` (PostgreSQL)
4. Update `ALLOWED_ORIGINS` on the backend to your actual frontend URL
5. Done — `SECRET_KEY` and `DATABASE_URL` are auto-configured

> **Free tier note:** Services sleep after 15 min of inactivity. First request after idle takes ~30s.

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI, SQLAlchemy, Pydantic, slowapi (rate limiting) |
| **AI Engine** | Google Gemini 2.0 Flash + Lite (per-user keys, encrypted at rest) |
| **ML Service** | Sentence-Transformers (`all-MiniLM-L6-v2`), scikit-learn |
| **Frontend** | Streamlit with custom dark theme (Inter font) |
| **Auth** | JWT (python-jose) + bcrypt password hashing |
| **Database** | SQLite (dev) / PostgreSQL 16 (prod) — auto-migrates on startup |
| **Local AI** | Ollama (Mistral) — optional offline fallback |
| **Container** | Docker Compose, Render Blueprint |

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./rolefit.db` | SQLite (dev) or PostgreSQL connection string |
| `SECRET_KEY` | — | JWT signing key (**change in production**) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Token expiry (7 days) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Primary Gemini model |
| `GEMINI_FALLBACK_MODEL` | `gemini-2.0-flash-lite` | Fallback model |
| `ML_SERVICE_URL` | `http://localhost:8001` | ML microservice URL |
| `ML_INTERNAL_KEY` | — | Shared key for backend ↔ ML auth |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | CORS origins (comma-separated) |
| `OLLAMA_MODEL` | `mistral` | Local Ollama model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `ENVIRONMENT` | `development` | Set to `production` to disable `/docs` |

### Frontend (`frontend/.env`)
| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Backend API base URL |

### ML Service (`ml/.env`)
| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:8000` | CORS origins |
| `ML_INTERNAL_KEY` | — | Must match backend's key |

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login (returns JWT) |
| `GET` | `/api/auth/me` | Current user profile |
| `PUT` | `/api/auth/me` | Update name / API key / preferences |
| `DELETE` | `/api/auth/me` | Delete account (cascades all data) |
| `POST` | `/api/resume/upload` | Upload resume (PDF/DOCX/TXT) |
| `GET` | `/api/resume/` | List all resumes |
| `POST` | `/api/resume/version` | Save resume version snapshot |
| `POST` | `/api/jobs/parse` | Parse job description (text or URL) |
| `GET` | `/api/jobs/` | List all jobs |
| `POST` | `/api/match/` | Match resume ↔ JD (multi-dimensional) |
| `POST` | `/api/match/suggest` | AI improvement suggestions |
| `POST` | `/api/coverletter/generate` | Generate cover letter |
| `GET` | `/api/coverletter/` | List saved cover letters |
| `POST` | `/api/projects/` | Add project |
| `POST` | `/api/projects/recommend` | Rank projects for a job |
| `POST` | `/api/advanced/skillgap` | Skill gap analysis |
| `POST` | `/api/advanced/roadmap-builder` | Generate learning roadmap |
| `POST` | `/api/advanced/recruiter-sim` | Recruiter simulation |
| `POST` | `/api/advanced/detect-ai-tone` | AI tone detection |
| `POST` | `/api/advanced/detect-bias` | Bias & redundancy scan |
| `POST` | `/api/advanced/industry-mode` | Industry-specific calibration |
| `GET` | `/api/advanced/dashboard-stats` | Dashboard statistics |
| `GET` | `/health` | Health check |

---

## 🧪 Running Tests

```bash
# Backend
cd backend && python -m pytest tests/ -v

# ML Service
cd ml && python -m pytest tests/ -v
```

---

## 📝 Notes

- **Users provide their own Gemini API key** via Settings → free at [aistudio.google.com](https://aistudio.google.com)
- **URL scraping**: LinkedIn, Indeed, Greenhouse block bots — use "Paste text" mode
- **Resume parsing**: Supports PDF, DOCX, TXT up to ~12,000 characters
- **Database auto-creates** all tables on first startup — no manual migrations needed
- **Auto-migration**: New columns added to ORM models are automatically migrated on startup

---

## 📄 License

MIT
