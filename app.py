import streamlit as st
from openai import OpenAI
import time

# 1. Page Config
st.set_page_config(page_title="EndoAfya", page_icon="🎗️")
st.title("🎗️ EndoAfya: Your Health, Our Purpose")
st.caption("Guided by ESHRE 2026 Standards")

# 2. Secure Connections (Using Secrets)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# 3. Session State (Remembers the conversation)
if "messages" not in st.session_state:
    st.session_state.messages = []
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# 4. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. User Input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send message to OpenAI Thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Start the "Run"
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Polling (Wait for the AI to think)
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)

    # Get the latest message
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    response = messages.data[0].content[0].text.value

    # Display Response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
