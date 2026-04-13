from streamlit_app import optimize_resume


def test_streamlit_fallback_optimizer() -> None:
    payload = {
        "job_description": (
            "We need a backend engineer with Python, FastAPI, SQL, Docker, and API design experience."
        ),
        "target_role": "Backend Engineer",
        "output_format": "text",
        "max_projects": 2,
    }

    result = optimize_resume(payload)

    assert "optimized_resume" in result
    assert result["ats_score"] >= 0
    assert isinstance(result["matched_skills"], list)
