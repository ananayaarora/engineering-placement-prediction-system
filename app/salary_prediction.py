"""
app/salary_prediction.py - Salary Prediction Page
Engineering Student Placement Prediction System
"""

import plotly.graph_objects as go
import streamlit as st

from app.utils import (
    load_placement_model, load_salary_model,
    predict_salary, predict_placement, models_exist
)

BRANCHES = ["CSE", "IT", "ECE", "ME", "CE"]


def show_salary_prediction():
    st.title("💰 Salary Prediction")
    st.markdown("Predict your expected salary package (in LPA) based on your academic and skill profile.")

    if not models_exist():
        st.warning("⚠️ Models not found. Run `python train.py` first.")
        return

    bundle = load_placement_model()
    salary_model = load_salary_model()

    if bundle is None or salary_model is None:
        st.error("Failed to load models.")
        return

    with st.form("salary_form"):
        st.subheader("Academic & Skill Profile")

        c1, c2, c3 = st.columns(3)
        with c1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            branch = st.selectbox("Branch", BRANCHES)
            cgpa = st.slider("CGPA (out of 10)", 5.0, 10.0, 8.0, step=0.05)

        with c2:
            tenth_percentage = st.slider("10th Percentage (%)", 40.0, 100.0, 80.0, step=0.5)
            twelfth_percentage = st.slider("12th Percentage (%)", 40.0, 100.0, 80.0, step=0.5)
            attendance_percentage = st.slider("Attendance Percentage (%)", 40.0, 100.0, 85.0, step=0.5)

        with c3:
            backlogs = st.number_input("Active Backlogs", min_value=0, max_value=10, value=0, step=1)
            projects_completed = st.number_input("Projects Completed", min_value=0, max_value=15, value=4, step=1)
            internships_completed = st.number_input("Internships Completed", min_value=0, max_value=5, value=1, step=1)

        st.markdown("##### Skill Ratings (1 = Low, 5 = High)")
        c4, c5, c6 = st.columns(3)
        with c4:
            coding_skill_rating = st.slider("Coding Skill Rating", 1, 5, 4)
        with c5:
            communication_skill_rating = st.slider("Communication Skill Rating", 1, 5, 3)
        with c6:
            aptitude_skill_rating = st.slider("Aptitude Skill Rating", 1, 5, 3)

        c7, c8 = st.columns(2)
        with c7:
            hackathons_participated = st.number_input("Hackathons Participated", min_value=0, max_value=10, value=1, step=1)
        with c8:
            certifications_count = st.number_input("Certifications Count", min_value=0, max_value=15, value=2, step=1)

        submitted = st.form_submit_button("💰 Predict Salary", use_container_width=True)

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

    placement_result = predict_placement(user_input, bundle)

    st.markdown("---")

    if placement_result["label"] == "Not Placed":
        st.warning(
            f"⚠️ Based on your profile, placement probability is only "
            f"**{placement_result['probability']}%**. "
            "Salary prediction is most relevant for placed candidates. "
            "Improve your profile first!"
        )
        st.info("Showing estimated salary assuming placement anyway:")

    salary_lpa = predict_salary(user_input, salary_model, bundle)

    # Salary display
    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Salary (LPA)", f"{salary_lpa:.2f} LPA")
    c2.metric("Annual (₹)", f"₹{salary_lpa*100000:,.0f}")
    c3.metric("Monthly (₹)", f"₹{salary_lpa*100000/12:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Salary gauge
    st.subheader("Salary Indicator")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=salary_lpa,
        delta={"reference": 14, "suffix": " LPA", "font": {"color": "#e2e8f0"}},
        title={"text": "Expected CTC (LPA)", "font": {"color": "#e2e8f0"}},
        number={"suffix": " LPA", "valueformat": ".2f", "font": {"color": "#e2e8f0"}},
        gauge={
            "axis": {"range": [0, 20], "tickfont": {"color": "#94a3b8"}},
            "bar": {"color": "#6366f1"},
            "bgcolor": "#1e293b",
            "steps": [
                {"range": [0, 8], "color": "#7f1d1d"},
                {"range": [8, 14], "color": "#7c2d12"},
                {"range": [14, 18], "color": "#14532d"},
                {"range": [18, 20], "color": "#312e81"},
            ],
            "threshold": {
                "line": {"color": "#6366f1", "width": 4},
                "thickness": 0.75,
                "value": salary_lpa,
            },
        },
    ))
    fig.update_layout(
        height=320, margin=dict(t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e2e8f0"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Salary breakdown
    st.subheader("Salary Breakdown")
    breakdown_items = {
        "Base Salary (70%)": salary_lpa * 0.70,
        "Variable Pay (15%)": salary_lpa * 0.15,
        "Joining Bonus (10%)": salary_lpa * 0.10,
        "Other Benefits (5%)": salary_lpa * 0.05,
    }

    bdf_labels = list(breakdown_items.keys())
    bdf_values = list(breakdown_items.values())

    fig2 = go.Figure(go.Pie(
        labels=bdf_labels,
        values=bdf_values,
        hole=0.4,
        textinfo="label+percent",
        textfont={"color": "#e2e8f0"},
        marker=dict(colors=["#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe"]),
    ))
    fig2.update_layout(
        showlegend=True, margin=dict(t=20, b=20), height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "#e2e8f0"}},
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Salary comparison
    st.subheader("Salary Comparison with Benchmarks")
    benchmarks = {
        "Industry Min": 5.0,
        "Industry Avg": 14.0,
        "Your Prediction": salary_lpa,
        "Industry Max": 20.0,
    }

    fig3 = go.Figure()
    colors = ["#64748b", "#818cf8", "#6366f1", "#312e81"]
    for i, (label, val) in enumerate(benchmarks.items()):
        fig3.add_trace(go.Bar(
            x=[label], y=[val],
            name=label,
            marker_color=colors[i],
            text=[f"{val:.2f}"],
            textposition="outside",
            textfont={"color": "#e2e8f0"},
        ))
    fig3.update_layout(
        yaxis_title="Salary (LPA)",
        showlegend=False,
        margin=dict(t=20, b=20),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1e293b",
        font={"color": "#e2e8f0"},
        xaxis={"color": "#e2e8f0"},
        yaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Salary tips
    st.subheader("💡 Tips to Increase Your Package")
    tips = []
    if internships_completed == 0:
        tips.append("🏢 Complete an internship — it can boost package by 15-25%")
    if cgpa < 8.0:
        tips.append("📈 Improve CGPA — top performers earn significantly more")
    if coding_skill_rating < 4:
        tips.append("🧠 Strengthen coding skills — high coding ratings are linked to top-tier offers")
    if backlogs > 0:
        tips.append("⚠️ Clear backlogs — recruiters often filter candidates with pending backlogs")
    if certifications_count < 3:
        tips.append("📜 Earn more domain certifications to stand out")
    tips.append("🔗 Build strong project portfolio and GitHub profile")
    tips.append("🎤 Develop communication and negotiation skills")

    for tip in tips[:5]:
        st.markdown(f"- {tip}")
