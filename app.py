"""Streamlit dashboard for the AI-Powered Applicant Tracking System."""

from io import BytesIO
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from auth_ui import (
    init_auth_session_state,
    is_logged_in,
    render_auth_page,
    render_settings_page,
    render_sidebar_user_panel,
)
from models import ParsedResume, ScreeningResult
from sample_data import SAMPLE_CANDIDATES_CSV, SAMPLE_JOB_DESCRIPTION
from screening_service import run_screening
from skill_gap import get_matched_skills


def init_session_state() -> None:
    """Initialize Streamlit session state keys."""
    init_auth_session_state()
    if "screening_result" not in st.session_state:
        st.session_state.screening_result = None
    if "jd_input" not in st.session_state:
        st.session_state.jd_input = ""


def render_header() -> None:
    """Render application header and metrics overview."""
    st.title("AI-Powered Applicant Tracking System")
    st.markdown(
        "Automate recruitment screening with NLP-based resume parsing, "
        "weighted ATS scoring, skill gap analysis, and recruiter analytics."
    )

    result: Optional[ScreeningResult] = st.session_state.screening_result
    if result and result.candidates:
        cols = st.columns(4)
        cols[0].metric("Candidates Screened", len(result.candidates))
        cols[1].metric("Avg ATS Score", f"{sum(c.ats_score for c in result.candidates) / len(result.candidates):.1f}")
        cols[2].metric("Top Score", f"{result.candidates[0].ats_score:.1f}")
        cols[3].metric("Required Skills", len(result.job.required_skills))


def render_screening_tab() -> None:
    """Render the resume upload and screening execution tab."""
    st.subheader("Job Description")

    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        if st.button("Load Sample Job Description"):
            st.session_state.jd_input = SAMPLE_JOB_DESCRIPTION
            st.rerun()
    with demo_col2:
        if st.button("Run Demo Screening (5 sample candidates)", type="secondary"):
            with st.spinner("Running demo with sample dataset..."):
                st.session_state.screening_result = run_screening(
                    SAMPLE_JOB_DESCRIPTION,
                    [("sample_candidates.csv", BytesIO(SAMPLE_CANDIDATES_CSV.encode()))],
                    persist=False,
                )
            st.success("Demo screening complete! Check Rankings tab for verdicts and reasoning.")
            st.rerun()

    job_description = st.text_area(
        "Paste the job description",
        placeholder="Python Developer\n\nRequired Skills:\nPython, SQL, Django, Docker\n\nExperience: 2+ Years",
        height=180,
        key="jd_input",
    )

    st.subheader("Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload candidate resumes (PDF / DOCX / CSV)",
        type=["pdf", "docx", "csv"],
        accept_multiple_files=True,
    )

    with st.expander("CSV format guide"):
        st.markdown(
            "Upload a CSV with **one candidate per row**. Supported columns "
            "(flexible naming):\n\n"
            "| Column | Examples |\n"
            "|--------|----------|\n"
            "| Name | `name`, `candidate_name`, `full_name` |\n"
            "| Email | `email`, `email_address` |\n"
            "| Phone | `phone`, `mobile`, `contact` |\n"
            "| Skills | `skills`, `technical_skills` (comma-separated) |\n"
            "| Experience | `experience`, `years_of_experience` |\n"
            "| Education | `education`, `degree`, `university` |\n"
            "| Certifications | `certifications`, `certs` |\n"
            "| Company | `company`, `current_company` |\n"
            "| Resume text | `resume_text`, `summary`, `profile` |"
        )
        st.code(
            "name,email,phone,skills,experience,education\n"
            "Rahul Kumar,rahul@email.com,9876543210,\"Python, SQL, Django\",3,B.Tech CS\n"
            "Priya Sharma,priya@email.com,9123456780,\"Java, SQL\",1,B.E IT",
            language="csv",
        )

    if uploaded_files:
        csv_count = sum(1 for f in uploaded_files if f.name.lower().endswith(".csv"))
        doc_count = len(uploaded_files) - csv_count
        st.info(
            f"{len(uploaded_files)} file(s) ready — "
            f"{doc_count} document(s), {csv_count} CSV file(s)."
        )

    if st.button("Run Screening", type="primary"):
        if not job_description.strip():
            st.error("Please paste a job description.")
            return
        if not uploaded_files:
            st.error("Please upload at least one resume (PDF, DOCX, or CSV).")
            return

        with st.spinner("Parsing resumes, scoring candidates, and generating insights..."):
            files = [(f.name, f) for f in uploaded_files]
            st.session_state.screening_result = run_screening(job_description, files)
        st.success("Screening complete! Explore the tabs for rankings, skill gaps, and analytics.")
        st.rerun()


def build_rankings_dataframe(candidates: list[ParsedResume]) -> pd.DataFrame:
    """
    Build a ranked candidate DataFrame for the dashboard.

    Args:
        candidates: Scored candidate list.

    Returns:
        DataFrame sorted by ATS score descending.
    """
    rows = []
    for i, c in enumerate(candidates, 1):
        matched = ", ".join(s.title() for s in c.matched_skills[:5]) or "None"
        missing = ", ".join(s.title() for s in c.missing_skills[:5]) or "None"
        rows.append({
            "Rank": i,
            "Candidate": c.name,
            "Verdict": c.match_verdict or "—",
            "ATS Score": c.ats_score,
            "Skill Match": c.skill_score,
            "Matched Skills": matched,
            "Missing Skills": missing,
            "Experience (Yrs)": c.experience_years,
            "Recommendation": c.match_summary or "—",
            "File": c.filename,
        })
    return pd.DataFrame(rows)


def render_rankings_tab() -> None:
    """Render candidate ranking dashboard with search and filters."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to see candidate rankings.")
        return

    df = build_rankings_dataframe(result.candidates)

    col1, col2, col3 = st.columns(3)
    search = col1.text_input("Search by name or email")
    min_score = col2.slider("Minimum ATS Score", 0, 100, 0)
    sort_by = col3.selectbox("Sort by", ["ATS Score", "Skill Match", "Quality Score", "Experience"])

    filtered = df[df["ATS Score"] >= min_score]
    if search:
        mask = filtered["Candidate"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    ascending = sort_by != "ATS Score"
    filtered = filtered.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
    filtered["Rank"] = range(1, len(filtered) + 1)

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.subheader("Candidate Classification & Reasoning")
    for rank, c in enumerate(result.candidates, 1):
        with st.expander(f"#{rank} {c.name} — {c.match_verdict} ({c.ats_score}/100)"):
            st.markdown(f"**Recommendation:** {c.match_summary}")
            st.markdown("**Why this score?**")
            for reason in c.match_reasoning:
                st.markdown(f"- {reason}")

    st.subheader("Resume Preview")
    names = [f"{c.name} ({c.filename})" for c in result.candidates]
    selected = st.selectbox("Select candidate to preview", names)
    idx = names.index(selected)
    candidate = result.candidates[idx]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Email:** {candidate.email or 'Not found'}")
        st.markdown(f"**Phone:** {candidate.phone or 'Not found'}")
        st.markdown(f"**Company:** {candidate.current_company or 'Not found'}")
        st.markdown(f"**Skills:** {', '.join(candidate.skills) or 'None detected'}")
    with col_b:
        st.markdown(f"**Education:** {', '.join(candidate.education) or 'Not found'}")
        st.markdown(f"**Certifications:** {', '.join(candidate.certifications) or 'None'}")
        st.markdown(f"**Quality Score:** {candidate.quality_score}/100")

    with st.expander("Full Resume Text"):
        st.text(candidate.raw_text[:5000] if candidate.raw_text else "No text extracted.")


def render_skill_gap_tab() -> None:
    """Render skill gap analysis for each candidate."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to see skill gap analysis.")
        return

    st.markdown(f"**Required Skills:** {', '.join(result.job.required_skills) or 'None detected'}")

    selected = st.selectbox(
        "Select candidate",
        [c.name for c in result.candidates],
        key="skill_gap_select",
    )
    candidate = next(c for c in result.candidates if c.name == selected)

    matched = get_matched_skills(candidate, result.job)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Matched Skills**")
        if matched:
            for skill in matched:
                st.success(f"✓ {skill.title()}")
        else:
            st.warning("No matching skills found.")

    with col2:
        st.markdown("**Missing Skills**")
        if candidate.missing_skills:
            for skill in candidate.missing_skills:
                st.error(f"✗ {skill.title()}")
        else:
            st.success("No skill gaps — full match!")

    if candidate.skill_recommendations:
        st.subheader("Learning Recommendations")
        for rec in candidate.skill_recommendations:
            st.markdown(f"- {rec}")


def render_interview_tab() -> None:
    """Render AI-generated interview questions per candidate."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to generate interview questions.")
        return

    selected = st.selectbox(
        "Select candidate",
        [c.name for c in result.candidates],
        key="interview_select",
    )
    candidate = next(c for c in result.candidates if c.name == selected)

    st.markdown(f"**Based on skills:** {', '.join(candidate.skills[:8]) or 'General'}")
    st.subheader("Suggested Interview Questions")
    for i, question in enumerate(candidate.interview_questions, 1):
        st.markdown(f"{i}. {question}")


def render_comparison_tab() -> None:
    """Render side-by-side candidate comparison."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or len(result.candidates) < 2:
        st.info("Upload at least 2 resumes and run screening to compare candidates.")
        return

    names = [c.name for c in result.candidates]
    col1, col2 = st.columns(2)
    sel_a = col1.selectbox("Candidate A", names, key="compare_a")
    sel_b = col2.selectbox("Candidate B", names, index=min(1, len(names) - 1), key="compare_b")

    a = next(c for c in result.candidates if c.name == sel_a)
    b = next(c for c in result.candidates if c.name == sel_b)

    compare_df = pd.DataFrame({
        "Metric": ["ATS Score", "Skill Match", "Experience Score", "Education Score",
                   "Certifications", "Quality Score", "Years Experience", "Skills Count"],
        sel_a: [a.ats_score, a.skill_score, a.experience_score, a.education_score,
                a.certification_score, a.quality_score, a.experience_years, len(a.skills)],
        sel_b: [b.ats_score, b.skill_score, b.experience_score, b.education_score,
                b.certification_score, b.quality_score, b.experience_years, len(b.skills)],
    })
    st.dataframe(compare_df, use_container_width=True, hide_index=True)

    fig = px.bar(
        compare_df.melt(id_vars="Metric", var_name="Candidate", value_name="Value"),
        x="Metric", y="Value", color="Candidate", barmode="group",
        title=f"{sel_a} vs {sel_b}",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_analytics_tab() -> None:
    """Render hiring analytics visualizations."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to see analytics.")
        return

    candidates = result.candidates

    col1, col2 = st.columns(2)

    with col1:
        score_df = pd.DataFrame({
            "Candidate": [c.name for c in candidates],
            "ATS Score": [c.ats_score for c in candidates],
        })
        fig_scores = px.bar(score_df, x="Candidate", y="ATS Score", title="ATS Scores by Candidate")
        st.plotly_chart(fig_scores, use_container_width=True)

    with col2:
        exp_df = pd.DataFrame({
            "Candidate": [c.name for c in candidates],
            "Experience (Years)": [c.experience_years for c in candidates],
        })
        fig_exp = px.bar(exp_df, x="Candidate", y="Experience (Years)", title="Experience Distribution")
        st.plotly_chart(fig_exp, use_container_width=True)

    all_skills: list[str] = []
    for c in candidates:
        all_skills.extend(c.skills)

    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().head(10).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        fig_skills = px.bar(skill_counts, x="Skill", y="Count", title="Top Skills Across Candidates")
        st.plotly_chart(fig_skills, use_container_width=True)

    score_breakdown = pd.DataFrame({
        "Candidate": [c.name for c in candidates],
        "Skill": [c.skill_score for c in candidates],
        "Experience": [c.experience_score for c in candidates],
        "Education": [c.education_score for c in candidates],
        "Certification": [c.certification_score for c in candidates],
    })
    melted = score_breakdown.melt(id_vars="Candidate", var_name="Component", value_name="Score")
    fig_breakdown = px.bar(
        melted, x="Candidate", y="Score", color="Component",
        barmode="stack", title="Score Component Breakdown",
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)


def render_duplicates_tab() -> None:
    """Render duplicate resume detection results."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to check for duplicates.")
        return

    if not result.duplicate_pairs:
        st.success("No duplicate resumes detected.")
        return

    st.warning(f"Found {len(result.duplicate_pairs)} potential duplicate pair(s).")
    dup_df = pd.DataFrame(result.duplicate_pairs, columns=["File A", "File B", "Similarity %"])
    st.dataframe(dup_df, use_container_width=True, hide_index=True)


def render_quality_tab() -> None:
    """Render resume quality analysis for all candidates."""
    result: Optional[ScreeningResult] = st.session_state.screening_result
    if not result or not result.candidates:
        st.info("Run screening first to analyze resume quality.")
        return

    from quality_analyzer import get_quality_issues

    rows = []
    for c in result.candidates:
        issues = get_quality_issues(c)
        rows.append({
            "Candidate": c.name,
            "Quality Score": f"{c.quality_score}/100",
            "Issues": "; ".join(issues) if issues else "None",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    fig = px.bar(
        pd.DataFrame({"Candidate": [c.name for c in result.candidates],
                      "Quality Score": [c.quality_score for c in result.candidates]}),
        x="Candidate", y="Quality Score", title="Resume Quality Scores",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_main_dashboard() -> None:
    """Render the ATS dashboard tabs for authenticated users."""
    render_header()

    tabs = st.tabs([
        "Screening",
        "Rankings",
        "Skill Gap",
        "Interview Questions",
        "Compare",
        "Analytics",
        "Duplicates",
        "Quality",
    ])

    with tabs[0]:
        render_screening_tab()
    with tabs[1]:
        render_rankings_tab()
    with tabs[2]:
        render_skill_gap_tab()
    with tabs[3]:
        render_interview_tab()
    with tabs[4]:
        render_comparison_tab()
    with tabs[5]:
        render_analytics_tab()
    with tabs[6]:
        render_duplicates_tab()
    with tabs[7]:
        render_quality_tab()


def main() -> None:
    """Render the full ATS Streamlit application."""
    st.set_page_config(
        page_title="AI-Powered ATS",
        page_icon="📋",
        layout="wide",
    )

    init_session_state()

    if not is_logged_in():
        render_auth_page()
        return

    render_sidebar_user_panel()

    if st.session_state.show_settings:
        render_settings_page()
        return

    render_main_dashboard()


if __name__ == "__main__":
    main()
