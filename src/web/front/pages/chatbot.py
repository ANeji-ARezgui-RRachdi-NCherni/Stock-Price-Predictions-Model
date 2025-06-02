import streamlit as st
import time
import asyncio
import gc
import torch
import os


from pathlib import Path
import sys
sys.path.insert(0, str(Path(os.path.dirname(__file__)) / '..' / '..'/ '..'))
from rag.rag_system import create_agents_graph

torch.classes.__path__ = []

async def handle_async_response(prompt):
    full_response = "" 
    message_placeholder = st.empty()
    
    with st.spinner("Thinking...", show_time=True):
        inputs = {"question": prompt}

    async for output in st.session_state.agents.astream(inputs, stream_mode="messages"):
        full_response += output[0].content
        if len(full_response) > 0:
            message_placeholder.markdown(full_response + "▌")  

    message_placeholder.markdown(full_response)
    return 'full_response'

st.set_page_config(page_title="StockWise", page_icon="📈", layout="centered")
st.header("💬 AI Chat Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]

if "agents" not in st.session_state:
    st.session_state.agents = None



def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Ask questions about Tunisian Stock Market trends 📈"}]
    gc.collect()


# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.button("Clear Chat", on_click=reset_chat)


# ===========================
#   Main Chat
# ===========================

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.agents is None:
        st.session_state.agents = create_agents_graph() 

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
       full_response =  asyncio.run(handle_async_response(prompt))
            
                
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


       