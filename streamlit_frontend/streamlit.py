import os
import streamlit as st
import streamlit_authenticator as stauth
import requests
from yaml.loader import SafeLoader

################################################################
# Authentication
################################################################


def initalize_authenticator():
    credentials = {
        "usernames": {
            os.getenv("CREDENTIALS_USERNAME"): {
                "name": os.getenv("CREDENTIALS_NAMES"),
                "password": os.getenv("CREDENTIALS_PASSWORD"),
            }
        }
    }

    return stauth.Authenticate(
        credentials,
        os.getenv("COOKIE_NAME"),
        os.getenv("COOKIE_KEY"),
        int(os.getenv("COOKIE_EXPIRY_DAYS")),
    )


def authenticate_user(authenticator):
    # Initialize authentication status if it's not in session state
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    # if user not authenticated, show login
    if st.session_state["authentication_status"] !=True:
        with st.sidebar:
            st.title("Login to Barney")
            authenticator.login()

        with st.container():
            st.image("banner_image.webp")
            st.title("Welcome to Barney - your personal sommelier")
            st.subheader("Please log in to access Barney.")

        if st.session_state["authentication_status"]:
            st.rerun()  # rerun script to update state
        elif st.session_state["authentication_status"] == False:
            st.error("Username or password is incorrect")
        elif st.session_state["authentication_status"] == None:
            st.warning("Please enter username or password")
    else:
        with st.sidebar:
            # about section
            with st.expander("About"):
                st.markdown(
                    """
                    Barney is your personal AI-powered sommelier designed to help you choose wines that you'll love. 
                    The app uses technologies such as Microsoft Azure, LangChain, and Retrieval-Augmented Generation (RAG) for providing tailored wine recommendations. 
                    
                    
                    This project is powered by FastAPI and Streamlit, showcasing the integration of cutting-edge technology in practical applications. 
                    """
                )

            with st.expander("What is Retrieval-Augmented Generation (RAG)?"):
                st.write("""
                    Retrieval-Augmented Generation is a technique in artificial intelligence that combines the best of both worlds: retrieving relevant information and generating new content from it.
                
                    RAG works by first searching a large database or knowledge base to find pieces of information that are relevant to a user's query. 
                    It then uses this information as a foundation to generate coherent and contextually appropriate responses. 
                    
                    
                    This approach is powerful because it allows the AI to provide answers that are not only accurate but also rich in detail and highly personalized, making it ideal for applications like wine recommendations where precision and personalization are key.
                    
                    
                    >Barney searches a database of 30k+ wine reviews based on the user input. For more details,
                    please check out the [repository.](https://github.com/GregoryTomy/wine-llmops)
                         
                """)

            # how to use section
            with st.expander("How to Use"):
                st.markdown(
                    """
                    - Enter any type of wine you're interested in.
                    - Example questions you might ask:
                        - 'What's a good dry wine from California?'
                        - 'Recommend a sweet white wine.'
                    - Barney will analyze your request and suggest the best wines for your taste.
                """
                )

            # user is authenticated, show logout and main app
            if st.button("Logout"):
                st.session_state["authentication_status"] = None
                st.rerun()
            
            if st.button("View Code"):
                import webbrowser
                webbrowser.open('https://github.com/GregoryTomy/wine-llmops')

########################################################################
# Application
########################################################################


def main_app():
    st.title("Barney - your personal sommelier")

    # initalize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat_history in st.session_state.chat_history:
        with st.chat_message(chat_history["role"]):
            st.markdown(chat_history["content"])

    user_input = st.chat_input("Ask Barney")

    if prompt := user_input:
        # add user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # display assistant response in chat message containter
        with st.chat_message("assistant"):
            # send input to FastAPI endpoint
            url = "http://backend:8000/ask"
            # url = "http://0.0.0.0:8000/ask"
            response = requests.post(url, json={"query": user_input})

            if response.status_code == 200:
                chat_response = response.json()["response"]
                st.write(chat_response)
            else:
                st.write("Failed to get response.")

        st.session_state.chat_history.append(
            {"role": "assistant", "content": chat_response}
        )


if __name__ == "__main__":
    st.set_page_config(page_title="Barney", layout="wide")
    authenticator = initalize_authenticator()
    authenticate_user(authenticator)
    if st.session_state["authentication_status"]:
        main_app()
