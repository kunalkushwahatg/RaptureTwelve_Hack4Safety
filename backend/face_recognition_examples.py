"""
Simple Usage Examples for Face Recognition Module
Run this after installing dependencies:
    pip install -r requirements_face_recognition.txt
"""

from face_recognition import FaceRecognizer

def example_1_single_face():
    """Extract embedding from a single face image"""
    print("\n" + "="*60)
    print("Example 1: Extract Face Embedding")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Replace with your image path
        image_path = 'photos/missing_persons/test_image.jpg'
        
        embedding = recognizer.extract_embedding(image_path)
        print(f"✓ Successfully extracted embedding")
        print(f"  - Shape: {embedding.shape}")
        print(f"  - Type: {type(embedding)}")
        print(f"  - Sample values: {embedding[:5]}")
        
        return embedding
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def example_2_compare_faces():
    """Compare two face images"""
    print("\n" + "="*60)
    print("Example 2: Compare Two Faces")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Replace with your image paths
        image1 = 'photos/missing_persons/person1.jpg'
        image2 = 'photos/missing_persons/person2.jpg'
        
        is_match, similarity = recognizer.compare_faces(
            image1, 
            image2, 
            threshold=0.5
        )
        
        print(f"✓ Comparison completed")
        print(f"  - Similarity Score: {similarity:.4f}")
        print(f"  - Match: {'✓ YES (Same person)' if is_match else '✗ NO (Different person)'}")
        print(f"  - Threshold used: 0.5")
        
        # Interpretation guide
        print("\n  Similarity Score Guide:")
        print(f"    > 0.6  : Strong match (very likely same person)")
        print(f"    0.4-0.6: Moderate match (possibly same person)")
        print(f"    < 0.4  : Weak match (likely different person)")
        
        return is_match, similarity
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None


def example_3_count_faces():
    """Count faces in an image"""
    print("\n" + "="*60)
    print("Example 3: Count Faces in Image")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Replace with your image path
        image_path = 'photos/preliminary_uidb/group_photo.jpg'
        
        count = recognizer.detect_faces_count(image_path)
        print(f"✓ Detected {count} face(s) in the image")
        
        return count
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 0


def example_4_multiple_faces():
    """Extract embeddings from all faces in an image"""
    print("\n" + "="*60)
    print("Example 4: Extract All Face Embeddings")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Replace with your image path
        image_path = 'photos/preliminary_uidb/group_photo.jpg'
        
        embeddings = recognizer.extract_all_embeddings(image_path)
        print(f"✓ Extracted {len(embeddings)} embedding(s)")
        
        for idx, emb in enumerate(embeddings):
            print(f"  Face {idx + 1}:")
            print(f"    - Shape: {emb.shape}")
            print(f"    - Sample: {emb[:3]}")
        
        return embeddings
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def example_5_face_details():
    """Get detailed face information"""
    print("\n" + "="*60)
    print("Example 5: Get Detailed Face Information")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Replace with your image path
        image_path = 'photos/missing_persons/person1.jpg'
        
        face_info = recognizer.get_face_info(image_path)
        print(f"✓ Found {len(face_info)} face(s)")
        
        for info in face_info:
            print(f"\n  Face #{info['face_index'] + 1}:")
            print(f"    - Detection Confidence: {info['det_score']:.4f}")
            print(f"    - Bounding Box: {info['bbox']}")
            print(f"    - Embedding Shape: {info['embedding_shape']}")
            if info['age'] is not None:
                print(f"    - Estimated Age: {info['age']}")
            if info['gender'] is not None:
                print(f"    - Gender: {info['gender']}")
        
        return face_info
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def example_6_batch_comparison():
    """Compare one face against multiple faces"""
    print("\n" + "="*60)
    print("Example 6: Batch Face Comparison")
    print("="*60)
    
    recognizer = FaceRecognizer(use_gpu=True)
    
    try:
        # Reference image
        reference_image = 'photos/missing_persons/missing_person.jpg'
        reference_embedding = recognizer.extract_embedding(reference_image)
        
        # Candidate images to compare against
        candidate_images = [
            'photos/preliminary_uidb/candidate1.jpg',
            'photos/preliminary_uidb/candidate2.jpg',
            'photos/preliminary_uidb/candidate3.jpg'
        ]
        
        print(f"Comparing reference image against {len(candidate_images)} candidates...\n")
        
        matches = []
        for idx, candidate_path in enumerate(candidate_images):
            try:
                candidate_embedding = recognizer.extract_embedding(candidate_path)
                similarity = recognizer.compute_similarity(reference_embedding, candidate_embedding)
                
                is_match = similarity > 0.5
                matches.append({
                    'image': candidate_path,
                    'similarity': similarity,
                    'is_match': is_match
                })
                
                print(f"  Candidate {idx + 1}: {similarity:.4f} - {'✓ MATCH' if is_match else '✗ No match'}")
                
            except Exception as e:
                print(f"  Candidate {idx + 1}: Error - {e}")
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"\n✓ Best match: {matches[0]['image']} (score: {matches[0]['similarity']:.4f})")
        
        return matches
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


if __name__ == "__main__":
    """
    Run all examples
    Note: Update image paths before running
    """
    
    print("\n" + "="*60)
    print("FACE RECOGNITION MODULE - EXAMPLES")
    print("="*60)
    print("\nMake sure to:")
    print("1. Install dependencies: pip install -r requirements_face_recognition.txt")
    print("2. Update image paths in the examples below")
    print("3. Have test images ready in the photos/ folder")
    
    # Uncomment the examples you want to run:
    
    # example_1_single_face()
    # example_2_compare_faces()
    # example_3_count_faces()
    # example_4_multiple_faces()
    # example_5_face_details()
    # example_6_batch_comparison()
    
    print("\n" + "="*60)
    print("Examples ready to run!")
    print("Uncomment the example you want to test in this file.")
    print("="*60 + "\n")
