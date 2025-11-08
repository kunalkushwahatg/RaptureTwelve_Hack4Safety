# Face Recognition Module - Documentation

## Overview

This module provides facial recognition capabilities for matching missing persons with unidentified bodies using InsightFace deep learning models.

## Files

- **`face_embedding.py`** - Core face embedding extraction functionality
- **`face_recognition_integration.py`** - Integration with the database for automated matching
- **`requirements.txt`** - Updated with face recognition dependencies

## Installation

### 1. Activate Your Environment
```powershell
conda activate hsf
```

### 2. Install Dependencies
```powershell
pip install insightface onnxruntime opencv-python
```

Or update all requirements:
```powershell
pip install -r requirements.txt
```

### 3. Download Face Recognition Models (First Run)

The InsightFace models will be downloaded automatically on first use (~100MB).

## Features

### 1. Face Embedding Extraction
- Extract 512-dimensional face embeddings from images
- Support for GPU acceleration (CUDA) or CPU
- Batch processing of multiple images
- Save/load embeddings for later use

### 2. Face Matching
- Compare two face images with similarity score (0-1)
- Configurable similarity threshold (default 0.5)
- Multiple face detection in single image

### 3. Database Integration
- Auto-match new UIDB entries with missing persons
- Find top N matches for any person
- Compare physical attributes (age, gender, height, etc.)
- Generate match confidence levels (high/medium/low)

## Usage Examples

### Basic Face Embedding Extraction

```python
from face_embedding import FaceEmbeddingExtractor

# Initialize extractor (GPU accelerated)
extractor = FaceEmbeddingExtractor(use_gpu=True)

# Extract embedding from a single image
embedding = extractor.extract_embedding('path/to/photo.jpg')
print(f"Embedding shape: {embedding.shape}")  # (512,)

# Extract all faces from an image with multiple people
embeddings = extractor.extract_all_faces('path/to/group_photo.jpg')
print(f"Found {len(embeddings)} faces")
```

### Compare Two Images

```python
from face_embedding import compare_faces

# Quick comparison
result = compare_faces(
    'photos/missing_persons/MP-2024-00001/profile.jpg',
    'photos/unidentified_bodies/UIDB-2024-00001/profile.jpg',
    threshold=0.5
)

print(f"Match: {result['match']}")
print(f"Similarity: {result['similarity']:.4f}")
```

### Database Integration - Find Matches

```python
from face_recognition_integration import FaceRecognitionMatcher
from db_helper import DatabaseHelper

# Initialize matcher
matcher = FaceRecognitionMatcher(use_gpu=True, similarity_threshold=0.5)

# Find matches for a missing person in UIDB database
with DatabaseHelper() as db:
    matches = matcher.find_matches_for_missing_person(
        db, 
        'MP-2024-00001', 
        top_n=10
    )
    
    for match in matches:
        print(f"UIDB: {match['uidb_pid']}")
        print(f"Similarity: {match['similarity']:.4f}")
        print(f"Match: {match['is_match']}")
        print(f"Found at: {match['found_address']}")
        print()
```

### Auto-Match New UIDB Entry

```python
from face_recognition_integration import FaceRecognitionMatcher
from db_helper import DatabaseHelper

matcher = FaceRecognitionMatcher(use_gpu=True, similarity_threshold=0.5)

with DatabaseHelper() as db:
    # When a new UIDB is added, automatically find potential matches
    result = matcher.auto_match_new_uidb(db, 'UIDB-2024-00001')
    
    print(f"High confidence matches: {len(result['high_confidence_matches'])}")
    print(f"Medium confidence matches: {len(result['medium_confidence_matches'])}")
    print(f"Low confidence matches: {len(result['low_confidence_matches'])}")
    
    # Show best matches
    for match in result['high_confidence_matches']:
        print(f"\nMissing Person: {match['mp_pid']} - {match['mp_name']}")
        print(f"Similarity: {match['similarity']:.4f}")
        print(f"Age: {match['age']}, Gender: {match['gender']}")
```

### Batch Processing

```python
from face_embedding import FaceEmbeddingExtractor

extractor = FaceEmbeddingExtractor(use_gpu=True)

# Process multiple images and save embeddings
image_paths = [
    'photos/missing_persons/MP-2024-00001/profile.jpg',
    'photos/missing_persons/MP-2024-00002/profile.jpg',
    'photos/missing_persons/MP-2024-00003/profile.jpg',
]

results = extractor.batch_extract_embeddings(
    image_paths, 
    output_dir='embeddings'  # Save embeddings to this folder
)

print(f"Processed {len(results)} images")
```

## Configuration

### Similarity Thresholds

Recommended thresholds based on use case:

| Threshold | Interpretation | Use Case |
|-----------|---------------|----------|
| > 0.7 | Very High Confidence | Auto-match with manual verification |
| 0.6 - 0.7 | High Confidence | Flag for investigation |
| 0.5 - 0.6 | Medium Confidence | Potential match, needs review |
| 0.4 - 0.5 | Low Confidence | Weak match, secondary check |
| < 0.4 | No Match | Different persons |

### GPU vs CPU

```python
# Use GPU (faster, recommended if NVIDIA GPU available)
extractor = FaceEmbeddingExtractor(use_gpu=True)

# Use CPU (slower but works everywhere)
extractor = FaceEmbeddingExtractor(use_gpu=False)
```

GPU Requirements:
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- For CPU-only: No special requirements

## API Reference

### FaceEmbeddingExtractor

#### `__init__(use_gpu=True)`
Initialize the face analysis model.

#### `extract_embedding(img_path, return_normalized=True)`
Extract face embedding from an image.
- Returns: `numpy.ndarray` (512 dimensions)
- Raises: `ValueError` if no face detected

#### `extract_all_faces(img_path, return_normalized=True)`
Extract embeddings for all faces in an image.
- Returns: `list` of embeddings

#### `compute_similarity(embedding1, embedding2)`
Calculate cosine similarity between two embeddings.
- Returns: `float` (0 to 1)

#### `compare_images(img_path1, img_path2, threshold=0.5)`
Compare two images and determine if they match.
- Returns: `dict` with match status and similarity

### FaceRecognitionMatcher

#### `find_matches_for_missing_person(db, missing_person_pid, top_n=5)`
Find potential UIDB matches for a missing person.
- Returns: `list` of match dictionaries

#### `find_matches_for_uidb(db, uidb_pid, top_n=5)`
Find potential missing persons matches for a UIDB.
- Returns: `list` of match dictionaries

#### `auto_match_new_uidb(db, uidb_pid, auto_update=False)`
Automatically find matches when new UIDB is added.
- Returns: `dict` with categorized matches

## Workflow Integration

### Typical Workflow

1. **New Missing Person Reported**
   ```python
   # Add to database with photos
   with DatabaseHelper() as db:
       pid = db.add_missing_person(data, profile_photo_path='photo.jpg')
   ```

2. **New Unidentified Body Found**
   ```python
   # Add preliminary report
   with DatabaseHelper() as db:
       pid = db.add_preliminary_uidb(data, profile_photo_path='photo.jpg')
       
       # Auto-match with missing persons
       matcher = FaceRecognitionMatcher()
       matches = matcher.auto_match_new_uidb(db, pid)
   ```

3. **Review Matches**
   ```python
   # Police review high-confidence matches
   for match in matches['high_confidence_matches']:
       # Compare physical attributes
       mp = db.get_by_pid('missing_persons', match['mp_pid'])
       uidb = db.get_by_pid('preliminary_uidb_reports', pid)
       
       # Manual verification
       print(f"Check: {match['mp_name']} vs UIDB-{pid}")
   ```

4. **Confirm Match**
   ```python
   # Update statuses
   db.update_status('missing_persons', mp_pid, 'Matched')
   db.update_status('unidentified_bodies', uidb_pid, 'Matched')
   ```

## Performance Considerations

- **GPU Acceleration**: ~10x faster than CPU
- **Image Size**: Larger images take longer (resize to max 1920x1080 recommended)
- **Batch Processing**: More efficient than processing one by one
- **First Run**: Models download (~100MB) on first use

## Troubleshooting

### "No faces detected"
- Ensure image has clear, visible faces
- Face should be front-facing (not profile)
- Minimum face size: ~50x50 pixels
- Good lighting conditions

### "CUDA not available"
- Install CUDA Toolkit from NVIDIA
- Or use `use_gpu=False` for CPU mode

### "Import error: insightface"
```powershell
conda activate hsf
pip install insightface onnxruntime opencv-python
```

## Advanced Usage

### Custom Threshold for Different Cases

```python
# High-security cases (minimize false positives)
matcher = FaceRecognitionMatcher(similarity_threshold=0.7)

# Preliminary screening (catch more possibilities)
matcher = FaceRecognitionMatcher(similarity_threshold=0.4)
```

### Combining Face + Physical Attributes

```python
matcher = FaceRecognitionMatcher()

with DatabaseHelper() as db:
    # Get face matches
    face_matches = matcher.find_matches_for_missing_person(db, 'MP-2024-00001')
    
    for match in face_matches:
        # Get full records
        mp = db.get_by_pid('missing_persons', 'MP-2024-00001')
        uidb = db.get_by_pid('unidentified_bodies', match['uidb_pid'])
        
        # Compare physical attributes
        attr_scores = matcher.compare_physical_attributes(mp, uidb)
        
        # Combined confidence
        if match['similarity'] > 0.6 and attr_scores['overall_match_percentage'] > 70:
            print(f"STRONG MATCH: {match['uidb_pid']}")
            print(f"  Face: {match['similarity']:.2%}")
            print(f"  Attributes: {attr_scores['overall_match_percentage']:.1f}%")
```

## Best Practices

1. **Always use normalized embeddings** for similarity comparison
2. **Set appropriate thresholds** based on your accuracy requirements
3. **Combine face matching with physical attributes** for better accuracy
4. **Manual verification required** for all matches before final confirmation
5. **Regular model updates** - check for InsightFace updates periodically
6. **Photo quality matters** - use clear, well-lit, front-facing photos

## Security & Privacy

- Embeddings are 512-dimensional vectors (not reversible to original photo)
- Store embeddings separately from photos for additional security
- Implement access controls on face recognition functionality
- Log all matching operations for audit trail

---

**Next Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Test with sample images: `python face_embedding.py`
3. Integrate with database: `python face_recognition_integration.py`
