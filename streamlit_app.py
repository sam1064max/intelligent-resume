from __future__ import annotations

import json

import httpx
import streamlit as st


API_URL = "http://127.0.0.1:8000/optimize-resume"

st.set_page_config(page_title="JD-Aware Resume Optimizer", layout="wide")

st.title("JD-Aware AI Resume Optimizer")
st.caption("Paste a job description, align the resume, and export the result.")

with st.sidebar:
    st.subheader("Settings")
    target_role = st.text_input("Target role", placeholder="Senior AI Engineer")
    output_format = st.selectbox("Output format", ["text", "docx", "pdf"], index=0)
    max_projects = st.slider("Max projects", min_value=1, max_value=6, value=4)

job_description = st.text_area("Job description", height=320, placeholder="Paste the JD here...")

if st.button("Optimize Resume", type="primary", use_container_width=True):
    if len(job_description.strip()) < 20:
        st.error("Please provide a longer job description.")
    else:
        payload = {
            "job_description": job_description,
            "target_role": target_role or None,
            "output_format": output_format,
            "max_projects": max_projects,
        }
        try:
            response = httpx.post(API_URL, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            st.error(f"Could not reach the API at {API_URL}. Start FastAPI first. Details: {exc}")
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
