"""
app/interview_generator.py
AI Career Copilot – Interview Question Generator
Rule-based, no paid API required
Developed by Ananaya Arora
"""

import random
import streamlit as st
from app.resume_analyzer import ROLES, LEVELS

# ── Question Bank ─────────────────────────────────────────────────────────────

HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want to work at our company?",
    "Where do you see yourself in 5 years?",
    "What is your greatest strength?",
    "What is your greatest weakness?",
    "Why are you leaving your current job?",
    "What is your expected salary?",
    "How do you handle work pressure and tight deadlines?",
    "Describe your ideal work environment.",
    "Are you open to relocation or travel?",
    "How do you handle conflicts with teammates?",
    "What motivates you to perform at your best?",
    "What does teamwork mean to you?",
    "How do you stay updated with industry trends?",
    "Tell me about a failure and what you learned from it.",
]

BEHAVIORAL_QUESTIONS = [
    "Describe a situation where you had to learn something new quickly.",
    "Tell me about a time you resolved a conflict in a team.",
    "Describe a project where you took initiative without being told to.",
    "Give an example of a time you missed a deadline and how you handled it.",
    "Tell me about a difficult technical problem you solved.",
    "Describe a time you disagreed with a senior and how you handled it.",
    "Give an example of when you had to manage multiple priorities at once.",
    "Tell me about a time you received critical feedback and acted on it.",
    "Describe a time when you helped a team member who was struggling.",
    "Tell me about the most challenging project you've worked on.",
]

SCENARIO_QUESTIONS = [
    "You are given a project with an unclear requirement. How do you proceed?",
    "Production is down and you are the only one available. Walk me through your response.",
    "You discover a bug in code pushed by a senior engineer. What do you do?",
    "Your manager assigns you a task you've never done before with a tight deadline. How do you handle it?",
    "Two features are both urgent but you can only do one. How do you prioritize?",
    "A client is unhappy with the deliverable. How do you respond?",
    "You are asked to estimate how long a task will take but you're not sure. What do you say?",
    "Your code review received many comments. How do you respond?",
    "The team is divided on a technical approach. How do you facilitate the decision?",
    "You realize you've been working on the wrong requirement for two days. What next?",
]

TECHNICAL_QUESTIONS = {
    "Data Scientist": [
        "Explain the bias-variance tradeoff.",
        "What is cross-validation and why is it used?",
        "How do you handle imbalanced datasets?",
        "Explain precision, recall, and F1 score with examples.",
        "What is overfitting and how do you prevent it?",
        "How would you choose between logistic regression and a decision tree?",
        "Explain gradient descent and its variants.",
        "What is regularization? Explain L1 vs L2.",
        "How does Random Forest work?",
        "Explain PCA and when you would use it.",
        "What is the curse of dimensionality?",
        "How do you deal with missing data in a dataset?",
        "Explain the difference between bagging and boosting.",
        "What is a confusion matrix?",
        "How would you detect outliers in a dataset?",
    ],
    "ML Engineer": [
        "What is MLOps and why does it matter?",
        "How do you deploy a machine learning model to production?",
        "What is model drift and how do you monitor for it?",
        "Explain feature engineering. Give an example.",
        "How do you handle large datasets that don't fit in memory?",
        "What is the difference between batch inference and real-time inference?",
        "Explain the components of an ML pipeline.",
        "How would you A/B test a new ML model?",
        "What is a feature store?",
        "Describe how you would containerize an ML model using Docker.",
        "What is Kubeflow / MLflow?",
        "How do you handle versioning of datasets and models?",
        "Explain the difference between model accuracy and business metric.",
        "What is transfer learning?",
        "How do you optimize a model for latency in production?",
    ],
    "Data Analyst": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Write a SQL query to find duplicate records.",
        "How would you detect an outlier in a dataset?",
        "Explain the difference between a measure and a dimension in BI tools.",
        "What is a pivot table?",
        "How do you define KPIs for a business problem?",
        "What is cohort analysis?",
        "Explain the difference between OLAP and OLTP.",
        "What is a moving average and when would you use it?",
        "How do you validate the quality of data before analysis?",
        "What is a Pareto chart and when is it useful?",
        "Explain window functions in SQL (ROW_NUMBER, RANK, DENSE_RANK).",
        "How do you present data insights to a non-technical audience?",
        "What is A/B testing? Explain with an example.",
        "How would you find the top 3 salary earners per department in SQL?",
    ],
    "Software Engineer": [
        "Explain the difference between a stack and a queue.",
        "What is the time complexity of binary search?",
        "What is a hash table and how does it handle collisions?",
        "Explain OOP principles: encapsulation, inheritance, polymorphism.",
        "What is the difference between a process and a thread?",
        "Explain REST API design principles.",
        "What is a deadlock? How do you prevent it?",
        "Explain the SOLID principles.",
        "What is the difference between SQL and NoSQL?",
        "What are design patterns? Give two examples.",
        "How does garbage collection work in Java or Python?",
        "What is a microservices architecture?",
        "Explain the difference between TCP and UDP.",
        "What is a singleton pattern?",
        "Describe how you would design a URL shortener.",
    ],
    "Backend Developer": [
        "What is the difference between authentication and authorization?",
        "Explain how JWT tokens work.",
        "What is database indexing and why does it matter?",
        "Explain N+1 query problem and how to fix it.",
        "What is caching? Give examples of when to use Redis.",
        "How does a REST API differ from a GraphQL API?",
        "What are HTTP status codes? List five common ones.",
        "Explain database transactions and ACID properties.",
        "What is middleware in a web framework?",
        "How would you design a rate limiter?",
        "What is horizontal scaling vs vertical scaling?",
        "Explain how message queues (e.g., RabbitMQ, Kafka) work.",
        "What is connection pooling?",
        "How do you secure a REST API?",
        "What is a webhook?",
    ],
    "Frontend Developer": [
        "What is the difference between == and === in JavaScript?",
        "Explain the CSS box model.",
        "What is the virtual DOM in React?",
        "Explain how closures work in JavaScript.",
        "What is the difference between var, let, and const?",
        "What is event delegation?",
        "Explain async/await vs Promises.",
        "What is CSS specificity?",
        "What is CORS and how do you handle it?",
        "Explain lazy loading.",
        "What is the difference between localStorage and sessionStorage?",
        "How does React useEffect work?",
        "What is responsive design? How do you implement it?",
        "Explain the difference between display: flex and display: grid.",
        "What is tree shaking in webpack?",
    ],
    "Full Stack Developer": [
        "Explain the MVC architecture.",
        "How does a web request flow from browser to database and back?",
        "What is the difference between server-side rendering and client-side rendering?",
        "How do you manage state in a React application?",
        "Explain how to implement authentication in a full-stack app.",
        "What is a RESTful API? How do you design one?",
        "Explain how WebSockets work.",
        "What is GraphQL and when would you choose it over REST?",
        "How do you handle CORS in a full-stack project?",
        "What is a reverse proxy and why would you use one?",
        "How would you optimize the performance of a web application?",
        "Explain CI/CD and how you would set it up.",
        "What is Docker and how does it help in deployment?",
        "How do you manage secrets and environment variables securely?",
        "Describe how you would implement file upload functionality.",
    ],
    "DevOps Engineer": [
        "What is Docker and how does containerisation work?",
        "Explain Kubernetes: pods, services, deployments.",
        "What is CI/CD? Walk me through a pipeline you've built.",
        "What is infrastructure as code? Name tools.",
        "How do you monitor a production system?",
        "Explain blue-green deployment.",
        "What is a load balancer?",
        "How does auto-scaling work?",
        "What is the difference between a VM and a container?",
        "Explain the 12-factor app methodology.",
        "What is a service mesh?",
        "How do you manage secrets in a Kubernetes cluster?",
        "What is observability? Explain logs, metrics, and traces.",
        "How do you handle a server outage at 3 AM?",
        "What is a rolling update?",
    ],
}

LEVEL_FILTERS = {
    "Intern":   {"q_count": 5, "difficulty": "basic"},
    "Fresher":  {"q_count": 8, "difficulty": "basic-medium"},
    "SDE-1":    {"q_count": 10, "difficulty": "medium"},
    "SDE-2":    {"q_count": 12, "difficulty": "medium-hard"},
    "Senior":   {"q_count": 15, "difficulty": "hard"},
}


def generate_questions(role: str, level: str, skills: list[str]) -> dict:
    """Generate a full set of interview questions for the given role, level, skills."""
    cfg = LEVEL_FILTERS.get(level, LEVEL_FILTERS["Fresher"])
    n = cfg["q_count"]

    tech_pool = TECHNICAL_QUESTIONS.get(role, TECHNICAL_QUESTIONS["Software Engineer"])
    random.shuffle(tech_pool)
    technical = tech_pool[:n]

    # Inject skill-specific questions
    skill_questions = []
    for skill in skills[:3]:
        skill_questions.extend(_skill_questions(skill, role))
    if skill_questions:
        technical = (skill_questions[:4] + technical[:max(n - 4, 0)])[:n]

    hr = random.sample(HR_QUESTIONS, min(5, len(HR_QUESTIONS)))
    behavioral = random.sample(BEHAVIORAL_QUESTIONS, min(4, len(BEHAVIORAL_QUESTIONS)))
    scenario = random.sample(SCENARIO_QUESTIONS, min(3, len(SCENARIO_QUESTIONS)))

    return {
        "technical": technical,
        "hr": hr,
        "behavioral": behavioral,
        "scenario": scenario,
        "role": role,
        "level": level,
        "total": len(technical) + len(hr) + len(behavioral) + len(scenario),
    }


def _skill_questions(skill: str, role: str) -> list[str]:
    """Return targeted questions for a specific skill."""
    bank = {
        "python": [
            "What are Python decorators? Give an example.",
            "Explain Python's GIL (Global Interpreter Lock).",
            "What is the difference between a list and a tuple in Python?",
            "How does Python's garbage collector work?",
        ],
        "machine learning": [
            "What is the difference between supervised and unsupervised learning?",
            "Explain how gradient boosting works.",
            "What is cross-entropy loss?",
        ],
        "sql": [
            "Write a SQL query to rank employees by salary within each department.",
            "What is the difference between HAVING and WHERE?",
            "Explain database normalization. What are 1NF, 2NF, 3NF?",
        ],
        "docker": [
            "What is the difference between a Docker image and a container?",
            "Explain Dockerfile instructions: FROM, RUN, CMD, ENTRYPOINT.",
            "How do Docker volumes work?",
        ],
        "react": [
            "What is the difference between controlled and uncontrolled components in React?",
            "Explain React's reconciliation algorithm.",
            "When would you use useCallback vs useMemo?",
        ],
        "aws": [
            "What is the difference between EC2, ECS, and Lambda?",
            "Explain S3 storage classes.",
            "What is IAM and how do roles work?",
        ],
    }
    return bank.get(skill.lower(), [])


# ── Interview Generator UI Page ───────────────────────────────────────────────

def show_interview_generator():
    st.title("🎤 Interview Question Generator")
    st.markdown("Get a personalised set of 20+ interview questions based on your target role, level, and skills.")

    has_resume = st.session_state.get("resume_uploaded", False)
    resume_skills = []
    if has_resume:
        resume_skills = st.session_state["parsed_resume"].get("skills_flat", [])
        st.info(f"📄 Using skills from your uploaded resume ({len(resume_skills)} skills).")

    c1, c2 = st.columns(2)
    with c1:
        role = st.selectbox("Target Role", ROLES)
    with c2:
        level = st.selectbox("Experience Level", LEVELS)

    extra_skills_raw = st.text_input(
        "Additional Skills (comma-separated, optional)",
        placeholder="e.g. kafka, terraform, nextjs"
    )
    extra_skills = [s.strip().lower() for s in extra_skills_raw.split(",") if s.strip()]
    all_skills = list(dict.fromkeys(resume_skills + extra_skills))

    if st.button("🎯 Generate Interview Questions", use_container_width=True):
        questions = generate_questions(role, level, all_skills)
        st.session_state["interview_questions"] = questions
        st.session_state["interview_role"] = role
        st.session_state["interview_level"] = level

    if "interview_questions" not in st.session_state:
        _show_placeholder()
        return

    q = st.session_state["interview_questions"]

    st.markdown("---")
    st.markdown(
        f"""
        <div style='background:#1e293b;border-radius:10px;padding:14px;border:1px solid #475569;
        display:flex;gap:30px;align-items:center;flex-wrap:wrap'>
            <div><span style='color:#94a3b8;font-size:0.8rem'>Role</span>
                 <div style='color:#c7d2fe;font-weight:700'>{q['role']}</div></div>
            <div><span style='color:#94a3b8;font-size:0.8rem'>Level</span>
                 <div style='color:#c7d2fe;font-weight:700'>{q['level']}</div></div>
            <div><span style='color:#94a3b8;font-size:0.8rem'>Total Questions</span>
                 <div style='color:#c7d2fe;font-weight:700'>{q['total']}</div></div>
        </div>
        """, unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        f"💻 Technical ({len(q['technical'])})",
        f"👔 HR ({len(q['hr'])})",
        f"🧠 Behavioral ({len(q['behavioral'])})",
        f"🎯 Scenario ({len(q['scenario'])})",
    ])

    with tab1:
        st.subheader(f"Technical Questions — {q['role']}")
        for i, question in enumerate(q["technical"], 1):
            _question_card(i, question, "#6366f1")

    with tab2:
        st.subheader("HR Questions")
        for i, question in enumerate(q["hr"], 1):
            _question_card(i, question, "#0891b2")

    with tab3:
        st.subheader("Behavioral Questions (STAR Method)")
        st.caption("Use the Situation → Task → Action → Result framework when answering these.")
        for i, question in enumerate(q["behavioral"], 1):
            _question_card(i, question, "#7c3aed")

    with tab4:
        st.subheader("Scenario-Based Questions")
        st.caption("Think aloud — explain your reasoning process step by step.")
        for i, question in enumerate(q["scenario"], 1):
            _question_card(i, question, "#b45309")

    # Tips section
    st.markdown("---")
    st.subheader("💡 Interview Preparation Tips")
    tips = [
        "For technical questions, write code before explaining — show, don't just tell.",
        "Use the STAR method (Situation, Task, Action, Result) for all behavioral questions.",
        "Research the company's tech stack and mention it in your answers.",
        "Prepare 2–3 questions to ask the interviewer at the end.",
        "Practice speaking answers aloud — 30 seconds to 2 minutes per question.",
        "For system design questions, clarify requirements before diving into solution.",
    ]
    for tip in tips:
        st.markdown(f"- {tip}")


def _question_card(num: int, text: str, color: str):
    st.markdown(
        f"""
        <div style='background:#1e293b;border-radius:8px;padding:12px 16px;
        margin-bottom:8px;border-left:3px solid {color}'>
            <span style='color:{color};font-weight:700;font-size:0.8rem'>Q{num}</span>
            <span style='color:#e2e8f0;font-size:0.92rem;margin-left:8px'>{text}</span>
        </div>
        """, unsafe_allow_html=True,
    )


def _show_placeholder():
    st.markdown(
        """
        <div style='background:#1e293b;border-radius:12px;padding:32px;
        text-align:center;border:1px dashed #475569;margin-top:20px'>
            <div style='font-size:3rem'>🎤</div>
            <div style='color:#c7d2fe;font-weight:700;font-size:1.1rem;margin:12px 0'>
                Select a Role & Level, then click Generate
            </div>
            <div style='color:#94a3b8;font-size:0.88rem'>
                You will get Technical, HR, Behavioral and Scenario questions tailored to your profile.
            </div>
        </div>
        """, unsafe_allow_html=True,
    )
