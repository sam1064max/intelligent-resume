from app.services.resume_parser import build_resume_data_from_text


def test_build_resume_data_from_text_extracts_projects_and_skills() -> None:
    text = """
    Sam Example
    Senior AI Engineer
    Built a FastAPI and Python service for LLM resume optimization that improved matching by 42%.
    Created a Streamlit dashboard for recruiter workflows and ATS review.
    """

    resume = build_resume_data_from_text(text)

    assert resume["name"] == "Sam Example"
    assert "Python" in resume["skills"]
    assert len(resume["experience"][0]["projects"]) >= 1
    assert resume["experience"][0]["projects"][0]["search_tokens"]
