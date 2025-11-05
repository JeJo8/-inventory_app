import streamlit as st
import pandas as pd
import os
from PIL import Image

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="🏪 Shop Inventory App", layout="wide")

DATA_FILE = "inventory.csv"

# ===============================
# LOGO HEADER
# ===============================
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=100)
    with col2:
        st.title("Esquires Aylesbury Inventory")
else:
    st.title("Esquires Aylesbury Inventory")
st.subheader("JeJo")
# ===============================
# INITIALIZE INVENTORY
# ===============================
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Category", "Item", "Quantity", "Reorder_Level"])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# ===============================
# HELPER FUNCTIONS
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

def delete_item(item):
    global df
    df.drop(df[df["Item"] == item].index, inplace=True)
    save_data(df)

# ===============================
# USER ROLE SELECTION
# ===============================
role = st.sidebar.radio("Select Role", ["Staff - View Only", "Admin"])

if role == "Admin":
    # Password check
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    def password_entered():
        if st.session_state["password_input"] == st.secrets["PASSWORD"]:
            st.session_state.password_correct = True
            del st.session_state["password_input"]
        else:
            st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.text_input("Enter Admin Password:", type="password", key="password_input", on_change=password_entered)
        st.stop()

# ===============================
# MENU
# ===============================
menu = st.sidebar.radio("Menu", ["View Inventory", "Add Item", "Update Stock", "Delete Item", "Low Stock Report"])

# ===============================
# CATEGORY FILTER (Top Only)
# ===============================
categories = df["Category"].unique().tolist()
selected_category = st.selectbox("Filter by Category", ["All"] + categories)

# Apply filter
if selected_category != "All":
    df_filtered = df[df["Category"] == selected_category]
else:
    df_filtered = df.copy()

# -------------------------------
# VIEW INVENTORY
# -------------------------------
if menu == "View Inventory":
    st.subheader("Current Inventory")
    df_display = df_filtered.drop(columns=["Category"])
    st.dataframe(df_display)

# -------------------------------
# ADD ITEM (Admin Only)
# -------------------------------
elif menu == "Add Item":
    if role != "Admin":
        st.warning("⚠️ Only Admin can add new items.")
    else:
        st.subheader("Add New Item")
        cat_options = df["Category"].unique().tolist() + ["Add New Category"]
        category = st.selectbox("Select Category", cat_options)
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
# UPDATE STOCK (Admin Only)
# -------------------------------
elif menu == "Update Stock":
    if role != "Admin":
        st.warning("⚠️ Only Admin can update stock.")
    else:
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
# DELETE ITEM (Admin Only)
# -------------------------------
elif menu == "Delete Item":
    if role != "Admin":
        st.warning("⚠️ Only Admin can delete items.")
    else:
        st.subheader("Delete Item")
        items = df["Item"].tolist()
        if len(items) == 0:
            st.info("No items found to delete.")
        else:
            item_to_delete = st.selectbox("Select Item to Delete", items)
            if st.button("Delete Item"):
                delete_item(item_to_delete)
                st.success(f"✅ '{item_to_delete}' has been deleted.")

# -------------------------------
# LOW STOCK REPORT
# -------------------------------
elif menu == "Low Stock Report":
    st.subheader("⚠️ Low Stock Items")
    low_stock = df_filtered[df_filtered["Quantity"] <= df_filtered["Reorder_Level"]]
    
    if low_stock.empty:
        st.success("🎉 All items are sufficiently stocked.")
    else:
        # Table without Category
        st.dataframe(low_stock.drop(columns=["Category"]))
        
        # CSV download without Category
        csv_data = low_stock.drop(columns=["Category"]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Low Stock List (CSV)", data=csv_data, file_name="low_stock_items.csv")
        
        # Text area still shows Category
        list_text = "\n".join([f"{r.Category} - {r.Item} (Qty: {r.Quantity})" for r in low_stock.itertuples()])
        st.text_area("Low Stock List", value=list_text, height=200)
