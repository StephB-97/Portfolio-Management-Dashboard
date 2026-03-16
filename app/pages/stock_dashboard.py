import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

from services.news      import fetch_articles
from services.sentiment import analyze_articles, aggregate_sentiment


def _show_sentiment_gauge(summary: dict):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=summary["avg_score"],
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": summary["label"], "font": {"color": "#A0AEC0", "size": 13}},
        number={"font": {"color": "#F7FAFC", "family": "JetBrains Mono", "size": 28}},
        gauge={
            "axis": {
                "range": [-1, 1],
                "tickcolor": "#2D3748",
                "tickfont": {"color": "#4A5568", "size": 10},
            },
            "bar":  {"color": summary["color"], "thickness": 0.25},
            "bgcolor": "#0D1526",
            "bordercolor": "#1E2D45",
            "steps": [
                {"range": [-1,    -0.05], "color": "#1F0A0A"},
                {"range": [-0.05,  0.05], "color": "#111827"},
                {"range": [0.05,   1],    "color": "#0A1F15"},
            ],
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#A0AEC0",
    )
    st.plotly_chart(fig, use_container_width=True)


def _page_header(ticker, company, price, delta, pct):
    color = "#00D4AA" if delta >= 0 else "#FC4444"
    sign  = "▲" if delta >= 0 else "▼"
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                padding:16px 0 20px 0; border-bottom:1px solid #1E2D45;
                margin-bottom:24px;">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:8px; height:8px; background:#00D4AA; border-radius:50%;
                        box-shadow:0 0 8px #00D4AA;"></div>
            <span style="font-family:'JetBrains Mono',monospace; font-size:1.4rem;
                         font-weight:700; color:#F7FAFC; letter-spacing:0.04em;">
                {ticker.upper()}
            </span>
            <span style="font-size:0.82rem; color:#4A5568;">{company}</span>
        </div>
        <div style="display:flex; align-items:baseline; gap:12px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:1.8rem;
                         font-weight:700; color:#F7FAFC;">${price:,.2f}</span>
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.9rem;
                         font-weight:600; color:{color};">
                {sign} ${abs(delta):.2f} ({abs(pct):.2f}%)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _stats_bar(info):
    vol    = info.get("volume", info.get("regularMarketVolume", 0))
    mktcap = info.get("marketCap", 0)
    high52 = info.get("fiftyTwoWeekHigh", 0)
    low52  = info.get("fiftyTwoWeekLow",  0)
    pe     = info.get("trailingPE", "—")

    def fmt(n):
        if n >= 1e12: return f"${n/1e12:.2f}T"
        if n >= 1e9:  return f"${n/1e9:.2f}B"
        if n >= 1e6:  return f"${n/1e6:.2f}M"
        return f"{n:,}"

    st.markdown(f"""
    <div style="display:flex; gap:1px; background:#1E2D45; border-radius:8px;
                overflow:hidden; margin-bottom:24px;">
        <div style="flex:1; background:#0D1526; padding:14px 18px; text-align:center;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:#4A5568; margin-bottom:5px;">Volume</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem;
                        font-weight:600; color:#F7FAFC;">{fmt(vol)}</div>
        </div>
        <div style="flex:1; background:#0D1526; padding:14px 18px; text-align:center;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:#4A5568; margin-bottom:5px;">Mkt Cap</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem;
                        font-weight:600; color:#F7FAFC;">{fmt(mktcap)}</div>
        </div>
        <div style="flex:1; background:#0D1526; padding:14px 18px; text-align:center;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:#4A5568; margin-bottom:5px;">52W High</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem;
                        font-weight:600; color:#00D4AA;">${high52:,.2f}</div>
        </div>
        <div style="flex:1; background:#0D1526; padding:14px 18px; text-align:center;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:#4A5568; margin-bottom:5px;">52W Low</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem;
                        font-weight:600; color:#FC4444;">${low52:,.2f}</div>
        </div>
        <div style="flex:1; background:#0D1526; padding:14px 18px; text-align:center;">
            <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:#4A5568; margin-bottom:5px;">P/E Ratio</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem;
                        font-weight:600; color:#F7FAFC;">
                {pe if isinstance(pe, str) else f"{pe:.1f}"}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_stock_dashboard():
    ticker     = st.sidebar.text_input("TICKER SYMBOL", "TSLA")
    start_date = st.sidebar.date_input("FROM", value=None)
    end_date   = st.sidebar.date_input("TO")

    # ── Fetch data ────────────────────────────────────────────────────────
    with st.spinner(f"Fetching {ticker.upper()}..."):
        data = yf.Ticker(ticker.upper()).history(
            start=pd.Timestamp(start_date) if start_date else None,
            end=pd.Timestamp(end_date),
        )

    if data.empty:
        st.error(f"No data for **{ticker.upper()}**. Check the symbol and date range.")
        return

    info           = yf.Ticker(ticker.upper()).info
    current_price  = info.get("currentPrice", info.get("regularMarketPrice", float(data["Close"].iloc[-1])))
    previous_close = info.get("previousClose", current_price)
    company_name   = info.get("shortName", ticker.upper())
    delta          = current_price - previous_close
    pct_change     = (delta / previous_close * 100) if previous_close else 0

    # ── Header + stats bar ────────────────────────────────────────────────
    _page_header(ticker, company_name, current_price, delta, pct_change)
    _stats_bar(info)

    # ── Price chart ───────────────────────────────────────────────────────
    close_col  = "Close" if "Close" in data.columns else data.columns[0]
    color_line = "#00D4AA" if delta >= 0 else "#FC4444"
    fill_color = "rgba(0,212,170,0.06)" if delta >= 0 else "rgba(252,68,68,0.06)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[close_col],
        mode="lines",
        name="Close",
        line=dict(color=color_line, width=1.5),
        fill="tozeroy",
        fillcolor=fill_color,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#080B12",
        font=dict(family="Inter", color="#A0AEC0", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        height=320,
        xaxis=dict(
            showgrid=True, gridcolor="#111827",
            zeroline=False, showline=False,
            tickfont=dict(size=10, color="#4A5568"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#111827",
            zeroline=False, showline=False,
            tickfont=dict(size=10, color="#4A5568"),
            tickprefix="$",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0D1526",
            bordercolor="#1E2D45",
            font=dict(family="JetBrains Mono", color="#F7FAFC"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    pricing_tab, financials_tab, news_tab = st.tabs([
        "  📊  PRICING  ", "  📋  FINANCIALS  ", "  📰  NEWS & SENTIMENT  "
    ])

    with pricing_tab:
        df2             = data.copy()
        df2["% Change"] = df2[close_col].pct_change()
        df2.dropna(inplace=True)
        annual_return   = df2["% Change"].mean() * 252 * 100
        stdev           = np.std(df2["% Change"]) * np.sqrt(252) * 100
        sharpe          = annual_return / stdev if stdev else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Annual Return",        f"{annual_return:.2f}%")
        c2.metric("Annualized Std Dev",   f"{stdev:.2f}%")
        c3.metric("Risk-Adjusted Return", f"{sharpe:.3f}")

        st.dataframe(
            df2[[close_col, "% Change"]].rename(
                columns={close_col: "Close ($)", "% Change": "Daily Return"}
            ),
            use_container_width=True,
        )

    with financials_tab:
        stock = yf.Ticker(ticker.upper())
        st.markdown('<div class="section-label">Balance Sheet</div>',
                    unsafe_allow_html=True)
        st.dataframe(stock.balance_sheet, use_container_width=True)
        st.markdown('<div class="section-label">Income Statement</div>',
                    unsafe_allow_html=True)
        st.dataframe(stock.income_stmt, use_container_width=True)
        st.markdown('<div class="section-label">Cash Flow</div>',
                    unsafe_allow_html=True)
        st.dataframe(stock.cashflow, use_container_width=True)

    with news_tab:
        st.markdown(f'<div class="section-label">News Sentiment — {ticker.upper()}</div>',
                    unsafe_allow_html=True)
        api_key = st.secrets["NEWS"]["API_KEY"]

        with st.spinner("Analyzing sentiment..."):
            df_news = fetch_articles(ticker, api_key)
            if df_news.empty:
                st.info("No news articles found.")
                return
            df_news = analyze_articles(df_news)
            summary = aggregate_sentiment(df_news)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Score",  f"{summary['avg_score']:.3f}")
        c2.metric("🟢 Bullish", summary["bullish"])
        c3.metric("🟡 Neutral", summary["neutral"])
        c4.metric("🔴 Bearish", summary["bearish"])

        _, gauge_col, _ = st.columns([1, 2, 1])
        with gauge_col:
            _show_sentiment_gauge(summary)

        st.markdown("---")
        st.markdown('<div class="section-label">Article Feed</div>',
                    unsafe_allow_html=True)

        for _, row in df_news.iterrows():
            color = row["sentiment_color"]
            score = row["sentiment_score"]
            st.markdown(f"""
            <div style="background:#0D1526; border:1px solid #1E2D45;
                        border-left:3px solid {color}; border-radius:8px;
                        padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between;
                            align-items:center; margin-bottom:8px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:0.72rem; font-weight:700; color:{color};">
                            {row['sentiment_label']}
                        </span>
                        <span style="font-family:'JetBrains Mono',monospace;
                                     font-size:0.7rem; color:#4A5568;">
                            {score:+.3f}
                        </span>
                    </div>
                    <div style="font-size:0.68rem; color:#4A5568;
                                font-family:'JetBrains Mono',monospace;">
                        {row['source']}  ·  {row['publishedAt'].strftime('%b %d, %Y')}
                    </div>
                </div>
                <a href="{row['url']}" target="_blank"
                   style="font-size:0.88rem; font-weight:600; color:#CBD5E0;
                          text-decoration:none; line-height:1.4;">
                    {row['title']}
                </a>
                <p style="font-size:0.75rem; color:#4A5568; margin-top:6px;
                           margin-bottom:0; line-height:1.5;">
                    {row.get('description', '') or ''}
                </p>
            </div>
            """, unsafe_allow_html=True)