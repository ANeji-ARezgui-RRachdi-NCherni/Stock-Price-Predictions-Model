import streamlit as st
import time
import asyncio
import gc
import torch
import os
import requests

from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.environ.get("BACKEND_URL")

torch.classes.__path__ = []

async def get_response(prompt):
    res = requests.post(
            f"{BACKEND_URL}/rag",
            headers={"Content-Type": "text/plain"},
            data=prompt,
            stream=True,
    )
    return res.json()

def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]
    gc.collect()

   
st.set_page_config(page_title="StockWise", page_icon="📈", layout="centered")
st.header("💬 AI Chat Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]

# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.button("Clear Chat", on_click=reset_chat)

# ===========================
#   Main Chat
# ===========================


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask me"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        full_response = "" 
        message_placeholder = st.empty()
        with st.spinner("Thinking...", show_time=True):
            res = asyncio.run(get_response(prompt))

        words = res['response']['generation'].split(' ')
        for i, word in enumerate(words):
            full_response += word
            if i < len(words) - 1: 
                full_response += ' '

            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.1)

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


       