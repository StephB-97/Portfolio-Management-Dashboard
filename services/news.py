import requests
import pandas as pd
import streamlit as st

NEWS_API_BASE = "https://newsapi.org/v2/everything"

def fetch_articles(ticker: str, api_key: str, limit: int = 10) -> pd.DataFrame:
    params = {
        "q":        ticker,
        "apiKey":   api_key,
        "pageSize": limit,
        "sortBy":   "publishedAt",
    }
    try:
        response = requests.get(NEWS_API_BASE, params=params, timeout=10)
        data     = response.json()
    except requests.exceptions.Timeout:
        st.error("News request timed out. Try again.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"News fetch error: {e}")
        return pd.DataFrame()

    if data.get("status") != "ok":
        st.error("NewsAPI error: " + data.get("message", "Unknown"))
        return pd.DataFrame()

    articles = data.get("articles", [])
    if not articles:
        return pd.DataFrame()

    for article in articles:
        article["source"] = article["source"].get("name", "Unknown")

    df = pd.DataFrame(articles)
    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    df = df.sort_values("publishedAt", ascending=False).head(limit)
    return df