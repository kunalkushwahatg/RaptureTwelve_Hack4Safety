"""
Face Embedding Extraction Module
Extracts facial embeddings using InsightFace for missing persons identification
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis
import os
from pathlib import Path
import json


class FaceEmbeddingExtractor:
    """
    Extract face embeddings from images for facial recognition matching
    """
    
    def __init__(self, use_gpu=True):
        """
        Initialize the face analysis model
        
        Args:
            use_gpu: If True, use CUDA (GPU) if available, else CPU
        """
        print("Initializing Face Analysis model...")
        
        # Set providers based on GPU availability
        if use_gpu:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            providers = ['CPUExecutionProvider']
        
        # Initialize FaceAnalysis
        self.app = FaceAnalysis(providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        print(f"✓ Face Analysis model initialized (Providers: {providers})")
    
    def extract_embedding(self, img_path, return_normalized=True):
        """
        Extract face embedding from a single image
        
        Args:
            img_path: Path to the image file
            return_normalized: If True, return L2-normalized embedding
        
        Returns:
            numpy.ndarray: Face embedding vector (512 dimensions)
        
        Raises:
            ValueError: If image cannot be loaded or no face detected
        """
        # Validate path
        if not os.path.exists(img_path):
            raise ValueError(f"Image file not found: {img_path}")
        
        # Load image
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Failed to load image at {img_path}. Check path, extension, or file integrity.")
        
        # Detect faces
        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError(f"No faces detected in the image: {img_path}")
        
        # Get the first (largest) face
        # InsightFace returns faces sorted by area (largest first)
        if return_normalized:
            embedding = faces[0].normed_embedding  # L2-normalized for cosine similarity
        else:
            embedding = faces[0].embedding  # Raw embedding
        
        return embedding
    
    def extract_all_faces(self, img_path, return_normalized=True):
        """
        Extract embeddings for all faces detected in an image
        
        Args:
            img_path: Path to the image file
            return_normalized: If True, return L2-normalized embeddings
        
        Returns:
            list: List of face embedding vectors
        """
        # Validate path
        if not os.path.exists(img_path):
            raise ValueError(f"Image file not found: {img_path}")
        
        # Load image
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Failed to load image at {img_path}")
        
        # Detect faces
        faces = self.app.get(img)
        if len(faces) == 0:
            return []
        
        # Extract embeddings for all faces
        embeddings = []
        for face in faces:
            if return_normalized:
                embeddings.append(face.normed_embedding)
            else:
                embeddings.append(face.embedding)
        
        return embeddings
    
    def compute_similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First face embedding (normalized)
            embedding2: Second face embedding (normalized)
        
        Returns:
            float: Similarity score (0 to 1, higher means more similar)
        """
        # If embeddings are normalized, dot product = cosine similarity
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)
    
    def compare_images(self, img_path1, img_path2, threshold=0.5):
        """
        Compare two images and determine if they match
        
        Args:
            img_path1: Path to first image
            img_path2: Path to second image
            threshold: Similarity threshold (default 0.5, common range 0.4-0.6)
        
        Returns:
            dict: {
                'match': bool,
                'similarity': float,
                'threshold': float
            }
        """
        # Extract embeddings
        embedding1 = self.extract_embedding(img_path1)
        embedding2 = self.extract_embedding(img_path2)
        
        # Compute similarity
        similarity = self.compute_similarity(embedding1, embedding2)
        
        # Check if match
        is_match = similarity > threshold
        
        return {
            'match': is_match,
            'similarity': similarity,
            'threshold': threshold
        }
    
    def save_embedding(self, embedding, output_path):
        """
        Save embedding to a file (JSON format)
        
        Args:
            embedding: Face embedding vector
            output_path: Path to save the embedding file
        """
        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist()
        
        data = {
            'embedding': embedding_list,
            'dimensions': len(embedding_list),
            'normalized': True
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f)
        
        print(f"✓ Embedding saved to {output_path}")
    
    def load_embedding(self, input_path):
        """
        Load embedding from a file
        
        Args:
            input_path: Path to the embedding file
        
        Returns:
            numpy.ndarray: Face embedding vector
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        embedding = np.array(data['embedding'], dtype=np.float32)
        return embedding
    
    def batch_extract_embeddings(self, image_paths, output_dir=None):
        """
        Extract embeddings from multiple images
        
        Args:
            image_paths: List of image file paths
            output_dir: Optional directory to save embeddings
        
        Returns:
            dict: {image_path: embedding}
        """
        results = {}
        
        for img_path in image_paths:
            try:
                embedding = self.extract_embedding(img_path)
                results[img_path] = embedding
                
                # Save if output directory specified
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    filename = Path(img_path).stem + '_embedding.json'
                    output_path = os.path.join(output_dir, filename)
                    self.save_embedding(embedding, output_path)
                
                print(f"✓ Extracted embedding from {img_path}")
                
            except Exception as e:
                print(f"✗ Failed to extract from {img_path}: {e}")
                results[img_path] = None
        
        return results


# Convenience functions
def extract_face_embedding(img_path, use_gpu=True):
    """
    Quick function to extract embedding from a single image
    
    Args:
        img_path: Path to the image file
        use_gpu: Use GPU if available
    
    Returns:
        numpy.ndarray: Face embedding (512 dimensions)
    """
    extractor = FaceEmbeddingExtractor(use_gpu=use_gpu)
    return extractor.extract_embedding(img_path)


def compare_faces(img_path1, img_path2, threshold=0.5, use_gpu=True):
    """
    Quick function to compare two face images
    
    Args:
        img_path1: Path to first image
        img_path2: Path to second image
        threshold: Similarity threshold (0.4-0.6 typical)
        use_gpu: Use GPU if available
    
    Returns:
        dict: Comparison results
    """
    extractor = FaceEmbeddingExtractor(use_gpu=use_gpu)
    return extractor.compare_images(img_path1, img_path2, threshold)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Face Embedding Extraction - Example Usage")
    print("=" * 70)
    print()
    
    # Initialize extractor
    try:
        extractor = FaceEmbeddingExtractor(use_gpu=True)
        
        # Example 1: Extract embedding from single image
        print("\n--- Example 1: Extract Single Embedding ---")
        # img_path = 'photos/missing_persons/MP-2024-00001/profile.jpg'
        # embedding = extractor.extract_embedding(img_path)
        # print(f"Embedding shape: {embedding.shape}")
        # print(f"Embedding (first 10 values): {embedding[:10]}")
        
        # Example 2: Compare two images
        print("\n--- Example 2: Compare Two Images ---")
        # img_path1 = 'photos/missing_persons/MP-2024-00001/profile.jpg'
        # img_path2 = 'photos/unidentified_bodies/UIDB-2024-00001/profile.jpg'
        # result = extractor.compare_images(img_path1, img_path2, threshold=0.5)
        # print(f"Match: {result['match']}")
        # print(f"Similarity: {result['similarity']:.4f}")
        # print(f"Threshold: {result['threshold']}")
        
        # Example 3: Batch processing
        print("\n--- Example 3: Batch Extract Embeddings ---")
        # image_paths = [
        #     'photos/missing_persons/MP-2024-00001/profile.jpg',
        #     'photos/missing_persons/MP-2024-00002/profile.jpg',
        # ]
        # results = extractor.batch_extract_embeddings(image_paths, output_dir='embeddings')
        # print(f"Processed {len(results)} images")
        
        print("\n✓ Face embedding extractor is ready!")
        print("\nNote: Uncomment the examples above and provide actual image paths to test.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to install InsightFace:")
        print("  pip install insightface onnxruntime opencv-python")
