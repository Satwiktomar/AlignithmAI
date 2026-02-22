from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import User, Project, Resume, ResumeVersion, JobDescription, CoverLetter, MatchScore  # noqa: F401
from app.api.routes import auth, resume, jobs, match, projects, coverletter, advanced

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RoleFit AI API",
    description="AI-Powered Resume & Career Optimization Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(coverletter.router, prefix="/api")
app.include_router(advanced.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "RoleFit AI API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
