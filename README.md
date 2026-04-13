# JD-Aware AI Resume Optimizer

This project implements an MVP of the design doc in `jd_aware_ai_resume_optimizer_design_doc.pdf`.
It provides:

- A FastAPI backend for resume optimization
- A Streamlit UI for interactive use
- A structured master resume knowledge base in JSON
- JD parsing, skill extraction, experience matching, bullet rewriting, ATS scoring, and skill gap analysis
- Resume export to `DOCX`, `PDF`, and plain text

## Architecture

User input -> JD parser -> skill extraction -> retrieval scoring -> experience ranking ->
bullet rewrite -> ATS scoring -> export generation

The MVP uses a lightweight local similarity engine based on token overlap and cosine-style scoring
so it can run without a separate vector database. The code is structured so a hosted embedding model
or Qdrant integration can be added later without changing the API shape.

## Project Structure

```text
app/
  main.py
  models.py
  services/
data/
  master_resume.json
outputs/
streamlit_app.py
```

## Quick Start

1. Create a virtual environment.
2. Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Start the API:

```powershell
uvicorn app.main:app --reload
```

4. Start the frontend in another terminal:

```powershell
streamlit run streamlit_app.py
```

## API

### `POST /optimize-resume`

Request:

```json
{
  "job_description": "Senior AI Engineer with Python, LLM, FastAPI, and RAG experience...",
  "target_role": "Senior AI Engineer",
  "output_format": "text"
}
```

Response includes:

- `optimized_resume`
- `ats_score`
- `missing_skills`
- `matched_skills`
- `recommended_experiences`
- `export_path`

### `GET /health`

Simple health check endpoint.

## Notes

- The bullet rewrite engine is deterministic and fact-preserving for local use.
- The scoring formula follows the design doc:

```text
ATS_SCORE = 0.6 * keyword_match + 0.4 * embedding_similarity
```

- "Embedding similarity" is approximated locally using normalized term overlap to avoid requiring
  external infrastructure in the first build.
