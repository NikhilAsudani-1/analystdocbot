import streamlit as st
import openai

# Title and Description
st.title("📚 AnalystDocBot")
st.write("Ask me anything about your clients, docs, or processes.")

# Securely load your OpenAI API Key from Streamlit Secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Memory for conversation
if "history" not in st.session_state:
    st.session_state.history = []

# Chat input box
user_input = st.text_input("Ask your question here:")

# Handle input
if user_input:
    # Construct conversation so far
    messages = [{"role": "system", "content": "You are an analytics documentation assistant. Answer clearly based on previously saved notes or input."}]
    
    for msg in st.session_state.history:
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_input})

    # Call OpenAI chat completion (latest SDK format)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Extract the reply
    answer = response.choices[0].message.content

    # Store chat history
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": answer})

    # Display the bot's response
    st.markdown("**Bot:** " + answer)
