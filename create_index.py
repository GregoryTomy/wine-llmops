import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (SimpleField, 
                                                   SearchIndex, 
                                                   SearchFieldDataType)

service_endpoint = os.getenv('SEARCH_SERVICE_NAME')
service_key = os.getenv('SEARCH_API_KEY')

# instantiate client
client = SearchIndexClient(service_endpoint,
                           AzureKeyCredential(service_key))


# # Test connection by listing all indexes
# try:
#     index_names = [index.name for index in client.list_indexes()]
#     print("Successfully connected to Azure Cognitive Search service.")
#     print("Found the following indexes:", index_names)
# except Exception as e:
#     print("Failed to connect or list indexes:")
#     print(e)

def create_index():
    name= "wine-index"
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="name", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="grape", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="region", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="variety", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="rating", type=SearchFieldDataType.Double, searchable=True),
        SimpleField(name="notes", type=SearchFieldDataType.String, searchable=True),
    ]

    # create the index
    index = SearchIndex(name=name,
                        fields=fields)
    
    # create index
    client.create_index(index)
    print(f"Index '{name} created successfully")
    
if __name__ == "__main__":
    create_index()