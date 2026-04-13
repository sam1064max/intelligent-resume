from __future__ import annotations

from math import sqrt


def cosine_overlap(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    shared = len(tokens_a & tokens_b)
    return shared / (sqrt(len(tokens_a)) * sqrt(len(tokens_b)))


def keyword_match_score(required_skills: list[str], available_skills: list[str]) -> float:
    if not required_skills:
        return 1.0
    required = {skill.lower() for skill in required_skills}
    available = {skill.lower() for skill in available_skills}
    return len(required & available) / len(required)


def compute_ats_score(required_skills: list[str], available_skills: list[str], jd_tokens: set[str], resume_tokens: set[str]) -> tuple[float, float, float]:
    keyword_score = keyword_match_score(required_skills, available_skills)
    similarity_score = min(cosine_overlap(jd_tokens, resume_tokens), 1.0)
    ats_score = round((0.6 * keyword_score) + (0.4 * similarity_score), 4)
    return ats_score, round(keyword_score, 4), round(similarity_score, 4)
