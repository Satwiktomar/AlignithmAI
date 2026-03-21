from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    has_api_key: bool = False
    has_openai_key: bool = False
    ai_provider: str = "gemini"
    prefer_local_model: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_provider: Optional[str] = None
    prefer_local_model: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    skills_json: Optional[List[str]] = []
    metrics_json: Optional[List[str]] = []
    domain: Optional[str] = None
    github_url: Optional[str] = None
    complexity_level: Optional[str] = None
    tags: Optional[List[str]] = []


class ProjectUpdate(ProjectCreate):
    pass


class ProjectOut(ProjectCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    user_id: int
    original_filename: Optional[str]
    parsed_json: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeVersionCreate(BaseModel):
    version_label: str
    job_id: Optional[int] = None
    notes: Optional[str] = None


class ResumeVersionOut(BaseModel):
    id: int
    resume_id: int
    job_id: Optional[int]
    version_label: str
    content_json: Optional[Any]
    match_score: Optional[float]
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobDescriptionCreate(BaseModel):
    raw_text: Optional[str] = None
    source_url: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None


class JobDescriptionOut(BaseModel):
    id: int
    user_id: int
    raw_text: Optional[str] = None
    parsed_json: Optional[Any] = None
    source_url: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True


class CoverLetterCreate(BaseModel):
    job_id: int
    resume_id: int
    tone: str = "semi-formal"


class CoverLetterOut(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int]
    generated_text: str
    tone: str
    created_at: datetime

    class Config:
        from_attributes = True


class MatchScoreOut(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    overall_score: float
    keyword_score: float
    skill_score: float
    experience_score: float
    ats_score: float
    details_json: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True
