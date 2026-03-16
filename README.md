# 📈 Portfolio Management & Stock Intelligence Platform

**Live Demo:** https://sb-portfolio-management.streamlit.app

A full-stack investment platform built with Python and Streamlit that combines real-time market data, AI-powered news sentiment analysis, event-driven portfolio intelligence, and Modern Portfolio Theory optimization — with persistent user data stored on AWS DynamoDB.

---

## What It Does

### Portfolio Manager
- Add stock positions by ticker, purchase date, and number of shares
- Real-time gain/loss tracking against your cost basis
- Performance benchmarked against the S&P 500
- Individual position deletion per ticker
- Full portfolio persistence — data survives refreshes and new sessions via AWS DynamoDB

### Portfolio Intelligence (Event-Driven Analysis)
- Automatically scans latest news for every ticker in your portfolio
- Classifies news into 5 event categories: **Supply Chain**, **Regulatory**, **Earnings**, **Macro**, **Geopolitical**
- Scores each article using VADER NLP sentiment analysis
- Calculates an impact score by combining sentiment strength with event-type weighting
- Surfaces only High and Medium impact signals — filters out noise
- Cards ranked by impact level so the most important signals appear first

### Portfolio Optimizer (Modern Portfolio Theory)
- Finds the portfolio weights that maximize the Sharpe Ratio using `scipy.optimize`
- Compares optimized vs equal-weight allocation side by side
- Explains: *"Given your holdings, you should put X% in AAPL and Y% in TSLA"*

### Stock Dashboard
- Bloomberg-style header with live price, delta, and % change
- 5-cell stats bar: Volume, Market Cap, 52W High/Low, P/E Ratio
- Dark area chart — teal when stock is up, red when down
- Financial statements: Balance Sheet, Income Statement, Cash Flow
- News feed with per-article sentiment scores and aggregate mood gauge

### Authentication
- Firebase user authentication (login + registration)
- Each user's portfolio is private and isolated by Firebase UID

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly |
| Finance Data | yFinance |
| News | NewsAPI |
| AI / NLP | VADER Sentiment Analysis |
| Optimization | SciPy (Modern Portfolio Theory) |
| Database | AWS DynamoDB (boto3) |
| Auth | Firebase Admin SDK |
| Language | Python 3.11 |

---

## Project Structure
```
portfolio_management/
├── main.py                          # Entry point — Firebase init + routing
├── navbar.py                        # Navigation between pages
├── requirements.txt
├── README.md
│
├── app/
│   ├── auth.py                      # Login and registration screens
│   ├── theme.py                     # Global CSS — dark finance terminal UI
│   └── pages/
│       ├── portfolio.py             # Portfolio Manager + Intelligence panel
│       └── stock_dashboard.py       # Stock Dashboard page
│
└── services/                        # Pure logic — no UI code
    ├── sentiment.py                 # VADER NLP + event-driven classifier
    ├── optimizer.py                 # MPT Sharpe ratio optimization
    ├── news.py                      # NewsAPI data fetching
    └── database.py                  # AWS DynamoDB read/write operations
```

**Architecture principle:** `app/` handles display, `services/` handles logic. Pages import from services — services never import from pages. This separation makes the codebase testable and maintainable.

---

## Local Setup

### Prerequisites
- Python 3.11+
- AWS account with DynamoDB table
- Firebase project with Admin SDK credentials
- NewsAPI key (free tier at newsapi.org)

### 1. Clone the repo
```bash
git clone https://github.com/StephB-97/Portfolio_Management.git
cd Portfolio_Management
```

### 2. Create and activate a virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create AWS DynamoDB table
- Table name: `portfolios`
- Partition key: `user_id` (String)
- Sort key: `entry_id` (String)
- Create an IAM user with `AmazonDynamoDBFullAccess` and generate an access key

### 5. Set up secrets
Create `.streamlit/secrets.toml` in the project root:
```toml
[NEWS]
API_KEY = "your_newsapi_key"

[FIREBASE]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = """-----BEGIN PRIVATE KEY-----
your_key_here
-----END PRIVATE KEY-----
"""
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
universe_domain = "googleapis.com"

[AWS]
access_key_id     = "your_access_key_id"
secret_access_key = "your_secret_access_key"
region            = "your_region"
```

> ⚠️ Never commit `secrets.toml` to GitHub. It is already excluded in `.gitignore`.

### 6. Run the app
```bash
streamlit run main.py
```

Open http://localhost:8501 in your browser.

---

## Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. In **Advanced settings → Secrets**, paste the contents of your `secrets.toml`
4. Deploy — Streamlit Cloud will install dependencies from `requirements.txt` automatically

---

## How the Event Detection Works

For each ticker in the user's portfolio:

1. Fetch the 10 most recent news articles from NewsAPI
2. Combine the title + description of each article
3. Run VADER sentiment analysis → compound score between -1.0 and +1.0
4. Scan the text for keywords across 5 event categories
5. Multiply the absolute sentiment score by the event category's weight
6. Filter out Low impact results
7. Sort remaining signals by impact level and sentiment strength
8. Display as styled cards with color-coded borders

**Event category weights** (based on historical price impact patterns):
- Regulatory: 1.2 (highest — fines, investigations cause large moves)
- Earnings: 1.0 (direct financial impact)
- Supply Chain: 0.8
- Geopolitical: 0.9
- Macro: 0.6 (lowest — affects all stocks, so impact is diluted)

---

## How the Portfolio Optimizer Works

Given a set of stocks, the optimizer finds the weights that maximize the **Sharpe Ratio**:
```
Sharpe = (Portfolio Return − Risk Free Rate) / Portfolio Volatility
```

Using `scipy.optimize.minimize` with SLSQP method, subject to:
- All weights sum to 1.0 (invest 100% of capital)
- Each weight between 0 and 1 (no short selling)

The result tells you the ideal allocation given historical return correlations.

---

## Security Notes

- No credentials are hardcoded anywhere in the codebase
- All secrets are loaded from `st.secrets` at runtime
- Firebase Admin SDK is initialized once using `try/except` to prevent duplicate initialization
- AWS IAM user has minimum required permissions (DynamoDB only)
- `.gitignore` excludes `secrets.toml`, `.env`, `*.json`, `venv/`, and `.idea/`





