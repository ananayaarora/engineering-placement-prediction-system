"""
app/utils.py - Shared Utility Functions
Engineering Student Placement Prediction System
"""

import os
import pickle
import pandas as pd
import numpy as np
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_PATH = os.path.join(BASE_DIR, "data", "placement.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

FEATURE_COLUMNS = [
    "gender_enc", "branch_enc",
    "cgpa", "tenth_percentage", "twelfth_percentage",
    "backlogs", "attendance_percentage",
    "projects_completed", "internships_completed",
    "coding_skill_rating", "communication_skill_rating",
    "aptitude_skill_rating", "hackathons_participated",
    "certifications_count",
]


@st.cache_resource
def load_placement_model():
    path = os.path.join(MODELS_DIR, "placement_model.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_resource
def load_salary_model():
    path = os.path.join(MODELS_DIR, "salary_model.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    return df


def encode_input(user_input: dict, label_encoders: dict) -> pd.DataFrame:
    """Encode a raw user input dict into a model-ready DataFrame."""
    mappings = {
        "gender": user_input["gender"],
        "branch": user_input["branch"],
    }

    encoded = {}
    for col, val in mappings.items():
        le = label_encoders.get(col)
        if le is not None:
            try:
                encoded[col + "_enc"] = le.transform([val])[0]
            except ValueError:
                encoded[col + "_enc"] = 0
        else:
            encoded[col + "_enc"] = 0

    row = {
        "gender_enc": encoded["gender_enc"],
        "branch_enc": encoded["branch_enc"],
        "cgpa": float(user_input["cgpa"]),
        "tenth_percentage": float(user_input["tenth_percentage"]),
        "twelfth_percentage": float(user_input["twelfth_percentage"]),
        "backlogs": int(user_input["backlogs"]),
        "attendance_percentage": float(user_input["attendance_percentage"]),
        "projects_completed": int(user_input["projects_completed"]),
        "internships_completed": int(user_input["internships_completed"]),
        "coding_skill_rating": int(user_input["coding_skill_rating"]),
        "communication_skill_rating": int(user_input["communication_skill_rating"]),
        "aptitude_skill_rating": int(user_input["aptitude_skill_rating"]),
        "hackathons_participated": int(user_input["hackathons_participated"]),
        "certifications_count": int(user_input["certifications_count"]),
    }

    feature_vector = pd.DataFrame([row], columns=FEATURE_COLUMNS)
    return feature_vector


def predict_placement(user_input: dict, bundle: dict):
    """Run placement prediction and return result dict."""
    feature_vector = encode_input(user_input, bundle["label_encoders"])

    best_model = bundle["best_model"]
    best_name = bundle["best_model_name"]
    scaler = bundle["scaler"]

    if best_name == "Logistic Regression":
        fv_scaled = scaler.transform(feature_vector)
        prediction = best_model.predict(fv_scaled)[0]
        probability = best_model.predict_proba(fv_scaled)[0][1]
    else:
        prediction = best_model.predict(feature_vector)[0]
        probability = best_model.predict_proba(feature_vector)[0][1]

    label = "Placed" if prediction == 1 else "Not Placed"
    prob_pct = round(probability * 100, 1)

    # Readiness score
    score = compute_readiness_score(user_input)

    # Strengths & weaknesses
    strengths, weaknesses = analyze_profile(user_input)

    # Recommendations
    recommendations = generate_recommendations(user_input, weaknesses)

    # Feature influences
    influences = compute_feature_influence(user_input)

    return {
        "label": label,
        "probability": prob_pct,
        "readiness_score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "influences": influences,
    }


def predict_salary(user_input: dict, salary_model, bundle: dict):
    """Predict expected salary (LPA) for placed students."""
    feature_vector = encode_input(user_input, bundle["label_encoders"])
    salary = salary_model.predict(feature_vector)[0]
    return round(float(salary), 2)


def compute_readiness_score(user_input: dict) -> int:
    """
    Generate a 0-100 Interview Readiness Score for engineering students.

    Weighted components:
      CGPA                 - 20
      Coding Skill          - 20
      Communication Skill   - 15
      Aptitude Skill         - 15
      Projects Completed    - 10
      Internships Completed - 10
      Certifications        - 5
      Hackathons            - 5
    Backlogs apply a penalty.
    """
    cgpa = float(user_input.get("cgpa", 6.0))
    coding = float(user_input.get("coding_skill_rating", 3))
    comm = float(user_input.get("communication_skill_rating", 3))
    aptitude = float(user_input.get("aptitude_skill_rating", 3))
    projects = float(user_input.get("projects_completed", 0))
    internships = float(user_input.get("internships_completed", 0))
    certifications = float(user_input.get("certifications_count", 0))
    hackathons = float(user_input.get("hackathons_participated", 0))
    backlogs = float(user_input.get("backlogs", 0))

    score = 0.0
    score += min(cgpa / 10 * 20, 20)
    score += min(coding / 5 * 20, 20)
    score += min(comm / 5 * 15, 15)
    score += min(aptitude / 5 * 15, 15)
    score += min(projects / 6 * 10, 10)
    score += min(internships / 3 * 10, 10)
    score += min(certifications / 5 * 5, 5)
    score += min(hackathons / 4 * 5, 5)

    # Backlog penalty: -4 points per backlog, capped
    score -= min(backlogs * 4, 20)

    return int(max(0, min(score, 100)))


def get_readiness_category(score: int) -> tuple:
    """Return (category_label, color) for a readiness score."""
    if score < 40:
        return "Poor", "#ef4444"
    elif score < 60:
        return "Average", "#f97316"
    elif score < 80:
        return "Good", "#22c55e"
    else:
        return "Excellent", "#6366f1"


def analyze_profile(user_input: dict) -> tuple:
    """Return (strengths_list, weaknesses_list) based on thresholds."""
    strengths = []
    weaknesses = []

    if float(user_input.get("cgpa", 0)) >= 8.0:
        strengths.append(f"High CGPA ({user_input.get('cgpa')})")
    elif float(user_input.get("cgpa", 0)) < 6.5:
        weaknesses.append(f"Low CGPA ({user_input.get('cgpa')})")

    if float(user_input.get("coding_skill_rating", 0)) >= 4:
        strengths.append("Strong Coding Skills")
    elif float(user_input.get("coding_skill_rating", 0)) <= 2:
        weaknesses.append("Weak Coding Skills")

    if float(user_input.get("communication_skill_rating", 0)) >= 4:
        strengths.append("Strong Communication Skills")
    elif float(user_input.get("communication_skill_rating", 0)) <= 2:
        weaknesses.append("Weak Communication Skills")

    if float(user_input.get("aptitude_skill_rating", 0)) >= 4:
        strengths.append("Strong Aptitude Score")
    elif float(user_input.get("aptitude_skill_rating", 0)) <= 2:
        weaknesses.append("Weak Aptitude Score")

    if int(user_input.get("internships_completed", 0)) >= 1:
        strengths.append("Has Internship Experience")
    else:
        weaknesses.append("No Internship Experience")

    if int(user_input.get("projects_completed", 0)) >= 4:
        strengths.append("Strong Project Portfolio")
    elif int(user_input.get("projects_completed", 0)) <= 1:
        weaknesses.append("Few Completed Projects")

    if int(user_input.get("certifications_count", 0)) >= 3:
        strengths.append("Good Number of Certifications")
    elif int(user_input.get("certifications_count", 0)) == 0:
        weaknesses.append("No Certifications")

    if int(user_input.get("backlogs", 0)) == 0:
        strengths.append("No Active Backlogs")
    else:
        weaknesses.append(f"{int(user_input.get('backlogs', 0))} Active Backlog(s)")

    if int(user_input.get("hackathons_participated", 0)) >= 2:
        strengths.append("Active Hackathon Participation")

    if float(user_input.get("attendance_percentage", 0)) >= 85:
        strengths.append("Excellent Attendance")
    elif float(user_input.get("attendance_percentage", 0)) < 65:
        weaknesses.append("Low Attendance")

    return strengths, weaknesses


def generate_recommendations(user_input: dict, weaknesses: list) -> list:
    """Generate personalised recommendations for engineering students."""
    recs = []

    if float(user_input.get("aptitude_skill_rating", 0)) < 4:
        recs.append("📚 Improve aptitude and quantitative skills via mock tests")
    if int(user_input.get("internships_completed", 0)) == 0:
        recs.append("💼 Pursue at least one internship to gain real-world experience")
    if float(user_input.get("coding_skill_rating", 0)) < 4:
        recs.append("💻 Practice DSA and coding challenges on platforms like LeetCode")
    if float(user_input.get("cgpa", 0)) < 7.5:
        recs.append("🎓 Focus on improving CGPA — strong academics build recruiter trust")
    if int(user_input.get("projects_completed", 0)) < 3:
        recs.append("🛠️ Build more hands-on projects for your portfolio")
    if int(user_input.get("certifications_count", 0)) < 2:
        recs.append("📜 Earn relevant certifications in your domain")
    if int(user_input.get("backlogs", 0)) > 0:
        recs.append("⚠️ Clear pending backlogs as soon as possible — recruiters screen for this")
    if int(user_input.get("hackathons_participated", 0)) == 0:
        recs.append("🏆 Participate in hackathons to demonstrate practical problem-solving")
    if float(user_input.get("communication_skill_rating", 0)) < 4:
        recs.append("🗣️ Practice group discussions and HR interview techniques")

    recs.append("🔗 Build a strong LinkedIn profile and GitHub portfolio")

    return recs[:6]


def compute_feature_influence(user_input: dict) -> list:
    """Compute feature-level influence on prediction (simplified explainability)."""
    influences = []

    numeric = {
        "CGPA": (float(user_input.get("cgpa", 0)), 10),
        "Coding Skill": (float(user_input.get("coding_skill_rating", 0)), 5),
        "Communication Skill": (float(user_input.get("communication_skill_rating", 0)), 5),
        "Aptitude Skill": (float(user_input.get("aptitude_skill_rating", 0)), 5),
        "Projects Completed": (float(user_input.get("projects_completed", 0)), 6),
        "Internships Completed": (float(user_input.get("internships_completed", 0)), 3),
    }

    for feature, (val, max_val) in numeric.items():
        normalised = (val / max_val) - 0.5  # center around midpoint
        direction = "positive" if normalised >= 0 else "negative"
        influences.append({
            "feature": feature,
            "value": val,
            "direction": direction,
            "magnitude": abs(normalised) * 2,
        })

    backlogs = int(user_input.get("backlogs", 0))
    influences.append({
        "feature": "Backlogs",
        "value": backlogs,
        "direction": "negative" if backlogs > 0 else "positive",
        "magnitude": min(backlogs * 0.25, 1.0),
    })

    influences.sort(key=lambda x: x["magnitude"], reverse=True)
    return influences[:6]


def models_exist() -> bool:
    pm = os.path.join(MODELS_DIR, "placement_model.pkl")
    sm = os.path.join(MODELS_DIR, "salary_model.pkl")
    return os.path.exists(pm) and os.path.exists(sm)
