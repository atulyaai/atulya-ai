#!/usr/bin/env python3
"""
Atulya AI Web UI
Simple Streamlit interface
"""

import streamlit as st
import requests
import json

st.set_page_config(page_title="Atulya AI", layout="wide")

st.title("🧠 Atulya AI - Dynamic Intelligence System")

# Simple chat interface
user_input = st.text_input("Ask me anything:", key="user_input")

if st.button("Send"):
    if user_input:
        try:
            response = requests.post("http://localhost:8000/chat", 
                                   json={"message": user_input, "user_id": "web_user"})
            if response.status_code == 200:
                result = response.json()
                st.write("**Response:**", result.get("response", "No response"))
            else:
                st.error("Error connecting to API")
        except:
            st.error("Cannot connect to Atulya AI server")

# Status
if st.button("Check Status"):
    try:
        response = requests.get("http://localhost:8000/status")
        if response.status_code == 200:
            status = response.json()
            st.success(f"✅ Server Status: {status.get('status', 'Unknown')}")
        else:
            st.error("❌ Server not responding")
    except:
        st.error("❌ Cannot connect to server") 