import streamlit as st
import pandas as pd
import os

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

st.set_page_config(page_title="Shop Inventory Tracker", layout="wide")

DATA_FILE = "inventory.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Item", "Quantity", "Reorder_Level"])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

def save_data(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

def add_item(name, quantity, reorder_level):
    global df
    new_row = pd.DataFrame([[name, quantity, reorder_level]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

def update_stock(item, new_quantity):
    global df
    df.loc[df["Item"] == item, "Quantity"] = new_quantity
    save_data(df)

st.title("📦 Shop Inventory Tracker")

menu = st.sidebar.radio("Menu", ["View Inventory", "Add Item", "Update Stock", "Low Stock Report"])

if menu == "View Inventory":
    st.subheader("Current Inventory")
    st.dataframe(df)

elif menu == "Add Item":
    st.subheader("Add New Item")
    name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    reorder_level = st.number_input("Reorder Level", min_value=0, step=1)

    if st.button("Add Item"):
        if name:
            add_item(name, quantity, reorder_level)
            st.success(f"✅ Added '{name}' to inventory.")
        else:
            st.warning("Please enter an item name.")

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

elif menu == "Low Stock Report":
    st.subheader("⚠️ Low Stock Items")
    low_stock = df[df["Quantity"] <= df["Reorder_Level"]]
    if low_stock.empty:
        st.success("🎉 All items are sufficiently stocked.")
    else:
        st.dataframe(low_stock)
        csv = low_stock.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Low Stock List (CSV)", data=csv, file_name="low_stock_items.csv")
        list_text = "\n".join([f"{r.Item} (Qty: {r.Quantity})" for r in low_stock.itertuples()])
        st.text_area("Low Stock List", value=list_text, height=200)
