import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
st.write("✅ Connected to:", st.secrets["SHEET_URL"])
# ---------------- CONFIG ----------------
st.set_page_config(page_title="Inventory App", layout="wide")
SHOP_NAME = "Esquires Aylesbury Central"
st.title(f"🏪 {SHOP_NAME} — Smart Inventory Management")

# ---------------- AUTH ----------------
ADMIN_PASSWORD = st.secrets["PASSWORD"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.auth = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Incorrect password")
    st.stop()

# ---------------- GOOGLE SHEET CONNECTION ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)
spreadsheet_url = st.secrets["SHEET_URL"]
spreadsheet = gc.open_by_url(spreadsheet_url)

# Main inventory sheet
worksheet = spreadsheet.sheet1

# Restock log sheet
try:
    log_sheet = spreadsheet.worksheet("Restock_Log")
except gspread.exceptions.WorksheetNotFound:
    spreadsheet.add_worksheet(title="Restock_Log", rows="100", cols="4")
    log_sheet = spreadsheet.worksheet("Restock_Log")


# ---------------- DATA FUNCTIONS ----------------
def load_inventory():
    """Load inventory data from Google Sheet"""
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame(columns=[
                "Category", "Item", "Quantity", "Reorder_Level",
                "Unit_Price", "Supplier", "Last_Updated"
            ])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame(columns=[
            "Category", "Item", "Quantity", "Reorder_Level",
            "Unit_Price", "Supplier", "Last_Updated"
        ])
    return df


def save_inventory(df):
    """Save inventory data back to Google Sheet"""
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("✅ Inventory updated in Google Sheets!")
    except Exception as e:
        st.error(f"Error saving data: {e}")


def append_restock_log(item, quantity, user):
    """Add a restock entry to the Restock_Log sheet"""
    try:
        log_data = log_sheet.get_all_records()
        log_df = pd.DataFrame(log_data)
    except Exception:
        log_df = pd.DataFrame(columns=["Timestamp", "Item", "Quantity", "User"])

    new_log = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        item, quantity, user
    ]], columns=["Timestamp", "Item", "Quantity", "User"])

    log_df = pd.concat([log_df, new_log], ignore_index=True)
    log_sheet.clear()
    log_sheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())


# ---------------- LOAD DATA ----------------
df = load_inventory()

# ---------------- SIDEBAR: ADD / UPDATE ITEM ----------------
st.sidebar.header("➕ Add / Update Item")

with st.sidebar.form("add_item_form"):
    category = st.text_input("Category")
    item = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    reorder = st.number_input("Reorder Level", min_value=0, step=1)
    price = st.number_input("Unit Price (£)", min_value=0.0, step=0.1)
    supplier = st.text_input("Supplier (optional)")
    add_btn = st.form_submit_button("💾 Add / Update")

if add_btn:
    if item.strip() == "":
        st.sidebar.warning("⚠️ Please enter an item name.")
    else:
        df["Item"] = df["Item"].astype(str)
        existing = df[df["Item"].str.lower() == item.lower()]
        if not existing.empty:
            idx = existing.index[0]
            df.at[idx, "Category"] = category
            df.at[idx, "Quantity"] = quantity
            df.at[idx, "Reorder_Level"] = reorder
            df.at[idx, "Unit_Price"] = price
            df.at[idx, "Supplier"] = supplier
            df.at[idx, "Last_Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.sidebar.info(f"🔁 Updated existing item: {item}")
        else:
            new_row = pd.DataFrame([[
                category, item, quantity, reorder, price, supplier,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ]], columns=[
                "Category", "Item", "Quantity", "Reorder_Level",
                "Unit_Price", "Supplier", "Last_Updated"
            ])
            df = pd.concat([df, new_row], ignore_index=True)
            st.sidebar.success(f"✅ Added new item: {item}")

        save_inventory(df)
        append_restock_log(item, quantity, "Admin")


# ---------------- MAIN SECTION: SEARCH / EDIT ----------------
st.header("🔍 Search and Manage Items")

search = st.text_input("Search by Item Name", placeholder="Type part of the name...")
filtered_df = df[df["Item"].str.contains(search, case=False, na=False)] if search else df.copy()

if filtered_df.empty:
    st.warning("No matching items found.")
else:
    styled = filtered_df.style.apply(
        lambda row: [
            "background-color: #ffcccc" if row.Quantity <= row.Reorder_Level else
            "background-color: #fff3cd" if row.Quantity <= row.Reorder_Level + 2 else
            "" for _ in row
        ],
        axis=1
    )
    st.dataframe(styled)

    if search and not filtered_df.empty:
        selected_item = st.selectbox("Select Item to Edit", filtered_df["Item"].tolist())
        item_data = filtered_df[filtered_df["Item"] == selected_item].iloc[0]

        st.subheader(f"✏️ Update Item — {selected_item}")
        new_qty = st.number_input("New Quantity", min_value=0, value=int(item_data["Quantity"]))
        new_reorder = st.number_input("Reorder Level", min_value=0, value=int(item_data["Reorder_Level"]))
        new_price = st.number_input("Unit Price (£)", min_value=0.0,
                                    value=float(item_data["Unit_Price"]) if not pd.isna(item_data["Unit_Price"]) else 0.0)
        new_supplier = st.text_input("Supplier", value=item_data["Supplier"])

        if st.button("💾 Save Changes"):
            idx = df[df["Item"] == selected_item].index[0]
            df.at[idx, "Quantity"] = new_qty
            df.at[idx, "Reorder_Level"] = new_reorder
            df.at[idx, "Unit_Price"] = new_price
            df.at[idx, "Supplier"] = new_supplier
            df.at[idx, "Last_Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_inventory(df)
            append_restock_log(selected_item, new_qty, "Admin")

        if st.button("❌ Delete Item"):
            df = df[df["Item"] != selected_item]
            save_inventory(df)
            st.warning(f"🗑️ Deleted item: {selected_item}")


# ---------------- LOW STOCK ALERT ----------------
st.header("⚠️ Low Stock Items")

df["Total_Value"] = df["Quantity"] * df["Unit_Price"]
low_stock = df[df["Quantity"] <= df["Reorder_Level"]]

if low_stock.empty:
    st.success("🎉 All items sufficiently stocked!")
else:
    st.error("⚠️ The following items are below reorder level:")
    st.dataframe(low_stock[["Category", "Item", "Quantity", "Reorder_Level", "Supplier"]])
    whatsapp_msg = "Low Stock Alert%0A" + "%0A".join(
        [f"{row['Item']} - Qty: {row['Quantity']} (Reorder at {row['Reorder_Level']})"
         for _, row in low_stock.iterrows()]
    )
    st.markdown(f"[📱 Send WhatsApp Notification](https://wa.me/?text={whatsapp_msg})")


# ---------------- REPORTS ----------------
st.header("📊 Inventory Summary")

if not df.empty:
    total_items = len(df)
    total_value = df["Total_Value"].sum()
    st.metric("Total Items", total_items)
    st.metric("Total Stock Value (£)", f"{total_value:,.2f}")

st.download_button(
    "⬇️ Download Full Inventory (CSV)",
    data=df.to_csv(index=False),
    file_name="inventory_backup.csv"
)
