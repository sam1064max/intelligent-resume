from app.services.runtime import optimize_resume_payload


def test_streamlit_fallback_optimizer() -> None:
    payload = {
        "job_description": (
            "We need a backend engineer with Python, FastAPI, SQL, Docker, and API design experience."
        ),
        "target_role": "Backend Engineer",
        "output_format": "text",
        "max_projects": 2,
    }

    result = optimize_resume_payload(payload)

    assert "optimized_resume" in result
    assert result["ats_score"] >= 0
    assert isinstance(result["matched_skills"], list)
