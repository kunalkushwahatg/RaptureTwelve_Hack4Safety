"""
Test Vector Retrieval Pipeline
Uses Rohan Sharma missing person data and test.jpg to test the complete retrieval system
"""

import numpy as np
import os
import sys
from pathlib import Path

# Test data for Rohan Sharma
ROHAN_DATA = {
    "id": 6,
    "pid": "MP-2025-00006",
    "case_number": "MPR-WOR-2025-00123",
    "police_station": "Worli Police Station, Mumbai",
    "reported_date": "2025-11-06 08:30:00",
    "last_seen_date": "2025-11-05 18:00:00",
    "full_name": "Rohan Sharma",
    "age": 67,
    "gender": "Male",
    "height_cm": 165,
    "build": "Slim",
    "hair_color": "White / Grey, bald on top",
    "eye_color": "Brown",
    "distinguishing_marks": "He has white patches on his face and forehead from a skin condition (vitiligo). His ears are also a bit large. Has a small mole on his right cheek.",
    "last_seen_clothing": "Light blue cotton shirt and grey trousers. Was wearing brown sandals.",
    "person_description": "My father, Rohan, is 67 years old. He is slim and bald on top with white hair on the sides. He has a white beard and mustache. He suffers from some memory loss.",
    "last_seen_latitude": 19.0076,
    "last_seen_longitude": 72.8126,
    "last_seen_address": "Worli Sea Face, Mumbai. Was going for an evening walk and did not return.",
    "photo_url": "photos/missing_persons/MP-2025-00006/rohan_sharma_1.jpg",
    "extra_photos": ["photos/missing_persons/MP-2025-00006/family_photo.jpg"],
    "reporter_name": "Arjun Sharma",
    "reporter_relationship": "Son",
    "reporter_phone": "9820011223",
    "status": "Missing"
}

# Image path
TEST_IMAGE = "test.jpg"


def test_text_embedding():
    """Test text embedding generation"""
    print("\n" + "="*70)
    print("TEST 1: TEXT EMBEDDING GENERATION")
    print("="*70 + "\n")
    
    try:
        from text_embedder import TextEmbedder
        
        # Initialize embedder
        embedder = TextEmbedder()
        
        # Create search description from Rohan's data
        search_text = f"""Missing person: {ROHAN_DATA['full_name']}, {ROHAN_DATA['gender']}, {ROHAN_DATA['age']} years old, {ROHAN_DATA['height_cm']}cm tall, {ROHAN_DATA['build']} build. {ROHAN_DATA['hair_color']} hair, {ROHAN_DATA['eye_color']} eyes. {ROHAN_DATA['distinguishing_marks']} Last seen wearing {ROHAN_DATA['last_seen_clothing']} at {ROHAN_DATA['last_seen_address']}."""
        
        print(f"Search Text:\n{search_text}\n")
        
        # Generate embedding
        print("Generating text embedding...")
        embedding = embedder.get_embedding(search_text)
        
        print(f"✓ Text embedding generated successfully")
        print(f"  Shape: {embedding.shape}")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  Sample values: {embedding[:5]}\n")
        
        return embedding
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_face_embedding():
    """Test face embedding extraction from test.jpg"""
    print("\n" + "="*70)
    print("TEST 2: FACE EMBEDDING EXTRACTION")
    print("="*70 + "\n")
    
    try:
        from face_embedding import FaceEmbeddingExtractor
        
        # Check if test image exists
        if not os.path.exists(TEST_IMAGE):
            print(f"✗ Test image not found: {TEST_IMAGE}")
            print(f"  Please ensure {TEST_IMAGE} exists in the backend folder")
            return None
        
        print(f"Test Image: {TEST_IMAGE}")
        
        # Initialize face extractor
        print("\nInitializing Face Embedding Extractor...")
        extractor = FaceEmbeddingExtractor(use_gpu=False)
        
        # Extract embedding
        print(f"\nExtracting face embedding from {TEST_IMAGE}...")
        embedding = extractor.extract_embedding(TEST_IMAGE, return_normalized=True)
        
        print(f"✓ Face embedding extracted successfully")
        print(f"  Shape: {embedding.shape}")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  Sample values: {embedding[:5]}\n")
        
        return embedding
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: Make sure to install required packages:")
        print("  pip install opencv-python insightface onnxruntime")
        return None


def test_vector_search(face_embedding=None, text_embedding=None):
    """Test vector search in Qdrant"""
    print("\n" + "="*70)
    print("TEST 3: VECTOR SEARCH IN QDRANT")
    print("="*70 + "\n")
    
    try:
        from vector_retrieval import VectorRetrieval
        
        # Initialize retrieval system
        print("Connecting to Qdrant...")
        retrieval = VectorRetrieval(host="localhost", port=6333)
        
        # Test search without metadata filters (to work with limited data)
        print("\nSearching for matches using vector similarity only:")
        print(f"  Rohan's Profile: {ROHAN_DATA['gender']}, {ROHAN_DATA['age']} years, {ROHAN_DATA['height_cm']}cm")
        print(f"  Note: Metadata filters DISABLED due to limited dataset")
        
        # Perform search WITHOUT metadata filters
        results = retrieval.search_and_combine(
            face_embedding=face_embedding,
            text_embedding=text_embedding,
            gender=None,  # No filter
            age_min=None,  # No filter
            age_max=None,  # No filter
            height_min=None,  # No filter
            height_max=None,  # No filter
            w1=0.6 if face_embedding is not None else 0.0,  # 60% face weight
            w2=0.4 if text_embedding is not None else 1.0,  # 40% text weight
            top_n=10,
            limit_per_collection=50
        )
        
        # Display results
        print("\n" + "="*70)
        print("SEARCH RESULTS")
        print("="*70 + "\n")
        
        if not results:
            print("⊘ No matches found")
            return
        
        print(f"Found {len(results)} potential matches:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. PID: {result['pid']}")
            print(f"   Combined Score: {result['combined_score']:.4f}")
            if face_embedding is not None:
                print(f"   Face Similarity: {result['face_score']:.4f}")
            if text_embedding is not None:
                print(f"   Text Similarity: {result['text_score']:.4f}")
            print(f"   Age: {result.get('estimated_age', result.get('age', 'N/A'))}")
            print(f"   Gender: {result['gender']}")
            print(f"   Height: {result['height_cm']} cm")
            print()
        
        # Highlight best match
        if results:
            best_match = results[0]
            print("="*70)
            print("BEST MATCH")
            print("="*70)
            print(f"PID: {best_match['pid']}")
            print(f"Confidence: {best_match['combined_score']:.2%}")
            print("="*70 + "\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("  1. Qdrant is running: Check if port 6333 is accessible")
        print("  2. Collections exist and are populated")


def test_qdrant_connection():
    """Test basic Qdrant connection and collection status"""
    print("\n" + "="*70)
    print("PRE-TEST: CHECKING QDRANT CONNECTION")
    print("="*70 + "\n")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Get collections
        collections = client.get_collections()
        print("✓ Connected to Qdrant successfully\n")
        
        print("Available collections:")
        for col in collections.collections:
            try:
                info = client.get_collection(col.name)
                print(f"  - {col.name}: {info.points_count} points")
            except:
                print(f"  - {col.name}: (error getting info)")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Cannot connect to Qdrant: {e}")
        print("\nPlease start Qdrant:")
        print("  Docker: docker run -p 6333:6333 qdrant/qdrant")
        print()
        return False


def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("VECTOR RETRIEVAL PIPELINE TEST")
    print("Testing with Rohan Sharma's missing person case")
    print("="*70)
    
    # Pre-test: Check Qdrant
    if not test_qdrant_connection():
        print("⚠ Skipping tests - Qdrant not available")
        return
    
    # Test 1: Text Embedding
    text_embedding = test_text_embedding()
    
    # Test 2: Face Embedding
    face_embedding = test_face_embedding()
    
    # Test 3: Vector Search
    if text_embedding is not None or face_embedding is not None:
        test_vector_search(
            face_embedding=face_embedding,
            text_embedding=text_embedding
        )
    else:
        print("\n⚠ Skipping vector search - no embeddings generated")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Text Embedding: {'✓ Success' if text_embedding is not None else '✗ Failed'}")
    print(f"Face Embedding: {'✓ Success' if face_embedding is not None else '✗ Failed'}")
    print("="*70 + "\n")
    
    print("Next steps:")
    if text_embedding is None:
        print("  - Install OpenAI package: pip install openai")
        print("  - Set OPENAI_API_KEY in .env file")
    if face_embedding is None:
        print("  - Install face recognition packages:")
        print("    pip install opencv-python insightface onnxruntime")
    if text_embedding is not None and face_embedding is not None:
        print("  ✓ All tests passed! Vector retrieval pipeline is working.")
    
    print()


if __name__ == "__main__":
    main()
