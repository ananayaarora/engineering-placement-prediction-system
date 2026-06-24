# 🎓 AI-Powered Engineering Placement Prediction System

A BTech AI/ML project that predicts whether an engineering student will get placed based on CGPA, academic scores, skill ratings, projects, internships, certifications, and backlog history — and estimates the expected salary package (LPA) for placed students. Built with Python, Scikit-Learn, and Streamlit.

**Developed by Ananaya Arora**

---

## 🚀 Live Features

| Feature | Description |
|---|---|
| 🎯 Placement Prediction | Placed / Not Placed with probability % |
| 💰 Salary Prediction | Expected CTC (LPA) using Random Forest Regressor |
| 📊 Analytics Dashboard | Interactive Plotly charts (branch-wise rate, CGPA, skills, internships) |
| 📈 Model Performance | Accuracy, Precision, Recall, F1, CV scores |
| 🔬 What-If Simulator | Change inputs and see probability shift live |
| 🔍 Explainable AI | Feature importance + prediction influences |
| 🧭 Interview Readiness Score | 0–100 score from CGPA, skills, projects, internships |
| 📄 PDF Report | Downloadable placement report with recommendations |
| 📜 Prediction History | All past predictions stored and displayed |

---

## 📁 Project Structure

```
placement_prediction_system/
│
├── data/
│   └── placement.csv              # 5,000-student engineering dataset
│
├── models/
│   ├── placement_model.pkl        # Best classifier + all models + encoders
│   └── salary_model.pkl           # Random Forest salary regressor (LPA)
│
├── app/
│   ├── app.py                     # Main Streamlit entry point
│   ├── dashboard.py               # Data Analytics Dashboard page
│   ├── prediction.py              # Placement Prediction page
│   ├── salary_prediction.py       # Salary Prediction page
│   ├── model_performance.py       # Model metrics & explainability page
│   ├── pdf_report.py              # PDF report generator (fpdf2)
│   └── utils.py                   # Shared utilities, encoding, scoring
│
├── notebooks/
│   └── EDA.ipynb                  # Full Exploratory Data Analysis
│
├── reports/                       # Auto-generated PDF reports saved here
├── screenshots/                   # App screenshots
├── train.py                       # Model training script
├── requirements.txt               # All Python dependencies
├── README.md                      # This file
└── .gitignore
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone / Download
```bash
git clone https://github.com/yourusername/placement-prediction-system.git
cd placement_prediction_system
```

### Step 2 — Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Train Models
```bash
python train.py
```
This will:
- Load `data/placement.csv` (merged engineering features + placement targets)
- Train Logistic Regression, Decision Tree, Random Forest
- Auto-select best model by F1 score
- Train salary regressor (placed students only, predicts `salary_lpa`)
- Save `models/placement_model.pkl` and `models/salary_model.pkl`

### Step 5 — Launch Streamlit App
```bash
streamlit run app/app.py
```
Open your browser at **http://localhost:8501**

---

## 📊 Dataset

**Indian Engineering Student Placement Dataset** — 5,000 BTech students

Source files merged on `Student_ID`:
- `indian_engineering_student_placement.csv` — student features
- `placement_targets.csv` — placement status & salary

| Column | Description |
|---|---|
| `gender` | Male / Female |
| `branch` | CSE / IT / ECE / ME / CE |
| `cgpa` | Cumulative GPA (out of 10) |
| `tenth_percentage` | 10th grade percentage |
| `twelfth_percentage` | 12th grade percentage |
| `backlogs` | Number of active backlogs |
| `attendance_percentage` | Overall attendance % |
| `projects_completed` | Number of academic/personal projects |
| `internships_completed` | Number of internships completed |
| `coding_skill_rating` | Self/assessed coding skill (1–5) |
| `communication_skill_rating` | Communication skill rating (1–5) |
| `aptitude_skill_rating` | Aptitude skill rating (1–5) |
| `hackathons_participated` | Number of hackathons attended |
| `certifications_count` | Number of certifications earned |
| `placement_status` | **Target** — Placed / Not Placed |
| `salary_lpa` | Salary offered in LPA (only for placed students) |

---

## 🤖 ML Pipeline

```
Raw Data (2 files) → Merge on Student_ID → Preprocessing → Feature Engineering → Model Training → Evaluation → Deployment
```

### Models Trained
| Model | Type | Notes |
|---|---|---|
| Logistic Regression | Classifier | Scaled features, max_iter=1000 |
| Decision Tree | Classifier | max_depth=8 |
| Random Forest | Classifier | 300 trees, max_depth=10 |
| Random Forest | Regressor | Salary (LPA) prediction — placed students only |

### Evaluation Metrics
- Accuracy, Precision, Recall, F1 Score
- 5-Fold Cross Validation
- Best model auto-selected by F1 Score

### Feature Importance
Top features driving placement (Random Forest):
1. Backlogs
2. CGPA
3. 12th Percentage
4. Coding Skill Rating
5. 10th Percentage
6. Projects Completed

---

## 📱 App Pages

### 🏠 Home
- Hero banner with project description
- Live dataset statistics (metric cards)
- Feature overview cards
- Technology stack
- Quick start commands

### 📊 Data Dashboard
- Placement distribution pie chart
- Placement rate by branch
- Average salary by branch
- CGPA distribution
- Coding skill distribution
- Internship analysis
- Backlogs vs placement rate
- Gender vs placement
- Salary distribution
- Correlation heatmap
- Feature importance
- Dataset overview table

### 🎯 Placement Prediction
- Engineering-specific input form (branch, CGPA, 10th/12th %, backlogs, attendance,
  projects, internships, coding/communication/aptitude skill ratings, hackathons, certifications)
- Prediction result card (Placed / Not Placed)
- Placement probability % card
- Interview Readiness Score (0–100) with category
- Probability gauge chart
- Strengths & Weaknesses analysis
- Personalised recommendations
- Prediction influence bars (XAI)
- What-If Simulator (live probability change)
- PDF report download
- Prediction history table

### 💰 Salary Prediction
- Full engineering input form
- Predicted salary (LPA, annual ₹, monthly ₹)
- Salary gauge chart
- Salary component breakdown (pie)
- Benchmark comparison bar chart
- Tips to increase package

### 📈 Model Performance
- Model comparison table (highlighted best)
- Grouped bar chart (all metrics)
- Radar chart comparison
- Cross-validation scores with error bars
- Feature importance horizontal bar chart
- Explainability notes

### ℹ️ About Project
- BTech AI/ML project description
- Project goals
- ML pipeline steps
- Full directory structure
- Troubleshooting guide
- Developer credit

---

## 🔧 Troubleshooting

**Models not found**
```bash
python train.py
```

**Missing dependencies**
```bash
pip install -r requirements.txt
```

**Port conflict**
```bash
streamlit run app/app.py --server.port 8502
```

**PDF not downloading**
```bash
pip install fpdf2
```

**Import errors**
- Always run `streamlit run app/app.py` from the **project root** directory
- Do not run from inside the `app/` folder

**CSV not loading**
- Ensure `data/placement.csv` exists in the project root
- Do not rename or move the file

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical computing |
| Scikit-Learn | ML models, preprocessing |
| Streamlit | Web application framework |
| Plotly | Interactive charts |
| Matplotlib / Seaborn | EDA visualisations |
| FPDF2 | PDF report generation |
| Pickle | Model serialisation |

---

## 📄 License

MIT License — free to use for learning and academic purposes.

---

## 👨‍💻 Developer

**Developed by Ananaya Arora**

A BTech AI/ML project demonstrating end-to-end machine learning skills: data merging,
preprocessing, model training, evaluation, explainability, and full-stack Streamlit deployment.
