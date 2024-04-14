import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (SimpleField,
                                                   SearchIndex,
                                                   SearchFieldDataType,
                                                   SearchableField,
                                                   SearchField,
                                                   VectorSearch,
                                                   HnswAlgorithmConfiguration,
                                                   HnswParameters,
                                                   VectorSearchAlgorithmKind,
                                                   VectorSearchAlgorithmMetric,
                                                   VectorSearchProfile)

service_endpoint = os.getenv('SEARCH_SERVICE_NAME')
service_key = os.getenv('SEARCH_API_KEY')
# instantiate client
client = SearchIndexClient(service_endpoint,
                           AzureKeyCredential(service_key))

def create_index():
    name= "wine-index"

    # Check if the index already exists
    existing_indexes = [index.name for index in client.list_indexes()]
    if name in existing_indexes:
        # Delete the existing index
        client.delete_index(name)
        print(f"Existing index '{name}' deleted successfully.")

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, searchable=True, retrievable=True),
        SearchableField(name="metadata", type=SearchFieldDataType.String, searchable=True, retrievable=True),
        SearchField(name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=1536,
                    vector_search_profile_name="my-vector-config",
                    )
    ]

    # configure the vector search
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="my-hnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE,
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-config",
                algorithm_configuration_name="my-hnsw"
            )
        ]
    )

    # create the index
    index = SearchIndex(name=name,
                        fields=fields,
                        vector_search=vector_search)
    
    # create index
    result = client.create_index(index)
    print(f"Index '{result.name} created successfully")
    
if __name__ == "__main__":
    create_index()