import streamlit as st
import datetime
import pandas as pd
import json
from groq import Groq

from google.oauth2 import service_account
from googleapiclient.discovery import build

# ===================== CONFIG =====================

groq_client = Groq(
    api_key="gsk_YOUR_GROQ_API_KEY_HERE"
)

SHEET_ID = "YOUR_GOOGLE_SHEET_ID"

creds = service_account.Credentials.from_service_account_file(
    "credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

sheets = build("sheets", "v4", credentials=creds).spreadsheets()

# ===================== GOOGLE SHEETS HELPERS =====================

def append_row(sheet_name, values):
    sheets.values().append(
        spreadsheetId=SHEET_ID,
        range=sheet_name,
        valueInputOption="USER_ENTERED",
        body={"values": [values]}
    ).execute()

def read_sheet(sheet_name):
    result = sheets.values().get(
        spreadsheetId=SHEET_ID,
        range=sheet_name
    ).execute()

    values = result.get("values", [])
    if len(values) < 2:
        return pd.DataFrame()

    return pd.DataFrame(values[1:], columns=values[0])

# ===================== GROQ NLP =====================

def parse_message(text):
    prompt = f"""
You are a finance assistant for small shop owners.

Extract intent and information from the message below.
Return ONLY valid JSON.

Message:
"{text}"

Possible intents:
- sale
- inventory_add
- query

JSON fields:
intent, item, quantity, selling_price, cost_price, customer
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        st.error("❌ AI response not valid JSON")
        return None

# ===================== STREAMLIT UI =====================

st.title("💼 Vyapar Vidya – Smart Finance Assistant")

user_input = st.text_input("💬 Speak or type your business update")

if st.button("Submit") and user_input:
    data = parse_message(user_input)
    if not data:
        st.stop()

    today = str(datetime.date.today())

    if data["intent"] == "sale":
        append_row(
            "Sales",
            [
                today,
                data.get("item"),
                data.get("quantity"),
                data.get("selling_price"),
                data.get("cost_price"),
                data.get("customer")
            ]
        )
        st.success("✅ Sale recorded")

    elif data["intent"] == "inventory_add":
        append_row(
            "Inventory",
            [
                data.get("item"),
                data.get("quantity"),
                data.get("cost_price")
            ]
        )
        st.success("📦 Inventory updated")

    else:
        sales_df = read_sheet("Sales")
        inventory_df = read_sheet("Inventory")

        if not sales_df.empty:
            sales_df["Selling Price"] = pd.to_numeric(
                sales_df["Selling Price"], errors="coerce"
            ).fillna(0)

        if not inventory_df.empty:
            inventory_df["Stock"] = pd.to_numeric(
                inventory_df["Stock"], errors="coerce"
            ).fillna(0)

        if "week" in user_input.lower() and not sales_df.empty:
            st.info(f"💰 Weekly earnings: ₹{sales_df['Selling Price'].sum()}")

        elif "best" in user_input.lower() and not sales_df.empty:
            st.info(f"🏆 Best-selling item: {sales_df['Item'].value_counts().idxmax()}")

        elif "inventory" in user_input.lower() and not inventory_df.empty:
            st.info(f"📦 Inventory units available: {inventory_df['Stock'].sum()}")

# ===================== DASHBOARD =====================

st.divider()
st.subheader("📊 Quick Dashboard")

sales_df = read_sheet("Sales")
inventory_df = read_sheet("Inventory")

if not sales_df.empty:
    sales_df["Selling Price"] = pd.to_numeric(
        sales_df["Selling Price"], errors="coerce"
    ).fillna(0)
    st.metric("Total Sales", f"₹{sales_df['Selling Price'].sum()}")

if not inventory_df.empty:
    inventory_df["Stock"] = pd.to_numeric(
        inventory_df["Stock"], errors="coerce"
    ).fillna(0)
    st.metric("Inventory Units", inventory_df["Stock"].sum())
