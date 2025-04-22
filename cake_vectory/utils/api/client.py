# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Base client for interacting with the Weaviate API."""

import requests
from typing import Dict, Any, Optional
from rich.console import Console

from cake_vectory.utils.config import get_config
from cake_vectory.utils.auth import get_auth_headers

console = Console()


class WeaviateClient:
    """Base client for interacting with the Weaviate API."""

    def __init__(self):
        """Initialize the API client with configuration."""
        self.config = get_config()
        self.base_url = self.config["api_url"]
        self.session = requests.Session()

        # Set authentication headers based on config
        auth_headers = get_auth_headers(api_key=self.config.get("api_key"))
        self.session.headers.update(auth_headers)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors.

        Args:
            response: Response object from requests

        Returns:
            Dict: Parsed JSON response

        Raises:
            Exception: If the API returns an error
        """
        try:
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = f"API Error: {error_data['message']}"
                elif "error" in error_data and isinstance(error_data["error"], list):
                    errors = [
                        err.get("message", str(err)) for err in error_data["error"]
                    ]
                    error_msg = f"API Error: {'; '.join(errors)}"
            except ValueError:
                pass
            raise Exception(error_msg)

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters

        Returns:
            Dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            data: JSON data to send

        Returns:
            Dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PUT request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            data: JSON data to send

        Returns:
            Dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)

    def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PATCH request to the API.

        Args:
            endpoint: API endpoint (without base URL)
            data: JSON data to send

        Returns:
            Dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.patch(url, json=data)
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request to the API.

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            Dict: Parsed JSON response or empty dict if no content
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url)
        return self._handle_response(response)
