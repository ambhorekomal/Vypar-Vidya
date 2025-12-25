"""
Final corrected script to add realistic sample data
- Fixed price order bug
- Added rate limiting
- Added progress tracking
"""
import datetime
import time
from sheets_manager import SheetsManager
import config

def add_sale_with_retry(sheets, date, item, quantity, selling_price, cost_price, customer, gst_rate, max_retries=3):
    """Add sale with retry logic and rate limiting"""
    for attempt in range(max_retries):
        try:
            success = sheets.add_sale(date, item, quantity, selling_price, cost_price, customer, gst_rate)
            if success:
                # Small delay to avoid rate limits
                time.sleep(0.5)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"    Retry {attempt + 1}/{max_retries}...")
                time.sleep(2)  # Wait longer on retry
            else:
                print(f"    Failed after {max_retries} attempts: {e}")
    return False

def add_expense_with_retry(sheets, date, category, description, amount, payment, max_retries=3):
    """Add expense with retry logic"""
    for attempt in range(max_retries):
        try:
            success = sheets.add_expense(date, category, description, amount, payment)
            if success:
                time.sleep(0.5)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def add_final_data():
    """Add realistic sample data with proper values"""

    print("="*60)
    print("  VYAPAR VIDYA - REALISTIC SAMPLE DATA GENERATOR")
    print("="*60)
    print("\nMake sure you've cleared existing data first!")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")

    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return

    print("\nConnecting to Google Sheets...")

    try:
        sheets = SheetsManager()
        print("Connected successfully!\n")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Define products: (Name, Cost Price, Selling Price, Initial Stock)
    products = [
        ("Red Kurti", 800, 1500, 50),
        ("Blue Kurti", 750, 1400, 45),
        ("Green Kurti", 800, 1500, 40),
        ("Pink Saree", 1500, 2800, 30),
        ("Blue Saree", 1400, 2600, 35),
        ("Yellow Saree", 1600, 3000, 25),
        ("Lipstick", 150, 300, 100),
        ("Sindoor", 50, 120, 80),
        ("Bindi Pack", 20, 50, 120),
        ("Bangles Set", 80, 200, 90),
        ("Gold Bangles", 300, 650, 40),
        ("Jhumka Earrings", 250, 550, 60),
        ("Necklace Set", 500, 1100, 30),
        ("Silk Dupatta", 400, 850, 45),
        ("Cotton Dupatta", 200, 450, 50),
    ]

    # Define customers
    customers = [
        ("Mrs. Sharma", "9876543210", "sharma@example.com", "Sector 15, Rohini, Delhi"),
        ("Priya Singh", "9123456789", "priya@example.com", "Nehru Nagar, Andheri, Mumbai"),
        ("Anita Desai", "9234567890", "anita@example.com", "MG Road, Bangalore"),
        ("Rekha Gupta", "9345678901", "rekha@example.com", "Park Street, Kolkata"),
        ("Sunita Verma", "9456789012", "sunita@example.com", "Banjara Hills, Hyderabad"),
        ("Meena Patel", "9567890123", "meena@example.com", "Satellite, Ahmedabad"),
        ("Kavita Reddy", "9678901234", "kavita@example.com", "Anna Nagar, Chennai"),
        ("Pooja Joshi", "9789012345", "pooja@example.com", "Koramangala, Bangalore"),
        ("Lakshmi Iyer", "9890123456", "lakshmi@example.com", "T Nagar, Chennai"),
        ("Deepa Rao", "9901234567", "deepa@example.com", "Indira Nagar, Bangalore"),
    ]

    # ===================== ADD INVENTORY =====================
    print("1/4 Adding Inventory...")
    for idx, (item, cost, selling, stock) in enumerate(products, 1):
        success, _, _ = sheets.add_or_update_inventory(item, stock, cost)
        status = "OK" if success else "FAIL"
        print(f"  [{idx:2d}/15] {status} | {item:20s} | Stock: {stock:3d} | Cost: Rs.{cost:4d} | Sell: Rs.{selling:4d}")
        time.sleep(0.5)  # Rate limiting

    # ===================== ADD CUSTOMERS =====================
    print("\n2/4 Adding Customers...")
    for idx, (name, phone, email, address) in enumerate(customers, 1):
        success = sheets.add_or_update_customer(name, phone, email, address)
        status = "OK" if success else "FAIL"
        print(f"  [{idx:2d}/10] {status} | {name}")
        time.sleep(0.5)

    # ===================== ADD EXPENSES =====================
    print("\n3/4 Adding Expenses...")
    today = datetime.date.today()

    # Monthly fixed expenses
    monthly_expenses = [
        ("Rent", "Shop rent - December", 15000, "Bank Transfer", 5),
        ("Utilities", "Electricity bill", 3500, "UPI", 6),
        ("Utilities", "Water bill", 800, "Cash", 6),
        ("Utilities", "Internet & Phone", 1200, "UPI", 6),
        ("Salaries", "Shop assistant salary", 12000, "Bank Transfer", 5),
        ("Salaries", "Helper wages", 8000, "Cash", 5),
    ]

    expense_count = 0
    for category, description, amount, payment, days_ago in monthly_expenses:
        expense_date = (today - datetime.timedelta(days=days_ago)).strftime(config.DATE_FORMAT)
        success = add_expense_with_retry(sheets, expense_date, category, description, amount, payment)
        expense_count += 1
        status = "OK" if success else "FAIL"
        print(f"  [{expense_count:2d}] {status} | {description:30s} | Rs.{amount:6,.0f}")

    # Variable expenses
    variable_expenses = [
        ("Transportation", "Auto fare", 600, "Cash", 28),
        ("Transportation", "Petrol", 1300, "Cash", 20),
        ("Transportation", "Delivery charges", 800, "UPI", 12),
        ("Office Supplies", "Packing materials", 500, "Cash", 25),
        ("Office Supplies", "Bills book", 180, "Cash", 15),
        ("Maintenance", "Shop cleaning", 350, "Cash", 22),
        ("Marketing", "Facebook ads", 1500, "UPI", 18),
        ("Maintenance", "AC servicing", 2500, "Cash", 25),
        ("Marketing", "Banner printing", 1800, "UPI", 20),
    ]

    for category, description, amount, payment, days_ago in variable_expenses:
        expense_date = (today - datetime.timedelta(days=days_ago)).strftime(config.DATE_FORMAT)
        success = add_expense_with_retry(sheets, expense_date, category, description, amount, payment)
        expense_count += 1
        status = "OK" if success else "FAIL"
        print(f"  [{expense_count:2d}] {status} | {description:30s} | Rs.{amount:6,.0f}")

    # ===================== ADD SALES =====================
    print("\n4/4 Adding Sales (this may take a minute)...")

    # Sales patterns: (Item, Customer, Quantity, Days Ago)
    sales_patterns = [
        # Week 1
        ("Red Kurti", "Mrs. Sharma", 2, 28),
        ("Lipstick", "Priya Singh", 3, 28),
        ("Bangles Set", "Anita Desai", 2, 27),
        ("Blue Saree", "Rekha Gupta", 1, 26),
        ("Sindoor", "Sunita Verma", 2, 26),
        ("Jhumka Earrings", "Meena Patel", 1, 25),
        ("Green Kurti", "Kavita Reddy", 1, 24),
        ("Bindi Pack", "Pooja Joshi", 4, 24),
        ("Silk Dupatta", "Lakshmi Iyer", 2, 23),
        ("Cotton Dupatta", "Deepa Rao", 1, 22),
        # Week 2
        ("Pink Saree", "Mrs. Sharma", 1, 21),
        ("Lipstick", "Anita Desai", 5, 21),
        ("Gold Bangles", "Priya Singh", 2, 20),
        ("Red Kurti", "Sunita Verma", 3, 19),
        ("Necklace Set", "Rekha Gupta", 1, 19),
        ("Blue Kurti", "Meena Patel", 2, 18),
        ("Bangles Set", "Kavita Reddy", 3, 17),
        ("Yellow Saree", "Pooja Joshi", 1, 17),
        ("Silk Dupatta", "Lakshmi Iyer", 1, 16),
        ("Jhumka Earrings", "Deepa Rao", 2, 15),
        # Week 3
        ("Red Kurti", "Mrs. Sharma", 2, 14),
        ("Blue Saree", "Priya Singh", 2, 14),
        ("Lipstick", "Anita Desai", 4, 13),
        ("Pink Saree", "Rekha Gupta", 1, 13),
        ("Green Kurti", "Sunita Verma", 2, 12),
        ("Bangles Set", "Meena Patel", 4, 12),
        ("Gold Bangles", "Kavita Reddy", 1, 11),
        ("Sindoor", "Pooja Joshi", 3, 11),
        ("Bindi Pack", "Lakshmi Iyer", 5, 10),
        ("Necklace Set", "Deepa Rao", 2, 10),
        ("Cotton Dupatta", "Mrs. Sharma", 2, 9),
        ("Jhumka Earrings", "Priya Singh", 1, 8),
        # Week 4
        ("Blue Kurti", "Anita Desai", 3, 7),
        ("Yellow Saree", "Rekha Gupta", 1, 7),
        ("Lipstick", "Sunita Verma", 6, 6),
        ("Red Kurti", "Meena Patel", 2, 6),
        ("Silk Dupatta", "Kavita Reddy", 3, 5),
        ("Bangles Set", "Pooja Joshi", 2, 5),
        ("Pink Saree", "Lakshmi Iyer", 1, 4),
        ("Sindoor", "Deepa Rao", 2, 4),
        ("Green Kurti", "Mrs. Sharma", 1, 3),
        ("Gold Bangles", "Priya Singh", 2, 3),
        ("Bindi Pack", "Anita Desai", 3, 2),
        ("Cotton Dupatta", "Rekha Gupta", 2, 2),
        ("Necklace Set", "Sunita Verma", 1, 1),
        ("Blue Saree", "Meena Patel", 1, 1),
    ]

    sales_count = 0
    failed_sales = []

    for idx, (item_name, customer_name, quantity, days_ago) in enumerate(sales_patterns, 1):
        # Find product
        product = next((p for p in products if p[0] == item_name), None)
        if not product:
            print(f"  [{idx:2d}/46] SKIP | Product not found: {item_name}")
            continue

        item, cost, selling, _ = product
        sale_date = (today - datetime.timedelta(days=days_ago)).strftime(config.DATE_FORMAT)

        # GST based on product type
        gst_rate = 5 if any(x in item for x in ["Kurti", "Saree", "Dupatta"]) else 18

        # Add sale with retry
        success = add_sale_with_retry(
            sheets, sale_date, item, quantity,
            selling, cost, customer_name, gst_rate  # CORRECT ORDER: selling, cost
        )

        if success:
            sales_count += 1
            sheets.update_inventory_stock(item, quantity)
            status = "OK"
        else:
            status = "FAIL"
            failed_sales.append(item_name)

        print(f"  [{idx:2d}/46] {status} | {item:20s} x{quantity} | Sell: Rs.{selling:4d} | Cost: Rs.{cost:4d}")

    # ===================== SUMMARY =====================
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)

    profit_data = sheets.get_profit()

    print(f"\nInventory Items:   15")
    print(f"Customers:         10")
    print(f"Expenses Added:    {expense_count}")
    print(f"Sales Added:       {sales_count}/46")
    if failed_sales:
        print(f"Failed Sales:      {len(failed_sales)}")

    print(f"\n{'Revenue:':<20} Rs.{profit_data['revenue']:>12,.2f}")
    print(f"{'COGS:':<20} Rs.{profit_data['cost']:>12,.2f}")
    print(f"{'Gross Profit:':<20} Rs.{(profit_data['revenue'] - profit_data['cost']):>12,.2f}")
    print(f"{'Expenses:':<20} Rs.{profit_data['expenses']:>12,.2f}")
    print(f"{'-'*40}")
    print(f"{'NET PROFIT:':<20} Rs.{profit_data['profit']:>12,.2f}")

    if profit_data['revenue'] > 0:
        gross_margin = ((profit_data['revenue'] - profit_data['cost']) / profit_data['revenue']) * 100
        net_margin = (profit_data['profit'] / profit_data['revenue']) * 100
        print(f"\n{'Gross Margin:':<20} {gross_margin:>11.1f}%")
        print(f"{'Net Margin:':<20} {net_margin:>11.1f}%")

    print("\n" + "="*60)
    print("  DONE! Run: streamlit run app.py")
    print("="*60)

if __name__ == "__main__":
    add_final_data()
