"""
evaluation_logic.py — Question bank, rubric definitions, and scoring helpers.
All evaluation constants live here so pages stay thin and data-driven.
"""

# ── Enums ──────────────────────────────────────────────────────────────────────

TEAMS = ["Technical", "Content", "Outreach", "Social"]

STAGES = [
    "Applied",
    "Interviewed",
    "Task Assigned",
    "Task Submitted",
    "Selected",
    "Rejected",
]

STATUSES = [
    "Pending",
    "Strong Select",
    "Conditional Select",
    "On Hold",
    "Reject",
]

YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Alumni"]

BRANCHES = [
    "Computer Science",
    "Information Technology",
    "Electronics & Communication",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Other",
]

# ── Standard Questions (all teams) ─────────────────────────────────────────────

STANDARD_QUESTIONS = [
    "1. Why DevCatalyst? What drew you to apply?",
    "2. What problem on campus do you most want to solve?",
    "3. Describe one thing you fully planned and executed end-to-end.",
    "4. If a teammate doesn't respond 24 hours before a deadline, what do you do?",
    "5. What skill are you currently actively improving and why?",
]

STANDARD_RUBRIC = [
    ("Communication", "How clearly and confidently does the candidate express ideas?"),
    ("Proof of Work", "Does the candidate provide concrete evidence of past contributions?"),
    ("Ownership", "Does the candidate take full responsibility for outcomes?"),
    ("Commitment", "How serious and consistent is the candidate's commitment level?"),
]  # 4 × 5 = 20 max


# ── Team-Specific Questions & Rubrics ─────────────────────────────────────────

TEAM_DATA: dict[str, dict] = {
    "Technical": {
        "questions": [
            "1. Describe a project you built from scratch. What was your role?",
            "2. What is the hardest bug you ever fixed? Walk us through your process.",
            "3. How do you approach debugging an unfamiliar codebase?",
            "4. Explain the difference between a client and a server.",
            "5. The event website crashes 2 hours before the event. What do you do?",
        ],
        "interview_rubric": [
            ("Code Understanding", "Does the candidate understand the code they've written?"),
            ("Logic & Debugging", "How systematic is their debugging and problem-solving?"),
            ("System Thinking", "Can they reason about systems beyond individual functions?"),
            ("Clarity", "Can they explain technical concepts in simple terms?"),
        ],  # 4 × 5 = 20 max
        "task_rubric": [
            ("Code Structure", "Is the code clean, modular, and readable?"),
            ("UI/UX", "Is the interface intuitive and visually appropriate?"),
            ("Git Usage", "Are commits atomic, well-labelled, and pushed on time?"),
            ("Optimization", "Is the solution efficient? Any obvious performance issues?"),
            ("Deadline", "Was the task submitted before or on the deadline?"),
            ("Explanation", "Can the candidate clearly explain their design decisions?"),
        ],  # 6 × 5 = 30 max
    },

    "Content": {
        "questions": [
            "1. Write 80 words explaining AI to a 10-year-old. (Give 5 minutes.)",
            "2. Simplify this technical paragraph: [Interviewer provides excerpt].",
            "3. How would you document a hackathon from Day 1 to Day 2?",
            "4. What makes content engaging vs merely informative?",
        ],
        "interview_rubric": [
            ("Clarity", "Are ideas expressed without ambiguity or jargon?"),
            ("Structure", "Is the response logically organised?"),
            ("Creativity", "Does the candidate bring a fresh or memorable angle?"),
            ("Simplicity", "Can they strip complexity without losing accuracy?"),
        ],
        "task_rubric": [
            ("Writing Quality", "Is the writing polished and audience-appropriate?"),
            ("Grammar", "Is grammar, punctuation, and spelling correct throughout?"),
            ("Storytelling", "Does the content have a compelling narrative arc?"),
            ("Design Quality", "Are visual elements (if any) clean and relevant?"),
            ("Originality", "Is the content fresh, not generic or templated?"),
            ("Deadline", "Was the task submitted before or on the deadline?"),
        ],
    },

    "Outreach": {
        "questions": [
            "1. How would you approach a potential sponsor who has never heard of us?",
            "2. Draft a cold email subject line and opening line for a tech company.",
            "3. A company says 'We're not interested.' How do you respond?",
            "4. What value do we offer sponsors that they cannot get elsewhere?",
        ],
        "interview_rubric": [
            ("Professionalism", "Is the tone appropriate for corporate communication?"),
            ("Persuasion", "Does the candidate know how to build compelling narratives?"),
            ("Research Ability", "Did they research the company/sponsor before pitching?"),
            ("Confidence", "Do they project confidence without being pushy?"),
        ],
        "task_rubric": [
            ("Email Quality", "Is the outreach email polished and persuasive?"),
            ("Value Proposition", "Is the value offer specific and compelling?"),
            ("Research Depth", "Did they research the sponsor's goals and past events?"),
            ("Structure", "Is the pitch logically sequenced?"),
            ("Negotiation Thinking", "Do they anticipate objections and address them?"),
            ("Deadline", "Was the task submitted before or on the deadline?"),
        ],
    },

    "Social": {
        "questions": [
            "1. How would you grow an Instagram account from 0 to 1000 engaged followers?",
            "2. Break down the Hook → Retention → CTA framework with an example.",
            "3. Which content format (Reels, Carousels, Stories) performs best and why?",
            "4. Walk us through how you'd interpret a post's analytics to improve next time.",
        ],
        "interview_rubric": [
            ("Growth Strategy", "Is the growth plan realistic and data-informed?"),
            ("Algorithm Knowledge", "Do they understand platform-specific ranking signals?"),
            ("Creativity", "Are their content ideas fresh and scroll-stopping?"),
            ("Trend Awareness", "Are they keeping up with current social media trends?"),
        ],
        "task_rubric": [
            ("Content Calendar Quality", "Is the calendar realistic, themed, and platform-appropriate?"),
            ("Reel Concept Strength", "Is the reel concept attention-grabbing?"),
            ("Hook Quality", "Does the hook make you stop scrolling within 1-2 seconds?"),
            ("Analytics Thinking", "Do they show data-driven reasoning?"),
            ("Consistency Plan", "Is there a sustainable posting cadence?"),
            ("Deadline", "Was the task submitted before or on the deadline?"),
        ],
    },
}


# ── Score helpers ──────────────────────────────────────────────────────────────

def calculate_total_score(
    standard: float,
    team: float,
    task: float,
    impression: float,
) -> float:
    """Return clamped total score (max 80)."""
    return min(standard + team + task + impression, 80.0)


def suggest_status(total_score: float) -> str:
    """
    Auto-derive status from total score.
    Thresholds:
        ≥ 65  → Strong Select
        55–64 → Conditional Select
        < 55  → Reject
    """
    if total_score >= 65:
        return "Strong Select"
    elif total_score >= 55:
        return "Conditional Select"
    else:
        return "Reject"


def status_color(status: str) -> str:
    """Return an emoji indicator for display."""
    return {
        "Strong Select":     "🟢",
        "Conditional Select": "🟡",
        "Reject":            "🔴",
        "On Hold":           "🔵",
        "Pending":           "⚪",
    }.get(status, "⚪")


def score_band_label(total: float) -> str:
    """Human-readable score band."""
    if total >= 65:
        return "Excellent"
    elif total >= 55:
        return "Good"
    elif total >= 40:
        return "Average"
    else:
        return "Below Par"
