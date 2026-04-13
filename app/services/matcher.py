from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass
class RankedProject:
    company: str
    role: str
    title: str
    description: str
    impact: str
    skills: list[str]
    score: float
    overlap: list[str]


def _score(project_tokens: set[str], jd_tokens: set[str], project_skills: list[str], jd_skills: list[str]) -> float:
    if not project_tokens or not jd_tokens:
        return 0.0
    token_overlap = len(project_tokens & jd_tokens) / (sqrt(len(project_tokens)) * sqrt(len(jd_tokens)))
    skill_overlap = len({s.lower() for s in project_skills} & {s.lower() for s in jd_skills})
    bonus = skill_overlap / max(len(jd_skills), 1)
    return round((0.7 * token_overlap) + (0.3 * bonus), 4)


def rank_projects(resume_data: dict, jd_tokens: set[str], jd_skills: list[str]) -> list[RankedProject]:
    ranked: list[RankedProject] = []
    for experience in resume_data.get("experience", []):
        for project in experience.get("projects", []):
            project_tokens = set(project.get("search_tokens", []))
            overlap = sorted({s for s in project.get("skills", []) if s.lower() in {x.lower() for x in jd_skills}})
            ranked.append(
                RankedProject(
                    company=experience["company"],
                    role=experience["role"],
                    title=project["title"],
                    description=project["description"],
                    impact=project["impact"],
                    skills=project.get("skills", []),
                    score=_score(project_tokens, jd_tokens, project.get("skills", []), jd_skills),
                    overlap=overlap,
                )
            )
    return sorted(ranked, key=lambda item: item.score, reverse=True)
