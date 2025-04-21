"""
Search API client for vector database operations.
"""

import json
from typing import Dict, Any, Optional, List, Union, Set
from rich.console import Console

from cake_vectory.utils.api.client import WeaviateClient
from cake_vectory.utils.api.objects import ObjectsClient

console = Console()


class SearchClient(WeaviateClient):
    """Client for search operations in the vector database."""

    def __init__(self):
        """Initialize the search client."""
        super().__init__()
        self.objects_client = ObjectsClient()

    def has_vectorizer(self, class_name: str) -> bool:
        """Check if a collection has a vectorizer.

        Args:
            class_name: Name of the class to check

        Returns:
            bool: True if the collection has a vectorizer, False otherwise
        """
        # Get schema for the class
        schemas = self.get_schemas()

        # Check if the class has a vectorizer
        for schema in schemas:
            if schema.get("class") == class_name:
                vectorizer = schema.get("vectorizer", "none")
                # If vectorizer is "none", it means the collection doesn't have a vectorizer
                return vectorizer != "none"

        # If class not found, assume no vectorizer
        return False

    def search_objects(
        self,
        class_name: str,
        query_text: str,
        limit: int = 10,
        tenant: Optional[str] = None,
        filter_obj: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search for objects using text search.

        Args:
            class_name: Name of the class to search in
            query_text: Text to search for
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            filter_obj: Optional filter criteria

        Returns:
            Dict: Search results or error information
        """
        # Get all objects (since we don't have vectorized search)
        has_vectorizer = self.has_vectorizer(class_name)
        console.print(f"[dim]DEBUG: Collection has vectorizer: {has_vectorizer}[/dim]")

        if has_vectorizer and query_text:
            # For collections with vectorizers, use the default search
            # TODO: Implement vectorized search
            pass
        else:
            # For collections without vectorizers, we need to use a different approach
            if not has_vectorizer and query_text:
                console.print(
                    f"[dim]DEBUG: Using direct text search for collection without vectorizer[/dim]"
                )

                # For collections without vectorizers, just list all objects and filter client-side
                console.print(
                    f"[dim]DEBUG: Listing all objects and filtering client-side[/dim]"
                )

                # Get all objects
                all_objects = self.objects_client.get_objects(
                    class_name, limit=1000, tenant=tenant
                )

                # Simple client-side search implementation
                matched_objects = []
                for obj in (
                    all_objects.get("data", {}).get("Get", {}).get(class_name, [])
                ):
                    # Convert properties to a single string for searching
                    object_text = ""
                    properties = obj.get("text", "")
                    if properties:
                        # Simple case-insensitive text matching
                        if query_text.lower() in properties.lower():
                            matched_objects.append(obj)

                    # Limit results to the specified limit
                    if len(matched_objects) >= limit:
                        break

                # Format results in the same structure as Weaviate would return
                results = {"data": {"Get": {class_name: matched_objects[:limit]}}}

                # Add score for consistency with vectorized search
                for obj in results["data"]["Get"][class_name]:
                    obj["_additional"] = {"score": 1.0}  # Default score

                return results

            # No query text, just return all objects up to the limit
            response = self.objects_client.get_objects(
                class_name, limit=limit, tenant=tenant
            )

            # Log the response
            console.print(
                f"[dim]DEBUG: Text search response: {json.dumps(response, indent=4)}[/dim]"
            )

            # Check for errors in the response
            if "error" in response:
                console.print(f"[bold red]API Error:[/bold red] {response['error']}")
                return {"error": response["error"], "objects": []}

            return response

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
        properties: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
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
            fields: Optional list of fields to return in the results

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
            console.print(
                f"[dim]DEBUG: Collection has vectorizer: {has_vectorizer}[/dim]"
            )

            # For collections without vectorizers, use the same approach as text search
            if not has_vectorizer:
                console.print(
                    f"[dim]DEBUG: Using text search for hybrid search in collection without vectorizer[/dim]"
                )
                return self.search_objects(class_name, query, limit, tenant, filter_obj)

        # Construct GraphQL query with hybrid operator
        # Build hybrid parameters
        console.print(f"[dim]DEBUG: Setting alpha={alpha} for hybrid search[/dim]")
        hybrid_params = {"query": query, "alpha": alpha, "fusionType": fusion_type}

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
                hybrid_params_str += f'\n              {key}: "{value}"'
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

        # Determine which fields to include in the query
        if fields is None:
            # Try to detect the schema to find available fields
            try:
                available_fields = self._get_available_fields(class_name)
                fields_to_query = []
                
                # Always include text field if it exists
                if "text" in available_fields:
                    fields_to_query.append("text")
                
                # Include common metadata fields if they exist
                for field in ["full_path", "chunk_index", "total_chunks", "ts"]:
                    if field in available_fields:
                        fields_to_query.append(field)
                
                # If no fields were found, default to all available fields
                if not fields_to_query and available_fields:
                    fields_to_query = list(available_fields)
                
                # If still no fields, use a minimal default set
                if not fields_to_query:
                    fields_to_query = ["text"]
                    
                console.print(f"[dim]DEBUG: Auto-detected fields for query: {fields_to_query}[/dim]")
            except Exception as e:
                console.print(f"[dim]DEBUG: Error detecting schema: {e}, using default fields[/dim]")
                # Default to the original set of fields
                fields_to_query = ["text", "full_path", "chunk_index", "total_chunks", "ts"]
        else:
            fields_to_query = fields
        
        # Construct the fields part of the query
        fields_str = "\n                  ".join(fields_to_query)
        
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  {f'where: {json.dumps(filter_obj)}' if filter_obj else ''}
                  {search_clause}
                ) {{
                  {fields_str}
                  _additional {{
                    id
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
        response = self.objects_client.execute_graphql(graphql_query)

        # Debug log the response
        console.print(
            f"[dim]DEBUG: Hybrid search response: {json.dumps(response, indent=4)}[/dim]"
        )

        # First check for GraphQL errors
        if response and "errors" in response:
            errors = response["errors"]
            error_messages = []

            for error in errors:
                message = error.get("message", "Unknown error")
                locations = error.get("locations", [])
                if locations:
                    location_str = ", ".join(
                        [
                            f"line {loc.get('line', '?')}, column {loc.get('column', '?')}"
                            for loc in locations
                        ]
                    )
                    error_messages.append(f"GraphQL error at {location_str}: {message}")
                else:
                    error_messages.append(f"GraphQL error: {message}")

            # Join all error messages
            error_string = "\n".join(error_messages)
            console.print(f"[bold red]GraphQL Error:[/bold red] {error_string}")

            # Return error format suitable for the CLI
            return {"error": error_string, "objects": []}

        # Format response to match expected format in commands/search.py
        if response and "data" in response and "Get" in response["data"]:
            get_data = response["data"]["Get"]
            if class_name in get_data and get_data[class_name]:
                # Transform the data to match the expected format
                objects = []
                for obj in get_data[class_name]:
                    # Extract ID from _additional.id
                    obj_id = obj.get("_additional", {}).get("id", "Unknown")

                    # Build properties from other fields
                    properties = {}
                    for key, value in obj.items():
                        if key != "_additional":
                            properties[key] = value

                    # Build additional data including score
                    additional = {}
                    if "_additional" in obj and "score" in obj["_additional"]:
                        additional["score"] = float(obj["_additional"]["score"])

                    # Create the transformed object
                    transformed_obj = {
                        "id": obj_id,
                        "properties": properties,
                        "additional": additional,
                    }
                    objects.append(transformed_obj)

                return {"objects": objects}
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] No results found for class '{class_name}' in the GraphQL response"
                )
                return {"objects": []}

        # If we get an empty response
        if not response or not response.get("data"):
            console.print(
                "[yellow]Warning:[/yellow] Empty response from GraphQL server"
            )

        # If we couldn't transform the response, return it as is
        return {"objects": [], "raw_response": response}

    def vector_search(
        self,
        class_name: str,
        vector: List[float],
        limit: int = 10,
        tenant: Optional[str] = None,
        filter_obj: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Search for objects using vector search.

        Args:
            class_name: Name of the class to search in
            vector: Vector to search for
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            filter_obj: Optional filter criteria
            fields: Optional list of fields to return in the results

        Returns:
            Dict: Search results
        """
        # Construct GraphQL query with nearVector operator
        # Determine which fields to include in the query
        if fields is None:
            # Try to detect the schema to find available fields
            try:
                available_fields = self._get_available_fields(class_name)
                fields_to_query = []
                
                # Always include text field if it exists
                if "text" in available_fields:
                    fields_to_query.append("text")
                
                # Include common metadata fields if they exist
                for field in ["full_path", "chunk_index", "total_chunks", "ts"]:
                    if field in available_fields:
                        fields_to_query.append(field)
                
                # If no fields were found, default to all available fields
                if not fields_to_query and available_fields:
                    fields_to_query = list(available_fields)
                
                # If still no fields, use a minimal default set
                if not fields_to_query:
                    fields_to_query = ["text"]
                    
                console.print(f"[dim]DEBUG: Auto-detected fields for vector search query: {fields_to_query}[/dim]")
            except Exception as e:
                console.print(f"[dim]DEBUG: Error detecting schema: {e}, using default fields[/dim]")
                # Default to the original set of fields
                fields_to_query = ["text", "full_path", "chunk_index", "total_chunks", "ts"]
        else:
            fields_to_query = fields
        
        # Construct the fields part of the query
        fields_str = "\n                  ".join(fields_to_query)
        
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  {f'where: {json.dumps(filter_obj)}' if filter_obj else ''}
                  nearVector: {{
                    vector: {json.dumps(vector)}
                  }}
                ) {{
                  {fields_str}
                  _additional {{
                    id
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
        return self.objects_client.execute_graphql(graphql_query)

    def filter_objects(
        self,
        class_name: str,
        filter_obj: Dict[str, Any],
        limit: int = 10,
        tenant: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Filter objects using a filter object.

        Args:
            class_name: Name of the class to filter
            filter_obj: Filter criteria
            limit: Maximum number of results to return
            tenant: Optional tenant name for multi-tenant collections
            fields: Optional list of fields to return in the results

        Returns:
            Dict: Filtered results or error information
        """
        # Check if collection has a vectorizer
        has_vectorizer = self.has_vectorizer(class_name)

        # For collections without vectorizers, use client-side filtering
        if not has_vectorizer:
            console.print(
                f"[dim]DEBUG: Using client-side filtering for collection without vectorizer[/dim]"
            )

            # Get all objects
            all_objects = self.objects_client.get_objects(
                class_name, limit=1000, tenant=tenant
            )

            # TODO: Implement client-side filtering
            return all_objects

        # Construct GraphQL query with where operator
        # Determine which fields to include in the query
        if fields is None:
            # Try to detect the schema to find available fields
            try:
                available_fields = self._get_available_fields(class_name)
                fields_to_query = []
                
                # Always include text field if it exists
                if "text" in available_fields:
                    fields_to_query.append("text")
                
                # Include common metadata fields if they exist
                for field in ["full_path", "chunk_index", "total_chunks", "ts"]:
                    if field in available_fields:
                        fields_to_query.append(field)
                
                # If no fields were found, default to all available fields
                if not fields_to_query and available_fields:
                    fields_to_query = list(available_fields)
                
                # If still no fields, use a minimal default set
                if not fields_to_query:
                    fields_to_query = ["text"]
                    
                console.print(f"[dim]DEBUG: Auto-detected fields for filter query: {fields_to_query}[/dim]")
            except Exception as e:
                console.print(f"[dim]DEBUG: Error detecting schema: {e}, using default fields[/dim]")
                # Default to the original set of fields
                fields_to_query = ["text", "full_path", "chunk_index", "total_chunks", "ts"]
        else:
            fields_to_query = fields
        
        # Construct the fields part of the query
        fields_str = "\n                  ".join(fields_to_query)
        
        graphql_query = {
            "query": f"""
            {{
              Get {{
                {class_name}(
                  limit: {limit}
                  where: {json.dumps(filter_obj)}
                ) {{
                  {fields_str}
                  _additional {{
                    id
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

        # Log the query
        console.print(f"[dim]DEBUG: Filter query: {json.dumps(graphql_query)}[/dim]")

        # Execute GraphQL query
        response = self.objects_client.execute_graphql(graphql_query)

        # Debug log the response
        console.print(
            f"[dim]DEBUG: Filter response: {json.dumps(response, indent=4)}[/dim]"
        )

        # First check for GraphQL errors
        if response and "errors" in response:
            errors = response["errors"]
            error_messages = []

            for error in errors:
                message = error.get("message", "Unknown error")
                locations = error.get("locations", [])
                if locations:
                    location_str = ", ".join(
                        [
                            f"line {loc.get('line', '?')}, column {loc.get('column', '?')}"
                            for loc in locations
                        ]
                    )
                    error_messages.append(f"GraphQL error at {location_str}: {message}")
                else:
                    error_messages.append(f"GraphQL error: {message}")

            # Join all error messages
            error_string = "\n".join(error_messages)
            console.print(f"[bold red]GraphQL Error:[/bold red] {error_string}")

            # Return error format suitable for the CLI
            return {"error": error_string, "objects": []}

        # Format response to match expected format in commands/search.py
        if response and "data" in response and "Get" in response["data"]:
            get_data = response["data"]["Get"]
            if class_name in get_data and get_data[class_name]:
                # Transform the data to match the expected format
                objects = []
                for obj in get_data[class_name]:
                    # Extract ID from _additional.id
                    obj_id = obj.get("_additional", {}).get("id", "Unknown")

                    # Build properties from other fields
                    properties = {}
                    for key, value in obj.items():
                        if key != "_additional":
                            properties[key] = value

                    # Build additional data including score
                    additional = {}
                    if "_additional" in obj and "score" in obj["_additional"]:
                        additional["score"] = float(obj["_additional"]["score"])

                    # Create the transformed object
                    transformed_obj = {
                        "id": obj_id,
                        "properties": properties,
                        "additional": additional,
                    }
                    objects.append(transformed_obj)

                return {"objects": objects}
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] No results found for class '{class_name}' in the GraphQL response"
                )
                return {"objects": []}

        # If we get an empty response
        if not response or not response.get("data"):
            console.print(
                "[yellow]Warning:[/yellow] Empty response from GraphQL server"
            )

        # If we couldn't transform the response, return it as is
        return {"objects": [], "raw_response": response}

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all schemas from the vector database.

        Returns:
            List[Dict]: List of schemas
        """
        # Construct GraphQL query to get schemas
        graphql_query = {
            "query": """
            {
              Schema {
                objects {
                  class
                  vectorizer
                  properties {
                    name
                    dataType
                  }
                }
              }
            }
            """
        }

        # Execute GraphQL query
        response = self.objects_client.execute_graphql(graphql_query)

        # Extract schemas from response
        schemas = response.get("data", {}).get("Schema", {}).get("objects", [])
        return schemas
        
    def _get_available_fields(self, class_name: str) -> Set[str]:
        """Get all available fields for a specific class.
        
        Args:
            class_name: Name of the class to get fields for
            
        Returns:
            Set[str]: Set of available field names
        """
        schemas = self.get_schemas()
        fields = set()
        
        for schema in schemas:
            if schema.get("class") == class_name:
                properties = schema.get("properties", [])
                for prop in properties:
                    fields.add(prop.get("name", ""))
                break
                
        return fields
