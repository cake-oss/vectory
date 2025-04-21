# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Main entry point for the Cake Vectory CLI."""

import typer
from rich.console import Console
from typing import Optional

from cake_vectory.commands import health, schema, collection, objects, search
from cake_vectory.utils.config import load_config

# Create the main app
app = typer.Typer(
    name="vectory",
    help="CLI tool for interacting with vector databases",
    add_completion=False,
)

# Create console for rich output
console = Console()

# Register command groups
app.add_typer(health.app, name="health", help="Check vector database health status")
app.add_typer(schema.app, name="schema", help="Manage vector database schemas")
app.add_typer(
    collection.app, name="collection", help="Manage vector database collections"
)
app.add_typer(objects.app, name="objects", help="Manage vector database objects")
app.add_typer(search.app, name="search", help="Search vector database objects")


@app.callback()
def callback(
    http_host: Optional[str] = typer.Option(
        None, "--http-host", help="Vector database HTTP host (overrides .env)"
    ),
    http_port: Optional[str] = typer.Option(
        None, "--http-port", help="Vector database HTTP port (overrides .env)"
    ),
    grpc_host: Optional[str] = typer.Option(
        None, "--grpc-host", help="Vector database gRPC host (overrides .env)"
    ),
    grpc_port: Optional[str] = typer.Option(
        None, "--grpc-port", help="Vector database gRPC port (overrides .env)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="API key for authentication (overrides .env)"
    ),
) -> None:
    """Initialize the CLI with configuration."""
    # Load configuration from .env file and environment variables
    load_config(http_host, http_port, grpc_host, grpc_port, api_key)


@app.command()
def version():
    """Show the CLI version."""
    from cake_vectory import __version__

    console.print(f"✨ Cake Vectory CLI v{__version__}")


if __name__ == "__main__":
    app()
