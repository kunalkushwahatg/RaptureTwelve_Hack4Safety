"""
Qdrant Vector Database Setup
Creates collections for face embeddings and text embeddings
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VectorDB:
    """
    Qdrant Vector Database manager for face and text embeddings
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host (default: localhost)
            port: Qdrant server port (default: 6333)
        """
        self.client = QdrantClient(host=host, port=port)
        self.face_collection = "face_embeddings"
        self.text_collection = "text_embeddings"
        
        print(f"✓ Connected to Qdrant at {host}:{port}")
    
    def setup_face_collection(self, vector_size: int = 512, recreate: bool = False):
        """
        Create collection for face embeddings.
        
        Args:
            vector_size: Dimension of face embeddings (default: 512 for InsightFace)
            recreate: If True, delete existing collection and recreate
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            exists = self.face_collection in collection_names
            
            if recreate and exists:
                self.client.delete_collection(self.face_collection)
                print(f"✓ Deleted existing collection: {self.face_collection}")
                exists = False
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.face_collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Created collection: {self.face_collection} (size: {vector_size}, distance: COSINE)")
            else:
                print(f"✓ Collection already exists: {self.face_collection}")
        except Exception as e:
            print(f"✗ Error setting up face collection: {e}")
    
    def setup_text_collection(self, vector_size: int = 1536, recreate: bool = False):
        """
        Create collection for text embeddings.
        
        Args:
            vector_size: Dimension of text embeddings (default: 1536 for OpenAI text-embedding-3-small)
            recreate: If True, delete existing collection and recreate
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            exists = self.text_collection in collection_names
            
            if recreate and exists:
                self.client.delete_collection(self.text_collection)
                print(f"✓ Deleted existing collection: {self.text_collection}")
                exists = False
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.text_collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Created collection: {self.text_collection} (size: {vector_size}, distance: COSINE)")
            else:
                print(f"✓ Collection already exists: {self.text_collection}")
        except Exception as e:
            print(f"✗ Error setting up text collection: {e}")
    
    def setup_all_collections(self, recreate: bool = False):
        """
        Setup both face and text embedding collections.
        
        Args:
            recreate: If True, delete existing collections and recreate
        """
        print("\n" + "="*60)
        print("Setting up Qdrant Vector Database Collections")
        print("="*60 + "\n")
        
        # Face embeddings: 512 dimensions (InsightFace)
        self.setup_face_collection(vector_size=512, recreate=recreate)
        
        # Text embeddings: 1536 dimensions (OpenAI text-embedding-3-small)
        self.setup_text_collection(vector_size=1536, recreate=recreate)
        
        print("\n" + "="*60)
        print("✓ Vector database setup complete!")
        print("="*60)
    
    def get_collection_info(self, collection_name: str) -> dict:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information dictionary
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name not in collection_names:
                return {"error": f"Collection '{collection_name}' does not exist"}
            
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names
        """
        collections = self.client.get_collections()
        return [col.name for col in collections.collections]
    
    def delete_collection(self, collection_name: str):
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name in collection_names:
                self.client.delete_collection(collection_name)
                print(f"✓ Deleted collection: {collection_name}")
            else:
                print(f"✗ Collection does not exist: {collection_name}")
        except Exception as e:
            print(f"✗ Error deleting collection: {e}")
    
    def verify_setup(self):
        """
        Verify that all collections are properly set up.
        """
        print("\n" + "="*60)
        print("Verifying Vector Database Setup")
        print("="*60 + "\n")
        
        # List all collections
        collections = self.list_collections()
        print(f"Total collections: {len(collections)}")
        print(f"Collections: {collections}\n")
        
        # Check face collection
        if self.face_collection in collections:
            info = self.get_collection_info(self.face_collection)
            if 'error' not in info:
                print(f"✓ {self.face_collection}:")
                print(f"    Vector size: {info['config']['vector_size']}")
                print(f"    Distance: {info['config']['distance']}")
                print(f"    Points count: {info['points_count']}")
                print(f"    Status: {info['status']}")
            else:
                print(f"✗ {self.face_collection}: {info['error']}")
        else:
            print(f"✗ {self.face_collection}: NOT FOUND")
        
        print()
        
        # Check text collection
        if self.text_collection in collections:
            info = self.get_collection_info(self.text_collection)
            if 'error' not in info:
                print(f"✓ {self.text_collection}:")
                print(f"    Vector size: {info['config']['vector_size']}")
                print(f"    Distance: {info['config']['distance']}")
                print(f"    Points count: {info['points_count']}")
                print(f"    Status: {info['status']}")
            else:
                print(f"✗ {self.text_collection}: {info['error']}")
        else:
            print(f"✗ {self.text_collection}: NOT FOUND")
        
        print("\n" + "="*60)


# Main setup script
if __name__ == "__main__":
    """
    Run this script to set up Qdrant vector database collections.
    
    Prerequisites:
    1. Qdrant server must be running on localhost:6333
       - Docker: docker run -p 6333:6333 qdrant/qdrant
       - Or install locally: https://qdrant.tech/documentation/quick-start/
    """
    
    print("\n" + "="*60)
    print("QDRANT VECTOR DATABASE SETUP")
    print("="*60)
    
    try:
        # Initialize vector database
        vector_db = VectorDB(host="localhost", port=6333)
        
        # Setup collections
        # Set recreate=True to delete and recreate existing collections
        vector_db.setup_all_collections(recreate=False)
        
        # Verify setup
        vector_db.verify_setup()
        
        print("\n✓ Setup completed successfully!")
        print("\nCollections created:")
        print("  - face_embeddings: 512 dimensions (for InsightFace)")
        print("  - text_embeddings: 1536 dimensions (for OpenAI)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Qdrant server is running:")
        print("  Docker: docker run -p 6333:6333 qdrant/qdrant")
        print("  Or visit: https://qdrant.tech/documentation/quick-start/")
