import streamlit as st
import openai

st.title("📚 AnalystDocBot")
st.write("Ask me anything about your clients, docs, or processes.")

openai.api_key = st.secrets["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"]

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask your question here:")

if user_input:
    messages = [{"role": "system", "content": "You are an analytics documentation assistant. Answer clearly based on previous saved notes."}]
    for msg in st.session_state.history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_input})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    answer = response.choices[0].message["content"]
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": answer})
    
    st.write("**Bot:**", answer)
