# Google Sheets Setup Guide

Complete guide for setting up Google Sheets API and structuring your spreadsheet.

---

# Part 1: Google Cloud & API Setup

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign in with your Google account
3. Click on the project dropdown at the top (next to "Google Cloud")
4. Click **"New Project"**
5. Enter project details:
   - **Project name**: `Vyapar-Vidya` (or any name you prefer)
   - **Organization**: Leave as default (No organization)
6. Click **"Create"**
7. Wait for the project to be created (takes a few seconds)
8. Make sure your new project is selected in the dropdown

---

## Step 2: Enable Google Sheets API

1. In the Google Cloud Console, make sure your project is selected
2. Go to **"APIs & Services"** → **"Library"** (from left sidebar)
   - Or use this direct link: https://console.cloud.google.com/apis/library
3. In the search box, type: `Google Sheets API`
4. Click on **"Google Sheets API"** from the results
5. Click the blue **"Enable"** button
6. Wait for it to enable (takes a few seconds)

---

## Step 3: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"** (from left sidebar)
   - Or use this direct link: https://console.cloud.google.com/apis/credentials
2. Click **"+ Create Credentials"** at the top
3. Select **"Service Account"** from the dropdown
4. Fill in the service account details:
   - **Service account name**: `vyapar-vidya-bot`
   - **Service account ID**: (auto-filled, leave as is)
   - **Description**: `Service account for Vyapar Vidya app`
5. Click **"Create and Continue"**
6. Grant access (optional, you can skip this):
   - Click **"Continue"** (no role needed for basic Sheets access)
7. Grant users access (optional):
   - Click **"Done"** (skip this step)

---

## Step 4: Create and Download JSON Key

1. You should now see your service account in the credentials list
2. Click on the **service account email** (looks like: `vyapar-vidya-bot@project-name.iam.gserviceaccount.com`)
3. Go to the **"Keys"** tab at the top
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** as the key type
6. Click **"Create"**
7. A JSON file will automatically download to your computer
8. **Important**: Rename this file to `credentials.json`
9. Move `credentials.json` to your project folder

---

# Part 2: Google Sheets Structure

## Required Sheets

You need **5 sheets** in your Google Spreadsheet:

### 1. Sales

**Headers (Row 1):**
```
Date | Item | Quantity | Cost Price | Selling Price | Customer | GST Rate
```

**Column Details:**
- `Date` - Transaction date (YYYY-MM-DD)
- `Item` - Product name
- `Quantity` - Number of units sold
- `Cost Price` - Cost per unit (for profit calculation)
- `Selling Price` - Selling price per unit
- `Customer` - Customer name (optional)
- `GST Rate` - GST percentage (e.g., 18 for 18%)

**Note:** GST Amount and Total Amount are calculated automatically by the app, not stored.

---

### 2. Inventory

**Headers (Row 1):**
```
Item | Stock | Cost Price
```

**Column Details:**
- `Item` - Product name
- `Stock` - Current stock quantity
- `Cost Price` - Cost per unit

---

### 3. Expenses

**Headers (Row 1):**
```
Date | Category | Description | Amount | Payment Method
```

**Column Details:**
- `Date` - Expense date (YYYY-MM-DD)
- `Category` - Expense category (Rent, Utilities, Salaries, etc.)
- `Description` - What the expense was for
- `Amount` - Expense amount
- `Payment Method` - Cash, UPI, Bank Transfer, Card

---

### 4. Customers

**Headers (Row 1):**
```
Name | Phone | Email | Address
```

**Column Details:**
- `Name` - Customer name
- `Phone` - Phone number (optional)
- `Email` - Email address (optional)
- `Address` - Customer address (optional)

---

### 5. Summary

**Headers (Row 1):**
```
Metric | Value
```

**Column Details:**
- `Metric` - Name of the metric
- `Value` - Metric value

**Note:** Reserved for future use. Leave empty for now.

---

## Step 5: Create Your Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **"+ Blank"** to create a new spreadsheet
3. Name it: `Vyapar Vidya Data` (or any name you prefer)
4. Create the 5 sheets with headers as shown above:
   - Rename "Sheet1" to "Sales"
   - Click "+" to add: Inventory, Expenses, Customers, Summary
   - Add headers to each sheet

### Example Data:

**Sales Sheet:**
```
Date       | Item      | Quantity | Cost Price | Selling Price | Customer    | GST Rate
2025-12-26 | Red Kurti | 2        | 800        | 1500          | Mrs. Sharma | 5
2025-12-26 | Lipstick  | 5        | 150        | 300           | Anita       | 18
```

**Inventory Sheet:**
```
Item      | Stock | Cost Price
Red Kurti | 10    | 800
Lipstick  | 50    | 150
```

**Expenses Sheet:**
```
Date       | Category  | Description      | Amount | Payment Method
2025-12-26 | Utilities | Electricity Bill | 5000   | UPI
2025-12-25 | Rent      | Shop Rent Dec    | 15000  | Bank Transfer
```

**Customers Sheet:**
```
Name        | Phone      | Email                 | Address
Mrs. Sharma | 9876543210 | sharma@example.com    | Delhi
Anita       | 9123456789 | anita@example.com     | Mumbai
```

---

## Step 6: Share Sheet with Service Account

1. Open your `credentials.json` file in a text editor
2. Find and copy the **"client_email"** value
   - It looks like: `vyapar-vidya-bot@project-name.iam.gserviceaccount.com`
3. Go back to your Google Sheet
4. Click the **"Share"** button (top right)
5. Paste the service account email in the "Add people and groups" field
6. Make sure the permission is set to **"Editor"**
7. **Uncheck** "Notify people" (the service account doesn't need notifications)
8. Click **"Share"** or **"Send"**

---

## Step 7: Get Your Sheet ID

1. Look at your Google Sheet URL in the browser:
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
   ```
2. Copy the ID between `/d/` and `/edit`:
   ```
   1a2b3c4d5e6f7g8h9i0j
   ```

---

## Step 8: Configure Your App

Create a `.env` file in your project folder:

```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_SHEET_ID=your_sheet_id_here
```

**Where to get these:**
- **GROQ_API_KEY**: Get from https://console.groq.com/keys
- **GOOGLE_SHEET_ID**: From Step 7 above

---

## Step 9: Test the Connection

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

3. If everything is set up correctly:
   - No warning messages about placeholder values
   - Dashboard loads without errors

4. Try a test input:
   ```
   Received delivery: 10 pens, ₹5 each
   ```

5. Check your Google Sheet - data should appear in the Inventory tab!

---

## Important Notes

✅ **Case Sensitive:** Sheet names must match exactly (e.g., "Sales" not "sales")

✅ **Header Row:** Always keep row 1 as headers - don't delete it

✅ **Calculated Fields:** The app calculates these automatically:
   - GST Amount = (Selling Price × Quantity × GST Rate) / 100
   - Total Amount = (Selling Price × Quantity) + GST Amount
   - Profit = (Selling Price - Cost Price) × Quantity

---

## Troubleshooting

### Error: "credentials.json not found"
- Make sure the file is in the same folder as `app.py`
- Check the filename is exactly `credentials.json` (not `credentials (1).json`)

### Error: "Failed to read from Google Sheets"
- Verify you shared the sheet with the service account email
- Check that you gave "Editor" permission (not just "Viewer")
- Make sure the SHEET_ID is correct

### Error: "Google Sheets API has not been enabled"
- Go back to Step 2 and enable the API
- Wait a few minutes after enabling before trying again

### Error: "Permission denied"
- The service account email must have "Editor" access to the sheet
- Re-check Step 6

---

## Security Best Practices

1. **Never commit secrets to GitHub**
   - `credentials.json` and `.env` are already in `.gitignore`

2. **Use environment variables**
   - Store API keys in `.env` file, not in code

3. **Restrict service account permissions**
   - Only share specific sheets with the service account
   - Don't give it access to your entire Google Drive

---

## Next Steps

Once connected, you can:
- Record sales, inventory, and expenses
- Track customers and their purchases
- Ask AI questions like "How much profit did I make this month?"
- View comprehensive dashboard with analytics
- Download financial reports

For more help, check the main README.md file.
