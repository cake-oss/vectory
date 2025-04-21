#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""
Hybrid Search Test Script

This script demonstrates the hybrid search capability of the Cake Vectory CLI,
including the ability to provide custom vectors via a JSON file.

Features demonstrated:
1. Basic text search
2. Hybrid search (combines vector + keyword search)
3. Hybrid search with a custom vector file
4. Support for collections with and without vectorizers

Requirements:
- Cake Vectory CLI installed
- Access to a Weaviate instance with collections
- Python 3.12+
"""

import json
import os
import subprocess
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

# Initialize console for rich output
console = Console()


def create_vector_file(dimensions: int, output_path: str) -> None:
    """
    Create a test vector file with specified dimensions.
    
    Args:
        dimensions: Number of dimensions for the vector
        output_path: File path where the vector will be saved
    """
    # Create a simple pattern vector (0.1, 0.2, 0.3, ...) wrapping around
    vector = [(i % 10 + 1) / 10 for i in range(dimensions)]
    
    # Save the vector to a JSON file
    with open(output_path, 'w') as f:
        json.dump(vector, f)
    
    console.print(f"✅ Created vector file with {dimensions} dimensions at: {output_path}")


def run_search_command(command: list, description: str) -> str:
    """
    Run a search command and return the output.
    
    Args:
        command: Command to run as a list of strings
        description: Description of the command for display
        
    Returns:
        The command output as a string
    """
    console.print(Panel(f"[bold cyan]Test: {description}[/bold cyan]"))
    console.print(f"[dim]Running command: {' '.join(command)}[/dim]")
    
    # Run the command and capture output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Display the output
    output = result.stdout if result.returncode == 0 else result.stderr
    return output


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Hybrid Search in Cake Vectory")
    parser.add_argument("--collection", type=str, default="TestCollectionBgem3",
                        help="The collection to search in")
    parser.add_argument("--query", type=str, default="education research",
                        help="The search query to use")
    parser.add_argument("--dimensions", type=int, default=768,
                        help="The number of dimensions for the test vector")
    parser.add_argument("--limit", type=int, default=3,
                        help="Maximum number of results to return")
    parser.add_argument("--alpha", type=float, default=0.7,
                        help="Balance between vector and keyword search (0.0-1.0)")
    parser.add_argument("--fusion-type", type=str, default="rankedFusion",
                        choices=["rankedFusion", "relativeScoreFusion"],
                        help="Type of fusion to use for hybrid search")
    parser.add_argument("--properties", type=str, default=None,
                        help="Comma-separated list of properties to search in (e.g., 'text,metadata_str')")
    args = parser.parse_args()
    
    # Create test directory if it doesn't exist
    test_dir = Path(__file__).parent
    test_dir.mkdir(exist_ok=True)
    
    # Create vector files with different dimensions
    vector_file = test_dir / f"test_vector_{args.dimensions}.json"
    create_vector_file(args.dimensions, str(vector_file))
    
    # Run various search tests
    console.print("\n[bold green]====== CAKE VECTORY HYBRID SEARCH TEST ======[/bold green]\n")
    
    # 1. Test regular text search
    command = ["python", "-m", "cake_vectory.main", "search", "text", 
               args.collection, args.query, "--limit", str(args.limit)]
    output = run_search_command(command, "Regular Text Search")
    console.print(Panel(Text(output)))
    
    # 2. Test hybrid search without vector file
    command = ["python", "-m", "cake_vectory.main", "search", "hybrid", 
               args.collection, args.query, "--alpha", str(args.alpha), 
               "--fusion-type", args.fusion_type,
               "--limit", str(args.limit)]
    
    # Add properties if specified
    if args.properties:
        command.extend(["--properties", args.properties])
        
    output = run_search_command(command, "Hybrid Search (without vector file)")
    console.print(Panel(Text(output)))
    
    # 3. Test hybrid search with vector file
    command = ["python", "-m", "cake_vectory.main", "search", "hybrid", 
               args.collection, args.query, "--alpha", str(args.alpha), 
               "--fusion-type", args.fusion_type,
               "--vector-file", str(vector_file), "--limit", str(args.limit)]
    
    # Add properties if specified
    if args.properties:
        command.extend(["--properties", args.properties])
        
    output = run_search_command(command, "Hybrid Search (with vector file)")
    console.print(Panel(Text(output)))
    
    console.print("\n[bold green]====== TEST SUMMARY ======[/bold green]")
    console.print("✓ Tested regular text search")
    console.print("✓ Tested hybrid search without vector file")
    console.print("✓ Tested hybrid search with custom vector file")
    console.print("\n[bold]Notes:[/bold]")
    console.print("- If the collection does not have a vectorizer, hybrid search falls back to text search")
    console.print("- When a vector file is provided, it's used regardless of the collection's vectorizer setting")
    console.print("- The vector dimensions should match what the collection expects")
    console.print("\n[bold]For more information, run:[/bold]")
    console.print("  python -m cake_vectory.test.hybrid_search_test --help")


if __name__ == "__main__":
    main()