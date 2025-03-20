# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Schema management functionality for the Weaviate API."""

import json
from typing import List, Dict, Any, Optional
from rich.console import Console

from cake_vectory.utils.api.client import WeaviateClient
from cake_vectory.utils.api.objects import ObjectsClient

console = Console()


class SchemaClient(ObjectsClient):
    """Client for schema management operations."""
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all schemas from Weaviate.
        
        Returns:
            List: List of schema objects
        """
        response = self.get("schema")
        return response.get("classes", [])
    
    def delete_schema(self, class_name: str) -> bool:
        """Delete a schema class from Weaviate.
        
        Args:
            class_name: Name of the schema class to delete
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If the API returns an error
        """
        url = f"schema/{class_name}"
        self.delete(url)
        return True
    
    def has_vectorizer(self, class_name: str) -> bool:
        """Check if a collection has a vectorizer configured.
        
        Args:
            class_name: Name of the collection/class
            
        Returns:
            bool: True if the collection has a vectorizer, False otherwise
        """
        try:
            schemas = self.get_schemas()
            schema = next((s for s in schemas if s.get("class") == class_name), None)
            if schema:
                return schema.get("vectorizer") not in [None, "none"]
            return False
        except Exception:
            return False
    
    def get_collection_stats(self, class_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.
        
        Args:
            class_name: Name of the collection/class
            
        Returns:
            Dict: Collection statistics
        """
        stats = {"object_count": 0, "meta": {}, "shards": [], "replication": {}}
        
        try:
            # Use the get_collection_count method from ObjectsClient
            # This is the most accurate way to get the total count
            stats["object_count"] = self.get_collection_count(class_name)
            
            # Try to get metadata about the collection
            try:
                meta_response = self.get(f"schema/{class_name}")
                stats["meta"] = meta_response
                
                # Extract replication info if available
                if "replicationConfig" in meta_response:
                    stats["replication"] = meta_response.get("replicationConfig", {})
                
                # Extract sharding info if available
                if "shardingConfig" in meta_response:
                    stats["sharding"] = meta_response.get("shardingConfig", {})
                
            except Exception:
                # If meta endpoint fails, try alternative approach
                try:
                    # Get schema info which might contain some metadata
                    schemas = self.get_schemas()
                    schema = next((s for s in schemas if s.get("class") == class_name), None)
                    if schema:
                        stats["meta"] = {"schema": schema}
                        
                        # Extract replication info if available
                        if "replicationConfig" in schema:
                            stats["replication"] = schema.get("replicationConfig", {})
                        
                        # Extract sharding info if available
                        if "shardingConfig" in schema:
                            stats["sharding"] = schema.get("shardingConfig", {})
                except Exception:
                    pass
            
            # Try to get shard status information
            try:
                shards_response = self.get(f"schema/{class_name}/shards")
                stats["shards"] = shards_response
            except Exception:
                # If shard endpoint fails, shards list remains empty
                pass
            
            return stats
        except Exception:
            # If the first approach fails, try a fallback method
            try:
                # Try to get schema info which might contain some metadata
                schemas = self.get_schemas()
                schema = next((s for s in schemas if s.get("class") == class_name), None)
                if schema:
                    stats["meta"] = {"schema": schema}
                    
                    # Extract replication info if available
                    if "replicationConfig" in schema:
                        stats["replication"] = schema.get("replicationConfig", {})
                    
                    # Extract sharding info if available
                    if "shardingConfig" in schema:
                        stats["sharding"] = schema.get("shardingConfig", {})
                return stats
            except Exception:
                return stats
                
    def get_shards(self, class_name: str) -> Dict[str, Any]:
        """Get shard information for a collection.
        
        Args:
            class_name: Name of the collection/class
            
        Returns:
            Dict: Shard information with keys as shard names and values as shard details
        """
        try:
            # First try the GET /schema/{class}/shards endpoint
            response = self.get(f"schema/{class_name}/shards")
            
            # Handle different API response formats
            if isinstance(response, list):
                # Convert list to dictionary using shard names as keys
                shard_dict = {}
                for shard in response:
                    if isinstance(shard, dict) and "name" in shard:
                        shard_dict[shard["name"]] = shard
                    elif isinstance(shard, dict):
                        # No name, use a generated key
                        shard_dict[f"shard_{len(shard_dict)}"] = shard
                
                # Try to update object counts from collection objects endpoint
                try:
                    # Get collection stats which includes accurate object count
                    stats = self.get_collection_stats(class_name)
                    total_objects = stats.get("object_count", 0)
                    
                    # If only one shard and we have a total count, assign all objects to it
                    if len(shard_dict) == 1 and total_objects > 0:
                        shard_key = list(shard_dict.keys())[0]
                        shard_dict[shard_key]["objectCount"] = total_objects
                except Exception:
                    # If it fails, use what we already have
                    pass
                
                return shard_dict
            return response
        except Exception:
            return {}
            
    def get_shard_details(self, class_name: str, shard_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific shard.
        
        Args:
            class_name: Name of the collection/class
            shard_name: Name of the shard
            
        Returns:
            Dict: Detailed shard information including metrics
        """
        try:
            # First get all shards
            shards = self.get_shards(class_name)
            
            # Return specific shard if found
            if shard_name in shards:
                return shards[shard_name]
                
            # Try getting additional metrics for this shard if available
            try:
                response = self.get(f"schema/{class_name}/shards/{shard_name}/metrics")
                
                # If successful, merge with basic info
                shard_info = shards.get(shard_name, {})
                if response:
                    # Make a deep copy to avoid modifying the original
                    shard_info = {**shard_info, **response}
                return shard_info
            except Exception:
                # If metrics endpoint not available, return basic info
                return shards.get(shard_name, {})
        except Exception:
            return {}
