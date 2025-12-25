"""
Google Sheets integration and data management
"""
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

logger = config.get_logger(__name__)

class SheetsManager:
    """Manages all Google Sheets operations"""

    def __init__(self):
        """Initialize Google Sheets connection"""
        self.sheets = None
        self._initialize_sheets()

    def _initialize_sheets(self):
        """Initialize Google Sheets API connection"""
        try:
            creds = service_account.Credentials.from_service_account_file(
                config.CREDENTIALS_FILE,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.sheets = build("sheets", "v4", credentials=creds).spreadsheets()
            logger.info("Google Sheets API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            raise

    # ===================== GENERIC OPERATIONS =====================

    def append_row(self, sheet_name, values):
        """Append a row to the specified sheet"""
        try:
            self.sheets.values().append(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=sheet_name,
                valueInputOption="USER_ENTERED",
                body={"values": [values]}
            ).execute()
            logger.info(f"Appended row to {sheet_name}: {values}")
            return True
        except HttpError as e:
            logger.error(f"Failed to append to {sheet_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in append_row: {e}")
            return False

    def read_sheet(self, sheet_name):
        """Read data from the specified sheet"""
        try:
            result = self.sheets.values().get(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=sheet_name
            ).execute()

            values = result.get("values", [])
            if len(values) < 2:
                return pd.DataFrame()

            df = pd.DataFrame(values[1:], columns=values[0])
            logger.info(f"Read {len(df)} rows from {sheet_name}")
            return df
        except HttpError as e:
            logger.error(f"Failed to read {sheet_name}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error in read_sheet: {e}")
            return pd.DataFrame()

    def update_cell(self, sheet_name, cell_range, value):
        """Update a specific cell"""
        try:
            self.sheets.values().update(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=f"{sheet_name}!{cell_range}",
                valueInputOption="USER_ENTERED",
                body={"values": [[value]]}
            ).execute()
            logger.info(f"Updated {sheet_name}!{cell_range} to {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update cell: {e}")
            return False

    # ===================== SALES OPERATIONS =====================

    def add_sale(self, date, item, quantity, selling_price, cost_price, customer, gst_rate=0):
        """Add a sale record - optimized structure"""
        values = [
            date,
            str(item),
            float(quantity),
            float(cost_price) if cost_price else "",
            float(selling_price),
            str(customer) if customer else "",
            float(gst_rate)
        ]

        return self.append_row(config.SHEET_SALES, values)

    def get_sales(self):
        """Get all sales records with calculated fields"""
        df = self.read_sheet(config.SHEET_SALES)
        if not df.empty and "Selling Price" in df.columns:
            # Convert numeric columns
            numeric_cols = ["Quantity", "Selling Price", "Cost Price", "GST Rate"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            # Calculate derived columns dynamically
            df["GST Amount"] = (df["Selling Price"] * df["Quantity"] * df["GST Rate"]) / 100
            df["Total Amount"] = (df["Selling Price"] * df["Quantity"]) + df["GST Amount"]
        return df

    # ===================== INVENTORY OPERATIONS =====================

    def add_or_update_inventory(self, item, quantity, cost_price):
        """Add new item or update existing inventory"""
        inventory_df = self.read_sheet(config.SHEET_INVENTORY)

        # Check if item exists
        if not inventory_df.empty and "Item" in inventory_df.columns:
            item_exists = any(inventory_df["Item"].str.lower() == item.lower())

            if item_exists:
                # Update existing item
                result = self.sheets.values().get(
                    spreadsheetId=config.GOOGLE_SHEET_ID,
                    range=config.SHEET_INVENTORY
                ).execute()
                values = result.get("values", [])

                for idx, row in enumerate(values[1:], start=2):
                    if len(row) > 0 and row[0].lower() == item.lower():
                        current_stock = float(row[1]) if len(row) > 1 else 0
                        new_stock = current_stock + float(quantity)

                        # Update stock
                        self.update_cell(config.SHEET_INVENTORY, f"B{idx}", new_stock)

                        # Update cost price if provided
                        if cost_price:
                            self.update_cell(config.SHEET_INVENTORY, f"C{idx}", float(cost_price))

                        logger.info(f"Updated inventory: {item} {current_stock} → {new_stock}")
                        return True, new_stock, current_stock

        # Add new item
        return self.append_row(
            config.SHEET_INVENTORY,
            [str(item), float(quantity), float(cost_price) if cost_price else ""]
        ), quantity, 0

    def update_inventory_stock(self, item, quantity_sold):
        """Deduct sold quantity from inventory"""
        try:
            result = self.sheets.values().get(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=config.SHEET_INVENTORY
            ).execute()
            values = result.get("values", [])

            for idx, row in enumerate(values[1:], start=2):
                if len(row) > 0 and row[0].lower() == item.lower():
                    current_stock = float(row[1]) if len(row) > 1 else 0
                    new_stock = current_stock - float(quantity_sold)

                    # Warn if stock goes negative
                    if new_stock < 0:
                        logger.warning(f"⚠️ Stock going negative for {item}: {current_stock} → {new_stock}")

                    self.update_cell(config.SHEET_INVENTORY, f"B{idx}", new_stock)
                    logger.info(f"Deducted inventory: {item} {current_stock} → {new_stock}")
                    return True, new_stock

            logger.warning(f"Item '{item}' not found in inventory - cannot deduct stock")
            return False, 0
        except Exception as e:
            logger.error(f"Failed to update inventory: {e}")
            return False, 0

    def get_inventory(self):
        """Get all inventory records"""
        df = self.read_sheet(config.SHEET_INVENTORY)
        if not df.empty:
            if "Stock" in df.columns:
                df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce").fillna(0)
            if "Cost Price" in df.columns:
                df["Cost Price"] = pd.to_numeric(df["Cost Price"], errors="coerce").fillna(0)
        return df

    # ===================== EXPENSE OPERATIONS =====================

    def add_expense(self, date, category, description, amount, payment_method="Cash"):
        """Add an expense record"""
        values = [
            date,
            str(category),
            str(description),
            float(amount),
            str(payment_method)
        ]
        return self.append_row(config.SHEET_EXPENSES, values)

    def get_expenses(self):
        """Get all expense records"""
        df = self.read_sheet(config.SHEET_EXPENSES)
        if not df.empty and "Amount" in df.columns:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df

    # ===================== CUSTOMER OPERATIONS =====================

    def add_or_update_customer(self, name, phone="", email="", address=""):
        """Add or update customer information"""
        customers_df = self.read_sheet(config.SHEET_CUSTOMERS)

        # Check if customer exists
        if not customers_df.empty and "Name" in customers_df.columns:
            customer_exists = any(customers_df["Name"].str.lower() == name.lower())

            if customer_exists:
                # Update existing customer
                result = self.sheets.values().get(
                    spreadsheetId=config.GOOGLE_SHEET_ID,
                    range=config.SHEET_CUSTOMERS
                ).execute()
                values = result.get("values", [])

                for idx, row in enumerate(values[1:], start=2):
                    if len(row) > 0 and row[0].lower() == name.lower():
                        # Update customer details
                        if phone:
                            self.update_cell(config.SHEET_CUSTOMERS, f"B{idx}", phone)
                        if email:
                            self.update_cell(config.SHEET_CUSTOMERS, f"C{idx}", email)
                        if address:
                            self.update_cell(config.SHEET_CUSTOMERS, f"D{idx}", address)
                        return True

        # Add new customer
        return self.append_row(
            config.SHEET_CUSTOMERS,
            [str(name), str(phone), str(email), str(address)]
        )

    def get_customers(self):
        """Get all customer records"""
        return self.read_sheet(config.SHEET_CUSTOMERS)

    # ===================== ANALYTICS =====================

    def get_total_revenue(self):
        """Calculate total revenue from sales"""
        sales_df = self.get_sales()
        if not sales_df.empty and "Total Amount" in sales_df.columns:
            return sales_df["Total Amount"].sum()
        return 0

    def get_total_expenses(self):
        """Calculate total expenses"""
        expenses_df = self.get_expenses()
        if not expenses_df.empty and "Amount" in expenses_df.columns:
            return expenses_df["Amount"].sum()
        return 0

    def get_profit(self):
        """Calculate profit (Revenue - Cost of Goods Sold - Expenses)"""
        sales_df = self.get_sales()
        total_cost_of_goods_sold = 0
        total_revenue = 0

        if not sales_df.empty:
            # Revenue = Total Amount from all sales (includes GST)
            if "Total Amount" in sales_df.columns:
                total_revenue = sales_df["Total Amount"].sum()

            # Cost of Goods Sold = Sum of (Cost Price × Quantity) for each sale
            if "Cost Price" in sales_df.columns and "Quantity" in sales_df.columns:
                # Only calculate for rows where Cost Price is not empty/zero
                sales_df_copy = sales_df.copy()
                sales_df_copy["COGS"] = sales_df_copy["Cost Price"] * sales_df_copy["Quantity"]
                total_cost_of_goods_sold = sales_df_copy["COGS"].sum()

        total_expenses = self.get_total_expenses()

        # Profit = Revenue - COGS - Operating Expenses
        profit = total_revenue - total_cost_of_goods_sold - total_expenses

        return {
            "revenue": total_revenue,
            "cost": total_cost_of_goods_sold,
            "expenses": total_expenses,
            "profit": profit
        }

    def get_low_stock_items(self, threshold=5):
        """Get items with stock below threshold"""
        inventory_df = self.get_inventory()
        if not inventory_df.empty and "Stock" in inventory_df.columns:
            low_stock = inventory_df[inventory_df["Stock"] < threshold]
            return low_stock
        return pd.DataFrame()

    def get_top_selling_items(self, limit=5):
        """Get top selling items"""
        sales_df = self.get_sales()
        if not sales_df.empty and "Item" in sales_df.columns:
            top_items = sales_df["Item"].value_counts().head(limit)
            return top_items
        return pd.Series()

    def get_top_customers(self, limit=5):
        """Get top customers by total purchase amount"""
        sales_df = self.get_sales()
        if not sales_df.empty and "Customer" in sales_df.columns and "Total Amount" in sales_df.columns:
            customer_totals = sales_df.groupby("Customer")["Total Amount"].sum().sort_values(ascending=False).head(limit)
            return customer_totals
        return pd.Series()
