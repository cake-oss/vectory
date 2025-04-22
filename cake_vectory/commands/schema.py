# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Schema management commands for the Cake Vectory CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json
from typing import Optional, List, Dict, Any
import time

from cake_vectory.utils.api import WeaviateAPI
from cake_vectory.utils.config import get_config

app = typer.Typer(help="Manage vector database schemas")
console = Console()


@app.callback(invoke_without_command=True)
def schema(ctx: typer.Context):
    """Manage vector database schemas."""
    if ctx.invoked_subcommand is not None:
        return

    # Default to listing schemas if no subcommand is provided
    list_schemas()


@app.command("list")
def list_schemas():
    """List all schemas in the vector database."""
    api = WeaviateAPI()
    config = get_config()

    console.print(f"🔍 Fetching schemas from [bold]{config['api_url']}[/bold]...")

    try:
        schemas = api.get_schemas()

        if not schemas:
            console.print("ℹ️ No schemas found.")
            return

        table = Table(title=f"Vector Database Collections ({len(schemas)} found)")
        table.add_column("Collection Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Properties", style="magenta")
        table.add_column("Objects", style="yellow")

        for schema in schemas:
            class_name = schema.get("class", "Unknown")
            description = schema.get("description", "")
            properties = len(schema.get("properties", []))

            # Get object count for this collection
            try:
                stats = api.get_collection_stats(class_name)
                object_count = stats.get("object_count", 0)
            except Exception:
                object_count = "N/A"

            table.add_row(class_name, description, str(properties), str(object_count))

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error fetching schemas: [bold red]{str(e)}[/bold red]")


@app.command()
def get(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection schema to get"
    ),
):
    """Get details of a specific collection schema."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching schema for collection [bold]{collection_name}[/bold] from [bold]{config['api_url']}[/bold]..."
    )

    try:
        schemas = api.get_schemas()

        # Find the requested schema
        schema = next((s for s in schemas if s.get("class") == collection_name), None)

        if not schema:
            console.print(
                f"❌ Collection schema [bold red]{collection_name}[/bold red] not found."
            )
            return

        # Get collection stats
        try:
            stats = api.get_collection_stats(collection_name)
            object_count = stats.get("object_count", 0)
        except Exception:
            object_count = "N/A"

        # Display schema details
        console.print(
            Panel(
                f"[bold cyan]Collection:[/bold cyan] {schema.get('class')}\n"
                f"[bold green]Description:[/bold green] {schema.get('description', 'No description')}\n"
                f"[bold yellow]Object Count:[/bold yellow] {object_count}\n",
                title=f"Schema: {collection_name}",
                expand=False,
            )
        )

        # Display properties in a table
        properties = schema.get("properties", [])

        if properties:
            table = Table(title="Properties")
            table.add_column("Name", style="cyan")
            table.add_column("Data Type", style="green")
            table.add_column("Description", style="magenta")

            for prop in properties:
                name = prop.get("name", "Unknown")
                data_type = prop.get("dataType", ["Unknown"])[0]
                description = prop.get("description", "")

                table.add_row(name, data_type, description)

            console.print(table)
        else:
            console.print("ℹ️ No properties defined for this schema.")

        # Display collection metadata if available
        if stats and stats.get("meta"):
            console.print("\n[bold]Collection Metadata:[/bold]")
            meta_syntax = Syntax(
                json.dumps(stats.get("meta", {}), indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(meta_syntax)

        # Display the raw JSON
        console.print("\n[bold]Raw Schema JSON:[/bold]")
        syntax = Syntax(
            json.dumps(schema, indent=2), "json", theme="monokai", line_numbers=True
        )
        console.print(syntax)

    except Exception as e:
        console.print(f"❌ Error fetching schema: [bold red]{str(e)}[/bold red]")


@app.command()
def delete(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection schema to delete"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
):
    """Delete a collection schema from the vector database."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Preparing to delete collection [bold]{collection_name}[/bold] from [bold]{config['api_url']}[/bold]..."
    )

    # Check if the collection exists
    try:
        schemas = api.get_schemas()
        schema = next((s for s in schemas if s.get("class") == collection_name), None)

        if not schema:
            console.print(
                f"❌ Collection schema [bold red]{collection_name}[/bold red] not found."
            )
            return

        # Get object count
        try:
            stats = api.get_collection_stats(collection_name)
            object_count = stats.get("object_count", 0)
            console.print(
                f"ℹ️ Collection [bold]{collection_name}[/bold] contains [bold yellow]{object_count}[/bold yellow] objects."
            )
        except Exception:
            console.print(
                f"⚠️ Could not determine object count for [bold]{collection_name}[/bold]."
            )

        # Confirm deletion if not forced
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete the collection '{collection_name}'? This action cannot be undone."
            )
            if not confirm:
                console.print("Operation cancelled.")
                return

        # Delete the collection
        console.print(f"🗑️ Deleting collection [bold]{collection_name}[/bold]...")
        api.delete_schema(collection_name)
        console.print(
            f"✅ Collection [bold green]{collection_name}[/bold green] deleted successfully!"
        )

    except Exception as e:
        console.print(f"❌ Error deleting schema: [bold red]{str(e)}[/bold red]")
