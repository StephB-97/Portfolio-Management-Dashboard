import streamlit as st
from firebase_admin import auth


def login_screen():
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        st.markdown("""
        <div style="text-align:center; padding:40px 0 32px 0;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                        font-weight:700; color:#0066FF; letter-spacing:0.06em;">
                ◈ PORTFOLIO MGR
            </div>
            <div style="font-size:0.68rem; color:#4A5568; letter-spacing:0.14em;
                        text-transform:uppercase; margin-top:6px;">
                Investment Intelligence Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#0D1526; border:1px solid #1E2D45;
                    border-radius:12px; padding:32px 32px 24px 32px;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.14em;
                        text-transform:uppercase; color:#0066FF; margin-bottom:20px;">
                — Secure Login
            </div>
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("Email Address", placeholder="trader@firm.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        def handle_login():
            if not email or not password:
                st.error("Both fields are required.")
                return
            try:
                from services.database import load_portfolio
                user = auth.get_user_by_email(email)
                st.session_state["logged_in"] = True
                st.session_state["username"]  = user.uid
                saved = load_portfolio(user.uid)
                st.session_state["portfolio"]   = saved
                st.session_state["stock_price"] = 0.0
                st.session_state["num_stocks"]  = 1
                st.rerun()
            except Exception:
                st.error("Invalid credentials or account not found.")

        # ← these are OUTSIDE handle_login, inside the `with col` block
        st.button("LOGIN  →", on_click=handle_login, use_container_width=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; font-size:0.72rem; color:#2D3748;">
            ──────  or  ──────
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Create Account", use_container_width=True):
            st.session_state["show_register"] = True
            st.rerun()

        st.markdown("""
        <div style="text-align:center; margin-top:28px; font-size:0.62rem;
                    color:#2D3748; letter-spacing:0.08em;">
            MARKET DATA  ·  REAL-TIME ANALYTICS  ·  AI SENTIMENT
        </div>
        """, unsafe_allow_html=True)


def register_screen():
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        st.markdown("""
        <div style="text-align:center; padding:40px 0 32px 0;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                        font-weight:700; color:#0066FF; letter-spacing:0.06em;">
                ◈ PORTFOLIO MGR
            </div>
            <div style="font-size:0.68rem; color:#4A5568; letter-spacing:0.14em;
                        text-transform:uppercase; margin-top:6px;">
                Create Your Account
            </div>
        </div>
        """, unsafe_allow_html=True)

        username         = st.text_input("Username")
        email            = st.text_input("Email Address")
        password         = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        def handle_register():
            if not all([username, email, password, confirm_password]):
                st.error("All fields are required.")
                return
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            try:
                auth.create_user(email=email, password=password, uid=username)
                st.success("Account created! You can now log in.")
                st.session_state["show_register"] = False
            except Exception as e:
                st.error(f"Registration failed: {e}")

        st.button("CREATE ACCOUNT  →", on_click=handle_register, use_container_width=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("← Back to Login", use_container_width=True):
            st.session_state["show_register"] = False
            st.rerun()