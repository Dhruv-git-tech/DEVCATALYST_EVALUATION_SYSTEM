"""
seed_db.py — Wipe existing data and load from the real recruitment CSV.
"""

import pandas as pd
from database import get_session, init_db, engine
from models import Candidate, Base
import evaluation_logic as el

CSV_FILE = "Copy of DevCatalyst-recruitment-forms - Sheet1.csv"

def wipe_db():
    print("Wiping existing database...")
    Base.metadata.drop_all(bind=engine)
    init_db()
    print("Database wiped and schema recreated.")

def seed():
    print(f"Loading data from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Mapping logic
    # CSV -> Model
    # Full Name -> name
    # Email -> email
    # Phone -> phone
    # Branch -> branch
    # Selected Track -> team_applied
    # GitHub / Portfolio Link -> github_or_portfolio
    
    # Team Mapping
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

    candidates_to_add = []
    
    print(f"Processing {len(df)} rows...")
    
    for _, row in df.iterrows():
        # Get raw team and map it
        raw_track = str(row.get("Selected Track", ""))
        team = "Technical" # Default
        for key, val in team_map.items():
            if key.lower() in raw_track.lower():
                team = val
                break
        
        # Determine portfolio link
        portfolio = str(row.get("GitHub", ""))
        if not portfolio or portfolio == "nan":
            portfolio = str(row.get("Portfolio Link", ""))
        if not portfolio or portfolio == "nan":
            portfolio = str(row.get("Portfolio", ""))
            
        # Notes: combine some fields
        reason = str(row.get("Why Join", ""))
        goals = str(row.get("Goals", ""))
        notes = f"Roll: {row.get('Roll Number', '')}\nSection: {row.get('Section', '')}\n\nWhy Join: {reason}\n\nGoals: {goals}"

        data = {
            "name": str(row.get("Full Name", "Unknown")),
            "email": str(row.get("Email", "")).lower().strip(),
            "phone": str(row.get("Phone", "")),
            "branch": str(row.get("Branch", "Other")),
            "year": "1st Year", # Default as it's not explicitly in CSV headers provided
            "team_applied": team,
            "github_or_portfolio": portfolio if portfolio != "nan" else "",
            "notes": notes,
            "status": "Pending",
            "stage": "Applied"
        }
        
        # Skip if no email
        if not data["email"]:
            continue
            
        candidates_to_add.append(Candidate(**data))

    with get_session() as session:
        # Deduplicate by email just in case
        seen_emails = set()
        unique_candidates = []
        for c in candidates_to_add:
            if c.email not in seen_emails:
                unique_candidates.append(c)
                seen_emails.add(c.email)
        
        session.add_all(unique_candidates)
        print(f"Successfully added {len(unique_candidates)} candidates.")

if __name__ == "__main__":
    wipe_db()
    seed()
