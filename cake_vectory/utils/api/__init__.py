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
class WeaviateAPI(SearchClient, SchemaClient, HealthClient, ObjectsClient):
    """Client for interacting with the Weaviate API.
    
    This class combines all specialized clients to maintain backward compatibility.
    """
    
    def get_shards(self, class_name: str):
        """Get shard information for a collection.
        
        Args:
            class_name: Name of the collection/class
            
        Returns:
            Dict: Shard information
        """
        return super().get_shards(class_name)
        
    def get_shard_details(self, class_name: str, shard_name: str):
        """Get detailed information about a specific shard.
        
        Args:
            class_name: Name of the collection/class
            shard_name: Name of the shard
            
        Returns:
            Dict: Detailed shard information including metrics
        """
        return super().get_shard_details(class_name, shard_name)
