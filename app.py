"""
Vyapar Vidya - Voice-First Financial Assistant for MSMEs
Frontend Application (Streamlit)
"""
import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import backend modules
import config
from sheets_manager import SheetsManager
from ai_helper import AIHelper

# ===================== PAGE CONFIG =====================

st.set_page_config(
    page_title="Vyapar Vidya - Smart Finance Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== INITIALIZE SERVICES =====================

@st.cache_resource
def init_services():
    """Initialize backend services (cached)"""
    # Validate configuration
    warnings = config.validate_config()
    for warning in warnings:
        st.sidebar.warning(f"⚠️ {warning}")

    try:
        sheets_manager = SheetsManager()
        ai_helper = AIHelper()
        return sheets_manager, ai_helper, None
    except Exception as e:
        return None, None, str(e)

sheets_manager, ai_helper, error = init_services()

if error:
    st.error(f"❌ Failed to initialize services: {error}")
    st.stop()

# ===================== SIDEBAR NAVIGATION =====================

st.sidebar.title("💼 Vyapar Vidya")
st.sidebar.caption("Smart Finance Assistant")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📊 Dashboard", "💰 Sales", "📦 Inventory", "💸 Expenses", "👥 Customers", "📈 Reports", "💡 Insights"]
)

st.sidebar.divider()
st.sidebar.caption(f"Today: {datetime.date.today().strftime('%d %b %Y')}")

# ===================== VALIDATION HELPERS =====================

def validate_sale_data(data):
    """Validate sale data"""
    if not data.get("item"):
        return False, "Item name is required"
    if not data.get("quantity") or data.get("quantity") <= 0:
        return False, "Valid quantity is required"
    if not data.get("selling_price") or data.get("selling_price") <= 0:
        return False, "Valid selling price is required"
    return True, "Valid"

def validate_inventory_data(data):
    """Validate inventory data"""
    if not data.get("item"):
        return False, "Item name is required"
    if not data.get("quantity") or data.get("quantity") <= 0:
        return False, "Valid quantity is required"
    return True, "Valid"

def validate_expense_data(data):
    """Validate expense data"""
    if not data.get("amount") or data.get("amount") <= 0:
        return False, "Valid amount is required"
    if not data.get("description"):
        return False, "Description is required"
    return True, "Valid"

# ===================== PAGE: HOME =====================

if page == "🏠 Home":
    st.title("💼 Vyapar Vidya - Voice-First Finance Assistant")
    st.markdown("### Transform your business conversations into financial insights")

    # Natural language input
    user_input = st.text_area(
        "💬 Tell me about your business activity",
        placeholder="Examples:\n- Sold 2 kurtis to Mrs. Sharma for ₹1500 each\n- Received delivery: 20 lipsticks, ₹150 each\n- Paid electricity bill ₹5000\n- How much profit did I make this month?",
        height=100
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit_btn = st.button("🚀 Submit", use_container_width=True, type="primary")

    if submit_btn and user_input:
        with st.spinner("Processing..."):
            # Parse message with AI
            data = ai_helper.parse_message(user_input)

            if not data:
                st.error("❌ Could not understand your input. Please try again.")
                st.stop()

            intent = data.get("intent")
            today = datetime.date.today().strftime(config.DATE_FORMAT)

            # Handle different intents
            if intent == "sale":
                is_valid, message = validate_sale_data(data)
                if not is_valid:
                    st.error(f"❌ {message}")
                    st.stop()

                # Add sale
                gst_rate = data.get("gst_rate", config.DEFAULT_GST_RATE)
                success = sheets_manager.add_sale(
                    today,
                    data.get("item"),
                    data.get("quantity"),
                    data.get("selling_price"),
                    data.get("cost_price", 0),
                    data.get("customer", ""),
                    gst_rate
                )

                if success:
                    # Update inventory
                    sheets_manager.update_inventory_stock(data.get("item"), data.get("quantity"))

                    # Add/update customer
                    if data.get("customer"):
                        sheets_manager.add_or_update_customer(data.get("customer"))

                    # Calculate details
                    quantity = data.get("quantity")
                    selling_price = data.get("selling_price")
                    cost_price = data.get("cost_price", 0)
                    gst_amount = (selling_price * quantity * gst_rate) / 100
                    total_amount = (selling_price * quantity) + gst_amount
                    profit = (selling_price - cost_price) * quantity if cost_price else 0

                    st.success("✅ Sale recorded successfully!")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Items Sold", quantity)
                    col2.metric("Subtotal", f"{config.CURRENCY}{selling_price * quantity:.2f}")
                    col3.metric(f"GST ({gst_rate}%)", f"{config.CURRENCY}{gst_amount:.2f}")
                    col4.metric("Total", f"{config.CURRENCY}{total_amount:.2f}")
                    if cost_price:
                        st.info(f"💰 Profit: {config.CURRENCY}{profit:.2f}")

            elif intent == "inventory_add":
                is_valid, message = validate_inventory_data(data)
                if not is_valid:
                    st.error(f"❌ {message}")
                    st.stop()

                # Add/update inventory
                success, new_stock, old_stock = sheets_manager.add_or_update_inventory(
                    data.get("item"),
                    data.get("quantity"),
                    data.get("cost_price", 0)
                )

                if success:
                    st.success("✅ Inventory updated successfully!")
                    if old_stock > 0:
                        st.info(f"📦 {data.get('item')}: {old_stock} → {new_stock} units")
                    else:
                        st.info(f"📦 New item added: {data.get('item')} ({new_stock} units)")

            elif intent == "expense":
                is_valid, message = validate_expense_data(data)
                if not is_valid:
                    st.error(f"❌ {message}")
                    st.stop()

                # Suggest category if not provided
                category = data.get("category") or ai_helper.suggest_category(data.get("description", ""))
                payment_method = data.get("payment_method", "Cash")

                success = sheets_manager.add_expense(
                    today,
                    category,
                    data.get("description"),
                    data.get("amount"),
                    payment_method
                )

                if success:
                    st.success("✅ Expense recorded successfully!")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Amount", f"{config.CURRENCY}{data.get('amount'):.2f}")
                    col2.metric("Category", category)
                    col3.metric("Payment", payment_method)

            else:  # query
                # Get all data for insights
                sales_df = sheets_manager.get_sales()
                inventory_df = sheets_manager.get_inventory()
                expenses_df = sheets_manager.get_expenses()
                profit_data = sheets_manager.get_profit()

                # Get AI insight
                insight = ai_helper.get_insight(user_input, sales_df, inventory_df, expenses_df, profit_data)
                st.info(f"💡 {insight}")

    # Quick stats
    st.divider()
    st.subheader("📊 Quick Overview")

    profit_data = sheets_manager.get_profit()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Revenue", f"{config.CURRENCY}{profit_data['revenue']:,.2f}")
    with col2:
        st.metric("💸 Expenses", f"{config.CURRENCY}{profit_data['expenses']:,.2f}")
    with col3:
        profit_color = "normal" if profit_data['profit'] >= 0 else "inverse"
        st.metric("📈 Profit", f"{config.CURRENCY}{profit_data['profit']:,.2f}")
    with col4:
        margin = (profit_data['profit'] / profit_data['revenue'] * 100) if profit_data['revenue'] > 0 else 0
        st.metric("📊 Margin", f"{margin:.1f}%")

# ===================== PAGE: DASHBOARD =====================

elif page == "📊 Dashboard":
    st.title("📊 Business Dashboard")

    # Financial metrics
    profit_data = sheets_manager.get_profit()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue", f"{config.CURRENCY}{profit_data['revenue']:,.2f}")
    with col2:
        st.metric("🏭 Cost of Goods", f"{config.CURRENCY}{profit_data['cost']:,.2f}")
    with col3:
        st.metric("💸 Operating Expenses", f"{config.CURRENCY}{profit_data['expenses']:,.2f}")
    with col4:
        profit_delta = profit_data['profit']
        delta_color = "normal" if profit_delta >= 0 else "inverse"
        st.metric("📈 Net Profit", f"{config.CURRENCY}{profit_data['profit']:,.2f}")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Sales trend
        st.subheader("📈 Sales Trend")
        sales_df = sheets_manager.get_sales()
        if not sales_df.empty and "Date" in sales_df.columns and "Total Amount" in sales_df.columns:
            daily_sales = sales_df.groupby("Date")["Total Amount"].sum().reset_index()
            fig = px.line(daily_sales, x="Date", y="Total Amount", markers=True)
            fig.update_layout(xaxis_title="Date", yaxis_title=f"Revenue ({config.CURRENCY})")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available yet")

    with col2:
        # Top selling items
        st.subheader("🏆 Top Selling Items")
        top_items = sheets_manager.get_top_selling_items(5)
        if not top_items.empty:
            fig = px.bar(x=top_items.values, y=top_items.index, orientation='h')
            fig.update_layout(xaxis_title="Number of Sales", yaxis_title="Item")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available yet")

    # Expense breakdown
    st.subheader("💸 Expense Breakdown")
    expenses_df = sheets_manager.get_expenses()
    if not expenses_df.empty and "Category" in expenses_df.columns and "Amount" in expenses_df.columns:
        expense_by_category = expenses_df.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(expense_by_category, values="Amount", names="Category")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available yet")

    # Low stock alerts
    st.divider()
    st.subheader("⚠️ Low Stock Alerts")
    low_stock = sheets_manager.get_low_stock_items(5)
    if not low_stock.empty:
        st.warning(f"⚠️ {len(low_stock)} items are running low on stock!")
        st.dataframe(low_stock, use_container_width=True)
    else:
        st.success("✅ All items are well-stocked")

# ===================== PAGE: SALES =====================

elif page == "💰 Sales":
    st.title("💰 Sales Management")

    tab1, tab2 = st.tabs(["➕ Add Sale", "📋 View Sales"])

    with tab1:
        st.subheader("Record New Sale")

        with st.form("sale_form"):
            col1, col2 = st.columns(2)

            with col1:
                item = st.text_input("Item Name*", placeholder="e.g., Red Kurti")
                quantity = st.number_input("Quantity*", min_value=1, value=1)
                selling_price = st.number_input(f"Selling Price per unit ({config.CURRENCY})*", min_value=0.0, step=0.01)

            with col2:
                customer = st.text_input("Customer Name", placeholder="e.g., Mrs. Sharma")
                cost_price = st.number_input(f"Cost Price per unit ({config.CURRENCY})", min_value=0.0, step=0.01)
                gst_rate = st.selectbox("GST Rate", list(config.GST_RATES.keys()), index=3)

            submitted = st.form_submit_button("💾 Record Sale", use_container_width=True, type="primary")

            if submitted:
                if not item or quantity <= 0 or selling_price <= 0:
                    st.error("❌ Please fill all required fields")
                else:
                    today = datetime.date.today().strftime(config.DATE_FORMAT)
                    gst_value = config.GST_RATES[gst_rate]

                    success = sheets_manager.add_sale(
                        today, item, quantity, selling_price, cost_price, customer, gst_value
                    )

                    if success:
                        sheets_manager.update_inventory_stock(item, quantity)
                        if customer:
                            sheets_manager.add_or_update_customer(customer)

                        st.success("✅ Sale recorded successfully!")
                        st.rerun()

    with tab2:
        st.subheader("Sales History")
        sales_df = sheets_manager.get_sales()

        if not sales_df.empty:
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                if "Item" in sales_df.columns:
                    items = ["All"] + sales_df["Item"].unique().tolist()
                    selected_item = st.selectbox("Filter by Item", items)
            with col2:
                if "Customer" in sales_df.columns:
                    customers = ["All"] + sales_df["Customer"].dropna().unique().tolist()
                    selected_customer = st.selectbox("Filter by Customer", customers)

            # Apply filters
            filtered_df = sales_df.copy()
            if selected_item != "All":
                filtered_df = filtered_df[filtered_df["Item"] == selected_item]
            if selected_customer != "All":
                filtered_df = filtered_df[filtered_df["Customer"] == selected_customer]

            st.dataframe(filtered_df, use_container_width=True)

            # Summary
            if not filtered_df.empty and "Total Amount" in filtered_df.columns:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Transactions", len(filtered_df))
                col2.metric("Total Revenue", f"{config.CURRENCY}{filtered_df['Total Amount'].sum():,.2f}")
                if "Quantity" in filtered_df.columns:
                    col3.metric("Total Items Sold", f"{int(filtered_df['Quantity'].sum())}")
        else:
            st.info("No sales recorded yet. Start by adding your first sale!")

# ===================== PAGE: INVENTORY =====================

elif page == "📦 Inventory":
    st.title("📦 Inventory Management")

    tab1, tab2 = st.tabs(["➕ Add Stock", "📋 View Inventory"])

    with tab1:
        st.subheader("Add New Stock")

        with st.form("inventory_form"):
            col1, col2 = st.columns(2)

            with col1:
                item = st.text_input("Item Name*", placeholder="e.g., Lipsticks")
                quantity = st.number_input("Quantity*", min_value=1, value=1)

            with col2:
                cost_price = st.number_input(f"Cost Price per unit ({config.CURRENCY})", min_value=0.0, step=0.01)

            submitted = st.form_submit_button("📦 Add to Inventory", use_container_width=True, type="primary")

            if submitted:
                if not item or quantity <= 0:
                    st.error("❌ Please fill all required fields")
                else:
                    success, new_stock, old_stock = sheets_manager.add_or_update_inventory(
                        item, quantity, cost_price
                    )

                    if success:
                        if old_stock > 0:
                            st.success(f"✅ Stock updated! {item}: {old_stock} → {new_stock} units")
                        else:
                            st.success(f"✅ New item added! {item}: {new_stock} units")
                        st.rerun()

    with tab2:
        st.subheader("Current Inventory")
        inventory_df = sheets_manager.get_inventory()

        if not inventory_df.empty:
            # Add stock status
            if "Stock" in inventory_df.columns:
                inventory_df["Status"] = inventory_df["Stock"].apply(
                    lambda x: "🔴 Low" if x < 5 else "🟡 Medium" if x < 20 else "🟢 Good"
                )

            st.dataframe(inventory_df, use_container_width=True)

            # Summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Items", len(inventory_df))
            if "Stock" in inventory_df.columns:
                col2.metric("Total Units", f"{int(inventory_df['Stock'].sum())}")
                low_stock = len(inventory_df[inventory_df["Stock"] < 5])
                col3.metric("Low Stock Items", low_stock, delta=None if low_stock == 0 else "⚠️")
        else:
            st.info("No inventory recorded yet. Start by adding your first item!")

# ===================== PAGE: EXPENSES =====================

elif page == "💸 Expenses":
    st.title("💸 Expense Tracking")

    tab1, tab2 = st.tabs(["➕ Add Expense", "📋 View Expenses"])

    with tab1:
        st.subheader("Record New Expense")

        with st.form("expense_form"):
            col1, col2 = st.columns(2)

            with col1:
                amount = st.number_input(f"Amount ({config.CURRENCY})*", min_value=0.0, step=0.01)
                category = st.selectbox("Category*", [
                    "Rent", "Utilities", "Salaries", "Transportation",
                    "Marketing", "Office Supplies", "Maintenance", "Other"
                ])

            with col2:
                description = st.text_input("Description*", placeholder="e.g., Monthly electricity bill")
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "UPI", "Card"])

            submitted = st.form_submit_button("💾 Record Expense", use_container_width=True, type="primary")

            if submitted:
                if amount <= 0 or not description:
                    st.error("❌ Please fill all required fields")
                else:
                    today = datetime.date.today().strftime(config.DATE_FORMAT)
                    success = sheets_manager.add_expense(today, category, description, amount, payment_method)

                    if success:
                        st.success("✅ Expense recorded successfully!")
                        st.rerun()

    with tab2:
        st.subheader("Expense History")
        expenses_df = sheets_manager.get_expenses()

        if not expenses_df.empty:
            # Filters
            if "Category" in expenses_df.columns:
                categories = ["All"] + expenses_df["Category"].unique().tolist()
                selected_category = st.selectbox("Filter by Category", categories)

                if selected_category != "All":
                    filtered_df = expenses_df[expenses_df["Category"] == selected_category]
                else:
                    filtered_df = expenses_df

                st.dataframe(filtered_df, use_container_width=True)

                # Summary
                if not filtered_df.empty and "Amount" in filtered_df.columns:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Expenses", len(filtered_df))
                    col2.metric("Total Amount", f"{config.CURRENCY}{filtered_df['Amount'].sum():,.2f}")
                    col3.metric("Average Expense", f"{config.CURRENCY}{filtered_df['Amount'].mean():,.2f}")
        else:
            st.info("No expenses recorded yet. Start by adding your first expense!")

# ===================== PAGE: CUSTOMERS =====================

elif page == "👥 Customers":
    st.title("👥 Customer Management")

    tab1, tab2, tab3 = st.tabs(["➕ Add Customer", "📋 View Customers", "🏆 Top Customers"])

    with tab1:
        st.subheader("Add New Customer")

        with st.form("customer_form"):
            name = st.text_input("Customer Name*", placeholder="e.g., Mrs. Sharma")
            phone = st.text_input("Phone Number", placeholder="e.g., 9876543210")
            email = st.text_input("Email", placeholder="e.g., customer@example.com")
            address = st.text_area("Address", placeholder="Enter customer address")

            submitted = st.form_submit_button("👤 Add Customer", use_container_width=True, type="primary")

            if submitted:
                if not name:
                    st.error("❌ Customer name is required")
                else:
                    success = sheets_manager.add_or_update_customer(name, phone, email, address)
                    if success:
                        st.success("✅ Customer added successfully!")
                        st.rerun()

    with tab2:
        st.subheader("All Customers")
        customers_df = sheets_manager.get_customers()

        if not customers_df.empty:
            st.dataframe(customers_df, use_container_width=True)
            st.metric("Total Customers", len(customers_df))
        else:
            st.info("No customers recorded yet. Customers are automatically added when you record sales!")

    with tab3:
        st.subheader("🏆 Top Customers by Purchase Value")
        top_customers = sheets_manager.get_top_customers(10)

        if not top_customers.empty:
            # Create bar chart
            fig = px.bar(
                x=top_customers.values,
                y=top_customers.index,
                orientation='h',
                labels={'x': f'Total Purchase ({config.CURRENCY})', 'y': 'Customer'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show table
            top_df = pd.DataFrame({
                'Customer': top_customers.index,
                'Total Purchase': [f"{config.CURRENCY}{val:,.2f}" for val in top_customers.values]
            })
            st.dataframe(top_df, use_container_width=True)
        else:
            st.info("No customer purchase data available yet")

# ===================== PAGE: REPORTS =====================

elif page == "📈 Reports":
    st.title("📈 Financial Reports")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("To Date", datetime.date.today())

    st.divider()

    # Profit & Loss Statement
    st.subheader("💰 Profit & Loss Statement")
    profit_data = sheets_manager.get_profit()

    pl_data = {
        "Category": ["Revenue", "Cost of Goods Sold", "Gross Profit", "Operating Expenses", "Net Profit"],
        "Amount": [
            profit_data['revenue'],
            profit_data['cost'],
            profit_data['revenue'] - profit_data['cost'],
            profit_data['expenses'],
            profit_data['profit']
        ]
    }
    pl_df = pd.DataFrame(pl_data)
    pl_df["Amount"] = pl_df["Amount"].apply(lambda x: f"{config.CURRENCY}{x:,.2f}")

    st.table(pl_df)

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Revenue vs Expenses")
        fig = go.Figure(data=[
            go.Bar(name='Revenue', x=['Total'], y=[profit_data['revenue']], marker_color='green'),
            go.Bar(name='Expenses', x=['Total'], y=[profit_data['expenses']], marker_color='red'),
            go.Bar(name='Profit', x=['Total'], y=[profit_data['profit']], marker_color='blue')
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 Cost Breakdown")
        breakdown_data = {
            'Category': ['Cost of Goods', 'Operating Expenses', 'Profit'],
            'Amount': [profit_data['cost'], profit_data['expenses'], profit_data['profit']]
        }
        fig = px.pie(breakdown_data, values='Amount', names='Category')
        st.plotly_chart(fig, use_container_width=True)

    # Download reports
    st.divider()
    st.subheader("📥 Download Reports")

    col1, col2, col3 = st.columns(3)

    with col1:
        sales_df = sheets_manager.get_sales()
        if not sales_df.empty:
            csv = sales_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Sales Report",
                data=csv,
                file_name=f"sales_report_{datetime.date.today()}.csv",
                mime="text/csv"
            )

    with col2:
        expenses_df = sheets_manager.get_expenses()
        if not expenses_df.empty:
            csv = expenses_df.to_csv(index=False)
            st.download_button(
                label="💸 Download Expenses Report",
                data=csv,
                file_name=f"expenses_report_{datetime.date.today()}.csv",
                mime="text/csv"
            )

    with col3:
        inventory_df = sheets_manager.get_inventory()
        if not inventory_df.empty:
            csv = inventory_df.to_csv(index=False)
            st.download_button(
                label="📦 Download Inventory Report",
                data=csv,
                file_name=f"inventory_report_{datetime.date.today()}.csv",
                mime="text/csv"
            )

# ===================== PAGE: INSIGHTS =====================

elif page == "💡 Insights":
    st.title("💡 Business Insights & Recommendations")

    # Get data
    profit_data = sheets_manager.get_profit()
    low_stock_items = sheets_manager.get_low_stock_items(5)
    top_items = sheets_manager.get_top_selling_items(5)

    # AI-powered business advice
    st.subheader("🤖 AI-Powered Business Advice")

    with st.spinner("Analyzing your business data..."):
        advice = ai_helper.get_business_advice(profit_data, low_stock_items, top_items)
        st.info(advice)

    st.divider()

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Net Profit", f"{config.CURRENCY}{profit_data['profit']:,.2f}")

    with col2:
        margin = (profit_data['profit'] / profit_data['revenue'] * 100) if profit_data['revenue'] > 0 else 0
        st.metric("📊 Profit Margin", f"{margin:.1f}%")

    with col3:
        st.metric("⚠️ Low Stock Items", len(low_stock_items))

    # Insights cards
    st.divider()
    st.subheader("📌 Quick Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Best Performers")
        if not top_items.empty:
            for idx, (item, count) in enumerate(top_items.head(3).items(), 1):
                st.markdown(f"**{idx}. {item}** - {int(count)} sales")
        else:
            st.info("No sales data yet")

    with col2:
        st.markdown("### ⚠️ Needs Attention")
        if not low_stock_items.empty:
            for idx, row in low_stock_items.head(3).iterrows():
                st.warning(f"📦 **{row['Item']}** - Only {int(row['Stock'])} units left")
        else:
            st.success("✅ All items well-stocked!")

    # Ask AI
    st.divider()
    st.subheader("💬 Ask AI About Your Business")

    question = st.text_input("Ask a question", placeholder="e.g., What can I do to increase profits?")

    if st.button("🔍 Get Answer"):
        if question:
            sales_df = sheets_manager.get_sales()
            inventory_df = sheets_manager.get_inventory()
            expenses_df = sheets_manager.get_expenses()

            with st.spinner("Thinking..."):
                answer = ai_helper.get_insight(question, sales_df, inventory_df, expenses_df, profit_data)
                st.success(answer)

# ===================== FOOTER =====================

st.sidebar.divider()
st.sidebar.caption("Made with ❤️ for MSMEs")
st.sidebar.caption("Powered by AI")
