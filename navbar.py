import streamlit as st
from streamlit_community_navigation_bar import st_navbar
from app.pages.stock_dashboard import show_stock_dashboard
from app.pages.portfolio        import show_portfolio


def show_navbar():
    styles = {
        "nav": {
            "background-color": "#0A0F1E",
            "border-bottom":    "1px solid #1E2D45",
        },
        "span": {
            "font-family":   "JetBrains Mono, monospace",
            "font-size":     "0.78rem",
            "font-weight":   "600",
            "letter-spacing":"0.08em",
            "color":         "#A0AEC0",
            "padding":       "0 16px",
        },
        "active": {
            "color":            "#0066FF",
            "border-bottom":    "2px solid #0066FF",
            "font-weight":      "700",
        },
        "hover": {
            "color":       "#F7FAFC",
            "cursor":      "pointer",
        },
    }

    page = st_navbar(
        ["Portfolio", "Stock Dashboard"],
        styles=styles,
        adjust=True,
    )

    if page == "Stock Dashboard":
        show_stock_dashboard()
    elif page == "Portfolio":
        show_portfolio()