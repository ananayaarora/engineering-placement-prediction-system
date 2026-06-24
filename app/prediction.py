"""
app/prediction.py - Placement Prediction Page
Engineering Student Placement Prediction System
"""

import os
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils import (
    load_placement_model, load_salary_model,
    predict_placement, predict_salary,
    get_readiness_category, models_exist
)
from app.pdf_report import generate_pdf_report

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports", "prediction_history.json"
)

BRANCHES = ["CSE", "IT", "ECE", "ME", "CE"]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(record: dict):
    history = load_history()
    history.append(record)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def show_prediction():
    st.title("🎯 Placement Prediction")
    st.markdown("Fill in your academic and skill profile to get your personalised placement prediction.")

    if not models_exist():
        st.warning("⚠️ Models not found. Run `python train.py` first.")
        return

    bundle = load_placement_model()
    salary_model = load_salary_model()

    if bundle is None:
        st.error("Failed to load placement model.")
        return

    # ── Input Form ────────────────────────────────────────
    with st.form("prediction_form"):
        st.subheader("Personal & Academic Profile")

        c1, c2, c3 = st.columns(3)
        with c1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            branch = st.selectbox("Branch", BRANCHES)
            cgpa = st.slider("CGPA (out of 10)", 5.0, 10.0, 7.5, step=0.05)

        with c2:
            tenth_percentage = st.slider("10th Percentage (%)", 40.0, 100.0, 75.0, step=0.5)
            twelfth_percentage = st.slider("12th Percentage (%)", 40.0, 100.0, 75.0, step=0.5)
            attendance_percentage = st.slider("Attendance Percentage (%)", 40.0, 100.0, 80.0, step=0.5)

        with c3:
            backlogs = st.number_input("Active Backlogs", min_value=0, max_value=10, value=0, step=1)
            projects_completed = st.number_input("Projects Completed", min_value=0, max_value=15, value=3, step=1)
            internships_completed = st.number_input("Internships Completed", min_value=0, max_value=5, value=0, step=1)

        st.markdown("##### Skill Ratings (1 = Low, 5 = High)")
        c4, c5, c6 = st.columns(3)
        with c4:
            coding_skill_rating = st.slider("Coding Skill Rating", 1, 5, 3)
        with c5:
            communication_skill_rating = st.slider("Communication Skill Rating", 1, 5, 3)
        with c6:
            aptitude_skill_rating = st.slider("Aptitude Skill Rating", 1, 5, 3)

        c7, c8 = st.columns(2)
        with c7:
            hackathons_participated = st.number_input("Hackathons Participated", min_value=0, max_value=10, value=0, step=1)
        with c8:
            certifications_count = st.number_input("Certifications Count", min_value=0, max_value=15, value=1, step=1)

        submitted = st.form_submit_button("🔮 Predict Placement", use_container_width=True)

    if not submitted:
        return

    user_input = {
        "gender": gender, "branch": branch, "cgpa": cgpa,
        "tenth_percentage": tenth_percentage, "twelfth_percentage": twelfth_percentage,
        "backlogs": backlogs, "attendance_percentage": attendance_percentage,
        "projects_completed": projects_completed, "internships_completed": internships_completed,
        "coding_skill_rating": coding_skill_rating,
        "communication_skill_rating": communication_skill_rating,
        "aptitude_skill_rating": aptitude_skill_rating,
        "hackathons_participated": hackathons_participated,
        "certifications_count": certifications_count,
    }

    result = predict_placement(user_input, bundle)
    salary = None
    if salary_model and result["label"] == "Placed":
        salary = predict_salary(user_input, salary_model, bundle)

    # ── Results ───────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Prediction Results")

    # Main result cards
    col1, col2, col3 = st.columns(3)

    with col1:
        color = "#6366f1" if result["label"] == "Placed" else "#ef4444"
        emoji = "✅" if result["label"] == "Placed" else "❌"
        st.markdown(
            f"""
            <div style='background:{color};border-radius:12px;padding:20px;text-align:center;color:#ffffff'>
                <div style='font-size:2.5rem'>{emoji}</div>
                <div style='font-size:1.4rem;font-weight:700;margin-top:8px;color:#ffffff'>{result['label']}</div>
                <div style='font-size:0.9rem;color:#f1f5f9'>Prediction</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        prob = result["probability"]
        st.markdown(
            f"""
            <div style='background:#1e293b;border-radius:12px;padding:20px;text-align:center;border:2px solid #6366f1'>
                <div style='font-size:2.5rem;font-weight:700;color:#c7d2fe'>{prob}%</div>
                <div style='font-size:0.9rem;color:#e2e8f0;margin-top:4px'>Placement Probability</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        score = result["readiness_score"]
        cat, cat_color = get_readiness_category(score)
        st.markdown(
            f"""
            <div style='background:#1e293b;border-radius:12px;padding:20px;text-align:center;border:2px solid {cat_color}'>
                <div style='font-size:2.5rem;font-weight:700;color:{cat_color}'>{score}/100</div>
                <div style='font-size:0.9rem;color:{cat_color};font-weight:700'>{cat}</div>
                <div style='font-size:0.8rem;color:#e2e8f0;margin-top:2px'>Interview Readiness Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Salary prediction
    if salary:
        st.info(f"💰 **Expected Salary Package:** {salary:.2f} LPA  (₹{salary*100000:,.0f} / year)")

    # Probability gauge
    st.subheader("Placement Probability Gauge")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=result["probability"],
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Probability (%)", "font": {"color": "#e2e8f0"}},
        number={"font": {"color": "#e2e8f0"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
            "bar": {"color": "#6366f1"},
            "bgcolor": "#1e293b",
            "steps": [
                {"range": [0, 40], "color": "#7f1d1d"},
                {"range": [40, 60], "color": "#7c2d12"},
                {"range": [60, 80], "color": "#14532d"},
                {"range": [80, 100], "color": "#312e81"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 50},
        },
    ))
    fig.update_layout(
        height=300, margin=dict(t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e2e8f0"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Strengths & weaknesses
    sw_col1, sw_col2 = st.columns(2)

    with sw_col1:
        st.subheader("💪 Strengths")
        if result["strengths"]:
            for s in result["strengths"]:
                st.success(f"✓ {s}")
        else:
            st.write("No significant strengths identified.")

    with sw_col2:
        st.subheader("⚠️ Weaknesses")
        if result["weaknesses"]:
            for w in result["weaknesses"]:
                st.error(f"✗ {w}")
        else:
            st.write("No major weaknesses detected. Great profile!")

    # Recommendations
    st.subheader("🚀 Recommendations")
    for rec in result["recommendations"]:
        st.markdown(f"- {rec}")

    # Feature influence
    st.subheader("🔍 Prediction Influences")
    st.caption("Factors that most influenced this prediction:")
    for inf in result["influences"]:
        arrow = "↑" if inf["direction"] == "positive" else "↓"
        color = "#22c55e" if inf["direction"] == "positive" else "#ef4444"
        bar_width = int(inf["magnitude"] * 100)
        display_val = inf['value'] if isinstance(inf['value'], str) else f"{inf['value']:.1f}"
        st.markdown(
            f"""
            <div style='display:flex;align-items:center;margin-bottom:6px;gap:10px'>
                <span style='width:170px;font-size:0.85rem;color:#cbd5e1'>{inf['feature']}</span>
                <span style='color:{color};font-weight:700'>{arrow}</span>
                <div style='flex:1;background:#1e293b;border-radius:4px;height:10px'>
                    <div style='width:{min(bar_width,100)}%;background:{color};height:10px;border-radius:4px'></div>
                </div>
                <span style='font-size:0.8rem;color:#cbd5e1;width:50px'>{display_val}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # What-if simulator
    st.markdown("---")
    st.subheader("🔬 What-If Simulator")
    st.caption("Adjust parameters to see how your probability changes.")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        sim_cgpa = st.slider("CGPA", 5.0, 10.0, float(cgpa), key="sim_cgpa")
    with sim_col2:
        sim_coding = st.slider("Coding Skill", 1, 5, int(coding_skill_rating), key="sim_coding")
    with sim_col3:
        sim_internships = st.slider("Internships Completed", 0, 5, int(internships_completed), key="sim_intern")

    sim_backlogs = st.slider("Active Backlogs", 0, 10, int(backlogs), key="sim_backlogs")

    sim_input = {
        **user_input,
        "cgpa": sim_cgpa, "coding_skill_rating": sim_coding,
        "internships_completed": sim_internships, "backlogs": sim_backlogs,
    }
    sim_result = predict_placement(sim_input, bundle)

    change = sim_result["probability"] - result["probability"]
    change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
    change_color = "#22c55e" if change >= 0 else "#ef4444"

    st.markdown(
        f"""
        <div style='background:#1e293b;border-radius:10px;padding:16px;margin-top:10px;display:flex;gap:30px;align-items:center;flex-wrap:wrap'>
            <div>
                <div style='font-size:0.8rem;color:#94a3b8'>Original Probability</div>
                <div style='font-size:1.8rem;font-weight:700;color:#c7d2fe'>{result['probability']}%</div>
            </div>
            <div style='font-size:2rem;color:#94a3b8'>→</div>
            <div>
                <div style='font-size:0.8rem;color:#94a3b8'>Simulated Probability</div>
                <div style='font-size:1.8rem;font-weight:700;color:#c7d2fe'>{sim_result['probability']}%</div>
            </div>
            <div>
                <div style='font-size:0.8rem;color:#94a3b8'>Change</div>
                <div style='font-size:1.8rem;font-weight:700;color:{change_color}'>{change_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Save & PDF
    st.markdown("---")
    history_record = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prediction": result["label"],
        "probability": result["probability"],
        "readiness_score": result["readiness_score"],
        "salary_lpa": salary,
    }
    save_history(history_record)

    col_pdf1, col_pdf2 = st.columns(2)
    with col_pdf1:
        if st.button("📄 Download Placement Report (PDF)", use_container_width=True):
            pdf_path = generate_pdf_report(user_input, result, salary)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Click to Download",
                        data=f,
                        file_name="placement_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

    with col_pdf2:
        if st.session_state.get("resume_uploaded"):
            if st.button("📄 Download Career Report (PDF)", use_container_width=True):
                from app.pdf_report import generate_career_report
                parsed = st.session_state.get("parsed_resume", {})
                resume_score = st.session_state.get("resume_score", {})
                skill_gap = st.session_state.get("skill_gap_data")
                questions = st.session_state.get("interview_questions")
                career_path = generate_career_report(
                    parsed, resume_score, skill_gap, questions, salary,
                    result["readiness_score"]
                )
                if career_path and os.path.exists(career_path):
                    with open(career_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Click to Download Career PDF",
                            data=f,
                            file_name="career_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
        else:
            st.info("💡 Upload your resume first to also download a full Career PDF report.")

    # Prediction history
    st.markdown("---")
    st.subheader("📜 Prediction History")
    history = load_history()
    if history:
        hist_df = pd.DataFrame(history)
        st.dataframe(hist_df[::-1].head(20), use_container_width=True)
    else:
        st.info("No predictions recorded yet.")
