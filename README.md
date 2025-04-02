<!--
SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.

SPDX-License-Identifier: Apache-2.0
-->

# Cake Vectory

A modern command-line interface for interacting with vector databases.

> **Note:** Cake Vectory currently supports Weaviate as the vector database backend, with plans to add support for other vector databases like Milvus in future releases.

## Features

- 🔍 Check vector database health status (live/ready)
- 📋 List and view schema details
- 📦 Manage objects (create, read, update, delete)
- 🔎 Advanced search capabilities (text, hybrid, filter)
- 🔄 View replication configuration and status
- 🧩 Detailed shard information and metrics
- ⚙️ Configurable via environment variables or command-line options
- ✨ Modern interface with rich formatting and emojis

## Installation

This project uses `uv` as the package manager. To install:

```bash
# Install as a tool
uv tool install .

# Now you can run the CLI directly
vectory --help
# Or use the full name
cake-vectory --help
```

### Uninstallation

```bash
# Uninstall the CLI
uv tool uninstall cake-vectory
```

### Development Mode

During development, you can run the CLI without installing it:

```bash
# Run directly with uv
uv run cake_vectory/main.py --help

# Example: List collections
uv run cake_vectory/main.py collection list
```

## Configuration

You can configure the CLI in several ways:

1. Create a `.env` file (see `.env.example`)
2. Set environment variables directly
3. Use command-line options

Example `.env` file:

```
# Weaviate Connection Settings
WEAVIATE_HTTP_HOST=localhost
WEAVIATE_HTTP_PORT=8080
WEAVIATE_GRPC_HOST=localhost
WEAVIATE_GRPC_PORT=50051

# API Key Authentication (uncomment and set if your vector database instance has auth enabled)
# WEAVIATE_API_KEY=your-api-key

# Note: Currently only Weaviate is supported as the vector database backend
```

## Usage

### Getting Help

To see all available commands and options:

```bash
vectory --help
```

For help on a specific command:

```bash
vectory <command> --help
```

Example:

```bash
vectory health --help
vectory schema --help
```

### Health Checks

Check if the vector database is live and ready:

```bash
vectory health
```

Check if the vector database is live:

```bash
vectory health live
```

Check if the vector database is ready:

```bash
vectory health ready
```

Show detailed health status:

```bash
vectory health status
```

### Schema Management

List all schemas:

```bash
vectory schema list
```

Get details of a specific schema:

```bash
vectory schema get <class-name>
```

### Object Management

List objects in a collection:

```bash
vectory objects list <class-name>
```

Get a specific object:

```bash
vectory objects get <class-name> <object-id>
```

Create a new object:

```bash
vectory objects create <class-name> --properties '{"property": "value"}'
```

Or from a JSON file:

```bash
vectory objects create <class-name> --file object-data.json
```

Update an object:

```bash
vectory objects update <class-name> <object-id> --properties '{"property": "new-value"}'
```

Delete an object:

```bash
vectory objects delete <class-name> <object-id>
```

Batch import objects from a JSON file:

```bash
vectory objects batch <class-name> objects.json
```

### Search

Search objects using text-based semantic search:

```bash
vectory search text <class-name> "your search query"
```

Search with hybrid search (vector + keyword):

```bash
vectory search hybrid <class-name> "your search query" --alpha 0.5
```

Search using filters:

```bash
vectory search filter <class-name> '{"path": ["property"], "operator": "Equal", "valueString": "value"}'
```

### General Options

Specify custom connection settings:

```bash
# Specify HTTP host and port
vectory --http-host custom-host --http-port 8080 <command>

# Specify gRPC host and port
vectory --grpc-host custom-host --grpc-port 50051 <command>

# Specify all connection settings
vectory --http-host custom-host --http-port 8080 --grpc-host custom-host --grpc-port 50051 <command>

# Specify API key for authentication
vectory --api-key your-api-key <command>

# Combined connection and authentication settings
vectory --http-host custom-host --http-port 8080 --api-key your-api-key <command>
```

Show CLI version:

```bash
vectory version
```

### Command Output

All commands provide rich, formatted output with:
- Color-coded text for better readability
- Emoji indicators for status (✅, ❌, 🔍, ℹ️)
- Tables for structured data
- Syntax highlighting for JSON output

### Health Check

```bash
vectory health
```

Output:
```
🔍 Checking if vector database is live at http://localhost:8080/v1...
✅ Vector database is live!
🔍 Checking if vector database is ready at http://localhost:8080/v1...
✅ Vector database is ready!
```

### Listing Collections

```bash
vectory collection list
```

Output:
```
🔍 Fetching collections from http://localhost:8080/v1...
                                                    Vector Database Collections (2 found)
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Collection Name ┃ Description                                                                               ┃ Properties ┃ Objects ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━┩
│ Collection1     │ Auto-generated collection                                                                 │ 2          │ 75      │
│ Collection2     │ Auto-generated collection                                                                 │ 2          │ 120     │
└─────────────────┴───────────────────────────────────────────────────────────────────────────────────────────┴────────────┴─────────┘
```

### Collection Details

```bash
vectory collection info Collection1
```

Output:
```
🔍 Fetching info for collection Collection1 from http://localhost:8080/v1...
╭───────────────────────────────────────── Collection: Collection1 ──────────────────────────────────────────╮
│ Collection: Collection1                                                                                    │
│ Description: Auto-generated collection                                                                     │
│ Object Count: 75                                                                                           │
│ Replication Factor: 1                                                                                      │
│ Shard Count: 3                                                                                             │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                                       Properties
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name         ┃ Data Type ┃ Description                                                                               ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ metadata     │ text      │ Metadata information                                                                      │
│ content      │ text      │ Main content                                                                              │
└──────────────┴───────────┴───────────────────────────────────────────────────────────────────────────────────────────┘

Collection Metadata:
   1 {
   2   "class": "Collection1",
   3   "description": "Auto-generated collection",
   4   "vectorIndexConfig": {
   5     "distance": "cosine",
   6     "ef": -1,
   7     "efConstruction": 128,
   8     "maxConnections": 32,
   9     "vectorCacheMaxObjects": 1000000000000
  10   },
  11   "vectorizer": "none"
  12 }
```

### Shard Information

```bash
vectory collection shards info Collection1 --detailed
```

Output:
```
🔍 Fetching shard information for collection Collection1 from http://localhost:8080/v1...
📊 Found 3 shards with a total of 75 objects.
    Shards for Collection: Collection1    
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Shard Name   ┃ Status ┃ Node          ┃ Objects ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ a1BzcFR7YTq2 │ READY  │ node-1        │ 25      │
│ b2HMCGgO8EWE │ READY  │ node-2        │ 25      │
│ c3KLmNpQ9FVD │ READY  │ node-3        │ 25      │
└──────────────┴────────┴───────────────┴─────────┘

Detailed information for shard: a1BzcFR7YTq2
╭─ Shard: a1BzcFR7YTq2 ─╮
│ Status: READY         │
│ Node: node-1          │
│ Object Count: 25      │
│ Memory Usage: 15MB    │
│ Disk Usage: 5MB       │
│ CPU Usage: 0.2%       │
│ Replicas: 0           │
│                       │
╰───────────────────────╯
```

### Replication Information

```bash
vectory collection replication Collection1
```

Output:
```
🔍 Fetching replication information for collection Collection1 from http://localhost:8080/v1...
╭─ Replication Configuration ─╮
│ Collection: Collection1     │
│ Replication Factor: 1       │
│                             │
╰─────────────────────────────╯

Detailed Replication Configuration:
  1 {                                                 
  2   "asyncEnabled": false,                          
  3   "deletionStrategy": "NoAutomatedResolution",    
  4   "factor": 1                                     
  5 }                                                 

Shard Replication Status:
               Shard Replicas                
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Shard Name   ┃ Replicated ┃ Replica Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ a1BzcFR7YTq2 │ ❌         │ 0             │
│ b2HMCGgO8EWE │ ❌         │ 0             │
│ c3KLmNpQ9FVD │ ❌         │ 0             │
└──────────────┴────────────┴───────────────┘
```

### Listing Objects

```bash
vectory objects list Collection1 --limit 3
```

Output:
```
🔍 Fetching objects from class Collection1 in http://localhost:8080/v1...
📊 Found 75 objects in total, showing 3.
                                                                                                  Objects in Collection1
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Properties                                                                                                                                            ┃ Created             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 00000000-0000-0000-0000-000000000001 │ metadata: {"source": "example.pdf", "chunk_index": 1}, content: "This is the first chunk of content from the document..."                            │ 2025-03-07 12:00:00 │
│ 00000000-0000-0000-0000-000000000002 │ metadata: {"source": "example.pdf", "chunk_index": 2}, content: "This is the second chunk of content from the document..."                           │ 2025-03-07 12:00:01 │
│ 00000000-0000-0000-0000-000000000003 │ metadata: {"source": "example.pdf", "chunk_index": 3}, content: "This is the third chunk of content from the document..."                            │ 2025-03-07 12:00:02 │
└──────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────┘
```

### Getting a Specific Object

```bash
vectory objects get Collection1 00000000-0000-0000-0000-000000000001
```

Output:
```
🔍 Fetching object 00000000-0000-0000-0000-000000000001 from class Collection1 in http://localhost:8080/v1...
╭─ Object: 00000000-0000-0000-0000-000000000001 ─╮
│ ID: 00000000-0000-0000-0000-000000000001       │
│ Class: Collection1                             │
│ Created: 2025-03-07 12:00:00                   │
│ Updated: 2025-03-07 12:00:00                   │
│                                                │
╰────────────────────────────────────────────────╯

Properties:
  1 {
  2   "metadata": {"source": "example.pdf", "chunk_index": 1},
  3   "content": "This is the first chunk of content from the document..."
  4 }
```

### Text Search

```bash
vectory search text Collection1 "example query" --limit 2
```

Output:
```
🔍 Searching in class Collection1 for: example query...
📊 Found 2 matching objects.
                                                                                        Search Results for 'example query'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ ID                                   ┃ Properties                                                                                                                                         ┃ Score  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 00000000-0000-0000-0000-000000000005 │ metadata: {"source": "example.pdf", "chunk_index": 5}, content: "This chunk contains information about the example query we're looking for..."    │ 0.8765 │
│ 00000000-0000-0000-0000-000000000012 │ metadata: {"source": "another.pdf", "chunk_index": 2}, content: "Here's another document that mentions the example query in a different context..." │ 0.7654 │
└──────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────┘

To view details of a specific result, use:
vectory objects get Collection1 <object-id>
```

### Hybrid Search

```bash
vectory search hybrid Collection1 "semantic search example" --limit 2
```

Output:
```
🔍 Hybrid searching in class Collection1 for: semantic search example (alpha=0.5)...
📊 Found 2 matching objects.
                                                                                 Search Results for 'semantic search example'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ ID                                   ┃ Properties                                                                                                                                         ┃ Score  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 00000000-0000-0000-0000-000000000020 │ metadata: {"source": "search.pdf", "chunk_index": 3}, content: "Semantic search goes beyond keyword matching to understand the meaning..."        │ 0.9234 │
│ 00000000-0000-0000-0000-000000000033 │ metadata: {"source": "vector.pdf", "chunk_index": 7}, content: "Vector search enables semantic understanding of queries and documents..."         │ 0.8765 │
└──────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────┘

To view details of a specific result, use:
vectory objects get Collection1 <object-id>
```

## Development

### Project Structure

```
cake-vectory/
├── .env.example              # Example environment variables
├── pyproject.toml            # Project configuration
├── README.md                 # Documentation
├── CLAUDE.md                 # Instructions for Claude AI assistant
└── cake_vectory/             # Main package
    ├── __init__.py           # Package initialization
    ├── main.py               # CLI entry point
    ├── commands/             # Command modules
    │   ├── __init__.py
    │   ├── collection.py     # Collection management commands
    │   ├── health.py         # Health check commands
    │   ├── objects.py        # Object management commands
    │   ├── schema.py         # Schema-related commands
    │   └── search.py         # Search commands
    └── utils/                # Utility functions
        ├── __init__.py
        ├── api.py            # API interaction helpers
        ├── api/              # Specialized API clients
        │   ├── __init__.py
        │   ├── client.py     # Base client
        │   ├── health.py     # Health check client
        │   ├── objects.py    # Objects client
        │   ├── schema.py     # Schema client
        │   └── search.py     # Search client
        └── config.py         # Configuration management
