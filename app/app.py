"""
app/app.py - Main Streamlit Application
AI Career Copilot – Resume Intelligence, Salary Estimation & Interview Preparation
Run: streamlit run app/app.py
Developed by Ananaya Arora
"""

import os
import sys

# Ensure project root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Copilot – Engineering Placement System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .main { background-color: #0f172a; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);
        border-right: 1px solid #312e81;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] { color: #c7d2fe !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #e2e8f0 !important; font-weight: 500 !important; }

    /* ── Buttons ── */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: opacity 0.2s;
    }
    div.stButton > button:hover { opacity: 0.88; }

    /* ── Form submit button ── */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] { border-radius: 8px; }

    /* ── Headings ── */
    h1 { color: #c7d2fe !important; font-weight: 700 !important; }
    h2, h3 { color: #e0e7ff !important; }
    h4, h5, h6 { color: #e2e8f0 !important; }

    /* ── Body text & markdown ── */
    p, li, span, label, .stMarkdown { color: #e2e8f0; }
    .stCaption, [data-testid="stCaptionContainer"] { color: #cbd5e1 !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader { color: #c7d2fe !important; }
    [data-testid="stExpander"] summary { color: #e0e7ff !important; }

    /* ── Success / Error / Warning / Info alerts ── */
    .stAlert { border-radius: 8px; }
    .stAlert p { color: #f8fafc !important; font-weight: 500; }

    /* ── Radio / Select / Slider / Number input labels ── */
    .stRadio > label, .stSelectbox > label, .stSlider > label,
    .stNumberInput > label, .stTextInput > label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    .stRadio div[role="radiogroup"] label { color: #e2e8f0 !important; }

    /* ── Selectbox / Number input fields ── */
    [data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #475569 !important;
        color: #f8fafc !important;
    }
    input, textarea {
        color: #f8fafc !important;
    }

    /* ── Slider numbers ── */
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
        color: #cbd5e1 !important;
    }
    .stSlider [data-testid="stThumbValue"] {
        color: #c7d2fe !important;
        font-weight: 700 !important;
    }

    /* ── Tables ── */
    [data-testid="stTable"] th { color: #e0e7ff !important; }
    [data-testid="stTable"] td { color: #e2e8f0 !important; }

    /* ── Hide default menu ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar Navigation ────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center;padding:10px 0 20px'>
                <div style='font-size:2.4rem'>🚀</div>
                <div style='font-size:1.0rem;font-weight:700;color:#c7d2fe;margin-top:4px;line-height:1.3'>AI Career Copilot</div>
                <div style='font-size:0.75rem;color:#94a3b8;margin-top:4px;line-height:1.5'>Engineering Placement &<br>Interview Preparation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown("<div style='font-size:0.7rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px'>Career Tools</div>", unsafe_allow_html=True)

        pages = {
            "🏠  Home": "Home",
            "📄  Resume Analyzer": "Resume",
            "🎯  Skill Gap Analysis": "SkillGap",
            "🎤  Interview Questions": "Interview",
            "👔  Recruiter Dashboard": "Recruiter",
            "─── Placement ML ───": "sep",
            "📊  Data Dashboard": "Dashboard",
            "🔮  Placement Prediction": "Prediction",
            "💰  Salary Prediction": "Salary",
            "📈  Model Performance": "Model",
            "─── Info ───": "sep2",
            "ℹ️  About Project": "About",
        }

        # Filter separators from actual options shown to user
        display_pages = {k: v for k, v in pages.items() if not v.startswith("sep")}
        separators = {k for k, v in pages.items() if v.startswith("sep")}

        selected = st.radio(
            "Navigate",
            list(display_pages.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Model status
        from app.utils import models_exist
        if models_exist():
            st.success("✅ Models Ready")
        else:
            st.warning("⚠️ Run train.py first")
            st.code("python train.py", language="bash")

        st.markdown(
            """
            <div style='margin-top:20px;font-size:0.75rem;color:#94a3b8;text-align:center'>
                Built with Streamlit · Scikit-Learn<br>
                Developed by Ananaya Arora
            </div>
            """,
            unsafe_allow_html=True,
        )

        return display_pages[selected]


# ── Home Page ─────────────────────────────────────────────────────────────────
def show_home():
    # ── Hero Banner ───────────────────────────────────────
    st.markdown(
        """
        <div style='
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            border-radius: 16px; padding: 52px 44px; margin-bottom: 28px;
            border: 1px solid #4338ca;
        '>
            <div style='font-size:0.85rem;font-weight:700;color:#818cf8;
            letter-spacing:2px;text-transform:uppercase;margin-bottom:12px'>
                🚀 AI Career Copilot · v2.0
            </div>
            <div style='font-size:2.8rem;font-weight:800;color:#f8fafc;line-height:1.2'>
                Resume Intelligence,<br>
                <span style='color:#c7d2fe'>Salary Estimation &</span><br>
                <span style='color:#a5b4fc'>Interview Preparation</span>
            </div>
            <div style='font-size:1rem;color:#cbd5e1;margin-top:18px;max-width:580px;line-height:1.7'>
                An end-to-end AI platform for B.Tech / Engineering students and recruiters —
                upload your resume, detect skill gaps, get ML-powered salary estimates,
                and generate 20+ personalised interview questions instantly.
            </div>
            <div style='display:flex;gap:10px;margin-top:24px;flex-wrap:wrap'>
                <span style='background:#4338ca;color:#f1f5f9;padding:6px 16px;border-radius:999px;font-size:0.8rem;font-weight:600'>📄 Resume AI</span>
                <span style='background:#0f766e;color:#f0fdfa;padding:6px 16px;border-radius:999px;font-size:0.8rem;font-weight:600'>🎯 Skill Gap</span>
                <span style='background:#7c3aed;color:#f5f3ff;padding:6px 16px;border-radius:999px;font-size:0.8rem;font-weight:600'>🎤 Interview Prep</span>
                <span style='background:#1d4ed8;color:#f1f5f9;padding:6px 16px;border-radius:999px;font-size:0.8rem;font-weight:600'>🤖 ML Placement</span>
                <span style='background:#b45309;color:#fef3c7;padding:6px 16px;border-radius:999px;font-size:0.8rem;font-weight:600'>👔 Recruiter Mode</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Live Dataset Stats ─────────────────────────────────
    from app.utils import load_data, models_exist
    df = load_data()
    if df is not None:
        placed = (df["placement_status"] == "Placed").sum()
        not_placed = (df["placement_status"] == "Not Placed").sum()
        avg_sal = df[df["placement_status"] == "Placed"]["salary_lpa"].mean()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Students in Dataset", f"{len(df):,}")
        c2.metric("Placed", f"{placed:,}")
        c3.metric("Not Placed", f"{not_placed:,}")
        c4.metric("Avg Salary", f"{avg_sal:.1f} LPA")
        c5.metric("Models Ready", "✅" if models_exist() else "⚠️ Run train.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature Cards (10 total across 2 rows) ────────────
    st.subheader("Platform Capabilities")
    features = [
        ("📄", "Resume Analyzer",       "Upload PDF/DOCX. Extracts name, email, skills, projects, certifications and education automatically."),
        ("🏆", "Resume Scoring",         "Score your resume out of 100 across 6 dimensions: Skills, Projects, Internships, Certifications, Education, Experience."),
        ("🎯", "Skill Gap Analysis",     "Compare your skills vs role requirements. Get a personalised learning roadmap with curated resources."),
        ("💰", "Salary Estimation",      "ML-powered salary prediction (LPA) using Random Forest trained on 5,000 engineering student records."),
        ("🎤", "Interview Questions",    "Generate 20+ Technical, HR, Behavioral and Scenario questions tailored to your role, level and skills."),
        ("👔", "Recruiter Dashboard",    "Evaluate candidates, compute match scores, assess salary fit and generate role-specific interview questions."),
        ("🔮", "Placement Prediction",   "Predict Placed / Not Placed with probability %. Powered by Logistic Regression, Decision Tree & Random Forest."),
        ("📊", "Analytics Dashboard",   "10+ Plotly charts: placement rate by branch, CGPA distribution, coding skills, internship impact and more."),
        ("📈", "Model Performance",      "Compare model accuracy, F1 score, CV scores and feature importance across all classifiers."),
        ("📄", "PDF Reports",            "Download complete career report with resume score, skill gap, salary estimate and interview questions."),
    ]

    for row_start in range(0, 10, 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(features):
                icon, title, desc = features[idx]
                col.markdown(
                    f"""
                    <div style='background:#1e293b;border:1px solid #475569;border-radius:12px;
                    padding:18px;min-height:160px;margin-bottom:12px'>
                        <div style='font-size:1.6rem'>{icon}</div>
                        <div style='font-weight:700;color:#c7d2fe;margin:8px 0 6px;font-size:0.9rem'>{title}</div>
                        <div style='font-size:0.78rem;color:#cbd5e1;line-height:1.5'>{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two user modes ────────────────────────────────────
    st.subheader("Who Is This For?")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            """
            <div style='background:#1e1b4b;border:1px solid #4338ca;border-radius:12px;padding:24px'>
                <div style='font-size:1.5rem'>🎓 Student Mode</div>
                <div style='color:#c7d2fe;font-weight:700;margin:8px 0'>For Engineering Students</div>
                <div style='color:#cbd5e1;font-size:0.88rem;line-height:1.8'>
                    ✦ Upload your resume and get a score<br>
                    ✦ Find skill gaps for your target role<br>
                    ✦ Get salary estimate and gap analysis<br>
                    ✦ Generate personalised interview questions<br>
                    ✦ Predict placement probability<br>
                    ✦ Download full career PDF report
                </div>
            </div>
            """, unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div style='background:#172554;border:1px solid #1d4ed8;border-radius:12px;padding:24px'>
                <div style='font-size:1.5rem'>👔 Recruiter Mode</div>
                <div style='color:#93c5fd;font-weight:700;margin:8px 0'>For Hiring Teams & Placement Cells</div>
                <div style='color:#cbd5e1;font-size:0.88rem;line-height:1.8'>
                    ✦ Upload candidate resume<br>
                    ✦ Select role, level and budget<br>
                    ✦ Get candidate match score<br>
                    ✦ View matched and missing skills<br>
                    ✦ Get salary recommendation<br>
                    ✦ Generate role-specific interview questions
                </div>
            </div>
            """, unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tech stack ────────────────────────────────────────
    st.subheader("Technology Stack")
    techs = ["Python 3.11", "Scikit-Learn", "Streamlit", "Plotly", "pdfplumber",
             "python-docx", "FPDF2", "Pandas", "NumPy", "Matplotlib"]
    cols = st.columns(len(techs))
    for col, tech in zip(cols, techs):
        col.markdown(
            f"<div style='text-align:center;background:#1e293b;border-radius:8px;padding:8px 4px;"
            f"font-size:0.72rem;color:#c7d2fe;font-weight:600;border:1px solid #475569'>{tech}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick start ───────────────────────────────────────
    st.subheader("Quick Start")
    st.code(
        """# 1. Install dependencies
pip install -r requirements.txt

# 2. Train ML models
python train.py

# 3. Launch the app
streamlit run app/app.py""",
        language="bash",
    )



# ── About Page ────────────────────────────────────────────────────────────────
def show_about():
    st.title("ℹ️ About AI Career Copilot")

    st.markdown(
        """
        <div style='background:#1e293b;border-radius:12px;padding:24px;border:1px solid #475569;margin-bottom:20px'>
            <h3 style='color:#c7d2fe;margin-top:0'>AI Career Copilot – v2.0</h3>
            <p style='color:#e2e8f0;font-size:0.95rem;line-height:1.7'>
                A BTech AI/ML project that combines <b>resume intelligence</b>, <b>ML-powered placement &
                salary prediction</b>, <b>skill gap analysis</b>, and <b>AI-generated interview preparation</b>
                into a single end-to-end platform for engineering students and recruiters.
            </p>
            <p style='color:#cbd5e1;font-size:0.85rem;margin-top:10px'>
                Developed by <b>Ananaya Arora</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🎯 Project Goals")
        goals = [
            "Parse resumes (PDF/DOCX) and extract skills automatically",
            "Score resumes out of 100 across 6 weighted dimensions",
            "Identify skill gaps vs target roles with learning roadmap",
            "Predict engineering student placement (Placed / Not Placed)",
            "Estimate salary package (LPA) using Random Forest Regressor",
            "Generate 20+ personalised interview questions per role & level",
            "Provide recruiter-mode candidate evaluation and scoring",
            "Generate downloadable PDF career reports",
        ]
        for g in goals:
            st.markdown(f"- {g}")

        st.subheader("📁 Dataset")
        st.markdown("""
**Indian Engineering Student Placement Dataset**
- 5,000 BTech / Engineering students
- Branches: CSE, IT, ECE, ME, CE
- 14 features: CGPA, 10th %, 12th %, backlogs, attendance, projects,
  internships, coding/communication/aptitude ratings, hackathons, certifications
- Binary target: Placed / Not Placed · Salary (LPA) for placed students
        """)

    with c2:
        st.subheader("🛠️ Full System Pipeline")
        steps = [
            ("1",  "Resume Upload",        "pdfplumber / python-docx"),
            ("2",  "Text Extraction",      "regex-based NLP parser"),
            ("3",  "Resume Scoring",       "6-dimension weighted scoring"),
            ("4",  "Skill Detection",      "keyword matching vs 70+ skills"),
            ("5",  "Skill Gap Analysis",   "role vs current skill comparison"),
            ("6",  "Data Preprocessing",   "LabelEncoder, StandardScaler"),
            ("7",  "Placement Prediction", "LR, DT, RF — auto best model"),
            ("8",  "Salary Prediction",    "RandomForestRegressor (LPA)"),
            ("9",  "Interview Generator",  "rule-based, 4 question types"),
            ("10", "Recruiter Scoring",    "candidate match & salary fit"),
            ("11", "PDF Reports",          "fpdf2 multi-page export"),
            ("12", "Dashboard Analytics", "Plotly interactive charts"),
        ]
        for num, step, tool in steps:
            st.markdown(
                f"""
                <div style='display:flex;gap:12px;align-items:center;margin-bottom:6px'>
                    <span style='background:#4338ca;color:#f8fafc;border-radius:50%;width:24px;height:24px;
                    display:flex;align-items:center;justify-content:center;font-size:0.65rem;
                    font-weight:700;flex-shrink:0'>{num}</span>
                    <div>
                        <span style='font-weight:600;color:#e2e8f0;font-size:0.85rem'>{step}</span>
                        <span style='color:#64748b;font-size:0.75rem;margin-left:8px'>({tool})</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.subheader("📂 Project Structure")
    st.code(
        """placement_prediction_system/
│
├── data/
│   └── placement.csv              # Engineering dataset (5,000 students)
│
├── models/
│   ├── placement_model.pkl        # Classifier bundle (LR, DT, RF)
│   └── salary_model.pkl           # Salary regressor
│
├── app/
│   ├── app.py                     # Main Streamlit app + router
│   ├── resume_analyzer.py         # Resume parsing, scoring, extraction
│   ├── skill_gap.py               # Skill gap analysis + learning roadmap
│   ├── interview_generator.py     # 20+ interview questions generator
│   ├── recruiter_dashboard.py     # Recruiter evaluation mode
│   ├── dashboard.py               # Analytics dashboard
│   ├── prediction.py              # Placement prediction page
│   ├── salary_prediction.py       # Salary prediction page
│   ├── model_performance.py       # Model metrics & feature importance
│   ├── pdf_report.py              # Career + placement PDF reports
│   └── utils.py                   # Shared utilities
│
├── notebooks/
│   └── EDA.ipynb                  # Exploratory Data Analysis
│
├── reports/                       # Generated PDF reports (auto-created)
├── train.py                       # Model training script
├── requirements.txt               # All Python dependencies
├── README.md                      # Full documentation
└── .gitignore""",
        language="text",
    )

    st.markdown("---")
    st.subheader("📦 Pages & Navigation")
    pages_info = [
        ("🏠 Home",               "Landing page with hero banner, feature cards, stats, user modes"),
        ("📄 Resume Analyzer",    "Upload PDF/DOCX → extract skills, score resume, view strengths/weaknesses"),
        ("🎯 Skill Gap Analysis", "Compare skills vs role, get learning roadmap, salary gap analysis"),
        ("🎤 Interview Questions","Select role + level → 20+ Technical, HR, Behavioral, Scenario questions"),
        ("👔 Recruiter Dashboard","Upload candidate, select role/level/budget → full evaluation report"),
        ("📊 Data Dashboard",     "10+ Plotly charts on the engineering placement dataset"),
        ("🔮 Placement Prediction","ML prediction: Placed/Not Placed + probability + What-If simulator"),
        ("💰 Salary Prediction",  "ML salary estimate (LPA) with gauge, breakdown and benchmarks"),
        ("📈 Model Performance",  "Accuracy, F1, CV scores, radar chart, feature importance"),
        ("ℹ️ About Project",      "System overview, pipeline, structure, troubleshooting"),
    ]
    for page, desc in pages_info:
        st.markdown(
            f"""
            <div style='display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #1e293b'>
                <span style='color:#c7d2fe;font-weight:700;min-width:210px;font-size:0.88rem'>{page}</span>
                <span style='color:#94a3b8;font-size:0.85rem'>{desc}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("🔧 Troubleshooting")
    with st.expander("Common Issues & Fixes"):
        st.markdown("""
**Models not found**
```bash
python train.py
```

**Missing dependencies**
```bash
pip install -r requirements.txt
```

**PDF/DOCX not parsing**
```bash
pip install pdfplumber python-docx
```

**Port conflict**
```bash
streamlit run app/app.py --server.port 8502
```

**Always run from project root:**
```bash
cd placement_prediction_system
streamlit run app/app.py
```

**Model accuracy reference:** ~88–90% on 5,000 rows (expected)
        """)

    st.markdown(
        """
        <div style='background:#1e1b4b;border-radius:10px;padding:16px;text-align:center;
        margin-top:20px;border:1px solid #4338ca'>
            <div style='color:#c7d2fe;font-weight:700;font-size:1rem'>Developed by Ananaya Arora</div>
            <div style='color:#94a3b8;font-size:0.8rem;margin-top:4px'>
                Python · Scikit-Learn · Streamlit · Plotly · pdfplumber · python-docx · FPDF2
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Router ────────────────────────────────────────────────────────────────────
def main():
    page = sidebar()

    if page == "Home":
        show_home()
    elif page == "Resume":
        from app.resume_analyzer import show_resume_analyzer
        show_resume_analyzer()
    elif page == "SkillGap":
        from app.skill_gap import show_skill_gap
        show_skill_gap()
    elif page == "Interview":
        from app.interview_generator import show_interview_generator
        show_interview_generator()
    elif page == "Recruiter":
        from app.recruiter_dashboard import show_recruiter_dashboard
        show_recruiter_dashboard()
    elif page == "Dashboard":
        from app.dashboard import show_dashboard
        show_dashboard()
    elif page == "Prediction":
        from app.prediction import show_prediction
        show_prediction()
    elif page == "Salary":
        from app.salary_prediction import show_salary_prediction
        show_salary_prediction()
    elif page == "Model":
        from app.model_performance import show_model_performance
        show_model_performance()
    elif page == "About":
        show_about()

    st.markdown(
        """
        <div style='margin-top:40px;padding-top:16px;border-top:1px solid #334155;
        text-align:center;font-size:0.78rem;color:#94a3b8'>
            AI Career Copilot · Developed by Ananaya Arora
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
