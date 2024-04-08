import os
from openai import AzureOpenAI
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI()

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


class Body(BaseModel):
    query: str


def search(query: str):
    """Send the query to Azure Coginitive search and return
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


def assistant(query: str, context: str):
    """Process user query and context to geenrate a response using Azure OpenAI API.

    Args:
        query (str): The input from the user to which the assistant will respond.
        context (str): Context retrieved from Azure AI Search that helps tailor the assistant's response.

    Returns:
        str: The assistant's generated response to the user's query, incorporating the provided context.
    """

    messages = [
        {
            "role": "system",
            "content": "Assistant is a chatbot that helps you find the best wine for your taste.",
        },
        {
            "role": "user",
            "content": query,
        },
        {"role": "assistant", "content": context},
    ]

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
def ask(body: Body):
    """Use the query parameter to interect with Azure OpenAI with
    Azure Cognitive Search for Retreival Augmented Generation.
    """
    search_result = search(body.query)
    chat_bot_response = assistant(body.query, search_result)

    return {"response": chat_bot_response}

