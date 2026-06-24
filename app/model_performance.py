"""
app/model_performance.py - Model Performance & Explainability Page
Engineering Student Placement Prediction System
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.utils import load_placement_model, models_exist

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1e293b",
    font={"color": "#e2e8f0"},
    legend={"font": {"color": "#e2e8f0"}},
    xaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
    yaxis={"color": "#e2e8f0", "gridcolor": "#334155"},
)


def show_model_performance():
    st.title("📈 Model Performance & Explainability")
    st.markdown("Compare trained models and understand what drives placement predictions for engineering students.")

    if not models_exist():
        st.warning("⚠️ Models not found. Run `python train.py` first.")
        return

    bundle = load_placement_model()
    if bundle is None:
        st.error("Failed to load placement model bundle.")
        return

    results = bundle.get("results", {})
    best_name = bundle.get("best_model_name", "Unknown")
    feature_importance = bundle.get("feature_importance", {})
    feature_names = bundle.get("feature_names", [])

    # ── Model Comparison ─────────────────────────────────
    st.subheader("Model Comparison")
    st.info(f"🏆 Best Model Selected: **{best_name}**")

    if results:
        metrics_df = pd.DataFrame(results).T.reset_index()
        metrics_df.columns = ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "CV Mean", "CV Std"]

        def highlight_best(row):
            if row["Model"] == best_name:
                return ["background-color: #312e81; color: #f8fafc"] * len(row)
            return ["color: #e2e8f0"] * len(row)

        styled = metrics_df.style.apply(highlight_best, axis=1).format({
            "Accuracy": "{:.4f}",
            "Precision": "{:.4f}",
            "Recall": "{:.4f}",
            "F1 Score": "{:.4f}",
            "CV Mean": "{:.4f}",
            "CV Std": "{:.4f}",
        })

        st.dataframe(styled, use_container_width=True)

        # Grouped bar chart
        st.subheader("Performance Metrics Comparison")
        chart_data = []
        for model, metrics in results.items():
            for metric, val in metrics.items():
                if metric not in ["cv_std"]:
                    chart_data.append({"Model": model, "Metric": metric.replace("_", " ").title(), "Score": val})

        chart_df = pd.DataFrame(chart_data)
        chart_df = chart_df[chart_df["Metric"].isin(["Accuracy", "Precision", "Recall", "F1 Score"])]

        fig = px.bar(
            chart_df, x="Metric", y="Score", color="Model", barmode="group",
            color_discrete_sequence=["#6366f1", "#f97316", "#22c55e"],
            text="Score",
        )
        fig.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                           textfont={"color": "#e2e8f0"})
        fig.update_layout(yaxis_range=[0, 1.1], **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

        # Radar chart
        st.subheader("Model Radar Chart")
        categories = ["Accuracy", "Precision", "Recall", "F1 Score"]
        fig_radar = go.Figure()

        colors = {"Logistic Regression": "#6366f1", "Decision Tree": "#f97316", "Random Forest": "#22c55e"}
        for model_name, metrics in results.items():
            vals = [metrics["accuracy"], metrics["precision"], metrics["recall"], metrics["f1_score"]]
            vals += [vals[0]]
            cats = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=cats, fill="toself",
                name=model_name,
                line_color=colors.get(model_name, "#6366f1"),
                opacity=0.7,
            ))

        fig_radar.update_layout(
            polar=dict(
                bgcolor="#1e293b",
                radialaxis=dict(visible=True, range=[0, 1], color="#e2e8f0", gridcolor="#334155"),
                angularaxis=dict(color="#e2e8f0"),
            ),
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0"},
            legend={"font": {"color": "#e2e8f0"}},
            margin=dict(t=30, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Feature Importance ───────────────────────────────
    st.subheader("Feature Importance (Random Forest)")

    if feature_importance:
        fi_df = pd.DataFrame(
            {"Feature": list(feature_importance.keys()), "Importance": list(feature_importance.values())}
        ).sort_values("Importance", ascending=True)

        fig_fi = px.bar(
            fi_df, x="Importance", y="Feature", orientation="h",
            color="Importance",
            color_continuous_scale=["#4338ca", "#818cf8"],
            text="Importance",
        )
        fig_fi.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                              textfont={"color": "#e2e8f0"})
        fig_fi.update_layout(
            coloraxis_showscale=False,
            yaxis_title="",
            **CHART_LAYOUT,
        )
        st.plotly_chart(fig_fi, use_container_width=True)

        top_feature = fi_df.iloc[-1]["Feature"]
        st.success(f"🔑 Most influential feature: **{top_feature}**")
        st.caption(
            "Feature importance shows which attributes the Random Forest model uses most to make decisions. "
            "Higher importance = stronger driver of placement outcomes for engineering students."
        )

    # ── Cross-Validation ─────────────────────────────────
    st.subheader("Cross-Validation Summary")
    if results:
        cv_data = {
            model: {"CV Mean": metrics["cv_mean"], "CV Std": metrics["cv_std"]}
            for model, metrics in results.items()
        }
        cv_df = pd.DataFrame(cv_data).T.reset_index()
        cv_df.columns = ["Model", "CV Mean", "CV Std"]

        fig_cv = go.Figure()
        for _, row in cv_df.iterrows():
            fig_cv.add_trace(go.Bar(
                x=[row["Model"]],
                y=[row["CV Mean"]],
                error_y=dict(type="data", array=[row["CV Std"]], visible=True, color="#e2e8f0"),
                name=row["Model"],
                marker_color=colors.get(row["Model"], "#6366f1"),
                text=[f"{row['CV Mean']:.3f}"],
                textposition="outside",
                textfont={"color": "#e2e8f0"},
            ))

        fig_cv.update_layout(
            yaxis_title="CV Accuracy",
            yaxis_range=[0, 1.15],
            showlegend=False,
            **CHART_LAYOUT,
        )
        st.plotly_chart(fig_cv, use_container_width=True)

    # ── Explainability Notes ─────────────────────────────
    st.subheader("📖 How Predictions Work")
    with st.expander("Model Architecture & Explainability"):
        st.markdown("""
**Logistic Regression**
- Linear model mapping engineering student features to placement probability
- Requires feature scaling (StandardScaler applied)
- Good baseline; interpretable coefficients

**Decision Tree**
- Hierarchical if-else rule structure
- Depth limited to 8 to prevent overfitting
- Human-readable decision paths

**Random Forest**
- Ensemble of 300 decision trees
- Feature importance via mean decrease in impurity
- Robust to overfitting; handles nonlinear interactions

**Model Selection**
- Best model chosen automatically by highest F1 Score
- F1 balances Precision and Recall — important for imbalanced placement data

**Feature Importance Interpretation**
- Backlogs, CGPA, and 12th % are typically the strongest predictors
- Coding skill and project count give significant uplift
- Internships and certifications act as reinforcing signals

**Prediction Probability**
- `model.predict_proba()` gives probability from 0–100%
- Threshold at 50%: above = Placed, below = Not Placed
        """)
