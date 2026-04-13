from __future__ import annotations

import re


KNOWN_SKILLS = {
    "python": "Python",
    "fastapi": "FastAPI",
    "streamlit": "Streamlit",
    "llm": "LLM",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "rag": "RAG",
    "qdrant": "Qdrant",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "postgresql": "PostgreSQL",
    "sql": "SQL",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "playwright": "Playwright",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "transformers": "Transformers",
    "api": "API",
    "microservices": "Microservices",
    "vector database": "Vector Database",
    "embeddings": "Embeddings",
    "prompt engineering": "Prompt Engineering",
}

STOPWORDS = {
    "and",
    "the",
    "with",
    "for",
    "you",
    "your",
    "our",
    "will",
    "this",
    "that",
    "from",
    "into",
    "using",
    "use",
    "are",
    "have",
    "has",
    "who",
    "their",
    "they",
    "them",
    "job",
    "role",
    "team",
    "work",
    "years",
    "year",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_title(job_description: str) -> str | None:
    patterns = [
        r"title\s*:\s*(.+)",
        r"position\s*:\s*(.+)",
        r"role\s*:\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            return match.group(1).splitlines()[0].strip()
    first_line = job_description.strip().splitlines()[0].strip()
    if len(first_line.split()) <= 8:
        return first_line
    return None


def _extract_responsibilities(job_description: str) -> list[str]:
    lines = [line.strip("-• \t") for line in job_description.splitlines()]
    return [line for line in lines if len(line.split()) > 5][:8]


def _extract_skills(job_description: str) -> list[str]:
    normalized = _normalize(job_description)
    found = []
    for skill in sorted(KNOWN_SKILLS):
        if skill in normalized:
            found.append(KNOWN_SKILLS[skill])
    return found


def _keywords(job_description: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-/+]{2,}", job_description.lower())
    counts: dict[str, int] = {}
    for token in tokens:
        if token in STOPWORDS:
            continue
        counts[token] = counts.get(token, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [token for token, _ in ordered[:12]]


def _tokens(job_description: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9\-/+]{2,}", job_description.lower()) if token not in STOPWORDS}


def parse_job_description(job_description: str, target_role: str | None = None) -> dict:
    return {
        "title": target_role or _extract_title(job_description),
        "responsibilities": _extract_responsibilities(job_description),
        "skills": _extract_skills(job_description),
        "keywords": _keywords(job_description),
        "tokens": _tokens(job_description),
    }
