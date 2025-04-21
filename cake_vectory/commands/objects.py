# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Object management commands for the Cake Vectory CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json
from typing import Optional, List, Dict, Any, Union
import uuid

from cake_vectory.utils.api import WeaviateAPI
from cake_vectory.utils.config import get_config

app = typer.Typer(help="Manage vector database objects")
console = Console()


@app.callback(invoke_without_command=True)
def objects(ctx: typer.Context):
    """Manage vector database objects."""
    if ctx.invoked_subcommand is not None:
        return

    # Default to listing objects if no subcommand is provided
    list_objects()


@app.command("list")
def list_objects(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to list objects from"
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of objects to return"
    ),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset for pagination"),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """List objects in a collection."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching objects from collection [bold]{collection_name}[/bold] in [bold]{config['api_url']}[/bold]..."
    )

    try:
        objects = api.get_objects(
            collection_name, limit=limit, offset=offset, tenant=tenant
        )

        if not objects or not objects.get("objects", []):
            console.print(
                f"ℹ️ No objects found in collection [bold]{collection_name}[/bold]."
            )
            return

        object_list = objects.get("objects", [])

        # Get the total count using the new method
        total_count = api.get_collection_count(collection_name, tenant=tenant)

        console.print(
            f"📊 Found [bold]{total_count}[/bold] objects in total, showing {len(object_list)}."
        )

        table = Table(title=f"Objects in {collection_name}")
        table.add_column("ID", style="cyan")
        table.add_column("Properties", style="green")
        table.add_column("Created", style="magenta")

        for obj in object_list:
            obj_id = obj.get("id", "Unknown")

            # Format properties for display
            properties = obj.get("properties", {})
            props_str = ", ".join([f"{k}: {str(v)}" for k, v in properties.items()])

            # Format creation time
            created = obj.get("creationTimeUnix", 0)
            if created:
                from datetime import datetime

                created_str = datetime.fromtimestamp(created / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                created_str = "Unknown"

            table.add_row(obj_id, props_str, created_str)

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error fetching objects: [bold red]{str(e)}[/bold red]")


@app.command("get")
def get_object(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection the object belongs to"
    ),
    object_id: str = typer.Argument(..., help="ID of the object to retrieve"),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Get a specific object by ID."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching object [bold]{object_id}[/bold] from collection [bold]{collection_name}[/bold] in [bold]{config['api_url']}[/bold]..."
    )

    try:
        obj = api.get_object(collection_name, object_id, tenant=tenant)

        if not obj:
            console.print(
                f"❌ Object [bold red]{object_id}[/bold red] not found in collection [bold]{collection_name}[/bold]."
            )
            return

        # Display object details
        console.print(
            Panel(
                f"[bold cyan]ID:[/bold cyan] {obj.get('id')}\n"
                f"[bold green]Collection:[/bold green] {obj.get('class')}\n"
                f"[bold yellow]Created:[/bold yellow] {datetime.fromtimestamp(obj.get('creationTimeUnix', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"[bold magenta]Updated:[/bold magenta] {datetime.fromtimestamp(obj.get('lastUpdateTimeUnix', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if obj.get('lastUpdateTimeUnix') else 'Never'}\n",
                title=f"Object: {object_id}",
                expand=False,
            )
        )

        # Display properties
        properties = obj.get("properties", {})
        if properties:
            console.print("\n[bold]Properties:[/bold]")
            props_syntax = Syntax(
                json.dumps(properties, indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(props_syntax)
        else:
            console.print("\nℹ️ No properties defined for this object.")

        # Display vector if included
        if "vector" in obj:
            console.print("\n[bold]Vector:[/bold] (first 5 dimensions shown)")
            vector = obj.get("vector", [])
            vector_preview = vector[:5]
            console.print(f"{vector_preview} ... ({len(vector)} dimensions)")

        # Display additional metadata if available
        if "additional" in obj and obj["additional"]:
            console.print("\n[bold]Additional Metadata:[/bold]")
            meta_syntax = Syntax(
                json.dumps(obj.get("additional", {}), indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(meta_syntax)

    except Exception as e:
        console.print(f"❌ Error fetching object: [bold red]{str(e)}[/bold red]")


@app.command("create")
def create_object(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to create the object in"
    ),
    properties_json: str = typer.Option(
        None, "--properties", "-p", help="JSON string of properties"
    ),
    properties_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="JSON file containing properties"
    ),
    object_id: Optional[str] = typer.Option(
        None, "--id", help="Custom UUID for the object (generated if not provided)"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Create a new object in a collection."""
    if not properties_json and not properties_file:
        console.print("❌ Either --properties or --file must be provided.")
        return

    api = WeaviateAPI()
    config = get_config()

    # Load properties
    properties = {}
    if properties_file:
        try:
            with open(properties_file, "r") as f:
                properties = json.load(f)
        except Exception as e:
            console.print(
                f"❌ Error reading properties file: [bold red]{str(e)}[/bold red]"
            )
            return
    elif properties_json:
        try:
            properties = json.loads(properties_json)
        except Exception as e:
            console.print(
                f"❌ Error parsing properties JSON: [bold red]{str(e)}[/bold red]"
            )
            return

    # Generate UUID if not provided
    if not object_id:
        object_id = str(uuid.uuid4())

    console.print(
        f"🔍 Creating object in collection [bold]{collection_name}[/bold] with ID [bold]{object_id}[/bold]..."
    )

    try:
        # Prepare object data
        object_data = {
            "class": collection_name,
            "id": object_id,
            "properties": properties,
        }

        if tenant:
            object_data["tenant"] = tenant

        # Create the object
        result = api.create_object(object_data)

        console.print(
            f"✅ Object created successfully with ID: [bold green]{result.get('id', object_id)}[/bold green]"
        )

    except Exception as e:
        console.print(f"❌ Error creating object: [bold red]{str(e)}[/bold red]")


@app.command("update")
def update_object(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection the object belongs to"
    ),
    object_id: str = typer.Argument(..., help="ID of the object to update"),
    properties_json: str = typer.Option(
        None, "--properties", "-p", help="JSON string of properties to update"
    ),
    properties_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="JSON file containing properties to update"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Update an existing object."""
    if not properties_json and not properties_file:
        console.print("❌ Either --properties or --file must be provided.")
        return

    api = WeaviateAPI()
    config = get_config()

    # Load properties
    properties = {}
    if properties_file:
        try:
            with open(properties_file, "r") as f:
                properties = json.load(f)
        except Exception as e:
            console.print(
                f"❌ Error reading properties file: [bold red]{str(e)}[/bold red]"
            )
            return
    elif properties_json:
        try:
            properties = json.loads(properties_json)
        except Exception as e:
            console.print(
                f"❌ Error parsing properties JSON: [bold red]{str(e)}[/bold red]"
            )
            return

    console.print(
        f"🔍 Updating object [bold]{object_id}[/bold] in collection [bold]{collection_name}[/bold]..."
    )

    try:
        # Prepare object data
        object_data = {"properties": properties}

        # Update the object
        api.update_object(collection_name, object_id, object_data, tenant=tenant)

        console.print(
            f"✅ Object [bold green]{object_id}[/bold green] updated successfully!"
        )

    except Exception as e:
        console.print(f"❌ Error updating object: [bold red]{str(e)}[/bold red]")


@app.command("delete")
def delete_object(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection the object belongs to"
    ),
    object_id: str = typer.Argument(..., help="ID of the object to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Delete an object."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Preparing to delete object [bold]{object_id}[/bold] from collection [bold]{collection_name}[/bold]..."
    )

    # Confirm deletion if not forced
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to delete the object '{object_id}'? This action cannot be undone."
        )
        if not confirm:
            console.print("Operation cancelled.")
            return

    try:
        # Delete the object
        api.delete_object(collection_name, object_id, tenant=tenant)
        console.print(
            f"✅ Object [bold green]{object_id}[/bold green] deleted successfully!"
        )

    except Exception as e:
        console.print(f"❌ Error deleting object: [bold red]{str(e)}[/bold red]")


@app.command("search")
def search_objects(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to search in"
    ),
    query_text: str = typer.Option(
        None, "--text", "-t", help="Text to search for (will be vectorized)"
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of results to return"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", help="Tenant name for multi-tenant collections"
    ),
    filter_json: Optional[str] = typer.Option(
        None, "--filter", help="JSON string with filter criteria"
    ),
):
    """Search for objects using text or vector search."""
    if not query_text:
        console.print("❌ At least one search parameter (--text) must be provided.")
        return

    api = WeaviateAPI()
    config = get_config()

    # Parse filter if provided
    filter_obj = None
    if filter_json:
        try:
            filter_obj = json.loads(filter_json)
        except Exception as e:
            console.print(
                f"❌ Error parsing filter JSON: [bold red]{str(e)}[/bold red]"
            )
            return

    console.print(
        f"🔍 Searching in collection [bold]{collection_name}[/bold] for: [bold]{query_text}[/bold]..."
    )

    try:
        # Perform the search
        results = api.search_objects(
            class_name=collection_name,
            query_text=query_text,
            limit=limit,
            tenant=tenant,
            filter_obj=filter_obj,
        )

        objects = results.get("objects", [])

        if not objects:
            console.print("ℹ️ No matching objects found.")
            return

        console.print(f"📊 Found [bold]{len(objects)}[/bold] matching objects.")

        table = Table(title=f"Search Results in '{collection_name}' for '{query_text}'")
        table.add_column("ID", style="cyan")
        table.add_column("Properties", style="green")
        table.add_column("Score", style="magenta")

        for obj in objects:
            obj_id = obj.get("id", "Unknown")

            # Format properties for display
            properties = obj.get("properties", {})
            props_str = ", ".join([f"{k}: {str(v)}" for k, v in properties.items()])

            # Get score if available
            score = "N/A"
            if "additional" in obj and "score" in obj["additional"]:
                score = f"{obj['additional']['score']:.4f}"

            table.add_row(obj_id, props_str, score)

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error searching objects: [bold red]{str(e)}[/bold red]")


@app.command("count")
def count_objects(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to count objects from"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Get the total count of objects in a collection."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Counting objects in collection [bold]{collection_name}[/bold] in [bold]{config['api_url']}[/bold]..."
    )

    try:
        # Get the total count
        count = api.get_collection_count(collection_name, tenant=tenant)

        console.print(
            f"📊 Collection [bold]{collection_name}[/bold] contains [bold green]{count}[/bold green] objects."
        )

    except Exception as e:
        console.print(f"❌ Error counting objects: [bold red]{str(e)}[/bold red]")


@app.command("batch")
def batch_objects(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to create objects in"
    ),
    input_file: str = typer.Argument(
        ..., help="JSON file containing array of objects to create"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", help="Tenant name for multi-tenant collections"
    ),
):
    """Batch create objects from a JSON file."""
    api = WeaviateAPI()
    config = get_config()

    console.print(f"🔍 Loading objects from [bold]{input_file}[/bold]...")

    try:
        # Load objects from file
        with open(input_file, "r") as f:
            objects_data = json.load(f)

        if not isinstance(objects_data, list):
            console.print("❌ Input file must contain a JSON array of objects.")
            return

        console.print(
            f"📦 Preparing to create [bold]{len(objects_data)}[/bold] objects in collection [bold]{collection_name}[/bold]..."
        )

        # Prepare batch objects
        batch_objects = []
        for obj_data in objects_data:
            # Ensure each object has the collection name
            obj = obj_data.copy()
            obj["class"] = collection_name

            # Add tenant if specified
            if tenant:
                obj["tenant"] = tenant

            # Generate UUID if not provided
            if "id" not in obj:
                obj["id"] = str(uuid.uuid4())

            batch_objects.append(obj)

        # Create batch objects
        results = api.batch_objects(batch_objects)

        # Count successes and failures
        success_count = 0
        failure_count = 0

        for result in results:
            if result.get("result", {}).get("status") == "SUCCESS":
                success_count += 1
            else:
                failure_count += 1

        console.print(
            f"✅ Batch operation completed: [bold green]{success_count}[/bold green] objects created successfully, [bold red]{failure_count}[/bold red] failed."
        )

        if failure_count > 0:
            console.print("\n[bold]Failed objects:[/bold]")
            for result in results:
                if result.get("result", {}).get("status") != "SUCCESS":
                    console.print(f"❌ Object ID: {result.get('id', 'Unknown')}")
                    console.print(
                        f"   Error: {result.get('result', {}).get('errors', 'Unknown error')}"
                    )

    except Exception as e:
        console.print(f"❌ Error in batch operation: [bold red]{str(e)}[/bold red]")


from datetime import datetime
