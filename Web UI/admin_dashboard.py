"""
Atulya AI - Admin Dashboard (v0.1.0)
Comprehensive system administration interface
"""

import streamlit as st
import requests
import json
import time
import subprocess
import psutil
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Page configuration
st.set_page_config(
    page_title="Atulya AI Admin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for admin dashboard
st.markdown("""
<style>
    .admin-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .status-online {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    .status-offline {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .status-warning {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .control-button {
        margin: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        border: none;
        cursor: pointer;
    }
    .start-button {
        background-color: #4caf50;
        color: white;
    }
    .stop-button {
        background-color: #f44336;
        color: white;
    }
    .restart-button {
        background-color: #ff9800;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used": memory.used // (1024**3),  # GB
            "memory_total": memory.total // (1024**3),  # GB
            "disk_percent": disk.percent,
            "disk_used": disk.used // (1024**3),  # GB
            "disk_total": disk.total // (1024**3),  # GB
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def check_service_status(port: int) -> bool:
    """Check if a service is running on a specific port"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_service(service_name: str) -> bool:
    """Start a service"""
    try:
        if service_name == "api":
            subprocess.Popen([
                "python", "-m", "uvicorn", "main:app",
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd="/root/atulya-ai")
        elif service_name == "webui":
            subprocess.Popen([
                "python", "-m", "streamlit", "run", "Web UI/web_ui.py",
                "--server.port", "8501", "--server.address", "0.0.0.0"
            ], cwd="/root/atulya-ai")
        return True
    except Exception as e:
        st.error(f"Failed to start {service_name}: {e}")
        return False

def stop_service(service_name: str) -> bool:
    """Stop a service"""
    try:
        if service_name == "api":
            subprocess.run(["pkill", "-f", "uvicorn.*main:app"])
        elif service_name == "webui":
            subprocess.run(["pkill", "-f", "streamlit.*web_ui.py"])
        return True
    except Exception as e:
        st.error(f"Failed to stop {service_name}: {e}")
        return False

def get_api_status() -> Dict[str, Any]:
    """Get API status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return response.json()
    except:
        return {}

def get_api_models() -> Dict[str, Any]:
    """Get API models"""
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=5)
        return response.json()
    except:
        return {}

def get_api_tools() -> Dict[str, Any]:
    """Get API tools"""
    try:
        response = requests.get(f"{API_BASE_URL}/tools", timeout=5)
        return response.json()
    except:
        return {}

def get_api_memory() -> Dict[str, Any]:
    """Get API memory"""
    try:
        response = requests.get(f"{API_BASE_URL}/memory", timeout=5)
        return response.json()
    except:
        return {}

def main():
    """Main admin dashboard"""
    
    # Header
    st.markdown('<h1 class="admin-header">⚙️ Atulya AI Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("🔧 Navigation")
        page = st.selectbox(
            "Select Page",
            ["System Overview", "Service Control", "API Management", "System Monitoring", "Logs"]
        )
        
        st.header("🔄 Manual Refresh")
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    if page == "System Overview":
        show_system_overview()
    elif page == "Service Control":
        show_service_control()
    elif page == "API Management":
        show_api_management()
    elif page == "System Monitoring":
        show_system_monitoring()
    elif page == "Logs":
        show_logs()

def show_system_overview():
    """Show system overview"""
    st.header("📊 System Overview")
    
    # Service status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔌 Service Status")
        
        api_status = check_service_status(8000)
        webui_status = check_service_status(8501)
        
        if api_status:
            st.markdown('<div class="status-card status-online">✅ API Server (Port 8000) - Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card status-offline">❌ API Server (Port 8000) - Offline</div>', unsafe_allow_html=True)
        
        if webui_status:
            st.markdown('<div class="status-card status-online">✅ Web UI (Port 8501) - Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card status-offline">❌ Web UI (Port 8501) - Offline</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("💻 System Resources")
        sys_info = get_system_info()
        
        if "error" not in sys_info:
            col2a, col2b = st.columns(2)
            
            with col2a:
                st.metric("CPU Usage", f"{sys_info['cpu_percent']}%")
                st.metric("Memory Usage", f"{sys_info['memory_percent']}%")
            
            with col2b:
                st.metric("Disk Usage", f"{sys_info['disk_percent']}%")
                st.metric("Memory Used", f"{sys_info['memory_used']} GB / {sys_info['memory_total']} GB")
        else:
            st.error(f"Error getting system info: {sys_info['error']}")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🚀 Start All Services", type="primary"):
            start_service("api")
            time.sleep(2)
            start_service("webui")
            st.success("Services started!")
            st.rerun()
    
    with col4:
        if st.button("🛑 Stop All Services"):
            stop_service("api")
            stop_service("webui")
            st.success("Services stopped!")
            st.rerun()
    
    with col5:
        if st.button("🔄 Restart All Services"):
            stop_service("api")
            stop_service("webui")
            time.sleep(2)
            start_service("api")
            time.sleep(2)
            start_service("webui")
            st.success("Services restarted!")
            st.rerun()

def show_service_control():
    """Show service control panel"""
    st.header("🎛️ Service Control")
    
    # API Server Control
    st.subheader("🔌 API Server Control")
    api_status = check_service_status(8000)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if api_status:
            st.success("✅ API Server is running")
        else:
            st.error("❌ API Server is not running")
    
    with col2:
        if not api_status:
            if st.button("🚀 Start API Server", type="primary"):
                start_service("api")
                st.success("API Server starting...")
                time.sleep(3)
                st.rerun()
        else:
            if st.button("🛑 Stop API Server"):
                stop_service("api")
                st.success("API Server stopped!")
                time.sleep(1)
                st.rerun()
    
    with col3:
        if api_status:
            if st.button("🔄 Restart API Server"):
                stop_service("api")
                time.sleep(2)
                start_service("api")
                st.success("API Server restarted!")
                time.sleep(3)
                st.rerun()
    
    # Web UI Control
    st.subheader("🌐 Web UI Control")
    webui_status = check_service_status(8501)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if webui_status:
            st.success("✅ Web UI is running")
        else:
            st.error("❌ Web UI is not running")
    
    with col5:
        if not webui_status:
            if st.button("🚀 Start Web UI", type="primary"):
                start_service("webui")
                st.success("Web UI starting...")
                time.sleep(3)
                st.rerun()
        else:
            if st.button("🛑 Stop Web UI"):
                stop_service("webui")
                st.success("Web UI stopped!")
                time.sleep(1)
                st.rerun()
    
    with col6:
        if webui_status:
            if st.button("🔄 Restart Web UI"):
                stop_service("webui")
                time.sleep(2)
                start_service("webui")
                st.success("Web UI restarted!")
                time.sleep(3)
                st.rerun()

def show_api_management():
    """Show API management"""
    st.header("🔧 API Management")
    
    api_status = check_service_status(8000)
    if not api_status:
        st.error("❌ API Server is not running. Please start it first.")
        return
    
    # API Status
    status = get_api_status()
    if status:
        st.subheader("📊 API Status")
        st.json(status)
    
    # Models
    models = get_api_models()
    if models:
        st.subheader("🤖 Models")
        st.json(models)
    
    # Tools
    tools = get_api_tools()
    if tools:
        st.subheader("🛠️ Tools")
        st.json(tools)
    
    # Memory
    memory = get_api_memory()
    if memory:
        st.subheader("🧠 Memory")
        st.json(memory)

def show_system_monitoring():
    """Show system monitoring"""
    st.header("📈 System Monitoring")
    
    # Real-time metrics
    st.subheader("📊 Real-time Metrics")
    
    # Create a placeholder for metrics
    metrics_placeholder = st.empty()
    
    # Update metrics every 5 seconds
    for i in range(10):
        sys_info = get_system_info()
        
        with metrics_placeholder.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("CPU", f"{sys_info.get('cpu_percent', 0)}%")
            
            with col2:
                st.metric("Memory", f"{sys_info.get('memory_percent', 0)}%")
            
            with col3:
                st.metric("Disk", f"{sys_info.get('disk_percent', 0)}%")
            
            with col4:
                st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
        
        time.sleep(5)

def show_logs():
    """Show system logs"""
    st.header("📋 System Logs")
    
    # Log file viewer
    log_file = st.selectbox(
        "Select Log File",
        ["No logs available"]
    )
    
    if log_file != "No logs available":
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
            st.text_area("Log Content", log_content, height=400)
        except Exception as e:
            st.error(f"Error reading log file: {e}")
    else:
        st.info("No log files found. Logs will appear here when available.")

if __name__ == "__main__":
    main() 