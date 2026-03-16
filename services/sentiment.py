from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from html import escape

_analyzer = SentimentIntensityAnalyzer()

def classify_sentiment(score: float):
    if score >= 0.05:
        return "🟢 Bullish", "#2ECC71"
    elif score <= -0.05:
        return "🔴 Bearish", "#E74C3C"
    else:
        return "🟡 Neutral", "#F39C12"

def analyze_text(text: str) -> dict:
    if not text or not isinstance(text, str):
        return {"compound": 0.0, "label": "🟡 Neutral", "color": "#F39C12"}
    scores   = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    label, color = classify_sentiment(compound)
    return {"compound": compound, "label": label, "color": color}

def analyze_articles(df):
    df = df.copy()
    df["combined_text"]    = df["title"].fillna("") + " " + df["description"].fillna("")
    results                = df["combined_text"].apply(analyze_text)
    df["sentiment_score"]  = results.apply(lambda r: r["compound"])
    df["sentiment_label"]  = results.apply(lambda r: r["label"])
    df["sentiment_color"]  = results.apply(lambda r: r["color"])
    return df

def aggregate_sentiment(df) -> dict:
    avg = df["sentiment_score"].mean()
    label, color = classify_sentiment(avg)
    return {
        "avg_score": avg,
        "label":     label,
        "color":     color,
        "bullish":   int((df["sentiment_score"] >= 0.05).sum()),
        "neutral":   int(((df["sentiment_score"] > -0.05) & (df["sentiment_score"] < 0.05)).sum()),
        "bearish":   int((df["sentiment_score"] <= -0.05).sum()),
    }

# ─────────────────────────────────────────────────────────────────────────────
# EVENT-DRIVEN IMPACT ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
#
# CONCEPT:
# Beyond knowing if news is positive or negative (sentiment),
# we want to know WHY and HOW MUCH it might affect the stock price.
#
# We do this by scanning for keywords that signal specific event types.
# Each event type has a base impact weight — regulatory events historically
# cause larger moves than general earnings commentary, for example.
#
# This is called "rules-based classification" — it's transparent,
# fast, and easy to explain in an interview, unlike a black-box ML model.
# ─────────────────────────────────────────────────────────────────────────────

# Event categories and the keywords that signal them
# Each keyword list was chosen based on common market-moving news patterns
EVENT_SIGNALS = {
    "Supply Chain": {
        "keywords": [
            "shortage", "supplier", "supply chain", "disruption", "factory",
            "manufacturing", "recall", "halt", "production", "inventory",
            "logistics", "tariff", "import", "export", "port", "shipping"
        ],
        "weight": 0.8,   # how much this event type amplifies the sentiment score
        "icon":   "🏭",
    },
    "Regulatory": {
        "keywords": [
            "SEC", "DOJ", "FTC", "lawsuit", "investigation", "fine", "penalty",
            "ban", "regulation", "compliance", "antitrust", "probe", "subpoena",
            "settlement", "sanction", "violation"
        ],
        "weight": 1.2,   # regulatory events tend to cause bigger moves
        "icon":   "⚖️",
    },
    "Earnings": {
        "keywords": [
            "revenue", "earnings", "profit", "loss", "guidance", "forecast",
            "beat", "miss", "EPS", "margin", "quarterly", "annual report",
            "dividend", "buyback", "outlook", "raise", "cut"
        ],
        "weight": 1.0,
        "icon":   "📊",
    },
    "Macro": {
        "keywords": [
            "Federal Reserve", "Fed", "interest rate", "inflation", "recession",
            "GDP", "unemployment", "CPI", "treasury", "bond yield", "monetary",
            "stimulus", "debt ceiling", "fiscal"
        ],
        "weight": 0.6,   # macro events affect all stocks so impact is diluted
        "icon":   "🌐",
    },
    "Geopolitical": {
        "keywords": [
            "war", "conflict", "sanctions", "trade war", "tariff", "embargo",
            "election", "political", "government", "China", "Russia",
            "hurricane", "earthquake", "disaster", "pipeline", "oil spill"
        ],
        "weight": 0.9,
        "icon":   "🌍",
    },
}


def classify_event_type(text: str) -> tuple[str, float]:
    """
    Scans text for keywords to identify the event type.

    HOW IT WORKS:
    For each event category, we count how many of its keywords
    appear in the text. The category with the most keyword matches wins.
    We also return that category's weight, which we'll use to calculate
    the final impact score.

    Returns:
        - event_type : str   e.g. "Regulatory"
        - weight     : float e.g. 1.2
    """
    if not text:
        return "General", 0.5

    text_lower = text.lower()
    scores     = {}

    for event_type, config in EVENT_SIGNALS.items():
        # Count how many keywords from this category appear in the text
        matches = sum(1 for kw in config["keywords"] if kw.lower() in text_lower)
        if matches > 0:
            scores[event_type] = matches

    if not scores:
        return "General", 0.5

    # Return the event type with the most keyword matches
    best = max(scores, key=scores.get)
    return best, EVENT_SIGNALS[best]["weight"]


def calculate_impact(compound_score: float, weight: float) -> tuple[str, str]:
    """
    Combines sentiment score + event weight into a final impact level.

    THE MATH:
    impact = abs(compound_score) × weight

    We use absolute value because we care about SIZE of move,
    not direction — direction comes from the sentiment label.

    - abs(compound) close to 1.0 = very strong sentiment signal
    - weight > 1.0 = event type historically causes larger moves
    - weight < 1.0 = event type typically causes smaller moves

    Impact thresholds (tuned for financial news):
    - HIGH   : > 0.6
    - MEDIUM : > 0.3
    - LOW    : everything else
    """
    impact_score = abs(compound_score) * weight

    if impact_score > 0.6:
        return "HIGH",   "🔴" if compound_score < 0 else "🟢"
    elif impact_score > 0.3:
        return "MEDIUM", "🟠" if compound_score < 0 else "🔵"
    else:
        return "LOW",    "⚪"


def analyze_portfolio_news(ticker: str, articles_df) -> list:
    """
    Takes a ticker and its news DataFrame (already sentiment-scored)
    and returns a list of impact signals — one per significant article.

    This is the function the UI calls. It filters out LOW impact
    articles and returns only things worth showing the user.

    Returns a list of dicts:
    [
        {
            "ticker":       "TSLA",
            "title":        "Tesla faces federal investigation...",
            "url":          "https://...",
            "source":       "Reuters",
            "date":         "Mar 15, 2026",
            "sentiment":    "🔴 Bearish",
            "event_type":   "Regulatory",
            "event_icon":   "⚖️",
            "impact_level": "HIGH",
            "impact_icon":  "🔴",
            "compound":     -0.72,
            "summary":      "Regulatory event detected — may signal..."
        },
        ...
    ]
    """
    signals = []

    for _, row in articles_df.iterrows():
        compound = row.get("sentiment_score", 0)
        text     = row.get("combined_text", row.get("title", ""))

        event_type, weight   = classify_event_type(text)
        impact_level, impact_icon = calculate_impact(compound, weight)

        # Only surface MEDIUM and HIGH impact articles
        # LOW impact = noise, not worth showing
        if impact_level == "LOW":
            continue

        event_icon = EVENT_SIGNALS.get(event_type, {}).get("icon", "📰")

        # Generate a plain-English explanation
        direction = "positive" if compound >= 0 else "negative"
        summary   = (
            f"{event_type} event detected — {direction} signal "
            f"with {impact_level.lower()} potential market impact. "
            f"Monitor for price movement in the next 24-48 hours."
        )

        # Clean text for safe HTML insertion
        # quote=True also escapes " characters which could break href attributes
        safe_title   = escape(str(row.get("title",   "")), quote=True)
        safe_source  = escape(str(row.get("source",  "")), quote=True)
        safe_summary = escape(str(summary),                quote=True)
        safe_url     = str(row.get("url", "#")).replace('"', '%22')

        signals.append({
            "ticker":       ticker.upper(),
            "title":        safe_title,
            "url":          safe_url,
            "source":       safe_source,
            "date":         row["publishedAt"].strftime("%b %d, %Y")
                            if hasattr(row.get("publishedAt"), "strftime")
                            else str(row.get("publishedAt", "")),
            "sentiment":    row.get("sentiment_label", ""),
            "event_type":   event_type,
            "event_icon":   event_icon,
            "impact_level": impact_level,
            "impact_icon":  impact_icon,
            "compound":     compound,
            "summary":      safe_summary,
        })

    # Sort by absolute compound score — most impactful first
    signals.sort(key=lambda x: abs(x["compound"]), reverse=True)
    return signals