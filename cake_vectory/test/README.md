# Cake Vectory Test Scripts

This directory contains test scripts for Cake Vectory features.

## Hybrid Search Test

The `hybrid_search_test.py` script demonstrates the hybrid search capability with custom vector support.

### Usage

```bash
# Run the test with default parameters
python -m cake_vectory.test.hybrid_search_test

# Run with custom parameters
python -m cake_vectory.test.hybrid_search_test --collection CollectionName --query "my search query" --dimensions 1536 --limit 5 --alpha 0.5
```

### Parameters

- `--collection`: The collection to search in (default: MyCollection)
- `--query`: The search query to use (default: "intelligence")
- `--dimensions`: The number of dimensions for the test vector (default: 1024)
- `--limit`: Maximum number of results to return (default: 3)
- `--alpha`: Balance between vector and keyword search, 0.0-1.0 (default: 0.7)
- `--fusion-type`: Type of fusion to use ("rankedFusion" or "relativeScoreFusion", default: "rankedFusion")
- `--properties`: Comma-separated list of properties to search in (e.g., 'text,metadata_str')

### Features Demonstrated

1. Regular text search
2. Hybrid search without a vector file
3. Hybrid search with a custom vector file

### Notes

- The script creates a test vector with the specified dimensions
- If the collection doesn't have a vectorizer, hybrid search falls back to text search
- When a vector file is provided, it's used regardless of the collection's vectorizer settings
- For production use, vectors should be generated using proper embedding models that match what your vector database expects