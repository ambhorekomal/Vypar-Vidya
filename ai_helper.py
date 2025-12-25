"""
AI-powered natural language processing and insights
"""
import json
from groq import Groq
import pandas as pd
import config

logger = config.get_logger(__name__)

class AIHelper:
    """Handles all AI-powered features"""

    def __init__(self):
        """Initialize Groq client"""
        try:
            self.client = Groq(api_key=config.GROQ_API_KEY)
            logger.info("Groq AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

    def parse_message(self, text):
        """Parse user message and extract intent and data"""
        prompt = f"""
You are a finance assistant for small shop owners in India.

Extract intent and information from the message below.
Return ONLY valid JSON without any markdown formatting or code blocks.

Message:
"{text}"

Possible intents:
- sale: When user mentions selling items (keywords: sold, sale, customer bought)
- inventory_add: When user mentions receiving stock/delivery (keywords: received, delivery, purchased stock)
- expense: When user mentions spending money on business expenses (keywords: paid, expense, spent, bill)
- query: When user asks questions about earnings, inventory, expenses, or sales

JSON fields to extract (use null for missing values):
- intent: one of [sale, inventory_add, expense, query]
- item: name of the product (string)
- quantity: number of units (number)
- selling_price: price per unit sold (number, for sales only)
- cost_price: cost per unit (number)
- customer: customer name (string, for sales only)
- gst_rate: GST percentage if mentioned (number, default 18 for sales)
- category: expense category (string, for expenses only)
- description: expense description (string, for expenses only)
- amount: expense amount (number, for expenses only)
- payment_method: payment method (string, for expenses only)

Examples:

Input: "Sold 2 red kurtis to Mrs. Sharma for ₹1500 each"
Output: {{"intent": "sale", "item": "red kurtis", "quantity": 2, "selling_price": 1500, "cost_price": null, "customer": "Mrs. Sharma", "gst_rate": 18, "category": null, "description": null, "amount": null, "payment_method": null}}

Input: "Received delivery: 20 lipsticks, ₹150 each"
Output: {{"intent": "inventory_add", "item": "lipsticks", "quantity": 20, "selling_price": null, "cost_price": 150, "customer": null, "gst_rate": null, "category": null, "description": null, "amount": null, "payment_method": null}}

Input: "Paid electricity bill ₹5000"
Output: {{"intent": "expense", "item": null, "quantity": null, "selling_price": null, "cost_price": null, "customer": null, "gst_rate": null, "category": "Utilities", "description": "electricity bill", "amount": 5000, "payment_method": "Cash"}}

Input: "How much did I earn this week?"
Output: {{"intent": "query", "item": null, "quantity": null, "selling_price": null, "cost_price": null, "customer": null, "gst_rate": null, "category": null, "description": null, "amount": null, "payment_method": null}}

Return ONLY the JSON object for the message above.
"""

        try:
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"AI response: {content}")

            # Handle markdown code blocks
            if content.startswith("```"):
                content = content.strip("`").strip()
                if content.startswith("json"):
                    content = content[4:].strip()

            parsed_data = json.loads(content)
            logger.info(f"Parsed data: {parsed_data}")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, Response: {content}")
            return None
        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            return None

    def get_insight(self, user_query, sales_df, inventory_df, expenses_df, profit_data):
        """Generate AI-powered insights based on business data"""
        # Prepare data summary
        sales_summary = self._summarize_sales(sales_df)
        inventory_summary = self._summarize_inventory(inventory_df)
        expenses_summary = self._summarize_expenses(expenses_df)
        financial_summary = self._summarize_financials(profit_data)

        prompt = f"""
You are a helpful financial advisor for small business owners in India.

User question: "{user_query}"

Business Data:

Sales Summary:
{sales_summary}

Inventory Summary:
{inventory_summary}

Expenses Summary:
{expenses_summary}

Financial Summary:
{financial_summary}

Provide a clear, actionable answer in 2-4 sentences. Use rupee (₹) symbol for money.
Be encouraging and supportive. If the data shows problems (low profit, high expenses),
suggest practical solutions. If the data shows success, congratulate them.
"""

        try:
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "Sorry, I couldn't generate insights at the moment."

    def get_business_advice(self, profit_data, low_stock_items, top_items):
        """Generate business advice based on current metrics"""
        prompt = f"""
You are a business consultant for small businesses in India.

Analyze this business data and provide 3 specific, actionable recommendations:

Financial Metrics:
- Revenue: ₹{profit_data['revenue']:.2f}
- Total Cost: ₹{profit_data['cost']:.2f}
- Expenses: ₹{profit_data['expenses']:.2f}
- Net Profit: ₹{profit_data['profit']:.2f}
- Profit Margin: {(profit_data['profit'] / profit_data['revenue'] * 100) if profit_data['revenue'] > 0 else 0:.1f}%

Low Stock Items: {len(low_stock_items)} items need restocking

Top Selling Items: {', '.join(top_items.index.tolist()[:3]) if not top_items.empty else 'None yet'}

Provide 3 specific recommendations to improve the business. Each should be:
1. Actionable (something they can do this week)
2. Specific to their data
3. Focused on increasing profit or reducing costs

Format as a numbered list.
"""

        try:
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Business advice generation failed: {e}")
            return "Unable to generate advice at the moment."

    # ===================== HELPER METHODS =====================

    def _summarize_sales(self, sales_df):
        """Create sales summary text"""
        if sales_df.empty:
            return "No sales recorded yet."

        total_sales = len(sales_df)
        if "Total Amount" in sales_df.columns:
            total_revenue = sales_df["Total Amount"].sum()
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0
            summary = f"Total sales: {total_sales} transactions, Revenue: ₹{total_revenue:.2f}, Avg sale: ₹{avg_sale:.2f}"
        else:
            summary = f"Total sales: {total_sales} transactions"

        if "Item" in sales_df.columns:
            top_item = sales_df["Item"].value_counts().idxmax()
            summary += f"\nTop selling item: {top_item}"

        return summary

    def _summarize_inventory(self, inventory_df):
        """Create inventory summary text"""
        if inventory_df.empty:
            return "No inventory recorded yet."

        total_items = len(inventory_df)
        if "Stock" in inventory_df.columns:
            total_stock = inventory_df["Stock"].sum()
            summary = f"Total inventory: {total_items} different items, {total_stock:.0f} total units"

            low_stock = inventory_df[inventory_df["Stock"] < 5]
            if not low_stock.empty:
                summary += f"\nWarning: {len(low_stock)} items low on stock"
        else:
            summary = f"Total inventory: {total_items} different items"

        return summary

    def _summarize_expenses(self, expenses_df):
        """Create expenses summary text"""
        if expenses_df.empty:
            return "No expenses recorded yet."

        total_expenses = len(expenses_df)
        if "Amount" in expenses_df.columns:
            total_amount = expenses_df["Amount"].sum()
            avg_expense = total_amount / total_expenses if total_expenses > 0 else 0
            summary = f"Total expenses: {total_expenses} entries, Amount: ₹{total_amount:.2f}, Avg: ₹{avg_expense:.2f}"

            if "Category" in expenses_df.columns:
                top_category = expenses_df.groupby("Category")["Amount"].sum().idxmax()
                summary += f"\nHighest expense category: {top_category}"
        else:
            summary = f"Total expenses: {total_expenses} entries"

        return summary

    def _summarize_financials(self, profit_data):
        """Create financial summary text"""
        summary = f"""Revenue: ₹{profit_data['revenue']:.2f}
Cost of Goods: ₹{profit_data['cost']:.2f}
Operating Expenses: ₹{profit_data['expenses']:.2f}
Net Profit: ₹{profit_data['profit']:.2f}"""

        if profit_data['revenue'] > 0:
            margin = (profit_data['profit'] / profit_data['revenue']) * 100
            summary += f"\nProfit Margin: {margin:.1f}%"

        return summary

    def suggest_category(self, description):
        """Suggest expense category based on description"""
        categories = {
            "rent": "Rent",
            "electricity": "Utilities",
            "water": "Utilities",
            "internet": "Utilities",
            "phone": "Utilities",
            "salary": "Salaries",
            "wages": "Salaries",
            "transport": "Transportation",
            "fuel": "Transportation",
            "advertising": "Marketing",
            "marketing": "Marketing",
            "stationery": "Office Supplies",
            "repair": "Maintenance",
            "maintenance": "Maintenance"
        }

        description_lower = description.lower()
        for keyword, category in categories.items():
            if keyword in description_lower:
                return category

        return "Other"
