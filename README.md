# DevCatalyst Recruitment Evaluation System

A production-ready Streamlit web application for evaluating club recruitment candidates in a structured, bias-free, score-driven way.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the application
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

**Default login credentials:**
| Username   | Password            |
|------------|---------------------|
| `admin`    | `devcatalyst2024`   |
| `recruiter`| `recruit@DC2024`    |

---

## Project Structure

```
DEVCATALYST EVALUATION SYSTEM/
├── app.py               ← Main Streamlit entry point (all 8 pages)
├── models.py            ← SQLAlchemy ORM (Candidate model)
├── database.py          ← DB init, sessions, CRUD, stats
├── auth.py              ← Admin authentication & login UI
├── evaluation_logic.py  ← Question bank, rubrics, scoring helpers
├── requirements.txt     ← Python dependencies
├── README.md            ← This file
└── devcatalyst.db       ← SQLite database (auto-created on first run)
```

---

## Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | Session-based admin login |
| 📊 **Dashboard** | KPI cards, team/status charts, top-10 leaderboard |
| ➕ **Add Candidate** | Full candidate registration form |
| 📋 **Evaluate Candidate** | Standard + team-specific interview rubric with live score preview |
| 🛠️ **Task Evaluation** | Team-specific task rubric (30 pts) |
| 🎯 **Final Selection** | Stage/status management, search, delete |
| 📈 **Analytics** | Histograms, box plots, score breakdowns by team |
| 📥 **Export** | Download full CSV, Excel, or shortlisted-only CSV |
| ✏️ **Edit Candidate** | Update any candidate's personal details |

---

## Scoring System

| Component        | Max Pts |
|------------------|---------|
| Standard Questions | 20   |
| Team Interview     | 20   |
| Task Evaluation    | 30   |
| Impression         | 10   |
| **Total**          | **80** |

**Status thresholds:**
- 🟢 **Strong Select** — Total ≥ 65
- 🟡 **Conditional Select** — Total 55–64
- 🔴 **Reject** — Total < 55

---

## Teams Supported

- **Technical** — Code, debugging, system thinking
- **Content** — Writing, storytelling, simplicity
- **Outreach** — Sponsorship, cold email, negotiation
- **Social Media** — Growth strategy, algorithm awareness, creativity

---

## Migrating to PostgreSQL

Change the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/devcatalyst"
streamlit run app.py
```

No other code changes are needed — SQLAlchemy handles the rest.
