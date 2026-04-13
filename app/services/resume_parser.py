from __future__ import annotations

import json
import re
from io import BytesIO

from docx import Document
from pypdf import PdfReader

from app.services.parser import KNOWN_SKILLS


def extract_resume_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".txt") or lower.endswith(".md"):
        return content.decode("utf-8", errors="ignore")
    if lower.endswith(".json"):
        parsed = json.loads(content.decode("utf-8", errors="ignore"))
        return json.dumps(parsed, indent=2)
    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if lower.endswith(".docx"):
        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    raise ValueError("Unsupported resume file type. Please upload TXT, MD, PDF, DOCX, or JSON.")


def build_resume_data_from_text(text: str) -> dict:
    cleaned = text.replace("\r", "\n")
    lines = [line.strip(" -•\t") for line in cleaned.splitlines() if line.strip()]
    name = _extract_name(lines)
    skills = _extract_skills(cleaned)
    bullets = _extract_bullets(lines)
    projects = [_build_project(index, bullet, skills) for index, bullet in enumerate(bullets, start=1)]

    if not projects:
        projects = [
            {
                "title": "Resume Summary",
                "skills": skills[:8],
                "description": cleaned[:400] or "Resume content provided by the user",
                "impact": "evidence captured from the uploaded resume",
                "search_tokens": sorted(_tokenize(cleaned)),
            }
        ]

    return {
        "name": name,
        "skills": skills,
        "experience": [
            {
                "company": "Candidate Resume",
                "role": _extract_role(lines),
                "projects": projects,
            }
        ],
    }


def _extract_name(lines: list[str]) -> str:
    if not lines:
        return "Candidate"
    first = lines[0]
    if 1 < len(first.split()) <= 5 and "@" not in first and len(first) <= 60:
        return first
    return "Candidate"


def _extract_role(lines: list[str]) -> str:
    for line in lines[:8]:
        if len(line.split()) <= 7 and "@" not in line and not any(char.isdigit() for char in line):
            return line
    return "Professional Experience"


def _extract_skills(text: str) -> list[str]:
    normalized = text.lower()
    found = []
    for skill, label in sorted(KNOWN_SKILLS.items()):
        if skill in normalized:
            found.append(label)
    return found


def _extract_bullets(lines: list[str]) -> list[str]:
    long_lines = [line for line in lines if len(line.split()) >= 8]
    return long_lines[:8]


def _build_project(index: int, bullet: str, skills: list[str]) -> dict:
    bullet_skills = [skill for skill in skills if skill.lower() in bullet.lower()]
    metric_match = re.search(r"(\d+%|\d+\+|\$\d[\d,]*|\d[\d,]*\s*(?:users|customers|projects|models|days|weeks|months))", bullet, re.IGNORECASE)
    title_words = bullet.split()[:6]
    return {
        "title": " ".join(title_words).rstrip(",.") or f"Resume Highlight {index}",
        "skills": bullet_skills[:8] or skills[:8],
        "description": bullet,
        "impact": metric_match.group(1) if metric_match else "documented impact from the resume",
        "search_tokens": sorted(_tokenize(bullet)),
    }


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9\-/+]{2,}", text.lower())}
