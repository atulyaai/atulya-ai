"""
Atulya AI - User Frontend (v0.1.0)
Clean, simple chat interface for end users
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="Atulya AI - Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for user frontend
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #9c27b0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online {
        background-color: #4caf50;
    }
    .status-offline {
        background-color: #f44336;
    }
    .admin-link {
        position: fixed;
        top: 10px;
        right: 10px;
        background-color: #ff9800;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        text-decoration: none;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_message(message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Send a chat message to the API"""
    try:
        payload = {
            "message": message,
            "user_id": user_id
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def reset_session():
    """Reset the current session"""
    try:
        response = requests.post(f"{API_BASE_URL}/reset", timeout=5)
        if response.status_code == 200:
            st.success("Session reset successfully!")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to reset session: {e}")

def main():
    """Main user frontend"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Atulya AI</h1>', unsafe_allow_html=True)
    
    # Admin link
    st.markdown('<a href="http://localhost:8502" target="_blank" class="admin-link">⚙️ Admin</a>', unsafe_allow_html=True)
    
    # Check API health
    api_online = check_api_health()
    if not api_online:
        st.error("❌ API server is not running. Please contact your administrator.")
        st.info("💡 The system administrator can start the services using the admin panel.")
        return
    
    # Status indicator
    status_color = "status-online" if api_online else "status-offline"
    status_text = "Online" if api_online else "Offline"
    st.markdown(f'<span class="status-indicator {status_color}"></span>System: {status_text}', 
               unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Hello! I'm Atulya AI, your intelligent assistant. How can I help you today?"
        })
    
    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><strong>Atulya AI:</strong> {message["content"]}</div>', 
                           unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    # Input area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_area(
            "💬 Ask me anything...",
            height=100,
            placeholder="Type your message here...",
            key=f"user_input_{st.session_state.input_key}"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)
    
    # Handle send button
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            response = send_chat_message(user_input.strip(), st.session_state.user_id)
            
            if response.get("success", False):
                ai_response = response.get("response", "I'm sorry, I couldn't process your request.")
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            else:
                error_msg = response.get("error", "Failed to get response from API")
                st.error(f"❌ Error: {error_msg}")
        
        # Increment input key to clear the text area
        st.session_state.input_key += 1
        
        # Rerun to update the display and clear input
        st.rerun()
    
    # Chat controls
    st.markdown("---")
    
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col4:
        if st.button("🔄 Reset Session"):
            reset_session()
    
    with col5:
        if st.button("💾 Save Chat"):
            if st.session_state.messages:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.txt"
                
                chat_content = ""
                for msg in st.session_state.messages:
                    chat_content += f"{msg['role'].upper()}: {msg['content']}\n\n"
                
                st.download_button(
                    label="📥 Download",
                    data=chat_content,
                    file_name=filename,
                    mime="text/plain"
                )
    
    with col6:
        if st.button("❓ Help"):
            st.info("""
            **How to use Atulya AI:**
            
            • Simply type your questions or requests in the text area
            • Click "Send" or press Enter to get a response
            • Use "Clear Chat" to start a new conversation
            • Use "Reset Session" to clear your session data
            • Use "Save Chat" to download your conversation
            
            **Need admin access?** Click the "⚙️ Admin" button in the top right.
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        <p>🧠 Atulya AI v0.1.0 | Built with ❤️ by Atul Vij</p>
        <p>For technical support, contact your system administrator</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 