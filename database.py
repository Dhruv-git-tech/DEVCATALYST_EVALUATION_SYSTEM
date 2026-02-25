"""
database.py — Database initialisation and CRUD operations.
Uses SQLAlchemy with SQLite by default; switch to PostgreSQL by changing DATABASE_URL.
"""

import os
from contextlib import contextmanager
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Candidate

# ── Connection ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///devcatalyst.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Lifecycle ──────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables. Safe to call multiple times (idempotent)."""
    Base.metadata.create_all(bind=engine)
    # Auto-seed if SQLite and empty (useful for Streamlit Cloud deployment)
    if DATABASE_URL.startswith("sqlite"):
        auto_seed_if_empty()


def auto_seed_if_empty() -> None:
    """
    Check if the candidate table is empty. If so, seed from the provided CSV.
    Wraps everything in a try-except to ensure the app starts regardless.
    """
    try:
        with get_session() as session:
            count = session.query(func.count(Candidate.id)).scalar()
            if count == 0:
                csv_path = "Copy of DevCatalyst-recruitment-forms - Sheet1.csv"
                if os.path.exists(csv_path):
                    print(f"Database empty. Auto-seeding from {csv_path}...")
                    _seed_from_csv(csv_path)
                else:
                    print(f"Database empty but {csv_path} not found. Skipping auto-seed.")
    except Exception as e:
        print(f"Auto-seed failed (gracefully skipping): {e}")


def _seed_from_csv(csv_path: str) -> None:
    """Internal helper to parse and load candidates from CSV one-by-one."""
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV during auto-seed: {e}")
        return

    team_map = {
        "Technical Track": "Technical",
        "Technical": "Technical",
        "Content Writing and PR": "Content",
        "Content": "Content",
        "Outreach and Sponsorship": "Outreach",
        "Outreach": "Outreach",
        "Social Media and Graphic Design": "Social",
        "Social": "Social"
    }

    print(f"Processing {len(df)} rows for auto-seed...")
    imported = 0
    
    for _, row in df.iterrows():
        email = str(row.get("Email", "")).lower().strip()
        if not email or email == "nan":
            continue
        
        # Check if already exists (another guard against duplicates)
        with get_session() as session:
            exists = session.query(Candidate).filter(Candidate.email == email).first()
            if exists:
                continue

            raw_track = str(row.get("Selected Track", ""))
            team = "Technical" 
            for key, val in team_map.items():
                if key.lower() in raw_track.lower():
                    team = val
                    break
            
            portfolio = str(row.get("GitHub", ""))
            if not portfolio or portfolio == "nan":
                portfolio = str(row.get("Portfolio Link", ""))
            if not portfolio or portfolio == "nan":
                portfolio = str(row.get("Portfolio", ""))
                
            reason = str(row.get("Why Join", ""))
            goals = str(row.get("Goals", ""))
            notes = f"Roll: {row.get('Roll Number', '')}\nSection: {row.get('Section', '')}\n\nWhy Join: {reason}\n\nGoals: {goals}"

            data = {
                "name": str(row.get("Full Name", "Unknown")),
                "email": email,
                "phone": str(row.get("Phone", "")),
                "branch": str(row.get("Branch", "Other")),
                "year": "1st Year",
                "team_applied": team,
                "github_or_portfolio": portfolio if portfolio != "nan" else "",
                "notes": notes,
                "status": "Pending",
                "stage": "Applied"
            }
            
            try:
                candidate = Candidate(**data)
                candidate.recalculate_total()
                session.add(candidate)
                # Commit happens automatically via get_session()
                imported += 1
            except Exception as e:
                print(f"Skipping candidate {email} due to error: {e}")
                # Rollback happens automatically via get_session()

    print(f"Auto-seeded {imported} candidates successfully.")


@contextmanager
def get_session() -> Session:
    """Context manager that yields a DB session and handles commit/rollback."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ── CREATE ─────────────────────────────────────────────────────────────────────

def add_candidate(data: dict) -> Candidate:
    """Insert a new candidate and return the persisted object."""
    with get_session() as session:
        candidate = Candidate(**data)
        candidate.recalculate_total()
        session.add(candidate)
        session.flush()
        session.refresh(candidate)
        return candidate


# ── READ ───────────────────────────────────────────────────────────────────────

def get_all_candidates() -> list[dict]:
    """Return all candidates as a list of dicts."""
    with get_session() as session:
        rows = session.query(Candidate).order_by(Candidate.total_score.desc()).all()
        return [r.to_dict() for r in rows]


def get_candidate_by_id(candidate_id: int) -> Optional[dict]:
    """Return a single candidate dict, or None."""
    with get_session() as session:
        row = session.get(Candidate, candidate_id)
        return row.to_dict() if row else None


def search_candidates(query: str) -> list[dict]:
    """Full-text search across name, email, branch, and team_applied."""
    with get_session() as session:
        like = f"%{query}%"
        rows = (
            session.query(Candidate)
            .filter(
                Candidate.name.ilike(like)
                | Candidate.email.ilike(like)
                | Candidate.branch.ilike(like)
                | Candidate.team_applied.ilike(like)
            )
            .order_by(Candidate.total_score.desc())
            .all()
        )
        return [r.to_dict() for r in rows]


def get_candidates_by_team(team: str) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(Candidate)
            .filter(Candidate.team_applied == team)
            .order_by(Candidate.total_score.desc())
            .all()
        )
        return [r.to_dict() for r in rows]


def get_candidates_by_status(status: str) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(Candidate)
            .filter(Candidate.status == status)
            .order_by(Candidate.total_score.desc())
            .all()
        )
        return [r.to_dict() for r in rows]


# ── UPDATE ─────────────────────────────────────────────────────────────────────

def update_candidate(candidate_id: int, data: dict) -> Optional[dict]:
    """
    Update candidate fields from a dict.
    Automatically recalculates total_score if any score field is in data.
    """
    with get_session() as session:
        candidate = session.get(Candidate, candidate_id)
        if not candidate:
            return None

        score_fields = {"standard_score", "team_score", "task_score", "impression_score"}

        for key, value in data.items():
            if hasattr(candidate, key):
                setattr(candidate, key, value)

        # Recalculate total if any score was updated
        if score_fields & set(data.keys()):
            candidate.recalculate_total()

        session.flush()
        session.refresh(candidate)
        return candidate.to_dict()


# ── DELETE ─────────────────────────────────────────────────────────────────────

def delete_candidate(candidate_id: int) -> bool:
    """Delete a candidate by ID. Returns True if found and deleted."""
    with get_session() as session:
        candidate = session.get(Candidate, candidate_id)
        if not candidate:
            return False
        session.delete(candidate)
        return True


# ── STATS (for Dashboard / Analytics) ─────────────────────────────────────────

def get_stats() -> dict:
    """Return aggregate metrics for the dashboard."""
    with get_session() as session:
        total = session.query(func.count(Candidate.id)).scalar() or 0

        # Team distribution
        team_counts = (
            session.query(Candidate.team_applied, func.count(Candidate.id))
            .group_by(Candidate.team_applied)
            .all()
        )

        # Status distribution
        status_counts = (
            session.query(Candidate.status, func.count(Candidate.id))
            .group_by(Candidate.status)
            .all()
        )

        # Average score per team
        avg_scores = (
            session.query(Candidate.team_applied, func.avg(Candidate.total_score))
            .group_by(Candidate.team_applied)
            .all()
        )

        # Top 10 candidates
        top10 = (
            session.query(Candidate)
            .order_by(Candidate.total_score.desc())
            .limit(10)
            .all()
        )

        return {
            "total": total,
            "team_counts": dict(team_counts),
            "status_counts": dict(status_counts),
            "avg_scores": {k: round(v, 2) for k, v in avg_scores if v is not None},
            "top10": [c.to_dict() for c in top10],
        }
