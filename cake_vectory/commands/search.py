# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Search commands for the Cake Vectory CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json
from typing import Optional, List, Dict, Any, Union

from cake_vectory.utils.api import WeaviateAPI
from cake_vectory.utils.config import get_config

app = typer.Typer(help="Search vector database objects")
console = Console()


@app.callback(invoke_without_command=True)
def search(ctx: typer.Context):
    """Search vector database objects."""
    if ctx.invoked_subcommand is not None:
        return
    
    # Show help if no subcommand is provided
    console.print("Please specify a search type. Use [bold]vectory search --help[/bold] for more information.")


@app.command("text")
def search_by_text(
    collection_name: str = typer.Argument(..., help="Name of the collection to search in"),
    query: str = typer.Argument(..., help="Text to search for"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results to return"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name for multi-tenant collections"),
    filter_json: Optional[str] = typer.Option(None, "--filter", "-f", help="JSON string with filter criteria")
):
    """Search for objects using text-based semantic search."""
    api = WeaviateAPI()
    config = get_config()
    
    # Parse filter if provided
    filter_obj = None
    if filter_json:
        try:
            filter_obj = json.loads(filter_json)
        except Exception as e:
            console.print(f"❌ Error parsing filter JSON: [bold red]{str(e)}[/bold red]")
            return
    
    console.print(f"🔍 Searching in collection [bold]{collection_name}[/bold] for: [bold]{query}[/bold]...")
    
    try:
        # Perform the search
        results = api.search_objects(
            class_name=collection_name,
            query_text=query,
            limit=limit,
            tenant=tenant,
            filter_obj=filter_obj
        )
        
        objects = results.get("objects", [])
        
        if not objects:
            console.print("ℹ️ No matching objects found.")
            return
        
        console.print(f"📊 Found [bold]{len(objects)}[/bold] matching objects.")
        
        table = Table(title=f"Search Results for '{query}'")
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
        
        # Ask if user wants to see details of a specific result
        console.print("\nTo view details of a specific result, use:")
        console.print(f"[bold]vectory objects get {collection_name} <object-id>[/bold]")
        
    except Exception as e:
        console.print(f"❌ Error searching objects: [bold red]{str(e)}[/bold red]")


@app.command("hybrid")
def search_hybrid(
    collection_name: str = typer.Argument(..., help="Name of the collection to search in"),
    query: str = typer.Argument(..., help="Text to search for"),
    alpha: float = typer.Option(0.5, "--alpha", "-a", help="Balance between vector and keyword search (0.0-1.0)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results to return"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name for multi-tenant collections"),
    filter_json: Optional[str] = typer.Option(None, "--filter", "-f", help="JSON string with filter criteria"),
    vector_file: Optional[str] = typer.Option(None, "--vector-file", help="Path to a JSON file containing a vector to use instead of generating one from the query text"),
    fusion_type: str = typer.Option("rankedFusion", "--fusion-type", help="Type of fusion to use (rankedFusion or relativeScoreFusion)"),
    properties: Optional[str] = typer.Option(None, "--properties", "-p", help="Comma-separated list of properties to search in (e.g., 'title,description' or 'title^3,description')")
):
    """Search for objects using hybrid search (vector + keyword)."""
    api = WeaviateAPI()
    config = get_config()
    
    # Parse filter if provided
    filter_obj = None
    if filter_json:
        try:
            filter_obj = json.loads(filter_json)
        except Exception as e:
            console.print(f"❌ Error parsing filter JSON: [bold red]{str(e)}[/bold red]")
            return
    
    # Parse properties if provided
    props_list = None
    if properties:
        props_list = [p.strip() for p in properties.split(',')]
        console.print(f"[dim]Searching in properties: {', '.join(props_list)}[/dim]")
    
    # Load vector from file if provided
    vector = None
    if vector_file:
        try:
            with open(vector_file, 'r') as f:
                vector_data = json.load(f)
                if isinstance(vector_data, list):
                    vector = vector_data
                else:
                    console.print(f"❌ Error: Vector file must contain a JSON array of numbers")
                    return
            console.print(f"✅ Loaded vector with [bold]{len(vector)}[/bold] dimensions from file")
        except Exception as e:
            console.print(f"❌ Error loading vector file: [bold red]{str(e)}[/bold red]")
            return
    
    # Validate fusion type
    if fusion_type not in ["rankedFusion", "relativeScoreFusion"]:
        console.print(f"❌ Error: fusion_type must be either 'rankedFusion' or 'relativeScoreFusion'")
        return
    
    console.print(f"🔍 Hybrid searching in collection [bold]{collection_name}[/bold] for: [bold]{query}[/bold] (alpha={alpha}, fusion={fusion_type})...")
    
    try:
        # Perform the hybrid search
        results = api.hybrid_search(
            class_name=collection_name,
            query=query,
            alpha=alpha,
            limit=limit,
            tenant=tenant,
            filter_obj=filter_obj,
            vector=vector,
            fusion_type=fusion_type,
            properties=props_list
        )
        
        objects = results.get("objects", [])
        
        if not objects:
            console.print("ℹ️ No matching objects found.")
            return
        
        console.print(f"📊 Found [bold]{len(objects)}[/bold] matching objects.")
        
        table = Table(title=f"Hybrid Search Results for '{query}'")
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
        
        # Ask if user wants to see details of a specific result
        console.print("\nTo view details of a specific result, use:")
        console.print(f"[bold]vectory objects get {collection_name} <object-id>[/bold]")
        
    except Exception as e:
        console.print(f"❌ Error searching objects: [bold red]{str(e)}[/bold red]")


@app.command("filter")
def search_by_filter(
    collection_name: str = typer.Argument(..., help="Name of the collection to search in"),
    filter_json: str = typer.Argument(..., help="JSON string with filter criteria"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results to return"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name for multi-tenant collections")
):
    """Search for objects using filters only."""
    api = WeaviateAPI()
    config = get_config()
    
    # Parse filter
    try:
        filter_obj = json.loads(filter_json)
    except Exception as e:
        console.print(f"❌ Error parsing filter JSON: [bold red]{str(e)}[/bold red]")
        return
    
    console.print(f"🔍 Filtering objects in collection [bold]{collection_name}[/bold]...")
    
    try:
        # Perform the filtered search
        results = api.filter_objects(
            class_name=collection_name,
            filter_obj=filter_obj,
            limit=limit,
            tenant=tenant
        )
        
        objects = results.get("objects", [])
        
        if not objects:
            console.print("ℹ️ No matching objects found.")
            return
        
        console.print(f"📊 Found [bold]{len(objects)}[/bold] matching objects.")
        
        table = Table(title=f"Filtered Objects in {collection_name}")
        table.add_column("ID", style="cyan")
        table.add_column("Properties", style="green")
        
        for obj in objects:
            obj_id = obj.get("id", "Unknown")
            
            # Format properties for display
            properties = obj.get("properties", {})
            props_str = ", ".join([f"{k}: {str(v)}" for k, v in properties.items()])
            
            table.add_row(obj_id, props_str)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error filtering objects: [bold red]{str(e)}[/bold red]")
