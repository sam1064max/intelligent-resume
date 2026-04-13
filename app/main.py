from fastapi import FastAPI

from app.models import OptimizeResumeRequest, OptimizeResumeResponse
from app.services.optimizer import ResumeOptimizer

app = FastAPI(title="JD-Aware AI Resume Optimizer", version="0.1.0")
optimizer = ResumeOptimizer()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/optimize-resume", response_model=OptimizeResumeResponse)
def optimize_resume(payload: OptimizeResumeRequest) -> OptimizeResumeResponse:
    return optimizer.optimize(payload)
