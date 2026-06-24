"""
app/skill_gap.py
AI Career Copilot – Skill Gap Analysis
Developed by Ananaya Arora
"""

import streamlit as st
import plotly.graph_objects as go
from app.resume_analyzer import ROLE_SKILL_MAP, ROLES

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1e293b",
    font={"color": "#e2e8f0"}, margin=dict(t=20, b=20),
    xaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
    yaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
)

LEARNING_RESOURCES = {
    "python":           ("Python", "https://docs.python.org/3/tutorial/"),
    "machine learning": ("ML Crash Course (Google)", "https://developers.google.com/machine-learning/crash-course"),
    "deep learning":    ("fast.ai", "https://www.fast.ai/"),
    "tensorflow":       ("TF Tutorials", "https://www.tensorflow.org/tutorials"),
    "pytorch":          ("PyTorch Tutorials", "https://pytorch.org/tutorials/"),
    "sql":              ("SQLZoo", "https://sqlzoo.net/"),
    "docker":           ("Docker Get Started", "https://docs.docker.com/get-started/"),
    "kubernetes":       ("K8s Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
    "aws":              ("AWS Free Tier", "https://aws.amazon.com/free/"),
    "react":            ("React Docs", "https://react.dev/"),
    "node.js":          ("Node.js Guides", "https://nodejs.org/en/docs/guides/"),
    "data structures":  ("DSA — NeetCode", "https://neetcode.io/"),
    "system design":    ("System Design Primer", "https://github.com/donnemartin/system-design-primer"),
    "pandas":           ("Pandas Docs", "https://pandas.pydata.org/docs/"),
    "javascript":       ("MDN JS", "https://developer.mozilla.org/en-US/docs/Learn/JavaScript"),
    "java":             ("Java Tutorials", "https://dev.java/learn/"),
    "tableau":          ("Tableau Public", "https://public.tableau.com/app/learn/how-to-videos"),
    "power bi":         ("Microsoft Power BI", "https://learn.microsoft.com/en-us/power-bi/"),
    "git":              ("Git Handbook", "https://guides.github.com/introduction/git-handbook/"),
    "nlp":              ("Hugging Face NLP Course", "https://huggingface.co/course/"),
}

TARGET_SALARY_SKILLS = {
    "5-8 LPA":   ["python", "sql", "pandas", "git", "rest api"],
    "8-12 LPA":  ["python", "sql", "machine learning", "docker", "rest api", "system design"],
    "12-18 LPA": ["python", "machine learning", "deep learning", "aws", "docker", "system design", "kubernetes"],
    "18-25 LPA": ["python", "deep learning", "llm", "aws", "kubernetes", "system design", "mlops"],
}


def _gap_analysis(current_skills: list[str], target_role: str) -> tuple[list[str], list[str]]:
    required = ROLE_SKILL_MAP.get(target_role, [])
    current_lower = {s.lower() for s in current_skills}
    matched = [s for s in required if s.lower() in current_lower]
    missing = [s for s in required if s.lower() not in current_lower]
    return matched, missing


def _salary_gap_skills(current_skills: list[str], target_lpa: float) -> list[str]:
    bracket = (
        "18-25 LPA" if target_lpa >= 18
        else "12-18 LPA" if target_lpa >= 12
        else "8-12 LPA" if target_lpa >= 8
        else "5-8 LPA"
    )
    needed = TARGET_SALARY_SKILLS[bracket]
    current_lower = {s.lower() for s in current_skills}
    return [s for s in needed if s not in current_lower]


def show_skill_gap():
    st.title("🎯 Skill Gap Analysis")
    st.markdown("Compare your current skills against role requirements and get a personalised learning roadmap.")

    # ── Source: uploaded resume or manual entry ───────────
    has_resume = st.session_state.get("resume_uploaded", False)

    if has_resume:
        parsed = st.session_state["parsed_resume"]
        current_skills = parsed.get("skills_flat", [])
        st.info(f"📄 Using skills extracted from your resume ({len(current_skills)} skills detected).")
        with st.expander("Detected skills from resume"):
            if current_skills:
                st.markdown(
                    " ".join(
                        f"<span style='background:#312e81;color:#c7d2fe;padding:3px 10px;"
                        f"border-radius:999px;font-size:0.8rem;margin:2px;display:inline-block'>{s}</span>"
                        for s in current_skills
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.write("None detected.")
    else:
        st.warning("No resume uploaded yet. You can manually enter skills below.")
        skills_input = st.text_area(
            "Enter your skills (comma separated)",
            placeholder="python, machine learning, sql, react ...",
        )
        current_skills = [s.strip().lower() for s in skills_input.split(",") if s.strip()] if skills_input else []

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        target_role = st.selectbox("Target Role", ROLES)
    with col_b:
        target_salary = st.number_input("Target Salary (LPA)", min_value=3.0, max_value=50.0,
                                         value=12.0, step=0.5)

    if not current_skills:
        st.info("Enter or upload skills to see your gap analysis.")
        return

    matched, missing = _gap_analysis(current_skills, target_role)
    salary_gap_skills = _salary_gap_skills(current_skills, target_salary)

    total_required = len(ROLE_SKILL_MAP.get(target_role, []))
    match_pct = int(len(matched) / total_required * 100) if total_required else 0

    # ── Role match summary ────────────────────────────────
    st.markdown("---")
    st.subheader(f"Role Fit: {target_role}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Skills Matched", f"{len(matched)} / {total_required}")
    m2.metric("Role Fit Score", f"{match_pct}%")
    m3.metric("Skills Missing", len(missing))

    # Radar / fit gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=match_pct,
        title={"text": "Role Fit (%)", "font": {"color": "#e2e8f0"}},
        number={"suffix": "%", "font": {"color": "#e2e8f0"}},
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
    fig.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e2e8f0"})
    st.plotly_chart(fig, use_container_width=True)

    # ── Skills breakdown ──────────────────────────────────
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("✅ Skills You Have")
        if matched:
            st.markdown(
                " ".join(
                    f"<span style='background:#14532d;color:#bbf7d0;padding:4px 12px;"
                    f"border-radius:999px;font-size:0.82rem;margin:2px;display:inline-block'>{s}</span>"
                    for s in matched
                ),
                unsafe_allow_html=True,
            )
        else:
            st.warning("No matching skills found for this role.")

    with g2:
        st.subheader("❌ Missing Skills")
        if missing:
            st.markdown(
                " ".join(
                    f"<span style='background:#7f1d1d;color:#fca5a5;padding:4px 12px;"
                    f"border-radius:999px;font-size:0.82rem;margin:2px;display:inline-block'>{s}</span>"
                    for s in missing
                ),
                unsafe_allow_html=True,
            )
        else:
            st.success("🎉 You have all required skills for this role!")

    # ── Salary gap analysis ───────────────────────────────
    st.markdown("---")
    st.subheader(f"💰 Salary Gap Analysis — Target: {target_salary} LPA")

    if salary_gap_skills:
        st.markdown(
            f"""
            <div style='background:#1e293b;border-radius:10px;padding:16px;border:1px solid #475569'>
                <div style='color:#fbbf24;font-weight:700;margin-bottom:8px'>
                    ⚠️ Skills needed to reach {target_salary} LPA:
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            " ".join(
                f"<span style='background:#78350f;color:#fde68a;padding:4px 12px;"
                f"border-radius:999px;font-size:0.82rem;margin:2px;display:inline-block'>{s}</span>"
                for s in salary_gap_skills
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"✅ Your skill set aligns with the {target_salary} LPA bracket!")

    # ── Learning roadmap ──────────────────────────────────
    st.markdown("---")
    st.subheader("📚 Personalised Learning Roadmap")
    roadmap_skills = list(dict.fromkeys(missing + salary_gap_skills))[:8]

    if roadmap_skills:
        for i, skill in enumerate(roadmap_skills, 1):
            resource = LEARNING_RESOURCES.get(skill.lower())
            link_text = (
                f"[{resource[0]}]({resource[1]})" if resource else "Search on Coursera / Udemy"
            )
            st.markdown(
                f"""
                <div style='background:#1e293b;border-radius:8px;padding:12px 16px;
                margin-bottom:8px;border-left:3px solid #6366f1'>
                    <span style='color:#c7d2fe;font-weight:700'>Step {i}: Learn {skill.upper()}</span><br>
                    <span style='color:#94a3b8;font-size:0.85rem'>Resource: {link_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("🎉 No gaps found! You are well prepared for the target role and salary.")

    # Save for PDF report
    st.session_state["skill_gap_data"] = {
        "target_role": target_role,
        "target_salary": target_salary,
        "matched": matched,
        "missing": missing,
        "match_pct": match_pct,
        "salary_gap_skills": salary_gap_skills,
    }
