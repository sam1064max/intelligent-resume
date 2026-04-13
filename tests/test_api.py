from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_optimize_resume() -> None:
    payload = {
        "job_description": (
            "Senior AI Engineer role requiring Python, FastAPI, LLM, RAG, "
            "embeddings, Docker, and Streamlit experience for intelligent workflows."
        ),
        "target_role": "Senior AI Engineer",
        "output_format": "text",
        "max_projects": 3,
    }
    response = client.post("/optimize-resume", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert "optimized_resume" in body
    assert body["ats_score"] >= 0
    assert "Python" in body["matched_skills"]
    assert len(body["recommended_experiences"]) >= 1
