from __future__ import annotations

import json
from pathlib import Path

from app.models import (
    JobDescriptionSummary,
    OptimizeResumeRequest,
    OptimizeResumeResponse,
    ProjectRecommendation,
)
from app.services.ats import compute_ats_score
from app.services.exporter import ResumeExporter
from app.services.matcher import rank_projects
from app.services.parser import parse_job_description
from app.services.resume_parser import build_resume_data_from_text
from app.services.rewrite import rewrite_bullet


class ResumeOptimizer:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.data_path = root / "data" / "master_resume.json"
        self.exporter = ResumeExporter(root / "outputs")

    def optimize(self, payload: OptimizeResumeRequest) -> OptimizeResumeResponse:
        resume_data = self._load_resume_data(payload.resume_text)
        parsed = parse_job_description(payload.job_description, payload.target_role)
        ranked = rank_projects(resume_data, parsed["tokens"], parsed["skills"])
        selected = ranked[: payload.max_projects]

        optimized_projects: list[ProjectRecommendation] = []
        collected_resume_tokens: set[str] = set()
        collected_skills: list[str] = []

        for item in selected:
            optimized_bullet = rewrite_bullet(
                role=payload.target_role or parsed["title"] or item.role,
                project_title=item.title,
                description=item.description,
                impact=item.impact,
                matched_skills=item.overlap,
            )
            optimized_projects.append(
                ProjectRecommendation(
                    company=item.company,
                    role=item.role,
                    title=item.title,
                    original_description=item.description,
                    optimized_bullet=optimized_bullet,
                    impact=item.impact,
                    matched_skills=item.overlap,
                    relevance_score=item.score,
                )
            )
            collected_resume_tokens.update(item.description.lower().split())
            collected_resume_tokens.update(skill.lower() for skill in item.skills)
            collected_skills.extend(item.skills)

        global_skills = resume_data.get("skills", [])
        collected_skills.extend(global_skills)
        matched_skills = sorted({skill for skill in parsed["skills"] if skill.lower() in {s.lower() for s in collected_skills}})
        missing_skills = sorted({skill for skill in parsed["skills"] if skill.lower() not in {s.lower() for s in collected_skills}})

        ats_score, keyword_score, similarity_score = compute_ats_score(
            parsed["skills"],
            collected_skills,
            parsed["tokens"],
            collected_resume_tokens,
        )

        optimized_resume = self._format_resume(
            name=resume_data["name"],
            target_role=payload.target_role or parsed["title"],
            matched_skills=matched_skills,
            summary_keywords=parsed["keywords"],
            recommendations=optimized_projects,
        )
        export_path = self.exporter.export(optimized_resume, payload.output_format)

        return OptimizeResumeResponse(
            optimized_resume=optimized_resume,
            ats_score=ats_score,
            keyword_match_score=keyword_score,
            embedding_similarity_score=similarity_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            recommended_experiences=optimized_projects,
            jd_summary=JobDescriptionSummary(
                title=parsed["title"],
                responsibilities=parsed["responsibilities"],
                extracted_skills=parsed["skills"],
                keywords=parsed["keywords"],
            ),
            export_path=export_path,
        )

    def _format_resume(
        self,
        name: str,
        target_role: str | None,
        matched_skills: list[str],
        summary_keywords: list[str],
        recommendations: list[ProjectRecommendation],
    ) -> str:
        summary = (
            f"{name}\n"
            f"Target Role: {target_role or 'Tailored Candidate Profile'}\n\n"
            "Professional Summary\n"
            f"Results-oriented engineer aligned to roles requiring {', '.join(summary_keywords[:8])}.\n\n"
            "Relevant Skills\n"
            f"{', '.join(matched_skills) if matched_skills else 'Adaptable problem-solving and applied software engineering'}\n\n"
            "Selected Experience\n"
        )
        bullets = []
        for rec in recommendations:
            bullets.append(
                f"- {rec.role}, {rec.company} | {rec.title}\n"
                f"  {rec.optimized_bullet}"
            )
        return summary + "\n".join(bullets)

    def _load_resume_data(self, resume_text: str | None) -> dict:
        if resume_text and resume_text.strip():
            return build_resume_data_from_text(resume_text)
        return json.loads(self.data_path.read_text(encoding="utf-8"))
