import streamlit as st
import time
import gc
import torch

from rag_system import create_workflow

torch.classes.__path__ = []


st.header("Tunisian Stock Market Agentic RAG :chart_with_upwards_trend: :flag-tn:")

st.subheader("Ask questions about Tunisian Stock Market trends")


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

if "pdf_tool" not in st.session_state:
    st.session_state.pdf_tool = None 

if "agents" not in st.session_state:
    st.session_state.agents = None    


def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]
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
if prompt := st.chat_input("Ask a question about Tunisian stock market and related news..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.agents is None:
        st.session_state.agents = create_workflow()
        print("Agents created")    

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = "" 

        # Get the complete response first
        with st.spinner("Thinking..."):
            inputs = {"question": prompt}
            for output in st.session_state.agents.stream(inputs):
                for key, value in output.items():
                    continue
            result = value["generation"]
                
        words = result.split(' ')
        # Simulate stream of response with milliseconds delay
        for i, word in enumerate(words):
            full_response += word
            if i < len(words) - 1:  # Don't add newline to the last line
                full_response += ' '
            
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.20)

        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


       