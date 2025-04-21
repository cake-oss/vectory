# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Configuration management for the Cake Vectory CLI."""

import os
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console

# Default values
DEFAULT_HTTP_HOST = "localhost"
DEFAULT_HTTP_PORT = "8080"
DEFAULT_GRPC_HOST = "localhost"
DEFAULT_GRPC_PORT = "50051"

# Global configuration
config = {
    "http_host": DEFAULT_HTTP_HOST,
    "http_port": DEFAULT_HTTP_PORT,
    "grpc_host": DEFAULT_GRPC_HOST,
    "grpc_port": DEFAULT_GRPC_PORT,
    "api_url": f"http://{DEFAULT_HTTP_HOST}:{DEFAULT_HTTP_PORT}/v1",
    "api_key": None,  # API key for authentication
}

console = Console()


def load_config(
    http_host: Optional[str] = None,
    http_port: Optional[str] = None,
    grpc_host: Optional[str] = None,
    grpc_port: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Load configuration from .env file and environment variables.

    Args:
        http_host: Optional HTTP host to override the one in .env
        http_port: Optional HTTP port to override the one in .env
        grpc_host: Optional gRPC host to override the one in .env
        grpc_port: Optional gRPC port to override the one in .env
        api_key: Optional API key for authentication

    Returns:
        dict: Configuration dictionary
    """
    # Load from .env file if it exists
    load_dotenv(override=True)

    # Update from environment variables
    env_http_host = os.getenv("WEAVIATE_HTTP_HOST")
    env_http_port = os.getenv("WEAVIATE_HTTP_PORT")
    env_grpc_host = os.getenv("WEAVIATE_GRPC_HOST")
    env_grpc_port = os.getenv("WEAVIATE_GRPC_PORT")
    env_api_key = os.getenv("WEAVIATE_API_KEY")

    if env_http_host:
        config["http_host"] = env_http_host
    if env_http_port:
        config["http_port"] = env_http_port
    if env_grpc_host:
        config["grpc_host"] = env_grpc_host
    if env_grpc_port:
        config["grpc_port"] = env_grpc_port
    if env_api_key:
        config["api_key"] = env_api_key

    # Override with command line arguments if provided
    if http_host:
        config["http_host"] = http_host
    if http_port:
        config["http_port"] = http_port
    if grpc_host:
        config["grpc_host"] = grpc_host
    if grpc_port:
        config["grpc_port"] = grpc_port
    if api_key:
        config["api_key"] = api_key

    # Construct API URL from HTTP host and port
    config["api_url"] = f"http://{config['http_host']}:{config['http_port']}/v1"

    # Ensure URL doesn't end with a slash
    if config["api_url"].endswith("/"):
        config["api_url"] = config["api_url"][:-1]

    return config


def get_config() -> dict:
    """Get the current configuration.

    Returns:
        dict: Configuration dictionary
    """
    return config
