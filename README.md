# JD-Aware AI Resume Optimizer

This project implements an MVP of the design doc in `jd_aware_ai_resume_optimizer_design_doc.pdf`.
It provides:

- A FastAPI backend for resume optimization
- A Streamlit UI for interactive use and single-service hosting
- A structured master resume knowledge base in JSON
- JD parsing, skill extraction, experience matching, bullet rewriting, ATS scoring, and skill gap analysis
- Resume export to `DOCX`, `PDF`, and plain text
- GitHub Actions CI for install and smoke tests
- Optional Telegram notifications for app updates and CI runs

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

If you only want a single hostable service, you can skip FastAPI entirely and run just:

```powershell
streamlit run streamlit_app.py
```

The Streamlit app now runs in standalone mode by default and calls the optimizer directly in-process.
If you do want Streamlit to use the API, set `RESUME_OPTIMIZER_API_URL`.

## Hosting

### Option 1: Streamlit Community Cloud

- Push the repo to GitHub
- Create a new Streamlit app pointed at `streamlit_app.py`
- No extra backend service is required

### GitHub Pages

- This repo also includes a GitHub Pages landing page from `docs/`
- It is useful as a public project URL on GitHub
- It does not run the interactive Streamlit or FastAPI app

### Option 2: Docker-based hosts

This repo includes a `Dockerfile` that serves the Streamlit app directly:

```bash
docker build -t intelligent-resume .
docker run -p 8501:8501 intelligent-resume
```

### Option 3: Split frontend/backend deployment

- Host FastAPI with `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Host Streamlit separately
- Set `RESUME_OPTIMIZER_API_URL` in the Streamlit environment

## Telegram Notifications

You can send optimization updates and CI notifications to Telegram.

### Create the bot

1. Open Telegram and message `@BotFather`
2. Run `/newbot`
3. Choose a bot name and username
4. Copy the bot token
5. Start a chat with your new bot and send it any message once

### Get your chat ID

Use this URL in a browser after replacing `<TOKEN>`:

```text
https://api.telegram.org/bot<TOKEN>/getUpdates
```

Find the `chat` object and copy its `id`.

### App environment variables

Set these where Streamlit runs:

```text
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Once set, the Streamlit sidebar will enable a `Send Telegram update` option after each optimization run.

### GitHub Actions secrets

Add these repository secrets in GitHub:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

When those secrets exist, the CI workflow will send Telegram messages for successful and failed runs.

Approvals still happen in GitHub and Codex. Telegram is only used for notifications and status updates.

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

## CI

GitHub Actions is configured in `.github/workflows/ci.yml` and runs:

- dependency installation
- FastAPI smoke tests
- optimizer import and execution checks
- optional Telegram success or failure notifications when secrets are configured

## Notes

- The bullet rewrite engine is deterministic and fact-preserving for local use.
- The scoring formula follows the design doc:

```text
ATS_SCORE = 0.6 * keyword_match + 0.4 * embedding_similarity
```

- "Embedding similarity" is approximated locally using normalized term overlap to avoid requiring
  external infrastructure in the first build.
