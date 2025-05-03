import streamlit as st
import time
import gc
import tempfile
import os
import base64
import torch


# from utils import process_pdf
from rag_system import create_workflow

torch.classes.__path__ = []


st.header("Tunisian Stock Market Agentic RAG :chart_with_upwards_trend: :flag-tn:")

st.subheader("Ask questions about Tunisian Stock Market trends")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

if "pdf_tool" not in st.session_state:
    st.session_state.pdf_tool = None 

if "agents" not in st.session_state:
    st.session_state.agents = None    


def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]
    gc.collect()

def display_pdf(file_bytes: bytes, file_name: str):
    """Displays the uploaded PDF in an iframe."""
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="600px" 
        type="application/pdf"
    >
    </iframe>
    """
    st.markdown(f"### Preview of {file_name}")
    st.markdown(pdf_display, unsafe_allow_html=True)    

# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.header("Add Your PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # If there's a new file and we haven't set pdf_tool yet...
        # if st.session_state.pdf_tool is None:
        #     with tempfile.TemporaryDirectory() as temp_dir:
        #         temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        #         with open(temp_file_path, "wb") as f:
        #             f.write(uploaded_file.getvalue())

        #         with st.spinner("Indexing PDF... Please wait..."):
        #             st.session_state.pdf_tool = process_pdf(file_path=temp_file_path)
            
        st.success("PDF indexed! Ready to chat.")

        # Optionally display the PDF in the sidebar
        display_pdf(uploaded_file.getvalue(), uploaded_file.name)

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

    # 2. Build or reuse the Crew (only once after PDF is loaded)
    if st.session_state.agents is None:
        st.session_state.agents = create_workflow()    

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


       