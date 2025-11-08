"""
Complete Example: Vector Retrieval Workflow
Demonstrates end-to-end search using face and text embeddings
"""

import numpy as np
from vector_retrieval import VectorRetrieval
from face_recognition import FaceRecognizer
from text_embedder import TextEmbedder


def example_search_missing_person():
    """
    Example: Search for a missing person using photo and description
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Search Missing Person with Photo & Description")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    face_rec = FaceRecognizer()
    text_emb = TextEmbedder()
    
    # Scenario: Someone reports seeing a person matching description
    print("Scenario: Witness reports seeing a person\n")
    
    # Get face embedding from photo
    print("Step 1: Extract face embedding from witness photo...")
    # Replace with actual photo path
    # face_vector = face_rec.extract_embedding("witness_photo.jpg")
    face_vector = np.random.rand(512)  # Dummy for demo
    print("✓ Face embedding extracted (512 dimensions)\n")
    
    # Get text embedding from description
    print("Step 2: Extract text embedding from description...")
    description = """
    Male person, approximately 25-30 years old, short black hair,
    wearing blue jeans and white t-shirt, around 175cm tall
    """
    text_vector = text_emb.get_embedding(description)
    print("✓ Text embedding extracted (1536 dimensions)\n")
    
    # Search with metadata filters
    print("Step 3: Search vector database with filters...")
    results = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        age_min=23,      # ±2-3 years from estimate
        age_max=32,
        height_min=170,  # ±5 cm from estimate
        height_max=180,
        w1=0.6,  # 60% weight to face (photo is clear)
        w2=0.4,  # 40% weight to text
        top_n=5
    )
    
    # Display results
    print("\n" + "-"*60)
    print(f"TOP {len(results)} MATCHES")
    print("-"*60 + "\n")
    
    for i, match in enumerate(results, 1):
        print(f"Match #{i}:")
        print(f"  PID: {match['pid']}")
        print(f"  Combined Score: {match['combined_score']:.4f} (Higher is better)")
        print(f"  Face Similarity: {match['face_score']:.4f}")
        print(f"  Text Similarity: {match['text_score']:.4f}")
        print(f"  Age: {match['age']} years")
        print(f"  Gender: {match['gender']}")
        print(f"  Height: {match['height_cm']} cm")
        print()


def example_text_only_search():
    """
    Example: Search with only text description (no photo)
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Text-Only Search (No Photo Available)")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    text_emb = TextEmbedder()
    
    print("Scenario: Verbal description from witness, no photo\n")
    
    # Get text embedding
    description = """
    Female, middle-aged around 45 years, blonde hair shoulder length,
    wearing glasses and red jacket, approximately 165cm tall
    """
    print(f"Description: {description.strip()}\n")
    
    text_vector = text_emb.get_embedding(description)
    print("✓ Text embedding extracted\n")
    
    # Search (text only)
    results = retrieval.search_and_combine(
        text_embedding=text_vector,  # No face embedding
        gender="Female",
        age_min=40,
        age_max=50,
        height_min=160,
        height_max=170,
        w1=0.0,  # No face
        w2=1.0,  # 100% text
        top_n=5
    )
    
    print(f"Found {len(results)} matches based on text similarity")


def example_face_only_search():
    """
    Example: Search with only face photo (no description)
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Face-Only Search (No Description)")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    face_rec = FaceRecognizer()
    
    print("Scenario: CCTV footage with clear face, no other info\n")
    
    # Get face embedding
    # face_vector = face_rec.extract_embedding("cctv_frame.jpg")
    face_vector = np.random.rand(512)  # Dummy for demo
    print("✓ Face embedding extracted from CCTV footage\n")
    
    # Estimate age and gender from photo (manually or using additional AI)
    estimated_gender = "Male"
    estimated_age_min = 30
    estimated_age_max = 40
    
    # Search (face only)
    results = retrieval.search_and_combine(
        face_embedding=face_vector,  # No text embedding
        gender=estimated_gender,
        age_min=estimated_age_min,
        age_max=estimated_age_max,
        w1=1.0,  # 100% face
        w2=0.0,  # No text
        top_n=5
    )
    
    print(f"Found {len(results)} matches based on face similarity")


def example_broad_search():
    """
    Example: Broad search with minimal filters
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Broad Search (Minimal Information)")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    face_rec = FaceRecognizer()
    
    print("Scenario: Poor quality photo, limited information\n")
    
    # Get face embedding
    face_vector = np.random.rand(512)  # Dummy for demo
    
    # Only gender known, age/height uncertain
    results = retrieval.search_and_combine(
        face_embedding=face_vector,
        gender="Female",  # Only reliable filter
        w1=1.0,
        w2=0.0,
        top_n=20  # Get more results due to broad search
    )
    
    print(f"Broad search returned {len(results)} potential matches")
    print("Recommend manual review of top results")


def example_weighted_comparison():
    """
    Example: Compare different weight configurations
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Weight Configuration Comparison")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    
    # Dummy embeddings
    face_vector = np.random.rand(512)
    text_vector = np.random.rand(1536)
    
    print("Testing different weight configurations:\n")
    
    # Config 1: Balanced
    print("1. Balanced (50/50):")
    results_balanced = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        age_min=25,
        age_max=35,
        w1=0.5,
        w2=0.5,
        top_n=3
    )
    print(f"   Top match: {results_balanced[0]['pid']} "
          f"(Score: {results_balanced[0]['combined_score']:.4f})\n")
    
    # Config 2: Face-focused
    print("2. Face-Focused (70/30):")
    results_face = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        age_min=25,
        age_max=35,
        w1=0.7,
        w2=0.3,
        top_n=3
    )
    print(f"   Top match: {results_face[0]['pid']} "
          f"(Score: {results_face[0]['combined_score']:.4f})\n")
    
    # Config 3: Text-focused
    print("3. Text-Focused (30/70):")
    results_text = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        age_min=25,
        age_max=35,
        w1=0.3,
        w2=0.7,
        top_n=3
    )
    print(f"   Top match: {results_text[0]['pid']} "
          f"(Score: {results_text[0]['combined_score']:.4f})\n")
    
    print("Note: Different weights may yield different top matches")


def example_integration_with_database():
    """
    Example: Complete integration with MySQL database
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Integration with Database")
    print("="*60 + "\n")
    
    # Initialize components
    retrieval = VectorRetrieval()
    # Uncomment when database is ready:
    # from db_helper import DatabaseHelper
    # db = DatabaseHelper()
    
    # Dummy embeddings
    face_vector = np.random.rand(512)
    text_vector = np.random.rand(1536)
    
    # Step 1: Vector search
    print("Step 1: Search vector database...")
    matches = retrieval.search_and_combine(
        face_embedding=face_vector,
        text_embedding=text_vector,
        gender="Male",
        age_min=20,
        age_max=30,
        w1=0.6,
        w2=0.4,
        top_n=10
    )
    print(f"✓ Found {len(matches)} vector matches\n")
    
    # Step 2: Fetch full records from MySQL
    print("Step 2: Fetch full records from MySQL...")
    for match in matches[:3]:  # Top 3 matches
        pid = match['pid']
        
        print(f"\nPID: {pid}")
        print(f"  Vector Score: {match['combined_score']:.4f}")
        
        # Uncomment when database is ready:
        # if pid.startswith('MP-'):
        #     records = db.search_records('missing_persons', {'pid': pid})
        #     if records:
        #         print(f"  Name: {records[0]['name']}")
        #         print(f"  Last Seen: {records[0]['last_seen_location']}")
        #         print(f"  Contact: {records[0]['reporter_contact']}")
        # elif pid.startswith('UIDB-'):
        #     records = db.search_records('unidentified_bodies', {'pid': pid})
        #     if records:
        #         print(f"  Found Location: {records[0]['found_location']}")
        #         print(f"  Discovery Date: {records[0]['discovery_date']}")
        
        # For demo (remove when database ready):
        print(f"  [Database record would be fetched here]")


if __name__ == "__main__":
    """
    Run all examples
    """
    
    print("\n" + "█"*60)
    print("VECTOR RETRIEVAL SYSTEM - COMPLETE EXAMPLES")
    print("█"*60)
    
    try:
        # Run examples
        example_search_missing_person()
        
        example_text_only_search()
        
        example_face_only_search()
        
        example_broad_search()
        
        example_weighted_comparison()
        
        example_integration_with_database()
        
        print("\n" + "█"*60)
        print("All examples completed successfully!")
        print("█"*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print("\nPrerequisites:")
        print("  1. Qdrant running: docker run -p 6333:6333 qdrant/qdrant")
        print("  2. Collections created: python setup_vectordb.py")
        print("  3. Sample data inserted in collections")
        print("  4. OpenAI API key in .env file")
        print("\n")
