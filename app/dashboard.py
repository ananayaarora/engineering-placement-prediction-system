"""
app/dashboard.py - Data Analytics Dashboard
Engineering Student Placement Prediction System
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from app.utils import load_data, load_placement_model

# Shared dark-mode chart styling for high-contrast readability
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1e293b",
    font={"color": "#e2e8f0"},
    legend={"font": {"color": "#e2e8f0"}},
    xaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
    yaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
    margin=dict(t=20, b=20),
)


def style_fig(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


def show_dashboard():
    st.title("📊 Data Analytics Dashboard")
    st.markdown("Explore placement patterns across the Engineering Student dataset.")

    df = load_data()
    if df is None:
        st.error("Dataset not found. Check data/placement.csv")
        return

    # ── Metric Cards ─────────────────────────────────────
    placed = (df["placement_status"] == "Placed").sum()
    not_placed = (df["placement_status"] == "Not Placed").sum()
    placement_rate = round(placed / len(df) * 100, 1)
    avg_salary = df[df["placement_status"] == "Placed"]["salary_lpa"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(df))
    c2.metric("Placed", placed)
    c3.metric("Not Placed", not_placed)
    c4.metric("Placement Rate", f"{placement_rate}%")

    st.markdown("---")
    placed_df_all = df[df["placement_status"] == "Placed"]
    avg_s = placed_df_all["salary_lpa"].mean()
    med_s = placed_df_all["salary_lpa"].median()
    max_s = placed_df_all["salary_lpa"].max()
    min_s = placed_df_all["salary_lpa"].min()

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Salary", f"{avg_s:.2f} LPA")
    c6.metric("Median Salary", f"{med_s:.2f} LPA")
    c7.metric("Max Salary", f"{max_s:.2f} LPA")
    c8.metric("Min Salary", f"{min_s:.2f} LPA")

    st.markdown("---")

    # Row 1 — Placement Distribution & Placement Rate by Branch
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.subheader("Placement Distribution")
        counts = df["placement_status"].value_counts()
        fig = px.pie(
            names=counts.index, values=counts.values,
            color=counts.index,
            color_discrete_map={"Placed": "#6366f1", "Not Placed": "#f97316"},
            hole=0.45
        )
        fig.update_traces(textposition="outside", textinfo="percent+label",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with r1c2:
        st.subheader("Placement Rate by Branch")
        branch_rate = df.groupby("branch")["placement_status"].apply(
            lambda x: (x == "Placed").mean() * 100
        ).reset_index(name="rate")
        branch_rate = branch_rate.sort_values("rate", ascending=False)
        fig = px.bar(
            branch_rate, x="branch", y="rate",
            color="rate", color_continuous_scale=["#312e81", "#818cf8", "#6366f1"],
            labels={"branch": "Branch", "rate": "Placement Rate (%)"},
            text="rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Row 2 — Average Salary by Branch & CGPA Distribution
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.subheader("Average Salary by Branch")
        branch_salary = placed_df_all.groupby("branch")["salary_lpa"].mean().reset_index()
        branch_salary = branch_salary.sort_values("salary_lpa", ascending=False)
        fig = px.bar(
            branch_salary, x="branch", y="salary_lpa",
            color="salary_lpa", color_continuous_scale=["#312e81", "#818cf8", "#6366f1"],
            labels={"branch": "Branch", "salary_lpa": "Avg Salary (LPA)"},
            text="salary_lpa",
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with r2c2:
        st.subheader("CGPA Distribution")
        fig = px.histogram(
            df, x="cgpa", color="placement_status", nbins=20, opacity=0.8,
            color_discrete_map={"Placed": "#6366f1", "Not Placed": "#f97316"},
            labels={"cgpa": "CGPA", "count": "Count"},
        )
        fig.update_layout(barmode="overlay")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Row 3 — Coding Skill Distribution & Internship Analysis
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.subheader("Coding Skill Distribution")
        coding_counts = df.groupby(["coding_skill_rating", "placement_status"]).size().reset_index(name="count")
        fig = px.bar(
            coding_counts, x="coding_skill_rating", y="count", color="placement_status",
            barmode="group",
            color_discrete_map={"Placed": "#6366f1", "Not Placed": "#f97316"},
            labels={"coding_skill_rating": "Coding Skill Rating (1-5)", "count": "Count", "placement_status": "Status"},
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with r3c2:
        st.subheader("Internship Analysis")
        intern_rate = df.groupby("internships_completed")["placement_status"].apply(
            lambda x: (x == "Placed").mean() * 100
        ).reset_index(name="rate")
        fig = px.bar(
            intern_rate, x="internships_completed", y="rate",
            color="rate", color_continuous_scale=["#312e81", "#818cf8", "#6366f1"],
            labels={"internships_completed": "Internships Completed", "rate": "Placement Rate (%)"},
            text="rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Row 4 — Backlogs vs Placement & Gender vs Placement
    r4c1, r4c2 = st.columns(2)

    with r4c1:
        st.subheader("Backlogs vs Placement Rate")
        backlog_rate = df.groupby("backlogs")["placement_status"].apply(
            lambda x: (x == "Placed").mean() * 100
        ).reset_index(name="rate")
        fig = px.bar(
            backlog_rate, x="backlogs", y="rate",
            color="rate", color_continuous_scale=["#7f1d1d", "#f97316", "#6366f1"],
            labels={"backlogs": "Active Backlogs", "rate": "Placement Rate (%)"},
            text="rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with r4c2:
        st.subheader("Gender vs Placement")
        gender_place = df.groupby(["gender", "placement_status"]).size().reset_index(name="count")
        fig = px.bar(
            gender_place, x="gender", y="count", color="placement_status",
            barmode="group",
            color_discrete_map={"Placed": "#6366f1", "Not Placed": "#f97316"},
            labels={"gender": "Gender", "count": "Count", "placement_status": "Status"},
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Row 5 — Salary Distribution & Projects vs Placement
    r5c1, r5c2 = st.columns(2)

    with r5c1:
        st.subheader("Salary Distribution (Placed)")
        fig = px.histogram(
            placed_df_all, x="salary_lpa", nbins=25,
            color_discrete_sequence=["#6366f1"],
            labels={"salary_lpa": "Salary (LPA)", "count": "Count"},
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with r5c2:
        st.subheader("Projects Completed vs Placement")
        proj_rate = df.groupby("projects_completed")["placement_status"].apply(
            lambda x: (x == "Placed").mean() * 100
        ).reset_index(name="rate")
        fig = px.line(
            proj_rate, x="projects_completed", y="rate", markers=True,
            labels={"projects_completed": "Projects Completed", "rate": "Placement Rate (%)"},
        )
        fig.update_traces(line_color="#6366f1", marker=dict(color="#a5b4fc", size=8))
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Correlation heatmap
    st.subheader("Correlation Heatmap")
    num_cols = [
        "cgpa", "tenth_percentage", "twelfth_percentage", "backlogs",
        "attendance_percentage", "projects_completed", "internships_completed",
        "coding_skill_rating", "communication_skill_rating", "aptitude_skill_rating",
    ]
    corr = df[num_cols].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        labels={"color": "Correlation"},
    )
    fig.update_traces(textfont={"color": "#0f172a"})
    fig.update_layout(margin=dict(t=20, b=20), paper_bgcolor="rgba(0,0,0,0)",
                       font={"color": "#e2e8f0"})
    st.plotly_chart(fig, use_container_width=True)

    # Feature Importance (from trained model, if available)
    st.subheader("Feature Importance")
    bundle = load_placement_model()
    if bundle and bundle.get("feature_importance"):
        fi = bundle["feature_importance"]
        fi_df = pd.DataFrame({"Feature": list(fi.keys()), "Importance": list(fi.values())})
        fi_df = fi_df.sort_values("Importance", ascending=True)
        fig = px.bar(
            fi_df, x="Importance", y="Feature", orientation="h",
            color="Importance", color_continuous_scale=["#312e81", "#6366f1"],
        )
        fig.update_layout(coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("Train the models first (`python train.py`) to see feature importance here.")

    # Dataset overview
    st.subheader("Dataset Overview")
    st.dataframe(df.head(20), use_container_width=True)

    with st.expander("Dataset Statistics"):
        st.dataframe(df.describe(), use_container_width=True)
