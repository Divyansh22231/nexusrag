import streamlit as st
import httpx
import os
import json

st.set_page_config(
    page_title="NexusRAG · AI Document Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Dark Theme & Component Styling
st.markdown("""
    <style>
        /* Base page & cleanup */
        .stAppDeployButton { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        header[data-testid="stHeader"] { background: transparent !important; }
        
        /* Clean file uploader */
        [data-testid="stFileUploadDropzone"] small { display: none !important; }
        [data-testid="stFileUploadDropzone"] div[data-testid="stText"] { display: none !important; }
        
        /* Main container layout */
        .main .block-container {
            max-width: 860px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 5rem !important;
        }

        /* Top Header */
        .nexus-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.8rem 1.2rem;
            margin-bottom: 1.8rem;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            backdrop-filter: blur(10px);
        }
        .nexus-header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .nexus-logo-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
        .nexus-title-group {
            display: flex;
            flex-direction: column;
        }
        .nexus-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .nexus-badge {
            font-size: 0.68rem;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 6px;
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.25);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .nexus-subtitle {
            font-size: 0.82rem;
            color: #94a3b8;
            font-weight: 400;
        }
        .nexus-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.76rem;
            font-weight: 500;
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .nexus-status-pill.offline {
            background: rgba(239, 68, 68, 0.1);
            color: #f87171;
            border-color: rgba(239, 68, 68, 0.2);
        }
        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
        }
        .status-dot.offline {
            background: #ef4444;
            box-shadow: 0 0 8px #ef4444;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0d1322 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0.5rem 0 1.2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 1.2rem;
        }
        .sidebar-brand-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .sidebar-section-label {
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            margin-bottom: 0.6rem;
        }
        .doc-ready-card {
            background: rgba(16, 185, 129, 0.06);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 0.8rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .doc-ready-icon {
            font-size: 1.3rem;
        }
        .doc-ready-info {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .doc-ready-status {
            font-size: 0.75rem;
            font-weight: 600;
            color: #34d399;
        }
        .doc-ready-name {
            font-size: 0.82rem;
            color: #e2e8f0;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 170px;
        }

        /* Empty State */
        .empty-welcome-card {
            text-align: center;
            padding: 2.6rem 1.8rem;
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.4) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            margin: 1.5rem 0 2rem 0;
        }
        .empty-welcome-icon {
            width: 52px;
            height: 52px;
            margin: 0 auto 1rem auto;
            border-radius: 14px;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
        }
        .empty-welcome-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 0.4rem;
            letter-spacing: -0.01em;
        }
        .empty-welcome-desc {
            font-size: 0.9rem;
            color: #94a3b8;
            max-width: 440px;
            margin: 0 auto;
            line-height: 1.5;
        }
        .suggestion-chips-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 10px;
            margin-top: 1.4rem;
        }
        .suggestion-chip {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 0.82rem;
            color: #cbd5e1;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            cursor: default;
        }
        .suggestion-chip:hover {
            border-color: rgba(99, 102, 241, 0.4);
            background: rgba(99, 102, 241, 0.08);
            color: #f8fafc;
        }
        .suggestion-chip-icon {
            font-size: 1rem;
            opacity: 0.8;
        }

        /* Document Ready Mini Alert */
        .doc-ready-banner {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: 10px;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34d399;
            font-size: 0.84rem;
            margin-bottom: 1.2rem;
        }

        /* Chat Message Styling */
        [data-testid="stChatMessage"] {
            border-radius: 14px !important;
            padding: 1rem 1.2rem !important;
            margin-bottom: 0.9rem !important;
            background: rgba(30, 41, 59, 0.35) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Thinking animation */
        .thinking-bubble {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
        }
        .thinking-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #818cf8;
            animation: thinking-bounce 1.4s infinite ease-in-out both;
        }
        .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
        .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
        .thinking-text {
            font-size: 0.85rem;
            color: #94a3b8;
            font-style: italic;
            margin-left: 6px;
        }
        @keyframes thinking-bounce {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* Clean Chat Input */
        [data-testid="stChatInput"] {
            border-radius: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            background: #111827 !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        }
        [data-testid="stChatInput"]:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
        }
    </style>
""", unsafe_allow_html=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@st.cache_data(ttl=10)
def check_backend_health():
    try:
        r = httpx.get(f"{BACKEND_URL}/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

backend_online = check_backend_health()
status_class = "" if backend_online else "offline"
status_text = "AI Ready" if backend_online else "Backend Offline"

# Header
st.markdown(f"""
    <div class="nexus-header">
        <div class="nexus-header-left">
            <div class="nexus-logo-icon">⚡</div>
            <div class="nexus-title-group">
                <div class="nexus-title">NexusRAG <span class="nexus-badge">v1.0</span></div>
                <div class="nexus-subtitle">Chat with your document</div>
            </div>
        </div>
        <div class="nexus-header-right">
            <div class="nexus-status-pill {status_class}">
                <span class="status-dot {status_class}"></span>
                <span>{status_text}</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_ready" not in st.session_state:
    st.session_state.document_ready = False
if "document_name" not in st.session_state:
    st.session_state.document_name = ""

# Sidebar: Document Panel
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="nexus-logo-icon" style="width:30px;height:30px;font-size:0.95rem;">⚡</div>
            <div class="sidebar-brand-title">NexusRAG</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section-label">Your Document</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload a PDF up to 200 MB to index and chat with"
    )
    
    if uploaded_file is not None:
        MAX_FILE_SIZE = 200 * 1024 * 1024
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error("File is too large. Please upload a PDF smaller than 200 MB.")
            st.session_state.document_ready = False
        else:
            # Show process button if new file or not yet ready
            if st.session_state.document_name != uploaded_file.name or not st.session_state.document_ready:
                if st.button("Index Document", type="primary", use_container_width=True):
                    with st.spinner("Processing & indexing document..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        try:
                            response = httpx.post(f"{BACKEND_URL}/upload", files=files, timeout=60.0)
                            if response.status_code == 200:
                                st.session_state.document_ready = True
                                st.session_state.document_name = uploaded_file.name
                                st.session_state.messages = []
                                st.rerun()
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Upload failed')}")
                        except Exception:
                            st.error("I couldn't connect to the document assistant. Please try again.")

    if st.session_state.document_ready:
        st.markdown(f"""
            <div class="doc-ready-card">
                <div class="doc-ready-icon">📄</div>
                <div class="doc-ready-info">
                    <span class="doc-ready-status">✓ Ready to chat</span>
                    <span class="doc-ready-name" title="{st.session_state.document_name}">{st.session_state.document_name}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Clear / Replace", use_container_width=True):
            st.session_state.document_ready = False
            st.session_state.document_name = ""
            st.session_state.messages = []
            st.rerun()

# Main Chat View
if not st.session_state.document_ready:
    st.markdown("""
        <div class="empty-welcome-card">
            <div class="empty-welcome-icon">📄</div>
            <div class="empty-welcome-title">Your document, ready to explore.</div>
            <div class="empty-welcome-desc">Upload a PDF in the sidebar to begin. Once indexed, you can ask questions, compare figures, and explore data with grounded answers.</div>
        </div>
        <div class="sidebar-section-label" style="text-align:center;margin-top:1.5rem;">Sample Inquiries</div>
        <div class="suggestion-chips-grid">
            <div class="suggestion-chip">
                <span class="suggestion-chip-icon">💬</span>
                <span>What is this document about?</span>
            </div>
            <div class="suggestion-chip">
                <span class="suggestion-chip-icon">📊</span>
                <span>Summarize the key points</span>
            </div>
            <div class="suggestion-chip">
                <span class="suggestion-chip-icon">📈</span>
                <span>What are the main figures?</span>
            </div>
            <div class="suggestion-chip">
                <span class="suggestion-chip-icon">⚖️</span>
                <span>Compare the latest values</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    if not st.session_state.messages:
        st.markdown(f"""
            <div class="doc-ready-banner">
                <span>✓</span>
                <strong>Document ready:</strong> {st.session_state.document_name}. Ask questions about your PDF below.
            </div>
            <div class="suggestion-chips-grid" style="margin-bottom:1.5rem;">
                <div class="suggestion-chip">
                    <span class="suggestion-chip-icon">💬</span>
                    <span>What is this document about?</span>
                </div>
                <div class="suggestion-chip">
                    <span class="suggestion-chip-icon">📊</span>
                    <span>Summarize the key points</span>
                </div>
                <div class="suggestion-chip">
                    <span class="suggestion-chip-icon">📈</span>
                    <span>What are the main figures?</span>
                </div>
                <div class="suggestion-chip">
                    <span class="suggestion-chip-icon">⚖️</span>
                    <span>Compare the latest values</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Render persistent conversation
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask anything about your document..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚡"):
            message_placeholder = st.empty()
            message_placeholder.markdown("""
                <div class="thinking-bubble">
                    <span class="thinking-dot"></span>
                    <span class="thinking-dot"></span>
                    <span class="thinking-dot"></span>
                    <span class="thinking-text">Thinking...</span>
                </div>
            """, unsafe_allow_html=True)
            full_response = ""
            
            try:
                with httpx.stream("POST", f"{BACKEND_URL}/chat", json={"message": prompt}, timeout=60.0) as response:
                    if response.status_code != 200:
                        message_placeholder.error("I couldn't connect to the document assistant. Please try again.")
                    else:
                        message_placeholder.empty()
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                try:
                                    data = json.loads(data_str)
                                    if "error" in data:
                                        message_placeholder.error(data["error"])
                                        break
                                    elif "token" in data:
                                        full_response += data["token"]
                                        message_placeholder.markdown(full_response + " ▌")
                                    elif "done" in data and data["done"]:
                                        message_placeholder.markdown(full_response)
                                        break
                                except json.JSONDecodeError:
                                    pass
            except Exception:
                message_placeholder.error("I couldn't connect to the document assistant. Please try again.")
            
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})

