import streamlit as st
import requests

st.title("Barney - your personal sommelier")

with st.expander("How to use this app"):
    st.write("""
        - Enter any type of wine you're interested in.
        - Example questions you might ask:
            - 'What's a good dry wine from California?'
            - 'Recommend a sweet white wine.'
        - Barney will analyze your request and suggest the best wines for your taste.
    """)

user_input = st.text_input("Ask Barney:",
                           placeholder="Suggest a dry wine from California")

# send input to FastAPI endpoint
if user_input:
    url = "http://0.0.0.0:8000/ask"
    response = requests.post(url, json={"query": user_input})

    if response.status_code == 200:
        chat_response = response.json()["response"]
        st.write(f"{chat_response}")
    else:
        st.write("Failed to get response.")
