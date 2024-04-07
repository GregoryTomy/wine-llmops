import os
import logging
from openai import AzureOpenAI
from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


load_dotenv(".env")

logging.basicConfig(level=logging.ERROR)

print(os.getenv("AZURE_OPENAI_API_VERSION_CHAT"))

embeddings = OpenAIEmbeddings()

azure_cog_search = AzureSearch(
    azure_search_endpoint=os.getenv("SEARCH_SERVICE_NAME"),
    azure_search_key=os.getenv("SEARCH_API_KEY"),
    index_name=os.getenv("SEARCH_INDEX_NAME"),
    embedding_function=embeddings.embed_query,
)


docs = azure_cog_search.similarity_search_with_relevance_scores(
    query="What is the best Cabernet Sauvignon wine from Nappa Valley above 90 rating points?",
    k=5,
)

messages = [
    {
        "role": "system",
        "content": "Assistant is a chatbot that helps you find the best wine for your taste.",
    },
    {
        "role": "user",
        "content": "What is the best Cabernet Sauvignon wine from Nappa Valley above 90 rating points?",
    },
    {"role": "assistant", "content": docs[0][0].page_content},
]

client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION_CHAT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)


def test_context_response():
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYEMENT"), messages=messages
        )

        pprint(response.choices[0].message.content)
        logging.info("Response recieved")
    except Exception as e:
        logging.error("An error occured: %s", e)


if __name__ == "__main__":
    test_context_response()
