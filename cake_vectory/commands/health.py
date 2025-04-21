# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Health check commands for the Cake Vectory CLI."""

import typer
from rich.console import Console
from rich.table import Table

from cake_vectory.utils.api import WeaviateAPI
from cake_vectory.utils.config import get_config

app = typer.Typer(help="Check vector database health status")
console = Console()


@app.callback(invoke_without_command=True)
def health(ctx: typer.Context):
    """Check if the vector database is live and ready."""
    if ctx.invoked_subcommand is not None:
        return

    # Show both live and ready status
    check_live()
    check_ready()


@app.command()
def live():
    """Check if the vector database is live."""
    check_live()


@app.command()
def ready():
    """Check if the vector database is ready."""
    check_ready()


def check_live():
    """Check if the vector database is live and display the result."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Checking if vector database is live at [bold]{config['api_url']}[/bold]..."
    )

    try:
        health = api.check_health()
        if health["live"]:
            console.print("✅ Vector database is [bold green]live[/bold green]!")
        else:
            console.print("❌ Vector database is [bold red]not live[/bold red]!")
    except Exception as e:
        console.print(f"❌ Error checking live status: [bold red]{str(e)}[/bold red]")


def check_ready():
    """Check if the vector database is ready and display the result."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Checking if vector database is ready at [bold]{config['api_url']}[/bold]..."
    )

    try:
        health = api.check_health()
        if health["ready"]:
            console.print("✅ Vector database is [bold green]ready[/bold green]!")
        else:
            console.print("❌ Vector database is [bold red]not ready[/bold red]!")
    except Exception as e:
        console.print(f"❌ Error checking ready status: [bold red]{str(e)}[/bold red]")


@app.command()
def status():
    """Show detailed health status."""
    api = WeaviateAPI()
    config = get_config()

    console.print(
        f"🔍 Checking vector database health status at [bold]{config['api_url']}[/bold]..."
    )

    try:
        health = api.check_health()

        table = Table(title="Vector Database Health Status", border_style="green")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="magenta")

        table.add_row("Live", "✅ Yes" if health["live"] else "❌ No")
        table.add_row("Ready", "✅ Yes" if health["ready"] else "❌ No")

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error checking health status: [bold red]{str(e)}[/bold red]")
