import os
from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch


load_dotenv(".env")


embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

azure_cog_search = AzureSearch(
    azure_search_endpoint=os.getenv("SEARCH_SERVICE_NAME"),
    azure_search_key=os.getenv("SEARCH_API_KEY"),
    index_name=os.getenv("SEARCH_INDEX_NAME"),
    embedding_function=embeddings.embed_query,
)


def test_azure_search_response():
    docs = azure_cog_search.similarity_search_with_relevance_scores(
        query="What is the best Cabernet Sauvignon wine from Nappa Valley above 90 rating points?",
        k=5,
    )

    pprint(docs[0][0].page_content)


if __name__ == "__main__":
    test_azure_search_response()
