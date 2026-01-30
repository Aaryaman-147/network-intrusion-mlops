import streamlit as st
import pandas as pd
import requests
import time
import os
import numpy as np

# --- Configuration ---
# In the cloud, both run on the same server, so we use localhost
API_URL = "http://localhost:8000/predict"
# Data is now in the same folder
DATA_PATH = "traffic_data.csv"

st.set_page_config(
    page_title="CyberGuard AI Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- Functions ---
@st.cache_data
def load_data():
    """Loads the dataset from the local file."""
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ File not found: {DATA_PATH}")
        return None
        
    try:
        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def get_prediction(features):
    try:
        response = requests.post(API_URL, json={"features": features})
        if response.status_code == 200:
            return response.json()
        else:
            return {"prediction": "Error", "details": f"Status {response.status_code}"}
    except Exception as e:
        return {"prediction": "Error", "details": str(e)}

# --- Sidebar ---
st.sidebar.title("🛡️ CyberGuard AI")
st.sidebar.markdown("Cloud Deployment")
st.sidebar.write("✅ **System Status:** Online")
st.sidebar.write("🤖 **Model:** Random Forest v7")

# --- Main Interface ---
st.title("🚨 Live Network Traffic Monitor")

df = load_data()

if df is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📊 Traffic Sample Loaded: {len(df)} packets")
    
    # --- Simulation Controls ---
    st.markdown("### 🕵️ Traffic Simulator")
    col_btn1, col_btn2 = st.columns(2)
    
    sample = None
    with col_btn1:
        if st.button("🎲 Simulate Random Packet", use_container_width=True):
            sample = df.sample(1)
    
    with col_btn2:
        if st.button("⚠️ Simulate DDoS Attack", use_container_width=True):
            # Check for attacks in the sample file
            if 'Label' in df.columns:
                attacks = df[df['Label'] != 'BENIGN']
                if not attacks.empty:
                    sample = attacks.sample(1)
                else:
                    st.warning("No attack examples in this sample file!")
                    # Fallback to random if no attacks found in sample
                    sample = df.sample(1)
            else:
                st.warning("Label column missing, using random sample.")
                sample = df.sample(1)

    # --- Processing ---
    if sample is not None:
        # Handle cases where Label might not exist in the small sample csv
        if 'Label' in sample.columns:
            actual_label = sample['Label'].values[0]
            features = sample.drop('Label', axis=1).to_dict(orient='records')[0]
        else:
            actual_label = "Unknown"
            features = sample.to_dict(orient='records')[0]
        
        with st.spinner("🔍 Scanning packet payload..."):
            time.sleep(0.5)
            result = get_prediction(features)
        
        st.markdown("---")
        
        pred_label = result.get('prediction', 'Error')
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            if pred_label == "BENIGN":
                st.success("## ✅ SAFE")
            elif pred_label == "DDoS":
                st.error("## 🚨 THREAT DETECTED")
            else:
                st.warning(f"## ⚠️ ERROR")
                st.write(f"Details: {result.get('details', 'Unknown')}")
        
        with c2:
            st.subheader("Analysis Report")
            m1, m2, m3 = st.columns(3)
            m1.metric("Predicted Status", pred_label)
            m2.metric("Actual Label", actual_label)
            m3.metric("Confidence", "High")
            
            st.markdown("### 📦 Packet Details")
            st.json(features, expanded=False)