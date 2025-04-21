# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Collection management commands for the Cake Vectory CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json
from typing import Optional, List, Dict, Any

from cake_vectory.utils.api import WeaviateAPI
from cake_vectory.utils.config import get_config

app = typer.Typer(help="Manage vector database collections")
console = Console()

# Create a shards subcommand group
shards_app = typer.Typer(help="Manage collection shards")
app.add_typer(shards_app, name="shards")


@app.callback(invoke_without_command=True)
def collection(ctx: typer.Context):
    """Manage vector database collections."""
    if ctx.invoked_subcommand is not None:
        return

    # Default to listing collections if no subcommand is provided
    list_collections()


@app.command("list")
def list_collections():
    """List all collections in the vector database."""
    api = WeaviateAPI()
    config = get_config()

    console.print(f"🔍 Fetching collections from [bold]{config['api_url']}[/bold]...")

    try:
        schemas = api.get_schemas()

        if not schemas:
            console.print("ℹ️ No collections found.")
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
        console.print(f"❌ Error fetching collections: [bold red]{str(e)}[/bold red]")


@app.command()
def info(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to get info for"
    ),
):
    """Get detailed information about a collection."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching info for collection [bold]{collection_name}[/bold] from [bold]{config['api_url']}[/bold]..."
    )

    try:
        schemas = api.get_schemas()

        # Find the requested schema
        schema = next((s for s in schemas if s.get("class") == collection_name), None)

        if not schema:
            console.print(
                f"❌ Collection [bold red]{collection_name}[/bold red] not found."
            )
            return

        # Get collection stats
        try:
            stats = api.get_collection_stats(collection_name)
            object_count = stats.get("object_count", 0)
        except Exception as e:
            console.print(f"⚠️ Could not get complete stats: {str(e)}")
            object_count = "N/A"
            stats = {"meta": {}}

        # Extract replication and sharding info
        replication_config = stats.get("replication", {})
        sharding_config = stats.get("sharding", {})

        # Build panel content with replication and sharding summary if available
        panel_content = (
            f"[bold cyan]Collection:[/bold cyan] {schema.get('class')}\n"
            f"[bold green]Description:[/bold green] {schema.get('description', 'No description')}\n"
            f"[bold yellow]Object Count:[/bold yellow] {object_count}\n"
        )

        # Add replication info if available
        if replication_config:
            factor = replication_config.get("factor", "N/A")
            panel_content += f"[bold blue]Replication Factor:[/bold blue] {factor}\n"

        # Add sharding info if available
        if sharding_config:
            strategy = sharding_config.get("desiredCount", "N/A")
            panel_content += f"[bold magenta]Shard Count:[/bold magenta] {strategy}\n"

        # Display collection details
        console.print(
            Panel(panel_content, title=f"Collection: {collection_name}", expand=False)
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
            console.print("ℹ️ No properties defined for this collection.")

        # Display replication configuration if available
        if replication_config:
            console.print("\n[bold blue]Replication Configuration:[/bold blue]")
            rep_syntax = Syntax(
                json.dumps(replication_config, indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(rep_syntax)

        # Display sharding configuration if available
        if sharding_config:
            console.print("\n[bold magenta]Sharding Configuration:[/bold magenta]")
            shard_syntax = Syntax(
                json.dumps(sharding_config, indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(shard_syntax)

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

    except Exception as e:
        console.print(
            f"❌ Error fetching collection info: [bold red]{str(e)}[/bold red]"
        )


@app.command()
def delete(
    collection_name: str = typer.Argument(..., help="Name of the collection to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
):
    """Delete a collection from the vector database."""
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
                f"❌ Collection [bold red]{collection_name}[/bold red] not found."
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
        console.print(f"❌ Error deleting collection: [bold red]{str(e)}[/bold red]")


@shards_app.command("info")
def shards_info(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to get shard info for"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed information about each shard"
    ),
    shard_name: str = typer.Option(
        None,
        "--shard",
        "-s",
        help="Show detailed information for a specific shard only",
    ),
):
    """Get detailed information about a collection's shards."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching shard information for collection [bold]{collection_name}[/bold] from [bold]{config['api_url']}[/bold]..."
    )

    try:
        # First, check if the collection exists
        schemas = api.get_schemas()
        schema = next((s for s in schemas if s.get("class") == collection_name), None)

        if not schema:
            console.print(
                f"❌ Collection [bold red]{collection_name}[/bold red] not found."
            )
            return

        # Get shard information
        shards = api.get_shards(collection_name)

        if not shards:
            console.print(
                f"ℹ️ No shard information available for collection [bold]{collection_name}[/bold]."
            )
            return

        # Display shards in a table
        table = Table(
            title=f"Shards for Collection: {collection_name}", border_style="cyan"
        )
        table.add_column("Shard Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Node", style="yellow")
        table.add_column("Objects", style="magenta")

        shard_count = 0
        total_objects = 0

        # The get_shards method already handles list/dict conversion
        shard_items = shards.items()

        for shard_name, shard_info in shard_items:
            shard_count += 1
            status = shard_info.get("status", "Unknown")
            node = shard_info.get("node", "Unknown")
            # Convert string to integer if needed
            objects_str = shard_info.get("objectCount", 0)
            objects = (
                int(objects_str)
                if isinstance(objects_str, str) and objects_str.isdigit()
                else objects_str
            )
            total_objects += objects

            # Color code the status
            if status == "READY":
                status_display = f"[green]{status}[/green]"
            elif status in ["CREATING", "PENDING"]:
                status_display = f"[yellow]{status}[/yellow]"
            elif status in ["ERROR", "FAILED"]:
                status_display = f"[red]{status}[/red]"
            else:
                status_display = status

            table.add_row(shard_name, status_display, node, str(objects))

        console.print(
            f"📊 Found [bold]{shard_count}[/bold] shards with a total of [bold]{total_objects}[/bold] objects."
        )
        console.print(table)

        # Prepare the list of shards to display details for
        detailed_shards = []
        if shard_name:
            # Just show details for the specified shard
            if shard_name in shards:
                detailed_shards = [(shard_name, shards[shard_name])]
            else:
                console.print(
                    f"❌ Shard [bold red]{shard_name}[/bold red] not found in collection [bold]{collection_name}[/bold]."
                )
                return
        elif detailed:
            # Show details for all shards
            detailed_shards = list(shard_items)

        # Show detailed information for selected shards
        for shard_name, shard_info in detailed_shards:
            # Try to get more detailed info for this specific shard
            try:
                shard_details = api.get_shard_details(collection_name, shard_name)
                if shard_details and len(shard_details) > len(shard_info):
                    shard_info = shard_details
            except Exception:
                # Use what we already have if fetching details fails
                pass

            console.print(
                f"\n[bold cyan]Detailed information for shard:[/bold cyan] {shard_name}"
            )

            # Create a panel with the shard details
            panel_content = ""

            # Basic shard info
            status = shard_info.get("status", "Unknown")
            status_color = (
                "green"
                if status == "READY"
                else "yellow"
                if status in ["CREATING", "PENDING"]
                else "red"
                if status in ["ERROR", "FAILED"]
                else "white"
            )
            panel_content += f"[bold blue]Status:[/bold blue] [{status_color}]{status}[/{status_color}]\n"
            panel_content += (
                f"[bold blue]Node:[/bold blue] {shard_info.get('node', 'Unknown')}\n"
            )
            panel_content += f"[bold blue]Object Count:[/bold blue] {shard_info.get('objectCount', 0)}\n"

            # Add hosted on information if available
            if "hostedOn" in shard_info:
                panel_content += f"[bold blue]Hosted On:[/bold blue] {shard_info.get('hostedOn', 'Unknown')}\n"

            # Add vector indexing info if available
            if "vectorIndexingStatus" in shard_info:
                vector_status = shard_info.get("vectorIndexingStatus", "Unknown")
                vector_color = (
                    "green"
                    if vector_status == "READY"
                    else "yellow"
                    if vector_status in ["BUILDING", "PENDING"]
                    else "red"
                    if vector_status in ["ERROR", "FAILED"]
                    else "white"
                )
                panel_content += f"[bold blue]Vector Indexing:[/bold blue] [{vector_color}]{vector_status}[/{vector_color}]\n"

            # Add resource usage if available
            if "memoryUsage" in shard_info:
                memory = shard_info.get("memoryUsage", "Unknown")
                panel_content += f"[bold blue]Memory Usage:[/bold blue] {memory}\n"

            if "diskUsage" in shard_info:
                disk = shard_info.get("diskUsage", "Unknown")
                panel_content += f"[bold blue]Disk Usage:[/bold blue] {disk}\n"

            # Add CPU usage if available
            if "cpuUsage" in shard_info:
                cpu = shard_info.get("cpuUsage", "Unknown")
                panel_content += f"[bold blue]CPU Usage:[/bold blue] {cpu}\n"

            # Add indexing progress if available
            if "indexingProgress" in shard_info:
                index_progress = shard_info.get("indexingProgress", "Unknown")
                panel_content += (
                    f"[bold blue]Indexing Progress:[/bold blue] {index_progress}\n"
                )

            # Add performance metrics if available
            if "queryTimeAvg" in shard_info:
                query_time = shard_info.get("queryTimeAvg", "Unknown")
                panel_content += (
                    f"[bold blue]Avg. Query Time:[/bold blue] {query_time}\n"
                )

            # Add network metrics if available
            if "networkIn" in shard_info:
                net_in = shard_info.get("networkIn", "Unknown")
                panel_content += f"[bold blue]Network In:[/bold blue] {net_in}\n"

            if "networkOut" in shard_info:
                net_out = shard_info.get("networkOut", "Unknown")
                panel_content += f"[bold blue]Network Out:[/bold blue] {net_out}\n"

            # Add replica information
            if "replicas" in shard_info and shard_info.get("replicas"):
                replicas = shard_info.get("replicas", [])
                panel_content += f"[bold blue]Replicas:[/bold blue] {len(replicas)}\n"

                for i, replica in enumerate(replicas):
                    r_status = replica.get("status", "Unknown")
                    r_status_color = (
                        "green"
                        if r_status == "READY"
                        else "yellow"
                        if r_status in ["CREATING", "PENDING"]
                        else "red"
                        if r_status in ["ERROR", "FAILED"]
                        else "white"
                    )
                    r_node = replica.get("node", "Unknown")
                    panel_content += f"  [bold]Replica {i+1}:[/bold] Node: {r_node}, Status: [{r_status_color}]{r_status}[/{r_status_color}]\n"

                    # Add replica health information if available
                    if "health" in replica:
                        health = replica.get("health", "Unknown")
                        health_color = (
                            "green"
                            if health == "HEALTHY"
                            else "red"
                            if health == "UNHEALTHY"
                            else "yellow"
                        )
                        panel_content += (
                            f"    Health: [{health_color}]{health}[/{health_color}]\n"
                        )

                    # Add replica sync status if available
                    if "syncStatus" in replica:
                        sync = replica.get("syncStatus", "Unknown")
                        sync_color = (
                            "green"
                            if sync == "IN_SYNC"
                            else "yellow"
                            if sync == "SYNCING"
                            else "red"
                        )
                        panel_content += (
                            f"    Sync Status: [{sync_color}]{sync}[/{sync_color}]\n"
                        )

                    # Add replica lag if available
                    if "replicationLag" in replica:
                        lag = replica.get("replicationLag", "Unknown")
                        panel_content += f"    Replication Lag: {lag}\n"

            # Display panel with shard details
            console.print(
                Panel(
                    panel_content,
                    title=f"Shard: {shard_name}",
                    border_style="cyan",
                    expand=False,
                )
            )

        # Display shard configuration from schema if available
        if "shardingConfig" in schema:
            console.print("\n[bold cyan]Sharding Configuration:[/bold cyan]")
            shard_config = schema.get("shardingConfig", {})
            shard_syntax = Syntax(
                json.dumps(shard_config, indent=2),
                "json",
                theme="monokai",
                line_numbers=True,
            )
            console.print(shard_syntax)

    except Exception as e:
        console.print(
            f"❌ Error fetching shard information: [bold red]{str(e)}[/bold red]"
        )


@app.command("replication")
def replication_info(
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to get replication info for"
    ),
):
    """Get replication information about a collection."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Fetching replication information for collection [bold]{collection_name}[/bold] from [bold]{config['api_url']}[/bold]..."
    )

    try:
        # First, check if the collection exists
        schemas = api.get_schemas()
        schema = next((s for s in schemas if s.get("class") == collection_name), None)

        if not schema:
            console.print(
                f"❌ Collection [bold red]{collection_name}[/bold red] not found."
            )
            return

        # Get collection stats
        try:
            stats = api.get_collection_stats(collection_name)
        except Exception as e:
            console.print(f"⚠️ Could not get collection stats: {str(e)}")
            return

        # Extract replication info
        replication_config = stats.get("replication", {})

        if not replication_config:
            console.print(
                f"ℹ️ No replication information available for collection [bold]{collection_name}[/bold]."
            )
            return

        # Display replication info in a panel
        factor = replication_config.get("factor", "N/A")

        console.print(
            Panel(
                f"[bold blue]Collection:[/bold blue] {collection_name}\n"
                f"[bold green]Replication Factor:[/bold green] {factor}\n",
                title="Replication Configuration",
                border_style="blue",
                expand=False,
            )
        )

        # Display detailed replication configuration
        console.print("\n[bold blue]Detailed Replication Configuration:[/bold blue]")
        rep_syntax = Syntax(
            json.dumps(replication_config, indent=2),
            "json",
            theme="monokai",
            line_numbers=True,
        )
        console.print(rep_syntax)

        # If shard info is available, show replication status per shard
        shards = api.get_shards(collection_name)
        if shards:
            console.print("\n[bold blue]Shard Replication Status:[/bold blue]")
            table = Table(title="Shard Replicas", border_style="blue")
            table.add_column("Shard Name", style="cyan")
            table.add_column("Replicated", style="green")
            table.add_column("Replica Count", style="yellow")

            for shard_name, shard_info in shards.items():
                is_replicated = (
                    "replicas" in shard_info and len(shard_info.get("replicas", [])) > 0
                )
                replica_count = len(shard_info.get("replicas", []))

                table.add_row(
                    shard_name, "✅" if is_replicated else "❌", str(replica_count)
                )

            console.print(table)

    except Exception as e:
        console.print(
            f"❌ Error fetching replication information: [bold red]{str(e)}[/bold red]"
        )
