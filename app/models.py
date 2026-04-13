from typing import Literal

from pydantic import BaseModel, Field


OutputFormat = Literal["text", "docx", "pdf"]


class OptimizeResumeRequest(BaseModel):
    job_description: str = Field(..., min_length=20, description="Raw job description text")
    resume_text: str | None = Field(default=None, description="Optional pasted or extracted resume text")
    target_role: str | None = Field(default=None, description="Optional target role override")
    output_format: OutputFormat = Field(default="text")
    max_projects: int = Field(default=4, ge=1, le=8)


class ProjectRecommendation(BaseModel):
    company: str
    role: str
    title: str
    original_description: str
    optimized_bullet: str
    impact: str
    matched_skills: list[str]
    relevance_score: float


class JobDescriptionSummary(BaseModel):
    title: str | None = None
    responsibilities: list[str]
    extracted_skills: list[str]
    keywords: list[str]


class OptimizeResumeResponse(BaseModel):
    optimized_resume: str
    ats_score: float
    keyword_match_score: float
    embedding_similarity_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recommended_experiences: list[ProjectRecommendation]
    jd_summary: JobDescriptionSummary
    export_path: str | None = None
