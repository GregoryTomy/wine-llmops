import os
from openai import AzureOpenAI
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from pydantic import BaseModel
from typing import List, Optional

################################################################
# Environment variables
################################################################

# Azure Search
AZURE_SEARCH_ENDPOINT = os.getenv("SEARCH_SERVICE_NAME")
AZURE_SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_API_VERSION_CHAT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYEMENT")

# OpenAI Key
# * Note: We have a separate OpenAI  key since the embeddings was done through
# * OpenAI API and not Azure.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

################################################################
# Connections
###############################################################

# TODO: Do embeddings using OpenAI
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

azure_search = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=AZURE_SEARCH_API_KEY,
    index_name=AZURE_SEARCH_INDEX_NAME,
    embedding_function=embeddings.embed_query,
)


################################################################
# Helper functions
###############################################################


class ChatMessage(BaseModel):
    role: str
    content: str


class Body(BaseModel):
    query: str


class ChatHistory:
    """Manages the history of a chat session, storing messages in a list
    """
    def __init__(self):
        self.messages = []

    def update(self, user_message: str, assistant_message: Optional[str] = None):
        """Update the chat history with new messages from the user and
        optionally from the assistant.

        Args:
            user_message (str): The message from the user to be added to the history
            assistant_message (Optional[str], optional): The response from assistant to be added to the history. Defaults to None.
        """
        self.messages.append({"role": "user", "content": user_message})
        if assistant_message:
            self.messages.append({"role": "assistant", "content": assistant_message})

    def get_history(self):
        """Retrieves the entire chat history
        """
        return self.messages


def search(query: str):
    """Send the query to Azure AI search and return
    the top result

    Args:
        query (str): The search query strong to find relevant documents.

    Returns:
        str: The page content of the most relevant document based on the query
    """
    docs = azure_search.similarity_search_with_relevance_scores(
        query=query,
        k=5,  # return top 5 results
    )

    result = docs[0][0].page_content

    return result


def get_chat_history():
    """Creates and returns a new instance of ChatHistory for managing chat messages.

    Returns:
        ChatHistory: A new instance of ChatHistory to track the messages of a chat session.
    """
    history = ChatHistory()
    return history


def assistant(query: str, context: str, chat_history: List[ChatMessage]):
    """Process user query and context to geenrate a response using Azure OpenAI API.

    Args:
        query (str): The input from the user to which the assistant will respond.
        context (str): Context retrieved from Azure AI Search that helps tailor the assistant's response.
        chat_history(List[ChatMessage]): The current chat history that includes all messages so far.

    Returns:
        str: The assistant's generated response to the user's query, incorporating the provided context and chat history.
    """

    messages = (
        [
            {
                "role": "system",
                "content": "Assistant is called Barney and is a chatbot that helps you find the best wine for your taste.",
            }
        ]
        + chat_history
        + [
            {
                "role": "user",
                "content": query,
            },
            {"role": "assistant", "content": context},
        ]
    )

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_VERSION,
        api_key=AZURE_OPENAI_KEY,
    )

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=messages,
    )

    return response.choices[0].message.content


################################################################
# App
###############################################################

app = FastAPI()


@app.get("/")
def root():
    return RedirectResponse(url="/docs", status_code=301)


@app.post("/ask")
def ask(body: Body, history: ChatHistory = Depends(get_chat_history)):
    """Handles user queries by interfacing with Azure Open AI and Azure AI Search.

    Args:
        body (Body): The user's query encapusulated by Body object.
        history (ChatHistory, optional): The chat history of the current session, managed by FastAPI's dependency injection. Defaults to Depends(get_chat_history).

    Returns:
        dict: A dictionary containing the 'response' key with the chatbot's generated text as its value.
    """
    search_result = search(body.query)
    chat_bot_response = assistant(body.query, search_result, history.get_history())
    history.update(body.query, chat_bot_response)

    return {"response": chat_bot_response}
