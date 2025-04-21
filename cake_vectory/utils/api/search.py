# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Search functionality for the Weaviate API."""

import json
from typing import Dict, Any, Optional, List, Union
from rich.console import Console

from cake_vectory.utils.api.client import WeaviateClient
from cake_vectory.utils.api.objects import ObjectsClient

console = Console()


class SearchClient(ObjectsClient):
    """Client for search operations."""
    
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
    
    def search_objects(
        self, 
        class_name: str, 
        query_text: Optional[str] = None,
        limit: int = 10,
        tenant: Optional[str] = None,
        filter_obj: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Search for objects using GraphQL.
        
        Args:
            class_name: Name of the class to search in
            query_text: Text to search for (will be vectorized)
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            filter_obj: Optional filter criteria
            vector: Optional vector to use instead of generating one from query text
            
        Returns:
            Dict: Search results
        """
        # If vector is provided, we skip the vectorizer check
        if vector is not None:
            console.print(f"[dim]DEBUG: Using provided vector for search[/dim]")
        else:
            # Check if collection has a vectorizer
            has_vectorizer = self.has_vectorizer(class_name)
            console.print(f"[dim]DEBUG: Collection has vectorizer: {has_vectorizer}[/dim]")
            
            # For collections without vectorizers, we need to use a different approach
            if not has_vectorizer and query_text:
                console.print(f"[dim]DEBUG: Using direct text search for collection without vectorizer[/dim]")
                
                # For collections without vectorizers, just list all objects and filter client-side
                console.print(f"[dim]DEBUG: Listing all objects and filtering client-side[/dim]")
                
                # Get all objects
                objects_response = self.get_objects(class_name, limit=100)
                
                # Filter objects client-side
                results = {"objects": []}
                
                if "objects" in objects_response:
                    for obj in objects_response["objects"]:
                        # Check if the query text is in any of the object's properties
                        properties = obj.get("properties", {})
                        text = properties.get("text", "").lower()
                        metadata_str = properties.get("metadata_str", "").lower()
                        
                        if query_text.lower() in text or query_text.lower() in metadata_str:
                            # Format object data
                            formatted_obj = {
                                "id": obj.get("id", ""),
                                "properties": properties,
                                "additional": {
                                    "score": 1.0  # Default score
                                }
                            }
                            
                            results["objects"].append(formatted_obj)
                
                # Sort results by relevance (simple exact match scoring)
                results["objects"].sort(
                    key=lambda obj: (
                        1 if query_text.lower() in obj["properties"].get("text", "").lower() else 0,
                        1 if query_text.lower() in obj["properties"].get("metadata_str", "").lower() else 0
                    ),
                    reverse=True
                )
                
                # Apply limit
                results["objects"] = results["objects"][:limit]
                
                return results
        
        # Construct the appropriate search clause
        search_clause = ""
        if vector is not None:
            # Use nearVector with the provided vector
            search_clause = f'nearVector: {{ vector: {json.dumps(vector)} }}'
        elif query_text:
            # If no vector is provided, use the standard approach based on vectorizer
            has_vectorizer = self.has_vectorizer(class_name)
            if has_vectorizer:
                # Use nearText for collections with vectorizers
                search_clause = f'nearText: {{ concepts: ["{query_text}"] }}'
            else:
                # Use BM25 for collections without vectorizers (fallback, should not reach here)
                search_clause = f'bm25: {{ query: "{query_text}" }}'
        
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  {f'where: {json.dumps(filter_obj)}' if filter_obj else ''}
                  {search_clause}
                ) {{
                  id
                  properties
                  _additional {{
                    score
                  }}
                }}
              }}
            }}
            """
        }
        
        # Add tenant if specified
        if tenant:
            graphql_query["tenant"] = tenant
        
        # Execute GraphQL query
        response = self.post("graphql", graphql_query)
        
        # Extract and format results
        results = {"objects": []}
        
        if response and "data" in response and "Get" in response["data"] and class_name in response["data"]["Get"]:
            objects = response["data"]["Get"][class_name]
            
            for obj in objects:
                # Format object data
                formatted_obj = {
                    "id": obj.get("id"),
                    "properties": obj.get("properties", {}),
                    "additional": {
                        "score": obj.get("_additional", {}).get("score")
                    }
                }
                
                results["objects"].append(formatted_obj)
        
        return results
    
    def hybrid_search(
        self, 
        class_name: str, 
        query: str,
        alpha: float = 0.5,
        limit: int = 10,
        tenant: Optional[str] = None,
        filter_obj: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None,
        fusion_type: str = "rankedFusion",
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search for objects using hybrid search (vector + keyword).
        
        Args:
            class_name: Name of the class to search in
            query: Text to search for
            alpha: Balance between vector and keyword search (0.0-1.0)
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            filter_obj: Optional filter criteria
            vector: Optional vector to use instead of generating one from query text
            fusion_type: Type of fusion to use (rankedFusion or relativeScoreFusion)
            properties: Optional list of properties to search in
            
        Returns:
            Dict: Search results
        """
        # If vector is provided, we don't need to check for a vectorizer
        # as we'll use the provided vector directly
        if vector is not None:
            console.print(f"[dim]DEBUG: Using provided vector for hybrid search[/dim]")
        else:
            # Check if collection has a vectorizer
            has_vectorizer = self.has_vectorizer(class_name)
            console.print(f"[dim]DEBUG: Collection has vectorizer: {has_vectorizer}[/dim]")
            
            # For collections without vectorizers, use the same approach as text search
            if not has_vectorizer:
                console.print(f"[dim]DEBUG: Using text search for hybrid search in collection without vectorizer[/dim]")
                return self.search_objects(class_name, query, limit, tenant, filter_obj)
        
        # Construct GraphQL query with hybrid operator
        # Build hybrid parameters
        hybrid_params = {
            "query": query,
            "alpha": alpha,
            "fusionType": fusion_type
        }
        
        # Add vector if provided
        if vector is not None:
            hybrid_params["vector"] = vector
        
        # Add properties if provided
        if properties is not None and len(properties) > 0:
            hybrid_params["properties"] = properties
        
        # Construct the search clause
        hybrid_params_str = ""
        for key, value in hybrid_params.items():
            if key == "query":
                hybrid_params_str += f"\n              {key}: \"{value}\""
            elif key == "alpha" or key == "fusionType":
                hybrid_params_str += f"\n              {key}: {value}"
            elif key == "vector":
                hybrid_params_str += f"\n              {key}: {json.dumps(value)}"
            elif key == "properties":
                properties_str = json.dumps(value)
                hybrid_params_str += f"\n              {key}: {properties_str}"
        
        search_clause = f"""
        hybrid: {{{hybrid_params_str}
        }}
        """
        
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  {f'where: {json.dumps(filter_obj)}' if filter_obj else ''}
                  {search_clause}
                ) {{
                  id
                  properties
                  _additional {{
                    score
                  }}
                }}
              }}
            }}
            """
        }
        
        # Add tenant if specified
        if tenant:
            graphql_query["tenant"] = tenant
        
        # Execute GraphQL query
        response = self.post("graphql", graphql_query)
        
        # Extract and format results
        results = {"objects": []}
        
        if response and "data" in response and "Get" in response["data"] and class_name in response["data"]["Get"]:
            objects = response["data"]["Get"][class_name]
            
            for obj in objects:
                # Format object data
                formatted_obj = {
                    "id": obj.get("id"),
                    "properties": obj.get("properties", {}),
                    "additional": {
                        "score": obj.get("_additional", {}).get("score")
                    }
                }
                
                results["objects"].append(formatted_obj)
        
        return results
    
    def filter_objects(
        self, 
        class_name: str, 
        filter_obj: Dict[str, Any],
        limit: int = 10,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for objects using filters only.
        
        Args:
            class_name: Name of the class to search in
            filter_obj: Filter criteria
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            
        Returns:
            Dict: Search results
        """
        # Check if we're using a vectorizer
        has_vectorizer = self.has_vectorizer(class_name)
        
        # For collections without vectorizers, use client-side filtering
        if not has_vectorizer:
            console.print(f"[dim]DEBUG: Using client-side filtering for collection without vectorizer[/dim]")
            
            # Get all objects
            objects_response = self.get_objects(class_name, limit=100)
            
            # Filter objects client-side
            results = {"objects": []}
            
            if "objects" in objects_response:
                for obj in objects_response["objects"]:
                    # Check if the object matches the filter
                    properties = obj.get("properties", {})
                    
                    # Simple client-side filtering for common operators
                    matches = False
                    
                    # Handle ContainsAny operator
                    if filter_obj.get("operator") == "ContainsAny" and "path" in filter_obj and "valueText" in filter_obj:
                        path = filter_obj["path"][0] if isinstance(filter_obj["path"], list) else filter_obj["path"]
                        value_text = filter_obj["valueText"]
                        if not isinstance(value_text, list):
                            value_text = [value_text]
                        
                        property_value = properties.get(path, "").lower()
                        for text in value_text:
                            if text.lower() in property_value:
                                matches = True
                                break
                    
                    # Handle Like operator
                    elif filter_obj.get("operator") == "Like" and "path" in filter_obj and "valueText" in filter_obj:
                        path = filter_obj["path"][0] if isinstance(filter_obj["path"], list) else filter_obj["path"]
                        value_text = filter_obj["valueText"]
                        
                        # Convert Like pattern to simple contains
                        # Remove * wildcards for simple contains check
                        simple_text = value_text.replace("*", "")
                        
                        property_value = properties.get(path, "").lower()
                        if simple_text.lower() in property_value:
                            matches = True
                    
                    # Add more operators as needed
                    
                    if matches:
                        # Format object data
                        formatted_obj = {
                            "id": obj.get("id", ""),
                            "properties": properties,
                            "additional": {
                                "score": 1.0  # Default score
                            }
                        }
                        
                        results["objects"].append(formatted_obj)
            
            # Apply limit
            results["objects"] = results["objects"][:limit]
            
            return results
        
        # For collections with vectorizers, use the standard approach
        # Construct GraphQL query
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  where: {json.dumps(filter_obj)}
                ) {{
                  id
                  properties
                  _additional {{
                    score
                  }}
                }}
              }}
            }}
            """
        }
        
        # Add tenant if specified
        if tenant:
            graphql_query["tenant"] = tenant
        
        # Execute GraphQL query
        response = self.post("graphql", graphql_query)
        
        # Extract and format results
        results = {"objects": []}
        
        if response and "data" in response and "Get" in response["data"] and class_name in response["data"]["Get"]:
            objects = response["data"]["Get"][class_name]
            
            for obj in objects:
                # Format object data
                formatted_obj = {
                    "id": obj.get("id"),
                    "properties": obj.get("properties", {}),
                    "additional": {
                        "score": obj.get("_additional", {}).get("score")
                    }
                }
                
                results["objects"].append(formatted_obj)
        
        return results
