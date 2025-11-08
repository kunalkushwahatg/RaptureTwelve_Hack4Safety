"""
Face Recognition Module using InsightFace
Provides face embedding extraction and similarity comparison
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from typing import Optional, Tuple, List
import os


class FaceRecognizer:
    """
    A class for face detection, embedding extraction, and similarity comparison.
    Uses InsightFace for high-accuracy face recognition.
    """
    
    def __init__(self, use_gpu: bool = True, det_size: Tuple[int, int] = (640, 640)):
        """
        Initialize the face recognition model.
        
        Args:
            use_gpu: Whether to use GPU (CUDA) if available
            det_size: Detection size for face detection (width, height)
        """
        print("Initializing Face Recognition Model...")
        
        # Set provider based on GPU availability
        providers = ['CUDAExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
        
        # Initialize InsightFace
        self.app = FaceAnalysis(providers=providers)
        self.app.prepare(ctx_id=0, det_size=det_size)
        
        print(f"✓ Model initialized with provider: {providers[0]}")
    
    def extract_embedding(self, image_path: str, normalize: bool = True) -> np.ndarray:
        """
        Extract face embedding from an image.
        
        Args:
            image_path: Path to the image file
            normalize: Whether to return L2-normalized embedding
            
        Returns:
            Face embedding as numpy array (512,)
            
        Raises:
            ValueError: If image cannot be loaded or no face is detected
        """
        # Validate file exists
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}. Check file format or integrity.")
        
        # Detect faces
        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError(f"No faces detected in image: {image_path}")
        
        # Get embedding from first detected face
        if normalize:
            embedding = faces[0].normed_embedding  # L2-normalized
        else:
            embedding = faces[0].embedding  # Raw embedding
        
        return embedding
    
    def extract_all_embeddings(self, image_path: str, normalize: bool = True) -> List[np.ndarray]:
        """
        Extract embeddings for ALL faces detected in an image.
        
        Args:
            image_path: Path to the image file
            normalize: Whether to return L2-normalized embeddings
            
        Returns:
            List of face embeddings
            
        Raises:
            ValueError: If image cannot be loaded
        """
        # Validate file exists
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}. Check file format or integrity.")
        
        # Detect faces
        faces = self.app.get(img)
        
        # Extract all embeddings
        embeddings = []
        for face in faces:
            if normalize:
                embeddings.append(face.normed_embedding)
            else:
                embeddings.append(face.embedding)
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First face embedding (normalized)
            embedding2: Second face embedding (normalized)
            
        Returns:
            Similarity score between -1 and 1 (higher means more similar)
        """
        # For normalized embeddings, dot product = cosine similarity
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)
    
    def compare_faces(self, image_path1: str, image_path2: str, threshold: float = 0.5) -> Tuple[bool, float]:
        """
        Compare two face images and determine if they match.
        
        Args:
            image_path1: Path to first image
            image_path2: Path to second image
            threshold: Similarity threshold for match (common range: 0.4-0.6)
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        # Extract embeddings
        embedding1 = self.extract_embedding(image_path1, normalize=True)
        embedding2 = self.extract_embedding(image_path2, normalize=True)
        
        # Compute similarity
        similarity = self.compute_similarity(embedding1, embedding2)
        
        # Determine match
        is_match = similarity > threshold
        
        return is_match, similarity
    
    def detect_faces_count(self, image_path: str) -> int:
        """
        Count the number of faces in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Number of faces detected
        """
        # Validate file exists
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}. Check file format or integrity.")
        
        # Detect faces
        faces = self.app.get(img)
        
        return len(faces)
    
    def get_face_info(self, image_path: str) -> List[dict]:
        """
        Get detailed information about all detected faces.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing face information
        """
        # Validate file exists
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}. Check file format or integrity.")
        
        # Detect faces
        faces = self.app.get(img)
        
        # Collect face information
        face_info_list = []
        for idx, face in enumerate(faces):
            info = {
                'face_index': idx,
                'bbox': face.bbox.tolist(),  # Bounding box [x1, y1, x2, y2]
                'det_score': float(face.det_score),  # Detection confidence
                'embedding_shape': face.embedding.shape,
                'gender': getattr(face, 'gender', None),
                'age': getattr(face, 'age', None)
            }
            face_info_list.append(info)
        
        return face_info_list


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of the FaceRecognizer class
    """
    
    # Initialize the recognizer
    recognizer = FaceRecognizer(use_gpu=True)
    
    # Example 1: Extract single embedding
    try:
        print("\n--- Example 1: Extract Embedding ---")
        embedding = recognizer.extract_embedding('WhatsApp Image 2025-11-08 at 12.06.23_9d81f1af.jpg')
        print(f"✓ Embedding extracted successfully")
        print(f"  Shape: {embedding.shape}")
        print(f"  First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
