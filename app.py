"""
app.py — DevCatalyst Recruitment Evaluation System
Main Streamlit entry point. Run with: streamlit run app.py
"""

import io
import pandas as pd
import plotly.express as px
import streamlit as st

import auth
import database as db
import evaluation_logic as el

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="DevCatalyst — Recruitment Evaluation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        border: 1px solid #3d3d5c;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #a78bfa;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3d3d5c;
    }

    /* Status badges */
    .badge-strong   { background:#065f46; color:#6ee7b7; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-cond     { background:#78350f; color:#fde68a; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-reject   { background:#7f1d1d; color:#fca5a5; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-hold     { background:#1e3a5f; color:#93c5fd; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-pending  { background:#374151; color:#d1d5db; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }

    /* Score bar background */
    .stProgress > div > div { border-radius: 8px; }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }

    /* Form styling */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #3d3d5c;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def status_badge(status: str) -> str:
    cls_map = {
        "Strong Select":      "badge-strong",
        "Conditional Select": "badge-cond",
        "Reject":             "badge-reject",
        "On Hold":            "badge-hold",
        "Pending":            "badge-pending",
    }
    cls = cls_map.get(status, "badge-pending")
    return f'<span class="{cls}">{el.status_color(status)} {status}</span>'


def score_progress(label: str, value: float, max_val: float) -> None:
    pct = int((value / max_val) * 100) if max_val else 0
    st.caption(f"{label}: **{value:.1f} / {max_val}**")
    st.progress(pct / 100)


def df_from_candidates(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def page_dashboard() -> None:
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)

    stats = db.get_stats()
    total = stats["total"]

    # ── KPI Row ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Candidates", total)
    k2.metric("Teams Active", len(stats["team_counts"]))

    selected_count = stats["status_counts"].get("Strong Select", 0) + stats["status_counts"].get("Conditional Select", 0)
    k3.metric("Shortlisted", selected_count)

    avg_all = (
        round(sum(stats["avg_scores"].values()) / len(stats["avg_scores"]), 1)
        if stats["avg_scores"] else 0
    )
    k4.metric("Avg Score (all)", avg_all)

    st.markdown("---")

    if total == 0:
        st.info("No candidates yet. Add your first candidate from the sidebar → **Add Candidate**.")
        return

    # ── Charts Row ──
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Team Distribution")
        team_df = pd.DataFrame(
            list(stats["team_counts"].items()), columns=["Team", "Count"]
        )
        fig = px.bar(
            team_df, x="Team", y="Count",
            color="Team",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Status Distribution")
        status_df = pd.DataFrame(
            list(stats["status_counts"].items()), columns=["Status", "Count"]
        )
        fig2 = px.pie(
            status_df, names="Status", values="Count",
            color_discrete_sequence=["#34d399", "#fbbf24", "#f87171", "#60a5fa", "#94a3b8"],
            template="plotly_dark",
            hole=0.45,
        )
        fig2.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Avg Score per Team ──
    if stats["avg_scores"]:
        st.subheader("Average Total Score by Team")
        avg_df = pd.DataFrame(
            [(k, v) for k, v in stats["avg_scores"].items()],
            columns=["Team", "Avg Score"],
        )
        fig3 = px.bar(
            avg_df, x="Team", y="Avg Score",
            color="Team",
            text="Avg Score",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
            template="plotly_dark",
        )
        fig3.update_layout(showlegend=False, margin=dict(t=20, b=20), yaxis_range=[0, 80])
        st.plotly_chart(fig3, use_container_width=True)

    # ── Top 10 Leaderboard ──
    st.subheader("🏆 Top 10 Candidates Leaderboard")
    if stats["top10"]:
        lb_df = pd.DataFrame(stats["top10"])[
            ["name", "team_applied", "branch", "total_score", "status", "stage"]
        ]
        lb_df.columns = ["Name", "Team", "Branch", "Total Score", "Status", "Stage"]
        lb_df.index = range(1, len(lb_df) + 1)
        st.dataframe(lb_df, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD CANDIDATE
# ══════════════════════════════════════════════════════════════════════════════

def page_add_candidate() -> None:
    st.markdown('<div class="section-header">➕ Add Candidate</div>', unsafe_allow_html=True)

    with st.form("add_candidate_form", clear_on_submit=True):
        st.subheader("Personal Information")
        c1, c2, c3 = st.columns(3)
        name   = c1.text_input("Full Name *", placeholder="Ravi Kumar")
        email  = c2.text_input("Email Address *", placeholder="ravi@college.edu")
        phone  = c3.text_input("Phone Number", placeholder="+91-XXXXXXXXXX")

        c4, c5, c6 = st.columns(3)
        branch = c4.selectbox("Branch *", el.BRANCHES)
        year   = c5.selectbox("Year *", el.YEARS)
        team   = c6.selectbox("Team Applied *", el.TEAMS)

        portfolio = st.text_input("GitHub / Portfolio Link", placeholder="https://github.com/username")

        st.subheader("Recruiter Details")
        r1, r2 = st.columns(2)
        interviewer = r1.text_input("Interviewer Name", placeholder="Your name")
        notes = r2.text_area("Initial Notes", placeholder="First impression, referral source, etc.")

        submitted = st.form_submit_button("✅ Add Candidate", use_container_width=True)

    if submitted:
        # Validation
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not email.strip():
            errors.append("Email is required.")

        if errors:
            for e in errors:
                st.error(e)
            return

        data = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "phone": phone.strip(),
            "branch": branch,
            "year": year,
            "team_applied": team,
            "github_or_portfolio": portfolio.strip(),
            "interviewer": interviewer.strip(),
            "notes": notes.strip(),
            "status": "Pending",
            "stage": "Applied",
        }

        try:
            db.add_candidate(data)
            st.success(f"✅ **{name}** has been added successfully!")
            st.balloons()
        except Exception as exc:
            if "UNIQUE constraint" in str(exc) or "unique" in str(exc).lower():
                st.error("A candidate with this email already exists.")
            else:
                st.error(f"Database error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EVALUATE CANDIDATE (Standard + Team Interview Rubric)
# ══════════════════════════════════════════════════════════════════════════════

def page_evaluate_candidate() -> None:
    st.markdown('<div class="section-header">📋 Evaluate Candidate</div>', unsafe_allow_html=True)

    all_candidates = db.get_all_candidates()
    if not all_candidates:
        st.info("No candidates found. Add a candidate first.")
        return

    # ── Candidate Selector ──
    name_map = {f"#{c['id']} — {c['name']} ({c['team_applied']})": c["id"] for c in all_candidates}
    selected_label = st.selectbox("Select Candidate", list(name_map.keys()))
    candidate_id = name_map[selected_label]
    c = db.get_candidate_by_id(candidate_id)
    if not c:
        st.error("Candidate not found.")
        return

    team = c["team_applied"]
    team_data = el.TEAM_DATA.get(team, {})

    # ── Candidate Info Card ──
    with st.expander("📌 Candidate Profile", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Name", c["name"])
        col2.metric("Team", c["team_applied"])
        col3.metric("Branch / Year", f"{c['branch']} • {c['year']}")
        col4.metric("Current Stage", c["stage"])
        if c["github_or_portfolio"]:
            st.markdown(f"🔗 [Portfolio / GitHub]({c['github_or_portfolio']})")

    # ── Tabs: Standard | Team-Specific | Impression ──
    tab_std, tab_team, tab_imp = st.tabs(
        ["📝 Standard Questions", f"🔍 {team} Team Questions", "⭐ Impression & Notes"]
    )

    # ─ Standard Questions ─
    with tab_std:
        st.info("Read each question aloud to the candidate. Score each rubric dimension below.")
        with st.expander("▶ View Standard Questions", expanded=True):
            for q in el.STANDARD_QUESTIONS:
                st.markdown(f"- {q}")

        st.markdown("**Standard Rubric** *(4 criteria × 5 pts = 20 max)*")
        std_scores: dict[str, int] = {}
        for crit, hint in el.STANDARD_RUBRIC:
            std_scores[crit] = st.slider(
                crit, 0, 5,
                value=0,
                help=hint,
                key=f"std_{candidate_id}_{crit}",
            )
        std_total = sum(std_scores.values())
        score_progress("Standard Score", std_total, 20)

    # ─ Team Questions ─
    with tab_team:
        questions = team_data.get("questions", [])
        rubric = team_data.get("interview_rubric", [])

        st.info(f"Team-specific questions for the **{team}** team.")
        with st.expander(f"▶ View {team} Interview Questions", expanded=True):
            for q in questions:
                st.markdown(f"- {q}")

        st.markdown(f"**{team} Interview Rubric** *(4 criteria × 5 pts = 20 max)*")
        team_scores: dict[str, int] = {}
        for crit, hint in rubric:
            team_scores[crit] = st.slider(
                crit, 0, 5,
                value=0,
                help=hint,
                key=f"team_{candidate_id}_{crit}",
            )
        team_total = sum(team_scores.values())
        score_progress(f"{team} Interview Score", team_total, 20)

    # ─ Impression ─
    with tab_imp:
        st.markdown("**Overall Impression** *(max 10 pts)*")
        impression = st.slider(
            "Impression Score", 0, 10,
            value=0,
            key=f"imp_{candidate_id}",
            help="Holistic gut-feel score. Confidence, culture fit, enthusiasm.",
        )
        interviewer_name = st.text_input(
            "Interviewer Name",
            value=c.get("interviewer") or "",
            key=f"intvr_{candidate_id}",
        )
        notes = st.text_area(
            "Detailed Notes",
            value=c.get("notes") or "",
            key=f"notes_{candidate_id}",
            height=120,
        )

    # ── Live Score Preview ──
    st.markdown("---")
    prev_task = c.get("task_score") or 0
    live_total = el.calculate_total_score(std_total, team_total, prev_task, impression)
    suggested = el.suggest_status(live_total)

    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Standard", f"{std_total}/20")
    p2.metric("Team Interview", f"{team_total}/20")
    p3.metric("Task (saved)", f"{prev_task}/30")
    p4.metric("Impression", f"{impression}/10")
    p5.metric("🔢 Live Total", f"{live_total:.0f}/80")

    st.markdown(
        f"**Auto-suggested Status:** {status_badge(suggested)}",
        unsafe_allow_html=True,
    )
    score_progress("Total Score", live_total, 80)

    # ── Save ──
    if st.button("💾 Save Evaluation", use_container_width=True, type="primary"):
        db.update_candidate(candidate_id, {
            "standard_score": float(std_total),
            "team_score": float(team_total),
            "impression_score": float(impression),
            "interviewer": interviewer_name.strip(),
            "notes": notes.strip(),
            "status": suggested,
            "stage": "Interviewed",
        })
        st.success("✅ Evaluation saved! Stage → **Interviewed**.")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TASK EVALUATION
# ══════════════════════════════════════════════════════════════════════════════

def page_task_evaluation() -> None:
    st.markdown('<div class="section-header">🛠️ Task Evaluation</div>', unsafe_allow_html=True)

    all_candidates = db.get_all_candidates()
    if not all_candidates:
        st.info("No candidates yet.")
        return

    name_map = {f"#{c['id']} — {c['name']} ({c['team_applied']})": c["id"] for c in all_candidates}
    selected_label = st.selectbox("Select Candidate", list(name_map.keys()))
    candidate_id = name_map[selected_label]
    c = db.get_candidate_by_id(candidate_id)
    if not c:
        st.error("Candidate not found.")
        return

    team = c["team_applied"]
    task_rubric = el.TEAM_DATA.get(team, {}).get("task_rubric", [])

    # ── Info ──
    col1, col2, col3 = st.columns(3)
    col1.metric("Candidate", c["name"])
    col2.metric("Team", team)
    col3.metric("Current Task Score", f"{c['task_score']:.0f}/30")

    st.markdown(f"**{team} Task Rubric** *(6 criteria × 5 pts = 30 max)*")
    st.info("Score based on the submitted task artefact (link, file, or live demo).")

    task_scores: dict[str, int] = {}
    cols = st.columns(2)
    for i, (crit, hint) in enumerate(task_rubric):
        with cols[i % 2]:
            task_scores[crit] = st.slider(
                crit, 0, 5,
                value=int(c.get(f"task_score", 0) // len(task_rubric)) if task_rubric else 0,
                help=hint,
                key=f"task_{candidate_id}_{crit}",
            )

    task_total = sum(task_scores.values())
    score_progress(f"{team} Task Score", task_total, 30)

    # Live combined preview
    updated_total = el.calculate_total_score(
        c["standard_score"], c["team_score"], task_total, c["impression_score"]
    )
    suggested = el.suggest_status(updated_total)

    st.markdown("---")
    t1, t2, t3 = st.columns(3)
    t1.metric("Task Score", f"{task_total}/30")
    t2.metric("Updated Total", f"{updated_total:.0f}/80")
    t3.metric("New Status", f"{el.status_color(suggested)} {suggested}")

    if st.button("💾 Save Task Score", use_container_width=True, type="primary"):
        db.update_candidate(candidate_id, {
            "task_score": float(task_total),
            "status": suggested,
            "stage": "Task Submitted",
        })
        st.success(f"✅ Task score saved. New total: **{updated_total:.0f}/80**.")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FINAL SELECTION
# ══════════════════════════════════════════════════════════════════════════════

def page_final_selection() -> None:
    st.markdown('<div class="section-header">🎯 Final Selection</div>', unsafe_allow_html=True)

    # ── Filters ──
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    search_q = fc1.text_input("🔍 Search candidates", placeholder="Name, email, branch…")
    filter_team   = fc2.selectbox("Filter by Team",   ["All"] + el.TEAMS)
    filter_status = fc3.selectbox("Filter by Status", ["All"] + el.STATUSES)

    # ── Fetch ──
    if search_q:
        rows = db.search_candidates(search_q)
    else:
        rows = db.get_all_candidates()

    if filter_team != "All":
        rows = [r for r in rows if r["team_applied"] == filter_team]
    if filter_status != "All":
        rows = [r for r in rows if r["status"] == filter_status]

    st.caption(f"Showing **{len(rows)}** candidate(s)")

    if not rows:
        st.info("No candidates match the selected filters.")
        return

    # ── Candidate Cards ──
    for c in rows:
        with st.expander(
            f"#{c['id']} — {c['name']}  |  {c['team_applied']}  |  "
            f"Score: {c['total_score']:.0f}/80  |  {el.status_color(c['status'])} {c['status']}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"**Email:** {c['email']}")
                st.markdown(f"**Branch / Year:** {c['branch']} • {c['year']}")
                if c["github_or_portfolio"]:
                    st.markdown(f"**Portfolio:** [{c['github_or_portfolio']}]({c['github_or_portfolio']})")
                if c["interviewer"]:
                    st.markdown(f"**Interviewer:** {c['interviewer']}")

            with col2:
                score_progress("Standard",   c["standard_score"],   20)
                score_progress("Team",       c["team_score"],       20)
                score_progress("Task",       c["task_score"],       30)
                score_progress("Impression", c["impression_score"], 10)

            with col3:
                new_status = st.selectbox(
                    "Status",
                    el.STATUSES,
                    index=el.STATUSES.index(c["status"]) if c["status"] in el.STATUSES else 0,
                    key=f"status_{c['id']}",
                )
                new_stage = st.selectbox(
                    "Stage",
                    el.STAGES,
                    index=el.STAGES.index(c["stage"]) if c["stage"] in el.STAGES else 0,
                    key=f"stage_{c['id']}",
                )
                new_notes = st.text_area(
                    "Notes",
                    value=c.get("notes") or "",
                    key=f"fnotes_{c['id']}",
                    height=80,
                )

                save_col, del_col = st.columns(2)
                with save_col:
                    if st.button("💾 Save", key=f"save_{c['id']}", use_container_width=True):
                        db.update_candidate(c["id"], {
                            "status": new_status,
                            "stage": new_stage,
                            "notes": new_notes,
                        })
                        st.success("Saved!")
                        st.rerun()
                with del_col:
                    if st.button("🗑️ Delete", key=f"del_{c['id']}", use_container_width=True):
                        db.delete_candidate(c["id"])
                        st.warning(f"Deleted **{c['name']}**.")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

def page_analytics() -> None:
    st.markdown('<div class="section-header">📈 Analytics</div>', unsafe_allow_html=True)

    all_rows = db.get_all_candidates()
    if not all_rows:
        st.info("No data yet. Add and evaluate candidates first.")
        return

    df = df_from_candidates(all_rows)

    # ── Filters ──
    fc1, fc2 = st.columns(2)
    filter_team   = fc1.multiselect("Filter by Team",   el.TEAMS,    default=el.TEAMS)
    filter_status = fc2.multiselect("Filter by Status", el.STATUSES, default=el.STATUSES)

    filtered = df[df["team_applied"].isin(filter_team) & df["status"].isin(filter_status)]
    st.caption(f"**{len(filtered)}** candidates in view")

    if filtered.empty:
        st.info("No candidates match the current filters.")
        return

    st.markdown("---")

    # ── Score Histogram ──
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Score Distribution")
        fig_hist = px.histogram(
            filtered, x="total_score", nbins=16,
            color="team_applied",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
            template="plotly_dark",
            labels={"total_score": "Total Score", "team_applied": "Team"},
        )
        fig_hist.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Team Performance Box Plot ──
    with c2:
        st.subheader("Score Range by Team")
        fig_box = px.box(
            filtered, x="team_applied", y="total_score",
            color="team_applied",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
            template="plotly_dark",
            labels={"total_score": "Total Score", "team_applied": "Team"},
        )
        fig_box.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Score Breakdown Comparison ──
    st.subheader("Score Breakdown by Team")
    avg_cols = ["team_applied", "standard_score", "team_score", "task_score", "impression_score"]
    avg_df = filtered[avg_cols].groupby("team_applied").mean().reset_index()
    fig_bar = px.bar(
        avg_df.melt(id_vars="team_applied", var_name="Score Type", value_name="Avg"),
        x="team_applied", y="Avg", color="Score Type", barmode="group",
        color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
        template="plotly_dark",
        labels={"team_applied": "Team", "Avg": "Average Score"},
    )
    fig_bar.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Raw Table ──
    st.subheader("Candidate Table")
    display_cols = ["name", "team_applied", "branch", "year", "standard_score",
                    "team_score", "task_score", "impression_score", "total_score", "status", "stage"]
    st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT DATA
# ══════════════════════════════════════════════════════════════════════════════

def page_export() -> None:
    st.markdown('<div class="section-header">📥 Export Data</div>', unsafe_allow_html=True)

    all_rows = db.get_all_candidates()
    if not all_rows:
        st.info("No candidates to export.")
        return

    df = df_from_candidates(all_rows)
    shortlisted_df = df[df["status"].isin(["Strong Select", "Conditional Select"])]

    st.metric("Total Candidates", len(df))
    col1, col2 = st.columns(2)
    col1.metric("Shortlisted Candidates", len(shortlisted_df))
    col2.metric("Rejected / Pending", len(df) - len(shortlisted_df))

    st.markdown("---")

    # ── CSV — All ──
    e1, e2, e3 = st.columns(3)
    with e1:
        st.subheader("📄 Full CSV")
        csv_all = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download All Candidates (CSV)",
            data=csv_all,
            file_name="devcatalyst_all_candidates.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Excel — All ──
    with e2:
        st.subheader("📊 Full Excel")
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="All Candidates")
        excel_buffer.seek(0)
        st.download_button(
            label="⬇️ Download All Candidates (Excel)",
            data=excel_buffer,
            file_name="devcatalyst_all_candidates.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ── CSV — Shortlisted ──
    with e3:
        st.subheader("🏆 Shortlisted CSV")
        if shortlisted_df.empty:
            st.info("No shortlisted candidates yet.")
        else:
            csv_short = shortlisted_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Shortlisted (CSV)",
                data=csv_short,
                file_name="devcatalyst_shortlisted.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ── Preview ──
    st.markdown("---")
    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EDIT CANDIDATE (Bonus)
# ══════════════════════════════════════════════════════════════════════════════

def page_edit_candidate() -> None:
    st.markdown('<div class="section-header">✏️ Edit Candidate</div>', unsafe_allow_html=True)

    all_candidates = db.get_all_candidates()
    if not all_candidates:
        st.info("No candidates yet.")
        return

    name_map = {f"#{c['id']} — {c['name']} ({c['team_applied']})": c["id"] for c in all_candidates}
    selected_label = st.selectbox("Select Candidate to Edit", list(name_map.keys()))
    candidate_id = name_map[selected_label]
    c = db.get_candidate_by_id(candidate_id)
    if not c:
        st.error("Candidate not found.")
        return

    with st.form(f"edit_form_{candidate_id}"):
        st.subheader("Edit Personal Information")
        col1, col2, col3 = st.columns(3)
        name      = col1.text_input("Full Name", value=c["name"])
        email     = col2.text_input("Email", value=c["email"])
        phone     = col3.text_input("Phone", value=c.get("phone") or "")

        col4, col5, col6 = st.columns(3)
        branch = col4.selectbox("Branch",    el.BRANCHES, index=el.BRANCHES.index(c["branch"]) if c["branch"] in el.BRANCHES else 0)
        year   = col5.selectbox("Year",      el.YEARS,    index=el.YEARS.index(c["year"]) if c["year"] in el.YEARS else 0)
        team   = col6.selectbox("Team",      el.TEAMS,    index=el.TEAMS.index(c["team_applied"]) if c["team_applied"] in el.TEAMS else 0)

        portfolio   = st.text_input("GitHub / Portfolio", value=c.get("github_or_portfolio") or "")
        interviewer = st.text_input("Interviewer", value=c.get("interviewer") or "")
        notes       = st.text_area("Notes", value=c.get("notes") or "")

        submitted = st.form_submit_button("✅ Update Candidate", use_container_width=True)

    if submitted:
        db.update_candidate(candidate_id, {
            "name": name.strip(),
            "email": email.strip().lower(),
            "phone": phone.strip(),
            "branch": branch,
            "year": year,
            "team_applied": team,
            "github_or_portfolio": portfolio.strip(),
            "interviewer": interviewer.strip(),
            "notes": notes.strip(),
        })
        st.success(f"✅ **{name}** updated successfully.")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: IMPORT CSV
# ══════════════════════════════════════════════════════════════════════════════

# Required columns that must exist in the uploaded CSV
_REQUIRED_IMPORT_COLS = {
    "name", "email", "team_applied",
}

# All recognised import columns → DB field mapping (same name = identity)
_IMPORT_COL_MAP = {
    "name":                 "name",
    "email":                "email",
    "phone":                "phone",
    "branch":               "branch",
    "year":                 "year",
    "team_applied":         "team_applied",
    "github_or_portfolio":  "github_or_portfolio",
    "interviewer":          "interviewer",
    "notes":                "notes",
    "standard_score":       "standard_score",
    "team_score":           "team_score",
    "task_score":           "task_score",
    "impression_score":     "impression_score",
    "status":               "status",
    "stage":                "stage",
}


def _make_template_csv() -> bytes:
    """Return a CSV bytes object that serves as the import template."""
    template_cols = [
        "name", "email", "phone", "branch", "year", "team_applied",
        "github_or_portfolio", "interviewer", "notes",
        "standard_score", "team_score", "task_score", "impression_score",
        "status", "stage",
    ]
    example_row = {
        "name": "Ravi Kumar",
        "email": "ravi@college.edu",
        "phone": "+91-9876543210",
        "branch": "Computer Science",
        "year": "2nd Year",
        "team_applied": "Technical",
        "github_or_portfolio": "https://github.com/ravikumar",
        "interviewer": "Admin",
        "notes": "Strong communicator, good project depth.",
        "standard_score": 16,
        "team_score": 15,
        "task_score": 22,
        "impression_score": 8,
        "status": "Pending",
        "stage": "Applied",
    }
    df_tmpl = pd.DataFrame([example_row], columns=template_cols)
    return df_tmpl.to_csv(index=False).encode("utf-8")


def page_import_csv() -> None:
    st.markdown('<div class="section-header">📤 Import CSV</div>', unsafe_allow_html=True)

    st.markdown(
        """
        Upload a CSV file to bulk-import candidates into the system.  
        Each row becomes one candidate record. Existing candidates with the
        same **email** are **skipped** (no overwrite) — duplicates are reported.
        """
    )

    # ── Download Template ──
    st.subheader("Step 1 — Download the Template")
    st.download_button(
        label="⬇️ Download CSV Template",
        data=_make_template_csv(),
        file_name="devcatalyst_import_template.csv",
        mime="text/csv",
        help="Fill this template and re-upload it below.",
    )

    st.markdown(
        """
        **Column guide:**
        | Column | Required? | Allowed values |
        |---|---|---|
        | `name` | ✅ | Any text |
        | `email` | ✅ | Valid email (must be unique) |
        | `phone` | ❌ | Any text |
        | `branch` | ❌ | Any text |
        | `year` | ❌ | 1st Year … 4th Year, Alumni |
        | `team_applied` | ✅ | Technical / Content / Outreach / Social |
        | `github_or_portfolio` | ❌ | URL to GitHub, portfolio, Drive, etc. |
        | `interviewer` | ❌ | Name of the interviewer |
        | `notes` | ❌ | Free text |
        | `standard_score` | ❌ | 0–20 |
        | `team_score` | ❌ | 0–20 |
        | `task_score` | ❌ | 0–30 |
        | `impression_score` | ❌ | 0–10 |
        | `status` | ❌ | Pending / Strong Select / Conditional Select / On Hold / Reject |
        | `stage` | ❌ | Applied / Interviewed / Task Assigned / Task Submitted / Selected / Rejected |
        """
    )

    st.markdown("---")

    # ── File Uploader ──
    st.subheader("Step 2 — Upload Your CSV")
    uploaded = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="UTF-8 encoded CSV. Max ~50 MB.",
    )

    if uploaded is None:
        st.info("Waiting for file upload…")
        return

    # ── Parse ──
    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not parse CSV: {exc}")
        return

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.fillna("")

    # ── Validate required columns ──
    missing_req = _REQUIRED_IMPORT_COLS - set(df.columns)
    if missing_req:
        st.error(
            f"Missing required columns: **{', '.join(sorted(missing_req))}**. "
            "Please fix your CSV and re-upload."
        )
        return

    total_rows = len(df)
    st.success(f"✅ File parsed successfully — **{total_rows}** rows found.")

    # ── Preview with clickable portfolio links ──
    st.subheader("Preview (first 10 rows)")
    preview_cols = [c for c in [
        "name", "email", "team_applied", "branch", "year",
        "github_or_portfolio", "standard_score", "team_score",
        "task_score", "impression_score", "status", "stage",
    ] if c in df.columns]

    preview_df = df[preview_cols].head(10).copy()

    # Render portfolio links as clickable HTML
    if "github_or_portfolio" in preview_df.columns:
        def _linkify(val: str) -> str:
            val = str(val).strip()
            if val and val.startswith("http"):
                return f'<a href="{val}" target="_blank">🔗 Open</a>'
            return val or "—"

        preview_html = preview_df.copy()
        preview_html["github_or_portfolio"] = preview_html["github_or_portfolio"].apply(_linkify)
        st.markdown(preview_html.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(preview_df, use_container_width=True)

    # ── Team breakdown in upload ──
    if "team_applied" in df.columns:
        team_counts = df["team_applied"].value_counts().reset_index()
        team_counts.columns = ["Team", "Count"]
        st.subheader("Team Distribution in Upload")
        fig = px.bar(
            team_counts, x="Team", y="Count",
            color="Team",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399", "#fb923c"],
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Import Button ──
    st.subheader("Step 3 — Import")
    if st.button("🚀 Import All Rows", use_container_width=True, type="primary"):
        imported   = 0
        skipped    = 0
        errors_log = []

        progress_bar = st.progress(0)
        status_text  = st.empty()

        for idx, row in df.iterrows():
            pct = int(((idx + 1) / total_rows) * 100)
            progress_bar.progress(pct / 100)
            status_text.caption(f"Processing row {idx + 1} / {total_rows}…")

            # Build candidate data dict from recognised columns
            data: dict = {
                "status": "Pending",
                "stage":  "Applied",
            }
            for col, field in _IMPORT_COL_MAP.items():
                if col in df.columns:
                    raw = row.get(col, "")
                    # Coerce numeric score columns
                    if field in {"standard_score", "team_score", "task_score", "impression_score"}:
                        try:
                            data[field] = float(raw) if str(raw).strip() != "" else 0.0
                        except ValueError:
                            data[field] = 0.0
                    else:
                        data[field] = str(raw).strip()

            # Validate required fields
            if not data.get("name") or not data.get("email") or not data.get("team_applied"):
                errors_log.append(f"Row {idx + 1}: Skipped — name/email/team_applied missing.")
                skipped += 1
                continue

            # Normalise email
            data["email"] = data["email"].lower()

            # Validate team
            if data["team_applied"] not in el.TEAMS:
                errors_log.append(
                    f"Row {idx + 1} ({data['name']}): Invalid team '{data['team_applied']}'. "
                    f"Must be one of {el.TEAMS}."
                )
                skipped += 1
                continue

            # Ensure branch/year default
            data.setdefault("branch", "Other")
            if not data.get("branch"):
                data["branch"] = "Other"
            data.setdefault("year", "1st Year")
            if not data.get("year"):
                data["year"] = "1st Year"

            try:
                db.add_candidate(data)
                imported += 1
            except Exception as exc:
                msg = str(exc)
                if "UNIQUE" in msg.upper() or "unique" in msg:
                    errors_log.append(f"Row {idx + 1} ({data['name']}): Duplicate email — skipped.")
                else:
                    errors_log.append(f"Row {idx + 1} ({data['name']}): {msg}")
                skipped += 1

        progress_bar.progress(1.0)
        status_text.empty()

        # ── Results summary ──
        r1, r2 = st.columns(2)
        r1.metric("✅ Imported", imported)
        r2.metric("⚠️ Skipped", skipped)

        if imported > 0:
            st.success(f"Successfully imported **{imported}** candidate(s)!")
        if errors_log:
            with st.expander(f"⚠️ {len(errors_log)} row(s) had issues — click to view"):
                for msg in errors_log:
                    st.warning(msg)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 1rem 0;">
                <div style="font-size:2.2rem;">🚀</div>
                <div style="font-size:1.15rem; font-weight:700; color:#a78bfa;">DevCatalyst</div>
                <div style="font-size:0.75rem; color:#64748b;">Recruitment Evaluation System</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        pages = {
            "📊 Dashboard":          "dashboard",
            "➕ Add Candidate":      "add_candidate",
            "📤 Import CSV":         "import_csv",
            "📋 Evaluate Candidate": "evaluate_candidate",
            "🛠️ Task Evaluation":    "task_evaluation",
            "🎯 Final Selection":    "final_selection",
            "📈 Analytics":          "analytics",
            "📥 Export Data":        "export_data",
            "✏️ Edit Candidate":     "edit_candidate",
        }

        if "active_page" not in st.session_state:
            st.session_state.active_page = "dashboard"

        for label, key in pages.items():
            is_active = st.session_state.active_page == key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state.active_page = key
                st.rerun()

        st.markdown("---")
        st.caption(f"Logged in as **{auth.get_current_user()}**")
        if st.button("🔓 Logout", use_container_width=True):
            auth.logout()

    return st.session_state.active_page


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Initialise database
    db.init_db()

    # Guard: unauthenticated users get the login page
    if not auth.is_authenticated():
        auth.render_login_page()
        return

    # Sidebar navigation
    active_page = render_sidebar()

    # Page dispatcher
    page_fn = {
        "dashboard":          page_dashboard,
        "add_candidate":      page_add_candidate,
        "import_csv":         page_import_csv,
        "evaluate_candidate": page_evaluate_candidate,
        "task_evaluation":    page_task_evaluation,
        "final_selection":    page_final_selection,
        "analytics":          page_analytics,
        "export_data":        page_export,
        "edit_candidate":     page_edit_candidate,
    }

    fn = page_fn.get(active_page, page_dashboard)
    fn()


if __name__ == "__main__":
    main()
