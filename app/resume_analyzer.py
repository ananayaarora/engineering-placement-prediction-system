"""
app/resume_analyzer.py
AI Career Copilot – Resume Analyzer & Scoring
Regex-based NLP extraction (no spaCy model download required)
Developed by Ananaya Arora
"""

import re
import io
import os
import streamlit as st

# ── Skill Knowledge Base ──────────────────────────────────────────────────────

ALL_SKILLS = {
    "Programming Languages": [
        "python", "java", "c++", "c", "javascript", "typescript", "go", "rust",
        "kotlin", "swift", "r", "scala", "matlab", "php", "ruby", "dart",
    ],
    "Web & Frontend": [
        "html", "css", "react", "angular", "vue", "nextjs", "tailwind",
        "bootstrap", "sass", "webpack", "jquery",
    ],
    "Backend & APIs": [
        "node.js", "nodejs", "django", "flask", "fastapi", "spring boot",
        "express", "rest api", "graphql", "microservices",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "opencv",
        "huggingface", "transformers", "llm", "generative ai",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "sqlite", "oracle", "cassandra", "dynamodb", "neo4j",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "jenkins", "github actions", "ci/cd", "linux",
        "nginx", "ansible",
    ],
    "Data Engineering": [
        "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake",
        "databricks", "etl", "data warehouse", "bigquery",
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "jira", "confluence", "figma",
        "postman", "jupyter", "vscode", "excel", "power bi", "tableau",
    ],
}

FLAT_SKILLS = sorted({s for skills in ALL_SKILLS.values() for s in skills})

ROLE_SKILL_MAP = {
    "Data Scientist": [
        "python", "machine learning", "deep learning", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch", "sql", "statistics",
        "nlp", "matplotlib", "jupyter",
    ],
    "ML Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "mlops", "docker", "aws", "kubernetes", "scikit-learn", "fastapi",
        "pandas", "numpy",
    ],
    "Data Analyst": [
        "python", "sql", "excel", "tableau", "power bi", "pandas",
        "matplotlib", "seaborn", "statistics", "data visualization",
    ],
    "Software Engineer": [
        "python", "java", "c++", "data structures", "algorithms",
        "system design", "sql", "git", "rest api", "docker",
    ],
    "Backend Developer": [
        "python", "java", "node.js", "django", "flask", "fastapi",
        "spring boot", "sql", "mongodb", "redis", "docker", "rest api",
    ],
    "Frontend Developer": [
        "javascript", "typescript", "react", "angular", "vue",
        "html", "css", "tailwind", "nextjs", "webpack", "git",
    ],
    "Full Stack Developer": [
        "javascript", "react", "node.js", "python", "sql", "mongodb",
        "rest api", "html", "css", "docker", "git",
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "aws", "azure", "terraform", "jenkins",
        "github actions", "ci/cd", "linux", "ansible", "python",
    ],
}

ROLES = sorted(ROLE_SKILL_MAP.keys())
LEVELS = ["Intern", "Fresher", "SDE-1", "SDE-2", "Senior"]


# ── Text Extraction ───────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from DOCX bytes using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        return f"[DOCX extraction error: {e}]"


def extract_text(uploaded_file) -> str:
    """Dispatch to PDF or DOCX extractor based on file extension."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(raw)
    elif name.endswith(".docx"):
        return extract_text_from_docx(raw)
    return ""


# ── Field Extraction ──────────────────────────────────────────────────────────

def extract_email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return m.group() if m else ""


def extract_phone(text: str) -> str:
    m = re.search(r"(\+?\d[\d\s\-().]{8,14}\d)", text)
    return m.group().strip() if m else ""


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line that is likely a name."""
    for line in text.splitlines():
        line = line.strip()
        if (
            line and 2 <= len(line.split()) <= 5
            and not any(c.isdigit() for c in line)
            and "@" not in line
            and len(line) < 60
        ):
            return line
    return ""


def extract_skills(text: str) -> dict[str, list[str]]:
    """Match skill keywords (case-insensitive) grouped by category."""
    lower = text.lower()
    found: dict[str, list[str]] = {}
    for category, skills in ALL_SKILLS.items():
        matched = [s for s in skills if re.search(r"\b" + re.escape(s) + r"\b", lower)]
        if matched:
            found[category] = matched
    return found


def extract_section(text: str, headings: list[str]) -> str:
    """Extract the text block under the first matching section heading."""
    pattern = r"(?i)(" + "|".join(re.escape(h) for h in headings) + r")[:\s]*\n(.*?)(?=\n[A-Z][A-Z\s]{2,}:|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(2).strip() if m else ""


def extract_education(text: str) -> list[str]:
    lines = []
    keywords = ["b.tech", "btech", "b.e", "m.tech", "mtech", "mba", "bsc", "msc",
                 "bachelor", "master", "phd", "12th", "10th", "cgpa", "gpa",
                 "university", "college", "institute", "school"]
    for line in text.splitlines():
        if any(kw in line.lower() for kw in keywords):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 5:
                lines.append(cleaned)
    return lines[:8]


def extract_experience(text: str) -> list[str]:
    items = []
    exp_pattern = re.findall(
        r"(?i)(intern|engineer|developer|analyst|scientist|lead|manager|consultant"
        r"|associate|trainee)[^\n]{0,120}",
        text
    )
    for match in exp_pattern[:5]:
        cleaned = match.strip()
        if len(cleaned) > 10:
            items.append(cleaned)
    return items


def count_projects(text: str) -> int:
    indicators = ["project", "built", "developed", "designed", "implemented",
                  "created", "deployed", "architected"]
    count = 0
    for line in text.splitlines():
        if any(kw in line.lower() for kw in indicators):
            count += 1
    return min(count, 12)


def count_certifications(text: str) -> int:
    keywords = ["certif", "course", "credential", "certified", "completion",
                 "coursera", "udemy", "edx", "nptel", "aws certified", "google cloud"]
    count = sum(1 for line in text.splitlines() if any(k in line.lower() for k in keywords))
    return min(count, 10)


def count_internships(text: str) -> int:
    count = len(re.findall(r"intern(?:ship)?", text, re.IGNORECASE))
    return min(count, 5)


def parse_resume(uploaded_file) -> dict:
    """Full pipeline: extract text → parse all fields → return structured dict."""
    text = extract_text(uploaded_file)
    all_skills = extract_skills(text)
    flat = [s for skills in all_skills.values() for s in skills]

    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills_by_category": all_skills,
        "skills_flat": flat,
        "skill_count": len(flat),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "project_count": count_projects(text),
        "certification_count": count_certifications(text),
        "internship_count": count_internships(text),
    }


# ── Resume Scoring ────────────────────────────────────────────────────────────

def score_resume(parsed: dict) -> dict:
    """
    Score the resume out of 100 across 6 weighted dimensions.
    Returns score, breakdown, strengths, weaknesses.
    """
    sc = parsed["skill_count"]
    pc = parsed["project_count"]
    ic = parsed["internship_count"]
    cc = parsed["certification_count"]
    edu = len(parsed["education"])
    exp = len(parsed["experience"])

    # Skill score (30 pts)
    skill_score = min(sc / 12 * 30, 30)

    # Projects score (20 pts)
    proj_score = min(pc / 6 * 20, 20)

    # Internships (20 pts)
    intern_score = min(ic / 3 * 20, 20)

    # Certifications (15 pts)
    cert_score = min(cc / 4 * 15, 15)

    # Education completeness (10 pts)
    edu_score = min(edu / 3 * 10, 10)

    # Experience mentions (5 pts)
    exp_score = min(exp / 3 * 5, 5)

    total = int(skill_score + proj_score + intern_score + cert_score + edu_score + exp_score)

    breakdown = {
        "Skills (30)": round(skill_score, 1),
        "Projects (20)": round(proj_score, 1),
        "Internships (20)": round(intern_score, 1),
        "Certifications (15)": round(cert_score, 1),
        "Education (10)": round(edu_score, 1),
        "Experience (5)": round(exp_score, 1),
    }

    strengths, weaknesses = [], []
    if sc >= 10:
        strengths.append(f"Strong skill set ({sc} skills detected)")
    elif sc < 5:
        weaknesses.append(f"Few skills listed — add more ({sc} detected)")

    if pc >= 4:
        strengths.append(f"Good project portfolio ({pc} projects)")
    elif pc <= 1:
        weaknesses.append("Very few projects — add 2–3 more")

    if ic >= 1:
        strengths.append(f"{ic} internship(s) listed")
    else:
        weaknesses.append("No internship experience found")

    if cc >= 3:
        strengths.append(f"{cc} certifications mentioned")
    elif cc == 0:
        weaknesses.append("No certifications detected")

    if edu:
        strengths.append("Education details present")
    else:
        weaknesses.append("Education section incomplete")

    if len(parsed["skills_by_category"]) >= 4:
        strengths.append("Diverse skill categories (technical breadth)")
    elif len(parsed["skills_by_category"]) <= 1:
        weaknesses.append("Skills concentrated in one area — add breadth")

    return {
        "total": total,
        "breakdown": breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


# ── Resume Analyzer UI Page ───────────────────────────────────────────────────

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1e293b",
    font={"color": "#e2e8f0"}, margin=dict(t=20, b=20),
)


def show_resume_analyzer():
    import plotly.graph_objects as go

    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume to extract skills, score your profile, and identify areas to improve.")

    uploaded = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Supports PDF and Word (.docx) formats",
    )

    if not uploaded:
        _render_sample_tip()
        return

    with st.spinner("Analyzing your resume..."):
        parsed = parse_resume(uploaded)
        score_data = score_resume(parsed)

    if "[extraction error]" in parsed["raw_text"].lower():
        st.error("Could not read the file. Please ensure it is a valid PDF or DOCX.")
        return

    st.success("✅ Resume analyzed successfully!")
    st.markdown("---")

    # ── Top metrics ──────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Resume Score", f"{score_data['total']}/100")
    c2.metric("Skills Found", parsed["skill_count"])
    c3.metric("Projects", parsed["project_count"])
    c4.metric("Internships", parsed["internship_count"])
    c5.metric("Certifications", parsed["certification_count"])

    st.markdown("---")

    # ── Identity section ──────────────────────────────────
    st.subheader("👤 Candidate Information")
    ic1, ic2, ic3 = st.columns(3)
    ic1.markdown(f"**Name:** {parsed['name'] or '—'}")
    ic2.markdown(f"**Email:** {parsed['email'] or '—'}")
    ic3.markdown(f"**Phone:** {parsed['phone'] or '—'}")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        # ── Resume score gauge ────────────────────────────
        st.subheader("📊 Resume Score")
        total = score_data["total"]
        if total >= 80:
            cat, col = "Excellent", "#22c55e"
        elif total >= 60:
            cat, col = "Good", "#6366f1"
        elif total >= 40:
            cat, col = "Average", "#f97316"
        else:
            cat, col = "Needs Work", "#ef4444"

        st.markdown(
            f"""
            <div style='text-align:center;padding:24px;background:#1e293b;border-radius:12px;border:2px solid {col}'>
                <div style='font-size:3.5rem;font-weight:800;color:{col}'>{total}</div>
                <div style='font-size:1rem;color:#e2e8f0'>out of 100</div>
                <div style='font-size:1rem;font-weight:700;color:{col};margin-top:6px'>{cat}</div>
            </div>
            """, unsafe_allow_html=True,
        )

        # Score breakdown bar chart
        st.markdown("<br>", unsafe_allow_html=True)
        bd = score_data["breakdown"]
        fig = go.Figure(go.Bar(
            x=list(bd.values()), y=list(bd.keys()),
            orientation="h", marker_color="#6366f1",
            text=[f"{v}" for v in bd.values()],
            textposition="outside", textfont={"color": "#e2e8f0"},
        ))
        max_val = [int(k.split("(")[1].rstrip(")")) for k in bd.keys()]
        fig.update_layout(xaxis=dict(range=[0, 32], color="#e2e8f0", gridcolor="#334155"),
                          yaxis=dict(color="#e2e8f0"), **_CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        # ── Skills by category ────────────────────────────
        st.subheader("🛠️ Detected Skills")
        if parsed["skills_by_category"]:
            for cat_name, skills in parsed["skills_by_category"].items():
                st.markdown(f"**{cat_name}**")
                st.markdown(
                    " ".join(
                        f"<span style='background:#312e81;color:#c7d2fe;padding:3px 10px;"
                        f"border-radius:999px;font-size:0.8rem;margin:2px;display:inline-block'>{s}</span>"
                        for s in skills
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown("")
        else:
            st.warning("No skills detected. Ensure skills are clearly listed in your resume.")

    st.markdown("---")

    # ── Strengths & Weaknesses ────────────────────────────
    sw1, sw2 = st.columns(2)
    with sw1:
        st.subheader("💪 Strengths")
        for s in score_data["strengths"]:
            st.success(f"✓ {s}")

    with sw2:
        st.subheader("⚠️ Weaknesses")
        for w in score_data["weaknesses"]:
            st.error(f"✗ {w}")

    # ── Education & Experience ────────────────────────────
    st.markdown("---")
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🎓 Education")
        if parsed["education"]:
            for line in parsed["education"]:
                st.markdown(f"- {line}")
        else:
            st.info("No education details detected.")

    with e2:
        st.subheader("💼 Experience Mentions")
        if parsed["experience"]:
            for line in parsed["experience"]:
                st.markdown(f"- {line}")
        else:
            st.info("No experience entries detected.")

    # Store in session state for use by other pages
    st.session_state["parsed_resume"] = parsed
    st.session_state["resume_score"] = score_data
    st.session_state["resume_uploaded"] = True

    st.markdown("---")
    st.caption("✅ Resume data stored — visit Salary Prediction, Skill Gap, or Interview Questions pages to continue.")


def _render_sample_tip():
    st.markdown(
        """
        <div style='background:#1e293b;border-radius:12px;padding:28px;border:1px dashed #475569;text-align:center;margin-top:20px'>
            <div style='font-size:3rem'>📄</div>
            <div style='color:#c7d2fe;font-size:1.1rem;font-weight:600;margin:10px 0'>Upload Your Resume to Get Started</div>
            <div style='color:#94a3b8;font-size:0.9rem;max-width:400px;margin:0 auto'>
                Supports <b>PDF</b> and <b>DOCX</b> formats.<br>
                The analyzer will extract your skills, education, projects, and experience automatically.
            </div>
            <div style='margin-top:20px;color:#64748b;font-size:0.8rem'>
                Your resume data is processed in-memory and never stored on any server.
            </div>
        </div>
        """, unsafe_allow_html=True,
    )
