#! Update Index
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchIndex,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    HnswParameters,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)

service_endpoint = os.getenv("SEARCH_SERVICE_NAME")
service_key = os.getenv("SEARCH_API_KEY")

# instantiate client
client = SearchIndexClient(service_endpoint, AzureKeyCredential(service_key))


# Test connection by listing all indexes
def search_client_index_test():
    print("Service Endpoint:", service_endpoint)
    print("Service API Key:", service_key)

    try:
        index_names = [index.name for index in client.list_indexes()]
        print("Successfully connected to Azure Cognitive Search service.")
        print("Found the following indexes:", index_names)
    except Exception as e:
        print("Failed to connect or list indexes:")
        print(e)


if __name__ == "__main__":
    search_client_index_test()
