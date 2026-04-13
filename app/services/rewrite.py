from __future__ import annotations


def rewrite_bullet(
    role: str,
    project_title: str,
    description: str,
    impact: str,
    matched_skills: list[str],
) -> str:
    skill_phrase = f" leveraging {', '.join(matched_skills)}" if matched_skills else ""
    return (
        f"Delivered {project_title} for {role} by {description.lower()}{skill_phrase}, "
        f"driving {impact.lower()} while keeping the narrative ATS-aligned and fact-based."
    )
