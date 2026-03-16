import streamlit as st
from streamlit_navigation_bar import st_navbar
from app.pages.stock_dashboard import show_stock_dashboard
from app.pages.portfolio        import show_portfolio


def show_navbar():
    page = st_navbar(["Portfolio", "Stock Dashboard"])
    if page == "Stock Dashboard":
        show_stock_dashboard()
    elif page == "Portfolio":
        show_portfolio()