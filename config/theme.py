import streamlit as st

def apply_theme():
    """Menerapkan styling CSS kustom dan dark mode"""
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stButton > button { border-radius: 8px; font-weight: 600; }
        div[data-testid="stMetric"] {
            background-color: #1e1e1e; border: 1px solid #333;
            border-radius: 8px; padding: 15px;
        }
        section[data-testid="stSidebar"] {
            background-color: #161b22; border-right: 1px solid #30363d;
        }
    </style>
    """, unsafe_allow_html=True)

def theme_toggle():
    """Info tema di sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.caption("💡 **Tip:** Edit `.streamlit/config.toml` untuk ubah tema Light/Dark.")
