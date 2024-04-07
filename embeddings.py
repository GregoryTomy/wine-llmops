import os
import openai
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import CharacterTextSplitter

load_dotenv('.env')

loader = CSVLoader("wine-ratings_100.csv")
documents = loader.load()


text_splitter = CharacterTextSplitter(chunk_size=1000,
                                      chunk_overlap=0)

split_docs =text_splitter.split_documents(documents)

print(os.getenv('SEARCH_SERVICE_NAME'))

embeddings = OpenAIEmbeddings()

# Connect and load to Azure Cognitive Search
azure_cog_search = AzureSearch(azure_search_endpoint=os.getenv('SEARCH_SERVICE_NAME'),
                               azure_search_key=os.getenv('SEARCH_API_KEY'),
                               index_name=os.getenv('SEARCH_INDEX_NAME'),
                               embedding_function=embeddings.embed_query)

azure_cog_search.add_documents(documents=split_docs)