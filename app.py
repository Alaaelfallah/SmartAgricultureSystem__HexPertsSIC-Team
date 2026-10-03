import streamlit as st

from styles.custom_css import apply_custom_css
from views.chat_view import render_chat_tab
from views.home_view import render_home_tab
from views.irrigation_view import render_irrigation_tab
from views.vision_view import render_vision_tab


st.set_page_config(
    page_title="HexPerts Smart Farm Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_custom_css()

tab_home, tab_vision, tab_irrigation, tab_chat = st.tabs(
    ["🏠 Home", "📷 Scan Leaf", "🚰 Smart Water", "🧠 Ask AI"]
)

with tab_home:
    render_home_tab()

with tab_vision:
    render_vision_tab()

with tab_irrigation:
    render_irrigation_tab()

with tab_chat:
    render_chat_tab()