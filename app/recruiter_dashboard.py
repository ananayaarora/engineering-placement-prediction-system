"""
app/recruiter_dashboard.py
AI Career Copilot – Recruiter Dashboard
Developed by Ananaya Arora
"""

import streamlit as st
import plotly.graph_objects as go
from app.resume_analyzer import parse_resume, score_resume, ROLE_SKILL_MAP, ROLES, LEVELS
from app.interview_generator import generate_questions

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1e293b",
    font={"color": "#e2e8f0"}, margin=dict(t=20, b=20),
)

SALARY_BENCHMARKS = {
    ("Data Scientist",   "Intern"):   (3, 5),
    ("Data Scientist",   "Fresher"):  (6, 10),
    ("Data Scientist",   "SDE-1"):    (10, 16),
    ("Data Scientist",   "SDE-2"):    (16, 25),
    ("ML Engineer",      "Intern"):   (3, 6),
    ("ML Engineer",      "Fresher"):  (7, 12),
    ("ML Engineer",      "SDE-1"):    (12, 18),
    ("ML Engineer",      "SDE-2"):    (18, 30),
    ("Data Analyst",     "Intern"):   (2, 4),
    ("Data Analyst",     "Fresher"):  (4, 7),
    ("Data Analyst",     "SDE-1"):    (7, 12),
    ("Data Analyst",     "SDE-2"):    (12, 18),
    ("Software Engineer","Intern"):   (3, 6),
    ("Software Engineer","Fresher"):  (6, 12),
    ("Software Engineer","SDE-1"):    (12, 20),
    ("Software Engineer","SDE-2"):    (20, 35),
    ("Backend Developer","Intern"):   (3, 5),
    ("Backend Developer","Fresher"):  (5, 10),
    ("Backend Developer","SDE-1"):    (10, 18),
    ("Backend Developer","SDE-2"):    (18, 28),
    ("Frontend Developer","Intern"):  (2, 4),
    ("Frontend Developer","Fresher"): (4, 8),
    ("Frontend Developer","SDE-1"):   (8, 14),
    ("Frontend Developer","SDE-2"):   (14, 22),
    ("Full Stack Developer","Intern"):(3, 6),
    ("Full Stack Developer","Fresher"):(6, 12),
    ("Full Stack Developer","SDE-1"): (12, 20),
    ("Full Stack Developer","SDE-2"): (20, 32),
    ("DevOps Engineer",  "Intern"):   (3, 5),
    ("DevOps Engineer",  "Fresher"):  (5, 10),
    ("DevOps Engineer",  "SDE-1"):    (10, 18),
    ("DevOps Engineer",  "SDE-2"):    (18, 28),
}


def _compute_candidate_score(parsed: dict, role: str, level: str, budget: float) -> dict:
    """Compute overall candidate fit score for a given role and budget."""
    score_data = score_resume(parsed)
    base_score = score_data["total"]

    # Skill match
    required_skills = ROLE_SKILL_MAP.get(role, [])
    current_lower = {s.lower() for s in parsed.get("skills_flat", [])}
    matched = [s for s in required_skills if s.lower() in current_lower]
    missing = [s for s in required_skills if s.lower() not in current_lower]
    skill_match_pct = int(len(matched) / len(required_skills) * 100) if required_skills else 0

    # Salary fit
    key = (role, level)
    sal_min, sal_max = SALARY_BENCHMARKS.get(key, (5, 12))
    salary_fit = "Within Budget" if sal_min <= budget <= sal_max * 1.3 else (
        "Over Budget" if budget < sal_min else "Well Within Budget"
    )

    # Overall match
    overall = int((base_score * 0.4) + (skill_match_pct * 0.6))

    if overall >= 80:
        recommendation = ("Strong Hire ✅", "#22c55e")
    elif overall >= 60:
        recommendation = ("Consider ✓", "#6366f1")
    elif overall >= 40:
        recommendation = ("Possible — Skill Gap ⚠️", "#f97316")
    else:
        recommendation = ("Not Recommended ✗", "#ef4444")

    return {
        "overall": overall,
        "resume_score": base_score,
        "skill_match_pct": skill_match_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "salary_range": (sal_min, sal_max),
        "salary_fit": salary_fit,
        "recommendation": recommendation,
        "strengths": score_data["strengths"],
        "weaknesses": score_data["weaknesses"],
    }


def show_recruiter_dashboard():
    st.title("👔 Recruiter Dashboard")
    st.markdown("Upload a candidate's resume and evaluate their fit for a specific role, level, and salary budget.")

    # ── Recruiter inputs ──────────────────────────────────
    with st.form("recruiter_form"):
        st.subheader("Hiring Parameters")
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            role = st.selectbox("Hiring Role", ROLES)
        with rc2:
            level = st.selectbox("Experience Level", LEVELS[:-1])  # Intern to SDE-2
        with rc3:
            budget = st.number_input("Salary Budget (LPA)", min_value=2.0,
                                      max_value=60.0, value=10.0, step=0.5)

        uploaded = st.file_uploader("Upload Candidate Resume (PDF or DOCX)",
                                     type=["pdf", "docx"])
        submitted = st.form_submit_button("🔍 Evaluate Candidate", use_container_width=True)

    if not submitted or not uploaded:
        _show_placeholder()
        return

    with st.spinner("Evaluating candidate..."):
        parsed = parse_resume(uploaded)
        eval_data = _compute_candidate_score(parsed, role, level, budget)
        questions = generate_questions(role, level, parsed.get("skills_flat", []))

    st.markdown("---")
    rec_label, rec_color = eval_data["recommendation"]

    # ── Recommendation banner ─────────────────────────────
    st.markdown(
        f"""
        <div style='background:{rec_color};border-radius:12px;padding:16px 24px;
        text-align:center;margin-bottom:20px'>
            <div style='font-size:1.6rem;font-weight:800;color:#ffffff'>
                Hiring Recommendation: {rec_label}
            </div>
        </div>
        """, unsafe_allow_html=True,
    )

    # ── Candidate summary ─────────────────────────────────
    st.subheader("👤 Candidate Summary")
    ci1, ci2, ci3 = st.columns(3)
    ci1.markdown(f"**Name:** {parsed['name'] or '—'}")
    ci2.markdown(f"**Email:** {parsed['email'] or '—'}")
    ci3.markdown(f"**Phone:** {parsed['phone'] or '—'}")

    st.markdown("---")

    # ── Scorecard ─────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Candidate Match Score", f"{eval_data['overall']}/100")
    s2.metric("Resume Score", f"{eval_data['resume_score']}/100")
    s3.metric("Skill Match", f"{eval_data['skill_match_pct']}%")
    s4.metric("Salary Fit", eval_data["salary_fit"])

    # ── Gauges ───────────────────────────────────────────
    g1, g2 = st.columns(2)
    with g1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eval_data["overall"],
            title={"text": "Overall Match Score", "font": {"color": "#e2e8f0"}},
            number={"font": {"color": "#e2e8f0"}, "suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
                "bar": {"color": rec_color},
                "bgcolor": "#1e293b",
                "steps": [
                    {"range": [0, 40], "color": "#7f1d1d"},
                    {"range": [40, 60], "color": "#7c2d12"},
                    {"range": [60, 80], "color": "#1e3a5f"},
                    {"range": [80, 100], "color": "#14532d"},
                ],
            },
        ))
        fig.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eval_data["skill_match_pct"],
            title={"text": "Skill Match", "font": {"color": "#e2e8f0"}},
            number={"font": {"color": "#e2e8f0"}, "suffix": "%"},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
                "bar": {"color": "#6366f1"},
                "bgcolor": "#1e293b",
                "steps": [
                    {"range": [0, 40], "color": "#7f1d1d"},
                    {"range": [40, 70], "color": "#7c2d12"},
                    {"range": [70, 100], "color": "#14532d"},
                ],
            },
        ))
        fig2.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Skills ────────────────────────────────────────────
    st.markdown("---")
    sk1, sk2 = st.columns(2)
    with sk1:
        st.subheader("✅ Matched Skills")
        if eval_data["matched_skills"]:
            st.markdown(
                " ".join(
                    f"<span style='background:#14532d;color:#bbf7d0;padding:4px 12px;"
                    f"border-radius:999px;font-size:0.8rem;margin:2px;display:inline-block'>{s}</span>"
                    for s in eval_data["matched_skills"]
                ), unsafe_allow_html=True,
            )
        else:
            st.warning("No role-required skills detected.")

    with sk2:
        st.subheader("❌ Missing Skills")
        if eval_data["missing_skills"]:
            st.markdown(
                " ".join(
                    f"<span style='background:#7f1d1d;color:#fca5a5;padding:4px 12px;"
                    f"border-radius:999px;font-size:0.8rem;margin:2px;display:inline-block'>{s}</span>"
                    for s in eval_data["missing_skills"]
                ), unsafe_allow_html=True,
            )
        else:
            st.success("Candidate has all required skills!")

    # ── Strengths & weaknesses ────────────────────────────
    st.markdown("---")
    st2a, st2b = st.columns(2)
    with st2a:
        st.subheader("💪 Strengths")
        for s in eval_data["strengths"]:
            st.success(f"✓ {s}")

    with st2b:
        st.subheader("⚠️ Weaknesses")
        for w in eval_data["weaknesses"]:
            st.error(f"✗ {w}")

    # ── Salary recommendation ─────────────────────────────
    st.markdown("---")
    sal_min, sal_max = eval_data["salary_range"]
    st.subheader("💰 Salary Recommendation")
    st.markdown(
        f"""
        <div style='background:#1e293b;border-radius:10px;padding:16px;border:1px solid #475569'>
            <div style='display:flex;gap:40px;flex-wrap:wrap'>
                <div><div style='color:#94a3b8;font-size:0.8rem'>Role Salary Range</div>
                     <div style='color:#c7d2fe;font-weight:700;font-size:1.2rem'>{sal_min}–{sal_max} LPA</div></div>
                <div><div style='color:#94a3b8;font-size:0.8rem'>Your Budget</div>
                     <div style='color:#c7d2fe;font-weight:700;font-size:1.2rem'>{budget} LPA</div></div>
                <div><div style='color:#94a3b8;font-size:0.8rem'>Fit Assessment</div>
                     <div style='color:#c7d2fe;font-weight:700;font-size:1.2rem'>{eval_data["salary_fit"]}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True,
    )

    # ── Interview questions for this candidate ────────────
    st.markdown("---")
    st.subheader(f"🎤 Suggested Interview Questions for {role} – {level}")
    with st.expander("Technical Questions", expanded=True):
        for i, q in enumerate(questions["technical"][:8], 1):
            st.markdown(f"**Q{i}.** {q}")

    with st.expander("HR Questions"):
        for i, q in enumerate(questions["hr"][:4], 1):
            st.markdown(f"**Q{i}.** {q}")

    with st.expander("Behavioral Questions"):
        for i, q in enumerate(questions["behavioral"][:3], 1):
            st.markdown(f"**Q{i}.** {q}")


def _show_placeholder():
    st.markdown(
        """
        <div style='background:#1e293b;border-radius:12px;padding:32px;
        text-align:center;border:1px dashed #475569;margin-top:20px'>
            <div style='font-size:3rem'>👔</div>
            <div style='color:#c7d2fe;font-weight:700;font-size:1.1rem;margin:12px 0'>
                Fill in Hiring Parameters & Upload Resume
            </div>
            <div style='color:#94a3b8;font-size:0.88rem'>
                The system will evaluate the candidate, compute a match score, and generate role-specific questions.
            </div>
        </div>
        """, unsafe_allow_html=True,
    )
