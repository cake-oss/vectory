#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""
Test for error handling in hybrid search.

This script intentionally creates an error condition to demonstrate
the error handling capabilities of the hybrid search functionality.
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to be able to import cake_vectory
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cake_vectory.utils.api import WeaviateAPI
from rich.console import Console

console = Console()


def test_error_handling():
    """Test error handling in the hybrid search functionality."""
    api = WeaviateAPI()

    # Intentionally use an invalid field in the GraphQL query
    class_name = "DesigningEcosystemsOfIntelligence"
    query = "intelligence"

    # Execute hybrid search with a forced error in the code
    # We'll simulate this by monkey patching the execute_graphql method temporarily
    original_execute_graphql = api.objects_client.execute_graphql

    def mock_execute_graphql(query_data):
        """Mock implementation to return only an error response with no data."""
        return {
            "errors": [
                {
                    "message": 'Cannot query field "id" on type "DesigningEcosystemsOfIntelligence".',
                    "locations": [{"line": 17, "column": 19}],
                },
                {
                    "message": 'Cannot query field "properties" on type "DesigningEcosystemsOfIntelligence".',
                    "locations": [{"line": 18, "column": 19}],
                },
            ],
            # No data field
        }

    # Replace the method temporarily
    api.objects_client.execute_graphql = mock_execute_graphql

    try:
        console.print("\n[bold]Testing error handling in hybrid search:[/bold]")
        results = api.hybrid_search(
            class_name=class_name,
            query=query,
            alpha=0.5,
            limit=3,
            vector=[0.1] * 1024,  # Create a simple test vector
            fusion_type="relativeScoreFusion",
        )

        # Check if error was handled correctly
        if "error" in results:
            console.print("[green]✓ Error was detected and handled correctly![/green]")
            console.print(f"Error message: {results['error']}")
        else:
            console.print("[red]✗ Error was not detected properly![/red]")
    finally:
        # Restore the original method
        api.objects_client.execute_graphql = original_execute_graphql


if __name__ == "__main__":
    test_error_handling()
