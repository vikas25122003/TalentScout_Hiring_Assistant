# app.py

import streamlit as st
from groq import Groq

# Set the title for the Streamlit app
st.title("TalentScout Hiring Assistant")

# --- CLIENT SETUP & PROMPT ENGINEERING ---
# Point to the Groq API
try:
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"],
    )
except Exception as e:
    st.error("Groq API key not found or invalid. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# Initialize the chat message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- INITIAL GREETING ---
# Greet the candidate and provide an overview [cite: 20]
if not st.session_state.messages:
    # This is the first message from the assistant
    initial_greeting = "Welcome to TalentScout! I'm your intelligent hiring assistant. I'll be asking you a few questions to get started with your application. Let's begin!"
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting})

# --- DISPLAY CHAT HISTORY ---
# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & DUMMY RESPONSE ---
# This part will be expanded in the next steps to add the real logic
if prompt := st.chat_input("Your response..."):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A simple acknowledgement from the assistant (for now)
    # In the next step, we'll replace this with real LLM calls
    assistant_response = f"Thank you. We will process that."
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)