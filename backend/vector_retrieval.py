"""
Vector Data Retrieval System
Searches face and text embeddings with metadata filters and weighted similarity
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
import numpy as np
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VectorRetrieval:
    """
    Retrieval system for searching face and text embeddings with metadata filtering
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize the retrieval system.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
        """
        self.client = QdrantClient(host=host, port=port)
        self.face_collection = "face_embeddings"
        self.text_collection = "text_embeddings"
        
        print(f"✓ Connected to Qdrant at {host}:{port}")
    
    def create_metadata_filter(
        self,
        gender: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        height_min: Optional[int] = None,
        height_max: Optional[int] = None
    ) -> Filter:
        """
        Create metadata filter for search.
        
        Args:
            gender: Exact gender match ("Male", "Female", "Other", "Unknown")
            age_min: Minimum age (approximate)
            age_max: Maximum age (approximate)
            height_min: Minimum height in cm (approximate)
            height_max: Maximum height in cm (approximate)
            
        Returns:
            Qdrant Filter object
        """
        must_conditions = []
        
        # Gender filter (exact match)
        if gender:
            must_conditions.append(
                FieldCondition(key="gender", match=MatchValue(value=gender))
            )
        
        # Age filter (range)
        if age_min is not None or age_max is not None:
            age_range = {}
            if age_min is not None:
                age_range["gte"] = age_min
            if age_max is not None:
                age_range["lte"] = age_max
            
            must_conditions.append(
                FieldCondition(key="age", range=Range(**age_range))
            )
        
        # Height filter (range)
        if height_min is not None or height_max is not None:
            height_range = {}
            if height_min is not None:
                height_range["gte"] = height_min
            if height_max is not None:
                height_range["lte"] = height_max
            
            must_conditions.append(
                FieldCondition(key="height_cm", range=Range(**height_range))
            )
        
        # If no conditions, return None (no filter)
        if not must_conditions:
            return None
        
        return Filter(must=must_conditions)
    
    def search_face_embeddings(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        metadata_filter: Optional[Filter] = None
    ) -> List[Dict]:
        """
        Search face embeddings collection.
        
        Args:
            query_embedding: Face embedding vector (512 dimensions)
            limit: Maximum number of results
            metadata_filter: Metadata filter for search
            
        Returns:
            List of search results with pid, score, and metadata
        """
        try:
            results = self.client.search(
                collection_name=self.face_collection,
                query_vector=query_embedding.tolist(),
                query_filter=metadata_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'pid': result.payload.get('pid'),
                    'score': result.score,
                    'age': result.payload.get('age'),
                    'gender': result.payload.get('gender'),
                    'height_cm': result.payload.get('height_cm'),
                    'source': 'face'
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"✗ Error searching face embeddings: {e}")
            return []
    
    def search_text_embeddings(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        metadata_filter: Optional[Filter] = None
    ) -> List[Dict]:
        """
        Search text embeddings collection.
        
        Args:
            query_embedding: Text embedding vector (1536 dimensions)
            limit: Maximum number of results
            metadata_filter: Metadata filter for search
            
        Returns:
            List of search results with pid, score, and metadata
        """
        try:
            results = self.client.search(
                collection_name=self.text_collection,
                query_vector=query_embedding.tolist(),
                query_filter=metadata_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'pid': result.payload.get('pid'),
                    'score': result.score,
                    'age': result.payload.get('age'),
                    'gender': result.payload.get('gender'),
                    'height_cm': result.payload.get('height_cm'),
                    'source': 'text'
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"✗ Error searching text embeddings: {e}")
            return []
    
    def parallel_search(
        self,
        face_embedding: Optional[np.ndarray] = None,
        text_embedding: Optional[np.ndarray] = None,
        limit: int = 10,
        gender: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        height_min: Optional[int] = None,
        height_max: Optional[int] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Search both collections in parallel.
        
        Args:
            face_embedding: Face embedding vector (512D)
            text_embedding: Text embedding vector (1536D)
            limit: Maximum results per collection
            gender: Exact gender match
            age_min: Minimum age
            age_max: Maximum age
            height_min: Minimum height (cm)
            height_max: Maximum height (cm)
            
        Returns:
            Tuple of (face_results, text_results)
        """
        # Create metadata filter
        metadata_filter = self.create_metadata_filter(
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            height_min=height_min,
            height_max=height_max
        )
        
        face_results = []
        text_results = []
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            
            # Submit face search if embedding provided
            if face_embedding is not None:
                future_face = executor.submit(
                    self.search_face_embeddings,
                    face_embedding,
                    limit,
                    metadata_filter
                )
                futures.append(('face', future_face))
            
            # Submit text search if embedding provided
            if text_embedding is not None:
                future_text = executor.submit(
                    self.search_text_embeddings,
                    text_embedding,
                    limit,
                    metadata_filter
                )
                futures.append(('text', future_text))
            
            # Collect results
            for search_type, future in futures:
                try:
                    result = future.result()
                    if search_type == 'face':
                        face_results = result
                    else:
                        text_results = result
                except Exception as e:
                    print(f"✗ Error in {search_type} search: {e}")
        
        return face_results, text_results
    
    def combine_results(
        self,
        face_results: List[Dict],
        text_results: List[Dict],
        w1: float = 0.5,
        w2: float = 0.5,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Combine face and text search results with weighted similarity.
        
        Args:
            face_results: Results from face search
            text_results: Results from text search
            w1: Weight for face similarity (0-1)
            w2: Weight for text similarity (0-1)
            top_n: Number of top results to return
            
        Returns:
            List of top N results sorted by combined similarity
        """
        # Normalize weights
        total_weight = w1 + w2
        w1_norm = w1 / total_weight if total_weight > 0 else 0.5
        w2_norm = w2 / total_weight if total_weight > 0 else 0.5
        
        # Create a dictionary to store combined scores
        combined_scores = {}
        
        # Add face results
        for result in face_results:
            pid = result['pid']
            if pid not in combined_scores:
                combined_scores[pid] = {
                    'pid': pid,
                    'face_score': 0.0,
                    'text_score': 0.0,
                    'age': result['age'],
                    'gender': result['gender'],
                    'height_cm': result['height_cm']
                }
            combined_scores[pid]['face_score'] = result['score']
        
        # Add text results
        for result in text_results:
            pid = result['pid']
            if pid not in combined_scores:
                combined_scores[pid] = {
                    'pid': pid,
                    'face_score': 0.0,
                    'text_score': 0.0,
                    'age': result['age'],
                    'gender': result['gender'],
                    'height_cm': result['height_cm']
                }
            combined_scores[pid]['text_score'] = result['score']
        
        # Calculate weighted combined scores
        final_results = []
        for pid, data in combined_scores.items():
            combined_score = (w1_norm * data['face_score']) + (w2_norm * data['text_score'])
            final_results.append({
                'pid': pid,
                'combined_score': combined_score,
                'face_score': data['face_score'],
                'text_score': data['text_score'],
                'age': data['age'],
                'gender': data['gender'],
                'height_cm': data['height_cm']
            })
        
        # Sort by combined score (descending)
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Return top N
        return final_results[:top_n]
    
    def search_and_combine(
        self,
        face_embedding: Optional[np.ndarray] = None,
        text_embedding: Optional[np.ndarray] = None,
        gender: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        height_min: Optional[int] = None,
        height_max: Optional[int] = None,
        w1: float = 0.5,
        w2: float = 0.5,
        top_n: int = 10,
        limit_per_collection: int = 50
    ) -> List[Dict]:
        """
        Complete search pipeline: parallel search + weighted combination.
        
        Args:
            face_embedding: Face embedding vector
            text_embedding: Text embedding vector
            gender: Exact gender filter ("Male", "Female", "Other", "Unknown") - NOT USED
            age_min: Minimum age - NOT USED
            age_max: Maximum age - NOT USED
            height_min: Minimum height in cm - NOT USED
            height_max: Maximum height in cm - NOT USED
            w1: Weight for face similarity (default: 0.5)
            w2: Weight for text similarity (default: 0.5)
            top_n: Number of top results to return (default: 10)
            limit_per_collection: Max results per collection (default: 50)
            
        Returns:
            List of top N results with combined scores
        """
        print(f"\n{'='*60}")
        print("Vector Retrieval Search")
        print(f"{'='*60}\n")
        
        # Validate inputs
        if face_embedding is None and text_embedding is None:
            raise ValueError("At least one embedding (face or text) must be provided")
        
        # Display search parameters
        print("Search Parameters:")
        print(f"  - Metadata Filters: DISABLED (searching all records)")
        print(f"  - Weights: Face={w1:.2f}, Text={w2:.2f}")
        print(f"  - Top N: {top_n}\n")
        
        # Parallel search WITHOUT metadata filters
        print("Searching collections...")
        face_results, text_results = self.parallel_search(
            face_embedding=face_embedding,
            text_embedding=text_embedding,
            limit=limit_per_collection,
            gender=None,
            age_min=None,
            age_max=None,
            height_min=None,
            height_max=None
        )
        
        print(f"✓ Face results: {len(face_results)}")
        print(f"✓ Text results: {len(text_results)}\n")
        
        # Combine results
        print("Combining results with weighted scores...")
        combined_results = self.combine_results(
            face_results=face_results,
            text_results=text_results,
            w1=w1,
            w2=w2,
            top_n=top_n
        )
        
        print(f"✓ Top {len(combined_results)} results retrieved\n")
        
        return combined_results


# Example usage
if __name__ == "__main__":
    """
    Example usage of VectorRetrieval
    """
    
    print("\n" + "="*60)
    print("VECTOR RETRIEVAL SYSTEM - EXAMPLE")
    print("="*60)
    
    try:
        # Initialize retrieval system
        retrieval = VectorRetrieval(host="localhost", port=6333)
        
        # Example: Create dummy embeddings (replace with actual embeddings)
        face_emb = np.random.rand(512)  # Replace with actual face embedding
        text_emb = np.random.rand(1536)  # Replace with actual text embedding
        
        # Example 1: Search with metadata filters
        print("\n--- Example 1: Search with Metadata Filters ---")
        results = retrieval.search_and_combine(
            face_embedding=face_emb,
            text_embedding=text_emb,
            gender="Male",
            age_min=20,
            age_max=30,
            height_min=165,
            height_max=180,
            w1=0.6,  # 60% weight to face similarity
            w2=0.4,  # 40% weight to text similarity
            top_n=5
        )
        
        print("Top 5 Results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. PID: {result['pid']}")
            print(f"     Combined Score: {result['combined_score']:.4f}")
            print(f"     Face Score: {result['face_score']:.4f}")
            print(f"     Text Score: {result['text_score']:.4f}")
            print(f"     Age: {result['age']}, Gender: {result['gender']}, Height: {result['height_cm']} cm")
        
        # Example 2: Search with only face embedding
        print("\n--- Example 2: Face-Only Search ---")
        results = retrieval.search_and_combine(
            face_embedding=face_emb,
            gender="Female",
            age_min=25,
            age_max=35,
            w1=1.0,  # 100% face
            w2=0.0,  # 0% text
            top_n=3
        )
        
        # Example 3: Search with only text embedding
        print("\n--- Example 3: Text-Only Search ---")
        results = retrieval.search_and_combine(
            text_embedding=text_emb,
            gender="Male",
            height_min=170,
            w1=0.0,  # 0% face
            w2=1.0,  # 100% text
            top_n=3
        )
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        print("  2. Collections exist: python setup_vectordb.py")
        print("  3. Data is inserted in collections")
    
    print("\n" + "="*60)
