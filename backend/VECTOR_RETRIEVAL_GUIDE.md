# Vector Retrieval System Guide

## Overview

The `vector_retrieval.py` module provides a comprehensive system for searching and matching missing persons and unidentified bodies using both face and text embeddings with metadata filtering.

## Features

✅ **Parallel Search**: Searches face and text collections simultaneously for faster results  
✅ **Metadata Filtering**: Filter by gender (exact), age range, height range  
✅ **Weighted Similarity**: Combine face and text scores with custom weights (w1, w2)  
✅ **Top-N Results**: Get ranked results based on combined similarity  
✅ **Flexible Queries**: Search with face only, text only, or both  

---

## Quick Start

### 1. Basic Usage

```python
from vector_retrieval import VectorRetrieval
import numpy as np

# Initialize
retrieval = VectorRetrieval(host="localhost", port=6333)

# Search with both face and text
results = retrieval.search_and_combine(
    face_embedding=face_vector,      # 512D numpy array
    text_embedding=text_vector,      # 1536D numpy array
    gender="Male",                   # Exact match
    age_min=25,                      # Approximate
    age_max=35,                      # Approximate
    height_min=165,                  # In cm, approximate
    height_max=180,                  # In cm, approximate
    w1=0.6,                          # 60% weight to face
    w2=0.4,                          # 40% weight to text
    top_n=10                         # Return top 10 matches
)

# Process results
for result in results:
    print(f"PID: {result['pid']}")
    print(f"Combined Score: {result['combined_score']:.4f}")
    print(f"Face Score: {result['face_score']:.4f}")
    print(f"Text Score: {result['text_score']:.4f}")
```

---

## Detailed Usage

### Metadata Filtering

#### Gender Filter (Exact Match)
```python
gender="Male"      # Must match exactly
gender="Female"    # Case-sensitive
gender="Other"
gender="Unknown"
```

#### Age Filter (Approximate Range)
```python
age_min=20         # Person aged 20 or older
age_max=30         # Person aged 30 or younger
# Combine both for range: 20-30 years
```

#### Height Filter (Approximate Range, in cm)
```python
height_min=165     # Person 165cm or taller
height_max=180     # Person 180cm or shorter
# Combine both for range: 165-180 cm
```

### Weighted Similarity

The system combines face and text similarity scores using weights:

```python
# Equal weight (default)
w1=0.5, w2=0.5  # 50% face, 50% text

# Face-focused
w1=0.7, w2=0.3  # 70% face, 30% text

# Text-focused
w1=0.3, w2=0.7  # 30% face, 70% text

# Face only
w1=1.0, w2=0.0  # 100% face, ignore text

# Text only
w1=0.0, w2=1.0  # Ignore face, 100% text
```

**Combined Score Formula:**
```
combined_score = (w1_normalized × face_score) + (w2_normalized × text_score)
```

Where weights are normalized: `w1_norm = w1 / (w1 + w2)`

---

## API Reference

### Class: `VectorRetrieval`

#### `__init__(host="localhost", port=6333)`
Initialize the retrieval system.

**Parameters:**
- `host` (str): Qdrant server host
- `port` (int): Qdrant server port

---

#### `search_and_combine()`
Complete search pipeline with parallel search and weighted combination.

**Parameters:**
- `face_embedding` (np.ndarray, optional): Face vector (512D)
- `text_embedding` (np.ndarray, optional): Text vector (1536D)
- `gender` (str, optional): "Male", "Female", "Other", "Unknown"
- `age_min` (int, optional): Minimum age
- `age_max` (int, optional): Maximum age
- `height_min` (int, optional): Minimum height in cm
- `height_max` (int, optional): Maximum height in cm
- `w1` (float): Face weight (default: 0.5)
- `w2` (float): Text weight (default: 0.5)
- `top_n` (int): Number of results (default: 10)
- `limit_per_collection` (int): Max results per collection (default: 50)

**Returns:**
List of dictionaries with:
```python
{
    'pid': str,              # Person ID
    'combined_score': float, # Weighted combined score
    'face_score': float,     # Face similarity (0-1)
    'text_score': float,     # Text similarity (0-1)
    'age': int,              # Person's age
    'gender': str,           # Person's gender
    'height_cm': int         # Person's height
}
```

---

#### `parallel_search()`
Search both collections in parallel.

**Parameters:** Same filters as `search_and_combine()` (without weights)

**Returns:** Tuple of `(face_results, text_results)`

---

#### `combine_results()`
Combine face and text results with weights.

**Parameters:**
- `face_results` (list): Results from face search
- `text_results` (list): Results from text search
- `w1` (float): Face weight
- `w2` (float): Text weight
- `top_n` (int): Number of results

**Returns:** List of combined results sorted by score

---

## Usage Examples

### Example 1: Search Missing Person with Photo and Description

```python
from vector_retrieval import VectorRetrieval
from face_recognition import FaceRecognizer
from text_embedder import TextEmbedder

# Initialize components
retrieval = VectorRetrieval()
face_rec = FaceRecognizer()
text_emb = TextEmbedder()

# Get embeddings
face_vector = face_rec.extract_embedding("photo.jpg")
text_vector = text_emb.get_embedding("Young man, brown hair, wearing blue shirt")

# Search with filters
results = retrieval.search_and_combine(
    face_embedding=face_vector,
    text_embedding=text_vector,
    gender="Male",
    age_min=18,
    age_max=30,
    height_min=170,
    height_max=185,
    w1=0.7,  # Prioritize face
    w2=0.3,
    top_n=5
)

print(f"Found {len(results)} potential matches")
```

### Example 2: Search with Only Text Description

```python
# When no photo is available
text_vector = text_emb.get_embedding(
    "Female, approximately 45 years old, wearing glasses, red jacket"
)

results = retrieval.search_and_combine(
    text_embedding=text_vector,  # No face embedding
    gender="Female",
    age_min=40,
    age_max=50,
    w1=0.0,
    w2=1.0,  # 100% text-based
    top_n=10
)
```

### Example 3: Search with Only Face Photo

```python
# When only photo is available, no description
face_vector = face_rec.extract_embedding("unknown_person.jpg")

results = retrieval.search_and_combine(
    face_embedding=face_vector,  # No text embedding
    gender="Male",  # Known from photo
    age_min=25,     # Approximate from photo
    age_max=35,
    w1=1.0,  # 100% face-based
    w2=0.0,
    top_n=10
)
```

### Example 4: Broad Search with Minimal Filters

```python
# Search with only gender filter
results = retrieval.search_and_combine(
    face_embedding=face_vector,
    text_embedding=text_vector,
    gender="Female",  # Only gender filter
    w1=0.5,
    w2=0.5,
    top_n=20  # Get more results due to broad search
)
```

### Example 5: Narrow Search with All Filters

```python
# Very specific search
results = retrieval.search_and_combine(
    face_embedding=face_vector,
    text_embedding=text_vector,
    gender="Male",
    age_min=28,      # Narrow age range
    age_max=32,
    height_min=175,  # Narrow height range
    height_max=182,
    w1=0.6,
    w2=0.4,
    top_n=5  # Fewer results expected
)
```

---

## Integration with Database

### Complete Workflow Example

```python
from vector_retrieval import VectorRetrieval
from face_recognition import FaceRecognizer
from text_embedder import TextEmbedder
from db_helper import DatabaseHelper

# Initialize all components
retrieval = VectorRetrieval()
face_rec = FaceRecognizer()
text_emb = TextEmbedder()
db = DatabaseHelper()

# Step 1: Get embeddings from query
query_face = face_rec.extract_embedding("query_photo.jpg")
query_text = text_emb.get_embedding("Description of missing person")

# Step 2: Search vector database
matches = retrieval.search_and_combine(
    face_embedding=query_face,
    text_embedding=query_text,
    gender="Male",
    age_min=20,
    age_max=30,
    w1=0.6,
    w2=0.4,
    top_n=10
)

# Step 3: Fetch full details from PostgreSQL
for match in matches:
    pid = match['pid']
    
    # Determine table based on PID prefix
    if pid.startswith('MP-'):
        record = db.search_records('missing_persons', {'pid': pid})
    elif pid.startswith('UIDB-'):
        record = db.search_records('unidentified_bodies', {'pid': pid})
    
    print(f"\nMatch: {pid} (Score: {match['combined_score']:.4f})")
    print(f"Name: {record[0]['name']}")
    print(f"Last Seen: {record[0]['last_seen_location']}")
```

---

## Performance Tips

### 1. Adjust `limit_per_collection`
- Default: 50 results per collection
- Increase for broader searches: `limit_per_collection=100`
- Decrease for faster searches: `limit_per_collection=20`

### 2. Use Appropriate Filters
- More filters = faster, more precise results
- Fewer filters = slower, more results

### 3. Weight Optimization
- If face photos are high quality → Increase `w1`
- If text descriptions are detailed → Increase `w2`
- If both are good quality → Use balanced weights (0.5, 0.5)

### 4. Top-N Selection
- Start with `top_n=10` for most searches
- Increase for broad searches or uncertain matches
- Decrease for very specific searches

---

## Error Handling

```python
try:
    results = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        w1=0.6,
        w2=0.4,
        top_n=10
    )
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Search error: {e}")
    # Check Qdrant connection
    # Verify collections exist
```

---

## Troubleshooting

### No Results Returned

**Possible Causes:**
1. Filters too strict (narrow age/height range)
2. No data in collections
3. Gender mismatch
4. Collection not indexed

**Solutions:**
- Broaden age/height ranges (±5 years, ±10 cm)
- Check collections have data: `python setup_vectordb.py`
- Verify gender values match exactly
- Relax filters one at a time

### Low Similarity Scores

**Possible Causes:**
1. Poor quality embeddings
2. No similar records in database
3. Incorrect metadata

**Solutions:**
- Use clearer face photos (frontal, well-lit)
- Provide more detailed text descriptions
- Verify data quality in collections

### Slow Search Performance

**Possible Causes:**
1. Large collections
2. No filters applied
3. High `limit_per_collection`

**Solutions:**
- Apply gender filter (most selective)
- Reduce `limit_per_collection` to 20-30
- Add age/height filters
- Ensure Qdrant has sufficient resources

---

## Best Practices

1. **Always provide at least one embedding** (face or text)
2. **Use gender filter when known** (most efficient filter)
3. **Set age range to ±5 years** for approximate ages
4. **Set height range to ±10 cm** for approximate heights
5. **Adjust weights based on data quality**:
   - Clear photo + vague description → `w1=0.8, w2=0.2`
   - Blurry photo + detailed description → `w1=0.2, w2=0.8`
   - Both good → `w1=0.5, w2=0.5`
6. **Start with `top_n=10`**, adjust based on results
7. **Combine with database queries** for full record details

---

## Next Steps

- **Integration**: Connect with `db_helper.py` for complete records
- **API**: Create REST API endpoint using Flask/FastAPI
- **UI**: Build search interface for users
- **Batch Search**: Process multiple queries in parallel
- **Analytics**: Track search performance and accuracy

---

## Dependencies

- `qdrant-client`: Vector database client
- `numpy`: Numerical operations
- `python-dotenv`: Environment variables
- Face embeddings: 512 dimensions
- Text embeddings: 1536 dimensions (OpenAI)

---

## Notes

- Metadata filters use **approximate values** for age and height
- Gender must be **exact match** (case-sensitive)
- Scores are normalized between 0 and 1 (higher = better match)
- Parallel search improves performance for dual-embedding queries
- Results are always sorted by combined score (descending)
