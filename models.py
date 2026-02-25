"""
models.py — SQLAlchemy ORM models for DevCatalyst Recruitment Evaluation System
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Candidate(Base):
    """
    Represents a recruitment candidate.
    Scores breakdown:
        standard_score  : 0-20  (standard questions rubric)
        team_score      : 0-20  (team-specific interview rubric)
        task_score      : 0-30  (task evaluation rubric)
        impression_score: 0-10  (overall impression)
        total_score     : auto-calculated (max 80)
    """

    __tablename__ = "candidates"

    # ── Identity ──────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    branch = Column(String(80), nullable=False)
    year = Column(String(20), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    team_applied = Column(String(40), nullable=False)          # Technical / Content / Outreach / Social
    github_or_portfolio = Column(String(255), nullable=True)

    # ── Scores ────────────────────────────────────────────────────────────────
    standard_score   = Column(Float, default=0.0)
    team_score       = Column(Float, default=0.0)
    task_score       = Column(Float, default=0.0)
    impression_score = Column(Float, default=0.0)
    total_score      = Column(Float, default=0.0)

    # ── Status & Stage ─────────────────────────────────────────────────────────
    status = Column(
        String(30),
        default="Pending",
    )  # Strong Select | Conditional Select | Reject | On Hold | Pending
    stage = Column(
        String(30),
        default="Applied",
    )  # Applied | Interviewed | Task Assigned | Task Submitted | Selected | Rejected

    # ── Metadata ──────────────────────────────────────────────────────────────
    interviewer = Column(String(80), nullable=True)
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def recalculate_total(self):
        """Recompute total_score from component scores."""
        self.total_score = (
            (self.standard_score or 0)
            + (self.team_score or 0)
            + (self.task_score or 0)
            + (self.impression_score or 0)
        )

    def to_dict(self):
        """Serialise candidate to a plain dict (for DataFrame / export)."""
        return {
            "id": self.id,
            "name": self.name,
            "branch": self.branch,
            "year": self.year,
            "email": self.email,
            "phone": self.phone,
            "team_applied": self.team_applied,
            "github_or_portfolio": self.github_or_portfolio,
            "standard_score": self.standard_score,
            "team_score": self.team_score,
            "task_score": self.task_score,
            "impression_score": self.impression_score,
            "total_score": self.total_score,
            "status": self.status,
            "stage": self.stage,
            "interviewer": self.interviewer,
            "notes": self.notes,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def __repr__(self):
        return f"<Candidate id={self.id} name={self.name!r} team={self.team_applied!r}>"
