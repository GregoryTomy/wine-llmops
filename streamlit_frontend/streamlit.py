import yaml
import streamlit as st
import streamlit_authenticator as stauth
import requests
from yaml.loader import SafeLoader

################################################################
# Authentication
################################################################

def load_config(path):
    with open(path) as file:
        return yaml.load(file, Loader=SafeLoader)

def initalize_authenticator(config):
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

def authenticate_user(authenticator):
    # Initialize authentication status if it's not in session state
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    # if user not authenticated, show login
    if st.session_state["authentication_status"] != True:
        st.title("Welcome to Barney - your personal sommelier")
        st.subheader("Please log in to access Barney.")
        authenticator.login()
        if st.session_state["authentication_status"]:
            st.rerun() # rerun script to update state
        elif st.session_state["authentication_status"]== False:
            st.error('Username or password is incorrect')
        elif st.session_state["authentication_status"] == None:
            st.warning('Please enter username or password')
    else: 
        # user is authenticated, show logout and main app
        if st.button("Logout"):
            st.session_state['authentication_status'] = None
            st.rerun()

########################################################################
# Application
########################################################################

def main_app():
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
        url = "http://backend:8000/ask"
        response = requests.post(url, json={"query": user_input})

        if response.status_code == 200:
            chat_response = response.json()["response"]
            st.write(f"{chat_response}")
        else:
            st.write("Failed to get response.")


if __name__ == "__main__":
    config = load_config('../config.yaml')
    authenticator = initalize_authenticator(config)
    authenticate_user(authenticator)
    if st.session_state["authentication_status"]:
        main_app()