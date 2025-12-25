
# 💼 Vyapar Vidya – Voice-First Financial Assistant for MSMEs

Vyapar Vidya is a natural-language financial assistant designed for women-led small businesses.  
It converts everyday business language into structured financial records and actionable insights using AI.

---

## 🚀 Features

- Natural language sales & inventory tracking  
- Automatic financial calculations  
- Google Sheets as a transparent backend  
- AI-powered financial insights  
- No accounting knowledge required  

---

## 🛠 Tech Stack

- **Frontend**: Streamlit  
- **AI**: Groq (LLaMA 3.1)  
- **Database**: Google Sheets  
- **Backend**: Python  

---

## 📂 Project Structure

```

vyapar-vidya/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── credentials.json   (not committed to GitHub)

````

---

## 🔑 Prerequisites

- Python 3.9 or above  
- Google account  
- Groq API key  

---

## 🔐 Step 1: Get Groq API Key

1. Go to 👉 https://console.groq.com/keys  
2. Create a new API key  
3. Open `app.py`  
4. Paste the key here:

```python
groq_client = Groq(
    api_key="gsk_YOUR_API_KEY"
)
````

---

## 📊 Step 2: Google Sheets Setup



### 2.1 Create Google Sheet

Create a new Google Sheet with **3 tabs**:

#### Sheet 1: Sales

| Date | Item | Quantity | Selling Price | Cost Price | Customer |

#### Sheet 2: Inventory

| Item | Stock | Cost Price |

#### Sheet 3: Summary

| Metric | Value |

---

### 2.2 Enable Google Sheets API

1. Go to 👉 [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. Open **APIs & Services → Library**
4. Search and enable **Google Sheets API**

---

### 2.3 Create Service Account

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Name: `vyapar-vidya-bot`
4. Role: **Editor**
5. Create a **JSON key**
6. Download and rename it to:

```
credentials.json
```

Place this file in the same folder as `app.py`.

---

### 2.4 Share Google Sheet with Service Account

1. Open `credentials.json`
2. Copy the value of `client_email`
3. Open your Google Sheet
4. Click **Share**
5. Paste the email and give **Editor access**

---

### 2.5 Add Sheet ID to Code

From your sheet URL:

```
https://docs.google.com/spreadsheets/d/XXXXXX/edit
```

Copy `XXXXXX` and paste into `app.py`:

```python
SHEET_ID = "XXXXXX"
```

---

## ▶️ Step 3: Install & Run the App

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

---

## 🧪 Demo Inputs (Use These)

### Inventory Inputs

```
Received delivery: 20 lipsticks, ₹150 each
Received delivery: 10 red kurtis, ₹800 each
```

### Sales Inputs

```
Sold 2 red kurtis to Mrs. Sharma for ₹1500 each
Sold 1 saree to Anita for ₹3200
```

### Financial Insights

```
How much did I earn this week?
What's my best-selling item?
How much inventory do I have?
```

---

## 🧑‍⚖️ Judge-Friendly Explanation

> *Vyapar Vidya helps informal businesses become financially visible by turning daily conversations into structured financial data.*

---

## 🔒 Security Note

* `credentials.json` is excluded using `.gitignore`
* API keys are hardcoded **only for demo purposes**
* In production, secrets should be stored using environment variables

---

## 📌 Future Scope

* Voice input
* GST calculations
* Loan readiness score
* WhatsApp integration

---

