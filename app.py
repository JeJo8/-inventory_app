import streamlit as st
import pandas as pd
import os

# ===============================
# AUTHENTICATION
# ===============================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    def password_entered():
        if st.session_state["password_input"] == st.secrets["PASSWORD"]:
            st.session_state.password_correct = True
            del st.session_state["password_input"]
        else:
            st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.text_input("Enter password:", type="password", key="password_input", on_change=password_entered)
        st.stop()

check_password()

# ===============================
# APP CONFIG
# ===============================
st.set_page_config(page_title="Shop Inventory Tracker", layout="wide")

DATA_FILE = "inventory.csv"

# ===============================
# INITIALIZE DATA
# ===============================
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Category","Item","Quantity","Reorder_Level"])
    df.to_csv(DATA_FILE, index=False)

# Load data
df = pd.read_csv(DATA_FILE)

# ===============================
# FUNCTIONS
# ===============================
def save_data(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

def add_item(category, name, quantity, reorder_level):
    global df
    new_row = pd.DataFrame([[category, name, quantity, reorder_level]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

def update_stock(item, new_quantity):
    global df
    df.loc[df["Item"] == item, "Quantity"] = new_quantity
    save_data(df)

# ===============================
# UI
# ===============================
st.title("📦 Esquires Aylesbury Inventory")
st.subheader("JeJo")

menu = st.sidebar.radio("Menu", ["View Inventory", "Add Item", "Update Stock", "Low Stock Report"])

# -------------------------------
# VIEW INVENTORY
# -------------------------------
if menu == "View Inventory":
    st.subheader("Current Inventory")
    categories = df["Category"].unique().tolist()
    selected_category = st.selectbox("Filter by Category", ["All"] + categories)
    if selected_category != "All":
        df_filtered = df[df["Category"] == selected_category]
    else:
        df_filtered = df.copy()
    st.dataframe(df_filtered)

# -------------------------------
# ADD ITEM
# -------------------------------
elif menu == "Add Item":
    st.subheader("Add New Item")
    
    # Categories selection / new category
    categories = df["Category"].unique().tolist()
    categories.append("Add New Category")
    category = st.selectbox("Select Category", categories)
    if category == "Add New Category":
        category = st.text_input("Enter new category")
    
    name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
    
    if st.button("Add Item"):
        if name and category:
            add_item(category, name, quantity, reorder_level)
            st.success(f"✅ Added '{name}' under '{category}'")
        else:
            st.warning("Please enter both item name and category")

# -------------------------------
# UPDATE STOCK
# -------------------------------
elif menu == "Update Stock":
    st.subheader("Update Item Quantity")
    items = df["Item"].tolist()
    
    if len(items) == 0:
        st.info("No items found. Add some first.")
    else:
        item = st.selectbox("Select Item", items)
        new_qty = st.number_input("New Quantity", min_value=0, step=1)
        if st.button("Update Quantity"):
            update_stock(item, new_qty)
            st.success(f"✅ Updated '{item}' quantity to {new_qty}.")

# -------------------------------
# LOW STOCK REPORT
# -------------------------------
elif menu == "Low Stock Report":
    st.subheader("⚠️ Low Stock Items")
    categories = df["Category"].unique().tolist()
    selected_category = st.selectbox("Filter by Category", ["All"] + categories)
    
    if selected_category != "All":
        df_filtered = df[df["Category"] == selected_category]
    else:
        df_filtered = df.copy()
    
    low_stock = df_filtered[df_filtered["Quantity"] <= df_filtered["Reorder_Level"]]
    if low_stock.empty:
        st.success("🎉 All items are sufficiently stocked.")
    else:
        st.dataframe(low_stock)
        csv = low_stock.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Low Stock List (CSV)", data=csv, file_name="low_stock_items.csv")
        list_text = "\n".join([f"{r.Category} - {r.Item} (Qty: {r.Quantity})" for r in low_stock.itertuples()])
        st.text_area("Low Stock List", value=list_text, height=200)
