from __future__ import annotations

import json
import os

import streamlit as st

from app.services.runtime import optimize_resume_payload
from app.services.resume_parser import extract_resume_text
from app.services.telegram import (
    build_optimization_message,
    get_telegram_config,
    send_telegram_message,
)

API_URL = os.getenv("RESUME_OPTIMIZER_API_URL", "").strip()
telegram_config = get_telegram_config()

st.set_page_config(page_title="JD-Aware Resume Optimizer", layout="wide")

st.title("JD-Aware AI Resume Optimizer")
st.caption("Upload or paste a resume, add a job description, and tailor the resume to the role.")

mode_label = f"API mode ({API_URL})" if API_URL else "Standalone mode (hostable without a separate API service)"
st.info(mode_label)

with st.sidebar:
    st.subheader("Settings")
    target_role = st.text_input("Target role", placeholder="Senior AI Engineer")
    output_format = st.selectbox("Output format", ["text", "docx", "pdf"], index=0)
    max_projects = st.slider("Max projects", min_value=1, max_value=6, value=4)
    send_telegram_update = st.checkbox(
        "Send Telegram update",
        value=False,
        disabled=not telegram_config.enabled,
        help="Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.",
    )

if not telegram_config.enabled:
    st.caption("Telegram notifications are disabled. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable them.")

resume_tab, jd_tab = st.tabs(["Resume", "Job Description"])

with resume_tab:
    uploaded_resume = st.file_uploader(
        "Upload resume",
        type=["txt", "md", "pdf", "docx", "json"],
        help="TXT, MD, PDF, DOCX, and JSON are supported.",
    )
    pasted_resume = st.text_area(
        "Or paste resume text",
        height=260,
        placeholder="Paste your resume content here...",
    )

with jd_tab:
    job_description = st.text_area("Job description", height=320, placeholder="Paste the JD here...")

if st.button("Optimize Resume", type="primary", use_container_width=True):
    resume_text = pasted_resume.strip()
    if uploaded_resume is not None:
        try:
            resume_text = extract_resume_text(uploaded_resume.name, uploaded_resume.getvalue()).strip()
        except Exception as exc:
            st.error(f"Could not read the uploaded resume. Details: {exc}")
            st.stop()

    if len(resume_text) < 20:
        st.error("Please upload or paste a resume first.")
    elif len(job_description.strip()) < 20:
        st.error("Please provide a longer job description.")
    else:
        payload = {
            "job_description": job_description,
            "resume_text": resume_text,
            "target_role": target_role or None,
            "output_format": output_format,
            "max_projects": max_projects,
        }
        try:
            data = optimize_resume_payload(payload)
        except Exception as exc:
            if API_URL:
                st.error(
                    f"Could not reach the API at {API_URL}. "
                    f"Set RESUME_OPTIMIZER_API_URL only when a backend is available. Details: {exc}"
                )
            else:
                st.error(f"Optimization failed in standalone mode. Details: {exc}")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Optimized Resume")
                st.code(data["optimized_resume"], language="text")
            with col2:
                st.subheader("ATS Summary")
                st.metric("ATS Score", f'{data["ats_score"]:.2f}')
                st.metric("Keyword Match", f'{data["keyword_match_score"]:.2f}')
                st.metric("Similarity", f'{data["embedding_similarity_score"]:.2f}')
                st.write("Matched skills:", ", ".join(data["matched_skills"]) or "None")
                st.write("Missing skills:", ", ".join(data["missing_skills"]) or "None")
                if data.get("export_path"):
                    st.write("Export saved to:")
                    st.code(data["export_path"], language="text")

            st.subheader("Recommended Experience")
            for project in data["recommended_experiences"]:
                with st.expander(f'{project["title"]} | {project["company"]}'):
                    st.write(f'Relevance score: {project["relevance_score"]:.2f}')
                    st.write(f'Matched skills: {", ".join(project["matched_skills"]) or "None"}')
                    st.write("Original:")
                    st.write(project["original_description"])
                    st.write("Optimized bullet:")
                    st.write(project["optimized_bullet"])

            st.subheader("Structured JD Summary")
            st.code(json.dumps(data["jd_summary"], indent=2), language="json")

            if send_telegram_update:
                try:
                    send_telegram_message(
                        build_optimization_message(
                            payload["target_role"],
                            data["ats_score"],
                            data["matched_skills"],
                            data["missing_skills"],
                        )
                    )
                except Exception as exc:
                    st.warning(f"Resume optimized, but Telegram notification failed: {exc}")
                else:
                    st.success("Telegram update sent.")
