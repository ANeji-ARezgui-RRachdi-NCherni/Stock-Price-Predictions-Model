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
    st.session_state.active_chat = None
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]
    gc.collect()

def save_chat():
    if st.session_state.active_chat is None and len(st.session_state.messages) > 1:
        st.session_state.counter += 1
        st.session_state.active_chat = {"chat_name" : "chat_" + str(st.session_state.counter), "messages": st.session_state.messages}
        st.session_state.chats.append(st.session_state.active_chat)
        st.session_state.active_chat = None


def new_chat():
    save_chat()
    reset_chat()

   
st.set_page_config(page_title="StockWise", page_icon="📈", layout="centered")
st.header("💬 AI Chat Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]

if "chats" not in st.session_state:
    st.session_state.chats = []

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

if "counter" not in st.session_state:
    st.session_state.counter = 0    

# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.subheader("Chat History")
    for i, chat in enumerate(st.session_state.chats):
        cols = st.columns([4, 1, 1])  # 5:1 ratio between chat name and delete
        with cols[0]:
            if st.button(chat["chat_name"], key=f"chat_{i}"):
                save_chat()
                st.session_state.active_chat = chat
                st.session_state.messages = chat["messages"]
                gc.collect()
        with cols[1]:
            if st.button("🗑️", key=f"delete_{i}"):
                st.session_state.chats.remove(chat)
                if st.session_state.active_chat == chat:
                    reset_chat()
                gc.collect()
                   
    st.button("New Chat", on_click=new_chat)

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

        response = res['response']['generation']
        result = res['response']['generation'].split(' ')
        for i, word in enumerate(result):
            full_response += word
            if i < len(result) - 1: 
                full_response += ' '

            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.1)

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


       