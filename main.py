import streamlit as st
import firebase_admin
from firebase_admin import credentials
from navbar import show_navbar
from app.auth import login_screen, register_screen
from app.theme import apply_theme


def initialize_firebase():
    try:
        firebase_admin.get_app()   # checks if app already exists
    except ValueError:
        # ValueError means no app exists yet — safe to initialize
        cred = credentials.Certificate({
            "type":                        st.secrets["FIREBASE"]["type"],
            "project_id":                  st.secrets["FIREBASE"]["project_id"],
            "private_key_id":              st.secrets["FIREBASE"]["private_key_id"],
            "private_key":                 st.secrets["FIREBASE"]["private_key"],
            "client_email":                st.secrets["FIREBASE"]["client_email"],
            "client_id":                   st.secrets["FIREBASE"]["client_id"],
            "auth_uri":                    st.secrets["FIREBASE"]["auth_uri"],
            "token_uri":                   st.secrets["FIREBASE"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["FIREBASE"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url":        st.secrets["FIREBASE"]["client_x509_cert_url"],
            "universe_domain":             st.secrets["FIREBASE"]["universe_domain"],
        })
        firebase_admin.initialize_app(cred)


def main():
    apply_theme()
    initialize_firebase()

    st.session_state.setdefault("logged_in",     False)
    st.session_state.setdefault("show_register", False)

    if st.session_state["logged_in"]:
        show_navbar()
    elif st.session_state["show_register"]:
        register_screen()
    else:
        login_screen()


if __name__ == "__main__":
    main()
