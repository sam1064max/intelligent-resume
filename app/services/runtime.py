from __future__ import annotations

import os

import httpx

from app.models import OptimizeResumeRequest
from app.services.optimizer import ResumeOptimizer


optimizer = ResumeOptimizer()
API_URL = os.getenv("RESUME_OPTIMIZER_API_URL", "").strip()


def optimize_resume_payload(payload: dict) -> dict:
    if API_URL:
        response = httpx.post(API_URL, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()

    result = optimizer.optimize(OptimizeResumeRequest(**payload))
    return result.model_dump()
