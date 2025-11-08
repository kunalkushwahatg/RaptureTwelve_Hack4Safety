# Qdrant Vector Database Setup Guide

## Quick Start

### Step 1: Start Qdrant Server

Choose one option:

#### Option A: Using Docker (Recommended)
```powershell
docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage qdrant/qdrant
```

#### Option B: Using Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

Then run:
```powershell
docker-compose up -d
```

#### Option C: Local Installation
Download from: https://qdrant.tech/documentation/quick-start/

### Step 2: Setup Collections

```powershell
# Activate environment
conda activate hsf

# Run setup script
python setup_vectordb.py
```

This creates two collections:
- **face_embeddings**: 512 dimensions (for InsightFace face vectors)
- **text_embeddings**: 1536 dimensions (for OpenAI text embeddings)

### Step 3: Verify Setup

Open browser: http://localhost:6333/dashboard

Or check in Python:
```python
from setup_vectordb import VectorDB

db = VectorDB()
db.verify_setup()
```

## Collections Info

### face_embeddings
- **Vector Size**: 512 dimensions
- **Distance Metric**: COSINE
- **Purpose**: Store face recognition embeddings from InsightFace
- **Use Case**: Match missing persons faces with unidentified bodies

### text_embeddings
- **Vector Size**: 1536 dimensions
- **Distance Metric**: COSINE
- **Purpose**: Store text description embeddings from OpenAI
- **Use Case**: Semantic search for person descriptions

## Usage Examples

### Initialize VectorDB
```python
from setup_vectordb import VectorDB

db = VectorDB(host="localhost", port=6333)
```

### List Collections
```python
collections = db.list_collections()
print(collections)  # ['face_embeddings', 'text_embeddings']
```

### Get Collection Info
```python
info = db.get_collection_info('face_embeddings')
print(f"Vector size: {info['config']['vector_size']}")
print(f"Points count: {info['points_count']}")
```

### Recreate Collections
```python
# Warning: This deletes existing data!
db.setup_all_collections(recreate=True)
```

## Troubleshooting

### Error: Connection refused
- Make sure Qdrant is running: `docker ps`
- Check port 6333 is accessible: http://localhost:6333

### Error: Collection already exists
- Use `recreate=True` to delete and recreate
- Or manually delete via dashboard

### Docker not installed?
Install Docker Desktop: https://www.docker.com/products/docker-desktop/

## Important Notes

- Qdrant data persists in `qdrant_storage/` folder
- Default port: 6333 (API), 6334 (gRPC)
- Web UI available at: http://localhost:6333/dashboard
- Use COSINE distance for normalized embeddings

## Stop Qdrant

```powershell
# If using docker run
docker stop <container_id>

# If using docker-compose
docker-compose down
```
