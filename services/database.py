"""
services/database.py
─────────────────────
All DynamoDB operations live here.
Pages never talk to AWS directly — they call these functions.

TABLE DESIGN:
  Table name    : portfolios
  Partition key : user_id  (Firebase UID — one "folder" per user)
  Sort key      : entry_id (TICKER#DATE — unique per stock entry)

WHY THIS DESIGN?
  DynamoDB is optimized for key-based lookups.
  Storing user_id as the partition key means all of a user's
  data lives together physically on the same server shard —
  so fetching an entire portfolio is a single fast query,
  not a slow full-table scan.
"""

import boto3
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from boto3.dynamodb.conditions import Key


# ── Connect to DynamoDB ───────────────────────────────────────────────────────
#
# boto3.resource() creates a high-level DynamoDB client.
# We pass credentials from st.secrets — never hardcoded.
# The resource is created once at module load time and reused.
#
def _get_table():
    """
    Returns the DynamoDB table resource.
    Called inside each function so Streamlit secrets are
    always loaded before we try to read them.
    """
    dynamodb = boto3.resource(
        "dynamodb",
        region_name          = st.secrets["AWS"]["region"],
        aws_access_key_id    = st.secrets["AWS"]["access_key_id"],
        aws_secret_access_key= st.secrets["AWS"]["secret_access_key"],
    )
    return dynamodb.Table("portfolios")


# ── Helper: float → Decimal ───────────────────────────────────────────────────
#
# DynamoDB rejects Python floats. We convert to Decimal before saving.
# ROUND_HALF_UP with 10 decimal places preserves enough precision
# for any realistic stock price.
#
def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(
        Decimal("0.0000000001"), rounding=ROUND_HALF_UP
    )


# ── Helper: Decimal → float ───────────────────────────────────────────────────
#
# When we load data back from DynamoDB, numbers come back as Decimal.
# Python and pandas work with float, so we convert back.
#
def _from_decimal(value) -> float:
    return float(value) if isinstance(value, Decimal) else value


# ── SAVE one portfolio entry ──────────────────────────────────────────────────
def save_entry(user_id: str, ticker: str, date: str,
               price: float, shares: int, amount: float) -> bool:
    """
    Saves a single stock purchase to DynamoDB.

    Parameters:
        user_id : Firebase UID of the logged-in user
        ticker  : stock symbol e.g. "AAPL"
        date    : purchase date as string e.g. "2026-03-13"
        price   : price per share at purchase
        shares  : number of shares purchased
        amount  : total amount invested (price × shares)

    Returns True on success, False on failure.

    HOW put_item WORKS:
    If an item with the same user_id + entry_id already exists,
    it gets overwritten. If not, a new item is created.
    This is called an "upsert" — update or insert.
    """
    try:
        table    = _get_table()
        entry_id = f"{ticker.upper()}#{date}"   # e.g. "AAPL#2026-03-13"

        table.put_item(Item={
            "user_id":  user_id,
            "entry_id": entry_id,
            "ticker":   ticker.upper(),
            "date":     date,
            "price":    _to_decimal(price),
            "shares":   shares,
            "amount":   _to_decimal(amount),
        })
        return True

    except Exception as e:
        st.error(f"Failed to save to database: {e}")
        return False


# ── LOAD all entries for a user ───────────────────────────────────────────────
def load_portfolio(user_id: str) -> list:
    """
    Loads all stock entries for a given user from DynamoDB.

    Returns a list of dicts — same format as st.session_state["portfolio"].

    HOW query WORKS:
    Unlike scan() which reads the entire table (slow and expensive),
    query() uses the partition key to jump directly to that user's
    data. This is O(1) regardless of how many total users exist.
    That's why partition key design matters so much in DynamoDB.
    """
    try:
        table    = _get_table()
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )

        items = response.get("items", response.get("Items", []))

        # Convert Decimals back to float for use in Python/pandas
        portfolio = []
        for item in items:
            portfolio.append({
                "ticker":     item["ticker"],
                "date":       item["date"],
                "price":      _from_decimal(item["price"]),
                "num_stocks": int(item["shares"]),
                "amount":     _from_decimal(item["amount"]),
            })

        return portfolio

    except Exception as e:
        st.error(f"Failed to load portfolio: {e}")
        return []


# ── DELETE one entry ──────────────────────────────────────────────────────────
def delete_entry(user_id: str, ticker: str, date: str) -> bool:
    """
    Deletes a single stock entry from the portfolio.

    To delete in DynamoDB you must provide BOTH keys —
    the partition key (user_id) AND the sort key (entry_id).
    You can't delete by partition key alone.
    """
    try:
        table    = _get_table()
        entry_id = f"{ticker.upper()}#{date}"

        table.delete_item(Key={
            "user_id":  user_id,
            "entry_id": entry_id,
        })
        return True

    except Exception as e:
        st.error(f"Failed to delete entry: {e}")
        return False


# ── CLEAR entire portfolio for a user ─────────────────────────────────────────
def clear_portfolio(user_id: str) -> bool:
    """
    Deletes ALL entries for a user — used for "reset portfolio".

    DynamoDB has no "delete all where user_id = X" command.
    We must:
      1. Query all items for the user
      2. Delete each one individually

    For large portfolios this would use batch_writer() for efficiency,
    but for a personal app with <100 entries, looping is fine.
    """
    try:
        table    = _get_table()
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        items = response.get("items", response.get("Items", []))

        for item in items:
            table.delete_item(Key={
                "user_id":  item["user_id"],
                "entry_id": item["entry_id"],
            })
        return True

    except Exception as e:
        st.error(f"Failed to clear portfolio: {e}")
        return False