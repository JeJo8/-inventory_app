# 📦 Shop Inventory Tracker

A simple Streamlit web app to manage your shop’s inventory and get alerts when stock runs low.

## 🚀 Features
✅ Add new items  
✅ Update stock quantities  
✅ View full inventory  
✅ Highlight low-stock items  
✅ Export low-stock list (CSV or text)  
✅ Password-protected access using Streamlit Secrets  

## 🛠 Setup Instructions

### 1. Clone or Upload to GitHub
```bash
git clone https://github.com/yourusername/inventory_app.git
cd inventory_app
```

### 2. (Optional) Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 3. Deploy on Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select this repo and the `app.py` file
4. In your app’s settings, go to **Secrets** and add:
   ```toml
   PASSWORD = "shopsecure123"
   ```
5. Save and deploy 🚀

Access your app at:
```
https://your-username-streamlit-app.streamlit.app
```
