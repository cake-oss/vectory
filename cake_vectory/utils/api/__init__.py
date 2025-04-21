# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""API interaction utilities for the Cake Vectory CLI."""

# Export all the specialized clients
from cake_vectory.utils.api.client import WeaviateClient
from cake_vectory.utils.api.health import HealthClient
from cake_vectory.utils.api.schema import SchemaClient
from cake_vectory.utils.api.objects import ObjectsClient
from cake_vectory.utils.api.search import SearchClient


# Define the WeaviateAPI class here
class WeaviateAPI(WeaviateClient):
    """Client for interacting with the Weaviate API.

    This class combines all specialized clients to maintain backward compatibility.
    """

    def __init__(self):
        """Initialize the Weaviate API."""
        super().__init__()
        self.search_client = SearchClient()
        self.objects_client = ObjectsClient()
        self.schema_client = SchemaClient()
        self.health_client = HealthClient()

    # Pass through search methods
    def search_objects(self, *args, **kwargs):
        return self.search_client.search_objects(*args, **kwargs)

    def hybrid_search(self, *args, **kwargs):
        return self.search_client.hybrid_search(*args, **kwargs)

    def vector_search(self, *args, **kwargs):
        return self.search_client.vector_search(*args, **kwargs)

    def filter_objects(self, *args, **kwargs):
        return self.search_client.filter_objects(*args, **kwargs)

    def has_vectorizer(self, *args, **kwargs):
        return self.search_client.has_vectorizer(*args, **kwargs)

    # Pass through schema methods
    def get_schemas(self, *args, **kwargs):
        return self.schema_client.get_schemas(*args, **kwargs)

    def delete_schema(self, *args, **kwargs):
        return self.schema_client.delete_schema(*args, **kwargs)

    def get_collection_stats(self, *args, **kwargs):
        return self.schema_client.get_collection_stats(*args, **kwargs)

    # Pass through health methods
    def check_health(self, *args, **kwargs):
        return self.health_client.check_health(*args, **kwargs)

    # Pass through objects methods
    def get_objects(self, *args, **kwargs):
        return self.objects_client.get_objects(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.objects_client.get_object(*args, **kwargs)

    def create_object(self, *args, **kwargs):
        return self.objects_client.create_object(*args, **kwargs)

    def update_object(self, *args, **kwargs):
        return self.objects_client.update_object(*args, **kwargs)

    def delete_object(self, *args, **kwargs):
        return self.objects_client.delete_object(*args, **kwargs)

    def batch_objects(self, *args, **kwargs):
        return self.objects_client.batch_objects(*args, **kwargs)

    def get_collection_count(self, *args, **kwargs):
        return self.objects_client.get_collection_count(*args, **kwargs)

    def execute_graphql(self, *args, **kwargs):
        return self.objects_client.execute_graphql(*args, **kwargs)

    def get_shards(self, class_name: str):
        """Get shard information for a collection.

        Args:
            class_name: Name of the collection/class

        Returns:
            Dict: Shard information
        """
        return self.schema_client.get_shards(class_name)

    def get_shard_details(self, class_name: str, shard_name: str):
        """Get detailed information about a specific shard.

        Args:
            class_name: Name of the collection/class
            shard_name: Name of the shard

        Returns:
            Dict: Detailed shard information including metrics
        """
        return self.schema_client.get_shard_details(class_name, shard_name)
