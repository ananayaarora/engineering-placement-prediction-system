"""
train.py - Complete Model Training Script
Engineering Student Placement Prediction System
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "placement.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1. LOAD & PREPROCESS DATA
# ─────────────────────────────────────────────

def load_and_preprocess(path: str):
    df = pd.read_csv(path)

    # Drop ID column
    if "Student_ID" in df.columns:
        df = df.drop("Student_ID", axis=1)

    # Encode target
    df["status_encoded"] = (df["placement_status"] == "Placed").astype(int)

    # Encode categorical features used as model inputs
    label_encoders = {}
    cat_cols = ["gender", "branch"]

    for col in cat_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

    return df, label_encoders


def get_feature_columns():
    return [
        "gender_enc", "branch_enc",
        "cgpa", "tenth_percentage", "twelfth_percentage",
        "backlogs", "attendance_percentage",
        "projects_completed", "internships_completed",
        "coding_skill_rating", "communication_skill_rating",
        "aptitude_skill_rating", "hackathons_participated",
        "certifications_count",
    ]


def get_feature_names():
    return [
        "Gender", "Branch",
        "CGPA", "10th %", "12th %",
        "Backlogs", "Attendance %",
        "Projects Completed", "Internships Completed",
        "Coding Skill", "Communication Skill",
        "Aptitude Skill", "Hackathons Participated",
        "Certifications Count",
    ]


# ─────────────────────────────────────────────
# 2. TRAIN PLACEMENT MODELS
# ─────────────────────────────────────────────

def train_placement_models(df, label_encoders):
    feature_cols = get_feature_columns()
    X = df[feature_cols]
    y = df["status_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=8),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42, max_depth=10),
    }

    results = {}
    trained_models = {}

    print("\n" + "=" * 60)
    print("  PLACEMENT MODEL TRAINING RESULTS")
    print("=" * 60)

    for name, model in models.items():
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        cv_scores = cross_val_score(
            model,
            X_train_scaled if name == "Logistic Regression" else X_train,
            y_train, cv=5
        )

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "cv_mean": round(cv_scores.mean(), 4),
            "cv_std": round(cv_scores.std(), 4),
        }
        trained_models[name] = model

        print(f"\n  [{name}]")
        print(f"    Accuracy  : {acc:.4f}")
        print(f"    Precision : {prec:.4f}")
        print(f"    Recall    : {rec:.4f}")
        print(f"    F1 Score  : {f1:.4f}")
        print(f"    CV Mean   : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Select best model by F1 score
    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best_model = trained_models[best_name]
    print(f"\n  ✅ Best Model: {best_name}  (F1={results[best_name]['f1_score']:.4f})")

    # Feature importances (Random Forest)
    rf_model = trained_models["Random Forest"]
    feature_importance = dict(zip(get_feature_names(), rf_model.feature_importances_))
    feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))

    print("\n  Top Feature Importances (Random Forest):")
    for feat, imp in list(feature_importance.items())[:8]:
        print(f"    {feat:<30} {imp:.4f}")

    return {
        "best_model": best_model,
        "best_model_name": best_name,
        "all_models": trained_models,
        "scaler": scaler,
        "label_encoders": label_encoders,
        "results": results,
        "feature_importance": feature_importance,
        "feature_cols": feature_cols,
        "feature_names": get_feature_names(),
        "X_test": X_test,
        "y_test": y_test,
        "X_test_scaled": X_test_scaled,
    }


# ─────────────────────────────────────────────
# 3. TRAIN SALARY MODEL
# ─────────────────────────────────────────────

def train_salary_model(df, label_encoders):
    # Only placed students have a non-zero salary
    placed_df = df[df["placement_status"] == "Placed"].copy()
    placed_df = placed_df[placed_df["salary_lpa"] > 0]

    feature_cols = get_feature_columns()
    X = placed_df[feature_cols]
    y = placed_df["salary_lpa"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    salary_model = RandomForestRegressor(n_estimators=300, random_state=42, max_depth=10)
    salary_model.fit(X_train, y_train)

    score = salary_model.score(X_test, y_test)
    print(f"\n  [Salary Regressor]")
    print(f"    R² Score  : {score:.4f}")
    print(f"    Train size: {len(X_train)}")
    print(f"    Test size : {len(X_test)}")

    return salary_model


# ─────────────────────────────────────────────
# 4. SAVE MODELS
# ─────────────────────────────────────────────

def save_models(placement_bundle: dict, salary_model):
    placement_path = os.path.join(MODELS_DIR, "placement_model.pkl")
    salary_path = os.path.join(MODELS_DIR, "salary_model.pkl")

    with open(placement_path, "wb") as f:
        pickle.dump(placement_bundle, f)

    with open(salary_path, "wb") as f:
        pickle.dump(salary_model, f)

    print(f"\n  💾 Models saved:")
    print(f"     {placement_path}")
    print(f"     {salary_path}")


# ─────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  ENGINEERING PLACEMENT PREDICTION — MODEL TRAINING")
    print("=" * 60)

    print(f"\n  Loading data from: {DATA_PATH}")
    df, label_encoders = load_and_preprocess(DATA_PATH)
    print(f"  Dataset shape: {df.shape}")
    placed = (df["placement_status"] == "Placed").sum()
    not_placed = (df["placement_status"] == "Not Placed").sum()
    print(f"  Placed: {placed} | Not Placed: {not_placed}")

    placement_bundle = train_placement_models(df, label_encoders)

    print("\n" + "=" * 60)
    print("  SALARY MODEL TRAINING RESULTS")
    print("=" * 60)
    salary_model = train_salary_model(df, label_encoders)

    save_models(placement_bundle, salary_model)

    print("\n" + "=" * 60)
    print("  ✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\n  Run the app with:")
    print("  streamlit run app/app.py")
    print()


if __name__ == "__main__":
    main()
