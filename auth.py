"""
auth.py — Simple session-based admin authentication for DevCatalyst Evaluation System.

Credentials are hardcoded here.  To add more admins, extend ADMIN_CREDENTIALS.
For production, replace with a proper hashed-password scheme.
"""

import streamlit as st

# ── Hardcoded admin credentials ────────────────────────────────────────────────
ADMIN_CREDENTIALS: dict[str, str] = {
    "admin": "devcatalyst2024",
    "recruiter": "recruit@DC2024",
}

SESSION_KEY = "dc_authenticated"
USER_KEY    = "dc_username"


# ── Public helpers ─────────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    """Return True if the user has an active session."""
    return st.session_state.get(SESSION_KEY, False)


def get_current_user() -> str:
    """Return the username of the currently logged-in admin."""
    return st.session_state.get(USER_KEY, "")


def login(username: str, password: str) -> bool:
    """
    Validate credentials.  On success, set session state and return True.
    """
    if ADMIN_CREDENTIALS.get(username) == password:
        st.session_state[SESSION_KEY] = True
        st.session_state[USER_KEY]    = username
        return True
    return False


def logout() -> None:
    """Clear session state and force a rerun."""
    st.session_state[SESSION_KEY] = False
    st.session_state[USER_KEY]    = ""
    st.rerun()


def require_auth() -> None:
    """
    Guard that must be called at the top of every protected page.
    Redirects (via st.stop()) to the login form if not authenticated.
    """
    if not is_authenticated():
        render_login_page()
        st.stop()


# ── Login UI ───────────────────────────────────────────────────────────────────

def render_login_page() -> None:
    """Render the full-page login form."""
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 420px;
            margin: 6rem auto 0;
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg, #1e1e2f 0%, #2a2a45 100%);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45);
        }
        .login-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #a78bfa;
            text-align: center;
            margin-bottom: 0.25rem;
        }
        .login-sub {
            font-size: 0.9rem;
            color: #94a3b8;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">🚀 DevCatalyst</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Recruitment Evaluation System</div>', unsafe_allow_html=True)
        st.markdown("---")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter admin username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

        if submitted:
            if login(username, password):
                st.success("Login successful! Redirecting…")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
