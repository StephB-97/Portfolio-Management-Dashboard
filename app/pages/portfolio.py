import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from services.optimizer import maximize_sharpe


def _portfolio_header():
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px;
                padding:16px 0 20px 0; border-bottom:1px solid #1E2D45;
                margin-bottom:24px;">
        <div style="width:8px; height:8px; background:#0066FF; border-radius:50%;
                    box-shadow:0 0 8px #0066FF;"></div>
        <span style="font-family:'JetBrains Mono',monospace; font-size:1.4rem;
                     font-weight:700; color:#F7FAFC; letter-spacing:0.04em;">
            PORTFOLIO MANAGER
        </span>
        <span style="font-size:0.72rem; color:#4A5568;
                     font-family:'JetBrains Mono',monospace;">
            Investment Tracker & Optimizer
        </span>
    </div>
    """, unsafe_allow_html=True)


def _show_optimizer_tab(ret_df, tickers):
    st.markdown('<div class="section-label">Max Sharpe Portfolio Optimizer</div>',
                unsafe_allow_html=True)

    with st.expander("📖 What is the Sharpe Ratio?"):
        st.markdown("""
        **Modern Portfolio Theory** finds the ideal mix of assets to maximize
        return per unit of risk — measured by the **Sharpe Ratio**.

        `Sharpe = (Portfolio Return − Risk Free Rate) / Volatility`

        - **Sharpe > 1.0** → Good
        - **Sharpe > 2.0** → Great
        - **Sharpe < 0**   → Taking risk with no reward

        Suggested weights are based on historical data and do not
        guarantee future performance.
        """)

    if len(ret_df.columns) < 2:
        st.info("Add at least 2 different stocks to use the optimizer.")
        return

    result      = maximize_sharpe(ret_df)
    opt_weights = result["weights"]
    opt_metrics = result["metrics"]
    eq_metrics  = result["equal_metrics"]
    n           = len(tickers)
    equal_w     = [1 / n] * n

    c1, c2, c3 = st.columns(3)
    c1.metric("Optimized Sharpe",    f"{opt_metrics['sharpe']:.3f}",
              delta=f"{opt_metrics['sharpe'] - eq_metrics['sharpe']:+.3f} vs equal")
    c2.metric("Equal-Weight Sharpe", f"{eq_metrics['sharpe']:.3f}")
    c3.metric("Optimized Return",    f"{opt_metrics['return']*100:.2f}%")

    st.markdown('<div class="section-label" style="margin-top:20px">Weight Comparison</div>',
                unsafe_allow_html=True)

    comparison = pd.DataFrame({
        "Ticker":           tickers,
        "Equal Weight":     [f"{w*100:.1f}%" for w in equal_w],
        "Suggested Weight": [f"{w*100:.1f}%" for w in opt_weights],
    })
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Equal Weight",
        x=tickers,
        y=[w * 100 for w in equal_w],
        marker_color="#1E2D45",
        marker_line_color="#2D4A6B",
        marker_line_width=1,
    ))
    fig.add_trace(go.Bar(
        name="Optimized Weight",
        x=tickers,
        y=[w * 100 for w in opt_weights],
        marker_color="#0066FF",
        marker_line_color="#0044CC",
        marker_line_width=1,
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#080B12",
        font=dict(family="Inter", color="#A0AEC0", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        height=280,
        yaxis=dict(
            title="Weight (%)",
            gridcolor="#111827",
            tickfont=dict(color="#4A5568"),
        ),
        xaxis=dict(tickfont=dict(color="#A0AEC0")),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#A0AEC0"),
        ),
        hoverlabel=dict(
            bgcolor="#0D1526",
            bordercolor="#1E2D45",
            font=dict(family="JetBrains Mono", color="#F7FAFC"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

def _portfolio_intelligence(portfolio: list, api_key: str):
    """
    Fetches news for every ticker in the portfolio and surfaces
    only the high and medium impact signals.

    WHY A SEPARATE FUNCTION?
    This is expensive — it makes one API call per ticker.
    Isolating it in its own function makes it easy to add
    caching later (e.g. only refresh every 30 minutes).
    """
    from services.news      import fetch_articles
    from services.sentiment import analyze_articles, analyze_portfolio_news

    if not portfolio:
        return

    st.markdown(
        '<div class="section-label" style="margin-top:32px">Portfolio Intelligence</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style="font-size:0.75rem; color:#4A5568; margin-bottom:16px;">
        Scanning latest news for market-moving events across your holdings.
        Only Medium and High impact signals are shown.
    </div>
    """, unsafe_allow_html=True)

    # Get unique tickers only — no need to fetch the same ticker twice
    tickers = list({s["ticker"] for s in portfolio})
    all_signals = []

    with st.spinner("Scanning news for portfolio signals..."):
        for ticker in tickers:
            df_news = fetch_articles(ticker, api_key)
            if df_news.empty:
                continue
            df_news  = analyze_articles(df_news)
            signals  = analyze_portfolio_news(ticker, df_news)
            all_signals.extend(signals)

    if not all_signals:
        st.info("No significant market-moving events detected for your holdings right now.")
        return

    # Sort all signals across all tickers by impact then sentiment strength
    impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_signals.sort(key=lambda x: (
        impact_order.get(x["impact_level"], 2),
        -abs(x["compound"])
    ))

    for signal in all_signals:
        # Color the card border based on sentiment direction
        border_color = "#FC4444" if signal["compound"] < 0 else "#00D4AA"
        if signal["impact_level"] == "MEDIUM":
            border_color = "#F6AD55" if signal["compound"] < 0 else "#0066FF"

        # Render header row separately
        st.markdown(f"""
        <div style="background:#0D1526; border:1px solid #1E2D45;
                    border-left:4px solid {border_color};
                    border-radius:8px; padding:16px 20px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-family:'JetBrains Mono',monospace;
                                 font-size:0.9rem; font-weight:700; color:#F7FAFC;">
                        {signal['ticker']}
                    </span>
                    <span style="background:#1A2440; border:1px solid #1E2D45;
                                 border-radius:4px; padding:2px 8px;
                                 font-size:0.65rem; font-weight:700;
                                 letter-spacing:0.1em; text-transform:uppercase;
                                 color:#A0AEC0;">
                        {signal['event_icon']} {signal['event_type']}
                    </span>
                    <span style="background:#1A2440;
                                 border-radius:4px; padding:2px 8px;
                                 font-size:0.65rem; font-weight:700;
                                 letter-spacing:0.1em; text-transform:uppercase;
                                 color:{border_color};">
                        {signal['impact_icon']} {signal['impact_level']} IMPACT
                    </span>
                </div>
                <div style="font-size:0.68rem; color:#4A5568;
                            font-family:'JetBrains Mono',monospace;">
                    {signal['source']} · {signal['date']}
                </div>
            </div>
            <div style="font-size:0.88rem; font-weight:600; color:#CBD5E0;
                        line-height:1.4; margin-bottom:8px;">
                <a href="{signal['url']}" target="_blank"
                   style="color:#CBD5E0; text-decoration:none;">
                    {signal['title']}
                </a>
            </div>
            <div style="font-size:0.75rem; color:#4A5568; line-height:1.6;
                        padding-top:8px; border-top:1px solid #1A2440;">
                {signal['summary']}
                &nbsp;·&nbsp;
                <span style="font-family:'JetBrains Mono',monospace;">
                    {signal['sentiment']} ({signal['compound']:+.3f})
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_portfolio():
    _portfolio_header()

    if "portfolio"   not in st.session_state: st.session_state["portfolio"]   = []
    if "stock_price" not in st.session_state: st.session_state["stock_price"] = 0.0
    if "num_stocks"  not in st.session_state: st.session_state["num_stocks"]  = 1

    # ── Load from DynamoDB if session is empty ────────────────────────────
    user_id = st.session_state.get("username", None)

    if user_id and len(st.session_state["portfolio"]) == 0:
        with st.spinner("Loading your portfolio..."):
            from services.database import load_portfolio
            saved = load_portfolio(user_id)
            if saved:
                st.session_state["portfolio"] = saved

    # ── Add stock form ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Add Position</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("TICKER SYMBOL", placeholder="e.g. AAPL, TSLA, NVDA")
    with col2:
        purchase_date = st.date_input("PURCHASE DATE")

    if st.button("Fetch Price", use_container_width=False):
        if ticker:
            with st.spinner(f"Fetching {ticker.upper()}..."):
                try:
                    start = pd.Timestamp(purchase_date)
                    end   = start + pd.Timedelta(days=7)
                    raw   = yf.Ticker(ticker.upper()).history(start=start, end=end)
                    if not raw.empty:
                        col = "Close" if "Close" in raw.columns else raw.columns[0]
                        st.session_state["stock_price"] = float(raw[col].iloc[0])
                        st.success(f"Price on {purchase_date}: **${st.session_state['stock_price']:,.2f}**")
                    else:
                        st.warning(f"No data for {ticker.upper()} on {purchase_date}.")
                except Exception as e:
                    st.error(f"Error: {e}")

    num_stocks = 1
    if st.session_state["stock_price"] > 0:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            <div style="background:#0D1526; border:1px solid #1E2D45;
                        border-left:3px solid #0066FF; border-radius:8px;
                        padding:12px 16px; margin:8px 0;">
                <span style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
                             text-transform:uppercase; color:#4A5568;">Fetched Price</span>
                <div style="font-family:'JetBrains Mono',monospace; font-size:1.2rem;
                            font-weight:700; color:#F7FAFC; margin-top:4px;">
                    ${st.session_state['stock_price']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            num_stocks = st.number_input(
                "SHARES",
                min_value=1,
                value=st.session_state["num_stocks"]
            )

    if st.button("Add to Portfolio ＋", use_container_width=False):
        if ticker and st.session_state["stock_price"] > 0:
            amount = st.session_state["stock_price"] * num_stocks
            entry  = {
                "ticker":     ticker.upper(),
                "date":       purchase_date,
                "price":      st.session_state["stock_price"],
                "num_stocks": num_stocks,
                "amount":     amount,
            }
            if user_id:
                from services.database import save_entry
                save_entry(
                    user_id = user_id,
                    ticker  = ticker.upper(),
                    date    = str(purchase_date),
                    price   = st.session_state["stock_price"],
                    shares  = num_stocks,
                    amount  = amount,
                )
            st.session_state["portfolio"].append(entry)
            st.session_state["stock_price"] = 0.0
            st.session_state["num_stocks"]  = 1
            st.success(f"Added **{ticker.upper()}** — {num_stocks} shares @ ${amount:,.2f} ✓ Saved")

    # ── Current holdings ──────────────────────────────────────────────────
    if st.session_state["portfolio"]:
        st.markdown('<div class="section-label" style="margin-top:24px">Current Holdings</div>',
                    unsafe_allow_html=True)

        for i, stock in enumerate(st.session_state["portfolio"]):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.5, 1.5, 2, 1])

            with col1:
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace; font-size:1rem;
                            font-weight:700; color:#F7FAFC; padding:10px 0;">
                    {stock['ticker']}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="font-size:0.78rem; color:#4A5568; padding:10px 0;">
                    {str(stock['date'])}
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.85rem;
                            color:#A0AEC0; padding:10px 0;">
                    ${stock['price']:,.2f}
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.85rem;
                            color:#A0AEC0; padding:10px 0;">
                    {stock['num_stocks']} shares
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.85rem;
                            color:#00D4AA; padding:10px 0;">
                    ${stock['amount']:,.2f}
                </div>
                """, unsafe_allow_html=True)
            with col6:
                if st.button("✕", key=f"del_{i}_{stock['ticker']}"):
                    if user_id:
                        from services.database import delete_entry
                        delete_entry(
                            user_id = user_id,
                            ticker  = stock["ticker"],
                            date    = str(stock["date"]),
                        )
                    st.session_state["portfolio"].pop(i)
                    st.success(f"Removed {stock['ticker']}")
                    st.rerun()

            st.markdown(
                "<div style='border-bottom:1px solid #1E2D45; margin:0;'></div>",
                unsafe_allow_html=True
            )

    # ── Reset portfolio ───────────────────────────────────────────────────
    # Placed BEFORE the Calculate button so it always shows
    # ── Portfolio Intelligence ────────────────────────────────────────────
    if st.session_state["portfolio"]:
        api_key = st.secrets["NEWS"]["API_KEY"]
        _portfolio_intelligence(st.session_state["portfolio"], api_key)
    st.markdown("---")
    st.markdown('<div class="section-label">Danger Zone</div>',
                unsafe_allow_html=True)
    if st.button("🗑 Clear Entire Portfolio"):
        if user_id:
            from services.database import clear_portfolio
            clear_portfolio(user_id)
        st.session_state["portfolio"]   = []
        st.session_state["stock_price"] = 0.0
        st.success("Portfolio cleared.")
        st.rerun()

    # ── Calculate button ──────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if not st.button("Calculate Performance  →", use_container_width=False):
        return
    if not st.session_state["portfolio"]:
        st.warning("Add at least one stock first.")
        return

    all_series, amounts, tickers_list = [], [], []

    with st.spinner("Loading market data..."):
        for stock in st.session_state["portfolio"]:
            try:
                raw = yf.Ticker(stock["ticker"]).history(
                    start=pd.Timestamp(stock["date"]),
                    end=pd.Timestamp.today(),
                )
                col = "Close" if "Close" in raw.columns else raw.columns[0]
                if not raw.empty:
                    all_series.append(raw[col].rename(stock["ticker"]))
                    amounts.append(stock["amount"])
                    tickers_list.append(stock["ticker"])
            except Exception as e:
                st.warning(f"Skipping {stock['ticker']}: {e}")

    if not all_series:
        st.error("Could not load data for any stocks.")
        return

    data           = pd.concat(all_series, axis=1).dropna()
    ret_df         = data.pct_change().dropna()
    cumul_ret      = (ret_df + 1).cumprod() - 1
    amounts_arr    = np.array(amounts)
    total_invested = amounts_arr.sum()
    num_shares     = [s["num_stocks"] for s in
                      st.session_state["portfolio"][:len(all_series)]]
    current_vals   = data.iloc[-1] * np.array(num_shares)
    invested_s     = pd.Series(amounts_arr, index=data.columns)
    gain_loss      = (current_vals - invested_s) / invested_s

    perf_df = pd.DataFrame({
        "Invested ($)":  amounts_arr,
        "Current ($)":   current_vals.values,
        "Gain/Loss ($)": (current_vals - invested_s).values,
        "Gain/Loss (%)": gain_loss.values * 100,
    }, index=data.columns)

    total_current = perf_df["Current ($)"].sum()
    total_gl      = total_current - total_invested
    total_gl_pct  = (total_gl / total_invested * 100) if total_invested else 0

    # ── Summary metrics ───────────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:24px">Performance Summary</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested",    f"${total_invested:,.2f}")
    c2.metric("Current Value",     f"${total_current:,.2f}")
    c3.metric("Total Gain / Loss", f"${total_gl:,.2f}",
              delta=f"{total_gl_pct:.2f}%")

    st.dataframe(perf_df, use_container_width=True)

    # ── S&P 500 benchmark ─────────────────────────────────────────────────
    try:
        start_bench = min(s["date"] for s in st.session_state["portfolio"])
        bench_raw   = yf.Ticker("^GSPC").history(
            start=pd.Timestamp(start_bench),
            end=pd.Timestamp.today(),
        )
        bench_col = "Close" if "Close" in bench_raw.columns else bench_raw.columns[0]
        bench_ret = bench_raw[bench_col].pct_change().dropna()
        bench_dev = (bench_ret + 1).cumprod() - 1
    except Exception:
        bench_dev = pd.Series(dtype=float)

    # ── Tabs ──────────────────────────────────────────────────────────────
    pct_tab, usd_tab, comp_tab, opt_tab = st.tabs([
        "  📈  % CHART  ", "  💵  USD CHART  ",
        "  🥧  COMPOSITION  ", "  🎯  OPTIMIZER  "
    ])

    def styled_chart(df, y_prefix=""):
        fig = go.Figure()
        colors = ["#0066FF", "#00D4AA", "#F6AD55", "#FC4444", "#B794F4"]
        for i, col in enumerate(df.columns):
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col],
                mode="lines", name=col,
                line=dict(color=colors[i % len(colors)], width=1.5),
            ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#080B12",
            font=dict(family="Inter", color="#A0AEC0", size=11),
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            xaxis=dict(showgrid=True, gridcolor="#111827",
                       zeroline=False, tickfont=dict(color="#4A5568")),
            yaxis=dict(showgrid=True, gridcolor="#111827",
                       zeroline=False, tickfont=dict(color="#4A5568"),
                       tickprefix=y_prefix),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#A0AEC0")),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="#0D1526", bordercolor="#1E2D45",
                            font=dict(family="JetBrains Mono", color="#F7FAFC")),
        )
        return fig

    with pct_tab:
        tog = pd.concat([bench_dev, cumul_ret.sum(axis=1)], axis=1)
        tog.columns = ["S&P 500", "Portfolio"]
        st.plotly_chart(styled_chart(tog), use_container_width=True)

    with usd_tab:
        usd_df = pd.DataFrame({
            "Portfolio": total_invested * (cumul_ret.sum(axis=1) + 1),
            "S&P 500":   total_invested * (bench_dev + 1),
        })
        st.plotly_chart(styled_chart(usd_df, "$"), use_container_width=True)

    with comp_tab:
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(go.Pie(
                labels=tickers_list,
                values=amounts_arr,
                hole=0.5,
                marker=dict(
                    colors=["#0066FF", "#00D4AA", "#F6AD55",
                            "#FC4444", "#B794F4"],
                    line=dict(color="#080B12", width=2),
                ),
                textfont=dict(family="JetBrains Mono", color="#F7FAFC"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#A0AEC0"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=280,
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#A0AEC0")),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            try:
                pf_std     = float(np.sqrt(
                    amounts_arr @ ret_df.cov().values @ amounts_arr
                ))
                bench_risk = float(bench_ret.std()) \
                    if not bench_dev.empty else float("nan")
                st.metric("Portfolio Daily Std Dev", f"{pf_std:.4f}",
                          help="Lower = more stable")
                st.metric("S&P 500 Daily Std Dev",   f"{bench_risk:.4f}")
            except Exception:
                st.info("Need more data to calculate risk metrics.")

    with opt_tab:
        _show_optimizer_tab(ret_df, tickers_list)