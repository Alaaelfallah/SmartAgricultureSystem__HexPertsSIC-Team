import streamlit as st

from models.rag_chain import generate_rag_llm_advice


def render_chat_tab() -> None:
    st.markdown('<h2 class="module-title">Interactive AI Agronomist</h2>', unsafe_allow_html=True)
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Welcome! I am the HexPerts AI agricultural advisor. How can I help you with your farm today?",
            }
        ]

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍🌾"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask about diseases, soil fertilization, or irrigation schedule..."
    )
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👨‍🌾"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Querying agricultural knowledge base..."):
                response = generate_rag_llm_advice(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
