# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Object management functionality for the Weaviate API."""

from typing import Dict, Any, Optional, List, Union

from cake_vectory.utils.api.client import WeaviateClient
import json


class ObjectsClient(WeaviateClient):
    """Client for object management operations."""
    
    def get_objects(self, class_name: str, limit: int = 10, offset: int = 0, tenant: Optional[str] = None) -> Dict[str, Any]:
        """Get objects from a class.
        
        Args:
            class_name: Name of the class to get objects from
            limit: Maximum number of objects to return
            offset: Offset for pagination
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            Dict: Object list response
        """
        params = {
            "class": class_name,
            "limit": limit,
            "offset": offset
        }
        
        if tenant:
            params["tenant"] = tenant
        
        return self.get("objects", params=params)
    
    def get_object(self, class_name: str, object_id: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific object by ID.
        
        Args:
            class_name: Name of the class the object belongs to
            object_id: ID of the object to retrieve
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            Dict: Object data
        """
        endpoint = f"objects/{class_name}/{object_id}"
        
        params = {}
        if tenant:
            params["tenant"] = tenant
        
        return self.get(endpoint, params=params)
    
    def create_object(self, object_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object.
        
        Args:
            object_data: Object data including class, properties, and optional ID
            
        Returns:
            Dict: Created object data
        """
        return self.post("objects", object_data)
    
    def update_object(self, class_name: str, object_id: str, object_data: Dict[str, Any], tenant: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing object.
        
        Args:
            class_name: Name of the class the object belongs to
            object_id: ID of the object to update
            object_data: Object data to update
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            Dict: Updated object data
        """
        endpoint = f"objects/{class_name}/{object_id}"
        
        params = {}
        if tenant:
            params["tenant"] = tenant
        
        # Use PUT for full update
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        response = self.session.put(url, json=object_data)
        return self._handle_response(response)
    
    def delete_object(self, class_name: str, object_id: str, tenant: Optional[str] = None) -> bool:
        """Delete an object.
        
        Args:
            class_name: Name of the class the object belongs to
            object_id: ID of the object to delete
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            bool: True if successful
        """
        endpoint = f"objects/{class_name}/{object_id}"
        
        params = {}
        if tenant:
            params["tenant"] = tenant
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        response = self.session.delete(url)
        self._handle_response(response)
        return True
    
    def batch_objects(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create objects in batch.
        
        Args:
            objects: List of object data
            
        Returns:
            List: List of results for each object
        """
        batch_data = {
            "objects": objects
        }
        
        response = self.post("batch/objects", batch_data)
        return response
    
    def get_collection_count(self, class_name: str, tenant: Optional[str] = None) -> int:
        """Get the total count of objects in a collection.
        
        Args:
            class_name: Name of the class to count objects from
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            int: Total count of objects in the collection
        """
        # Use GraphQL to get the count
        graphql_query = {
            "query": f"""
            {{
              Aggregate {{
                {class_name} {{
                  meta {{
                    count
                  }}
                }}
              }}
            }}
            """
        }
        
        # Add tenant if specified
        if tenant:
            graphql_query["query"] = f"""
            {{
              Aggregate {{
                {class_name}(tenant: "{tenant}") {{
                  meta {{
                    count
                  }}
                }}
              }}
            }}
            """
        
        response = self.post("graphql", graphql_query)
        
        # Extract the count from the response
        try:
            # The response structure has Vaskin1 as a list, not an object
            class_data = response.get("data", {}).get("Aggregate", {}).get(class_name, [])
            if isinstance(class_data, list) and len(class_data) > 0:
                count = class_data[0].get("meta", {}).get("count", 0)
                return count
            return 0
        except (KeyError, AttributeError, IndexError):
            return 0
