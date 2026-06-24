"""
app/pdf_report.py - PDF Report Generator
AI Career Copilot – Engineering Placement Prediction System
Developed by Ananaya Arora
"""

import os
import datetime

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports"
)
os.makedirs(REPORTS_DIR, exist_ok=True)

W = 190  # usable page width


def _safe(text: str) -> str:
    """Strip characters outside latin-1 range so fpdf2 Helvetica doesn't crash."""
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def _header(pdf, title1: str, title2: str = ""):
    from fpdf import FPDF
    pdf.set_fill_color(99, 102, 241)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 6)
    pdf.cell(W, 10, title1, align="C", new_x="LMARGIN", new_y="NEXT")
    if title2:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_xy(10, 18)
        pdf.cell(W, 8, title2, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(10, 30)
    ts = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    pdf.cell(W, 7, f"Generated on: {ts}  |  Developed by Ananaya Arora",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(16)


def _section(pdf, title: str, r=240, g=240, b=255):
    pdf.set_fill_color(r, g, b)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(W, 9, title, new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(2)


def _kv(pdf, label: str, val: str):
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(65, 7, f"  {_safe(label)}:", new_x="RIGHT", new_y="LAST")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(W - 65, 7, _safe(str(val)), new_x="LMARGIN", new_y="NEXT")


def _footer(pdf):
    pdf.set_y(-16)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(W, 7,
             "AI-Powered Engineering Placement Prediction System | Developed by Ananaya Arora",
             align="C", new_x="LMARGIN", new_y="NEXT")


# ── Career Copilot Comprehensive Report ──────────────────────────────────────

def generate_career_report(
    parsed_resume: dict,
    resume_score: dict,
    skill_gap_data: dict | None = None,
    interview_questions: dict | None = None,
    salary_estimate: float | None = None,
    readiness_score: int | None = None,
) -> str | None:
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(10, 10, 10)
        pdf.add_page()

        _header(pdf, "AI Career Copilot - Candidate Report",
                "Engineering Placement Prediction System")

        # ── Summary ──────────────────────────────────────
        _section(pdf, "Candidate Summary")
        _kv(pdf, "Name", _safe(parsed_resume.get("name") or "-"))
        _kv(pdf, "Email", _safe(parsed_resume.get("email") or "-"))
        _kv(pdf, "Phone", _safe(parsed_resume.get("phone") or "-"))
        _kv(pdf, "Resume Score", f"{resume_score.get('total', 0)} / 100")
        if readiness_score is not None:
            _kv(pdf, "Interview Readiness", f"{readiness_score} / 100")
        if salary_estimate is not None:
            _kv(pdf, "Salary Estimate", f"{salary_estimate:.2f} LPA")
        pdf.ln(4)

        # ── Skill Summary ─────────────────────────────────
        _section(pdf, "Detected Skills")
        all_skills = parsed_resume.get("skills_flat", [])
        _kv(pdf, "Total Skills", str(len(all_skills)))
        _kv(pdf, "Projects", str(parsed_resume.get("project_count", 0)))
        _kv(pdf, "Internships", str(parsed_resume.get("internship_count", 0)))
        _kv(pdf, "Certifications", str(parsed_resume.get("certification_count", 0)))
        pdf.ln(2)
        if all_skills:
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(W, 6, _safe("  Skills: " + ", ".join(all_skills)))
        pdf.ln(4)

        # ── Resume Score Breakdown ────────────────────────
        _section(pdf, "Resume Score Breakdown")
        for dim, score in resume_score.get("breakdown", {}).items():
            _kv(pdf, dim, str(score))
        pdf.ln(4)

        # ── Strengths & Weaknesses ────────────────────────
        _section(pdf, "Strengths", 220, 252, 231)
        pdf.set_font("Helvetica", "", 10)
        for s in resume_score.get("strengths", []):
            pdf.cell(W, 7, _safe(f"  + {s}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        _section(pdf, "Weaknesses", 254, 226, 226)
        pdf.set_font("Helvetica", "", 10)
        for w in resume_score.get("weaknesses", []):
            pdf.cell(W, 7, _safe(f"  - {w}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # ── Skill Gap ─────────────────────────────────────
        if skill_gap_data:
            _section(pdf, "Skill Gap Analysis")
            _kv(pdf, "Target Role", _safe(skill_gap_data.get("target_role", "-")))
            _kv(pdf, "Role Fit", f"{skill_gap_data.get('match_pct', 0)}%")
            _kv(pdf, "Target Salary", f"{skill_gap_data.get('target_salary', 0)} LPA")
            missing = skill_gap_data.get("missing", [])
            if missing:
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(W, 6, _safe("  Missing skills: " + ", ".join(missing)))
            pdf.ln(4)

        # ── Interview Questions ───────────────────────────
        if interview_questions:
            pdf.add_page()
            _header(pdf, "AI Career Copilot - Interview Questions",
                    f"{interview_questions.get('role','')} | {interview_questions.get('level','')}")

            _section(pdf, "Technical Questions")
            pdf.set_font("Helvetica", "", 9)
            for i, q in enumerate(interview_questions.get("technical", [])[:10], 1):
                clean = q.encode("ascii", errors="ignore").decode()
                pdf.multi_cell(W, 6, f"  Q{i}. {clean}")
            pdf.ln(3)

            _section(pdf, "HR Questions")
            pdf.set_font("Helvetica", "", 9)
            for i, q in enumerate(interview_questions.get("hr", [])[:5], 1):
                clean = q.encode("ascii", errors="ignore").decode()
                pdf.multi_cell(W, 6, f"  Q{i}. {clean}")
            pdf.ln(3)

            _section(pdf, "Behavioral Questions")
            pdf.set_font("Helvetica", "", 9)
            for i, q in enumerate(interview_questions.get("behavioral", [])[:4], 1):
                clean = q.encode("ascii", errors="ignore").decode()
                pdf.multi_cell(W, 6, f"  Q{i}. {clean}")

        _footer(pdf)

        ts_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(REPORTS_DIR, f"career_report_{ts_file}.pdf")
        pdf.output(pdf_path)
        return pdf_path

    except Exception as e:
        import traceback
        print(f"Career PDF generation error: {e}")
        traceback.print_exc()
        return None


# ── Placement Prediction Report (existing feature, preserved) ─────────────────

def generate_pdf_report(user_input: dict, result: dict, salary=None) -> str | None:
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(10, 10, 10)
        pdf.add_page()

        _header(pdf, "AI-Powered Engineering Placement Prediction System",
                "Placement Prediction Report")

        is_placed = result["label"] == "Placed"
        pdf.set_fill_color(220, 252, 231) if is_placed else pdf.set_fill_color(254, 226, 226)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(W, 10, f"RESULT:  {result['label']}", align="C",
                 new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(4)

        _section(pdf, "Key Metrics")
        _kv(pdf, "Placement Probability", f"{result['probability']}%")
        _kv(pdf, "Interview Readiness Score", f"{result['readiness_score']} / 100")
        if salary:
            _kv(pdf, "Expected Salary", f"{salary:.2f} LPA")
        pdf.ln(4)

        _section(pdf, "Academic & Skill Profile")
        profile = [
            ("Gender", user_input.get("gender", "—")),
            ("Branch", user_input.get("branch", "—")),
            ("CGPA", f"{user_input.get('cgpa', '—')}"),
            ("10th %", f"{user_input.get('tenth_percentage', '—')}%"),
            ("12th %", f"{user_input.get('twelfth_percentage', '—')}%"),
            ("Backlogs", str(user_input.get("backlogs", "—"))),
            ("Attendance %", f"{user_input.get('attendance_percentage', '—')}%"),
            ("Projects Completed", str(user_input.get("projects_completed", "—"))),
            ("Internships Completed", str(user_input.get("internships_completed", "—"))),
            ("Coding Skill Rating", f"{user_input.get('coding_skill_rating', '—')} / 5"),
            ("Communication Skill", f"{user_input.get('communication_skill_rating', '—')} / 5"),
            ("Aptitude Skill", f"{user_input.get('aptitude_skill_rating', '—')} / 5"),
            ("Hackathons Participated", str(user_input.get("hackathons_participated", "—"))),
            ("Certifications", str(user_input.get("certifications_count", "—"))),
        ]
        for label, val in profile:
            _kv(pdf, label, val)
        pdf.ln(4)

        if result.get("strengths"):
            _section(pdf, "Strengths", 220, 252, 231)
            pdf.set_font("Helvetica", "", 10)
            for s in result["strengths"]:
                pdf.cell(W, 7, _safe(f"  + {s}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        if result.get("weaknesses"):
            _section(pdf, "Weaknesses", 254, 226, 226)
            pdf.set_font("Helvetica", "", 10)
            for w in result["weaknesses"]:
                pdf.cell(W, 7, _safe(f"  - {w}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        if result.get("recommendations"):
            _section(pdf, "Recommendations")
            pdf.set_font("Helvetica", "", 10)
            for rec in result["recommendations"]:
                clean = rec.encode("ascii", errors="ignore").decode().strip()
                pdf.multi_cell(W, 7, f"  * {clean}")

        _footer(pdf)

        ts_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(REPORTS_DIR, f"placement_report_{ts_file}.pdf")
        pdf.output(pdf_path)
        return pdf_path

    except Exception as e:
        import traceback
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        return None
