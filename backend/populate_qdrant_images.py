"""
Populate Qdrant Vector Database with Face Embeddings
Extracts face embeddings from profile photos and stores them in Qdrant
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from face_embedding import FaceEmbeddingExtractor
from pathlib import Path

# Database configuration
DB_FILE = 'missing_persons.db'

# Qdrant configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
FACE_COLLECTION = "face_embeddings"

# Photo directories
PHOTO_BASE = "photos"
UIDB_PHOTO_DIR = os.path.join(PHOTO_BASE, "unidentified_bodies")


class FaceEmbeddingPopulator:
    """Populate Qdrant with face embeddings from unidentified bodies"""
    
    def __init__(self, use_gpu: bool = True):
        """Initialize database connections and face extractor"""
        # SQLite connection
        self.db_conn = sqlite3.connect(DB_FILE)
        self.db_conn.row_factory = sqlite3.Row
        
        # Qdrant client
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Face embedding extractor
        print("Initializing Face Embedding Extractor...")
        self.face_extractor = FaceEmbeddingExtractor(use_gpu=use_gpu)
        
        print("✓ Initialized FaceEmbeddingPopulator")
    
    def setup_collection(self, recreate: bool = False):
        """Setup Qdrant collection for face embeddings"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            exists = FACE_COLLECTION in collection_names
            
            if recreate and exists:
                self.qdrant_client.delete_collection(FACE_COLLECTION)
                print(f"✓ Deleted existing collection: {FACE_COLLECTION}")
                exists = False
            
            if not exists:
                self.qdrant_client.create_collection(
                    collection_name=FACE_COLLECTION,
                    vectors_config=VectorParams(
                        size=512,  # InsightFace embedding size
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Created collection: {FACE_COLLECTION}")
            else:
                print(f"✓ Collection already exists: {FACE_COLLECTION}")
        except Exception as e:
            print(f"✗ Error setting up collection: {e}")
            raise
    
    def fetch_unidentified_bodies(self) -> List[Dict]:
        """Fetch all unidentified bodies from database"""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM unidentified_bodies ORDER BY id")
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        records = []
        for row in rows:
            record = dict(row)
            # Parse extra_photos JSON if it exists
            if record.get('extra_photos'):
                try:
                    record['extra_photos'] = json.loads(record['extra_photos'])
                except:
                    pass
            records.append(record)
        
        print(f"✓ Fetched {len(records)} unidentified bodies from database")
        return records
    
    def find_profile_photo(self, record: Dict) -> Optional[str]:
        """
        Find the profile photo path for a record
        
        Args:
            record: Database record dict
            
        Returns:
            Full path to profile photo, or None if not found
        """
        pid = record.get('pid', '')
        profile_photo = record.get('profile_photo', '')
        
        if not profile_photo:
            return None
        
        # Try different possible paths
        possible_paths = [
            os.path.join(UIDB_PHOTO_DIR, profile_photo),  # photos/unidentified_bodies/1.jpg
            os.path.join(UIDB_PHOTO_DIR, pid, profile_photo),  # photos/unidentified_bodies/UIDB-2025-00101/1.jpg
            profile_photo if os.path.isabs(profile_photo) else None,  # Absolute path
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        
        return None
    
    def create_metadata(self, record: Dict) -> Dict:
        """
        Create metadata payload for Qdrant point (same as text embeddings)
        
        Args:
            record: Database record dict
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "pid": record.get('pid', ''),
            "record_type": "unidentified_body",
            "gender": record.get('gender', 'Unknown'),
            "estimated_age": record.get('estimated_age'),
            "height_cm": record.get('height_cm'),
            "build": record.get('build', ''),
            "complexion": record.get('complexion', ''),
            "face_shape": record.get('face_shape', ''),
            "hair_color": record.get('hair_color', ''),
            "eye_color": record.get('eye_color', ''),
            "distinguishing_marks": record.get('distinguishing_marks', ''),
            "distinctive_features": record.get('distinctive_features', ''),
            "clothing_description": record.get('clothing_description', ''),
            "jewelry_description": record.get('jewelry_description', ''),
            "found_address": record.get('found_address', ''),
            "found_latitude": record.get('found_latitude'),
            "found_longitude": record.get('found_longitude'),
            "police_station": record.get('police_station', ''),
            "found_date": record.get('found_date', ''),
            "postmortem_date": record.get('postmortem_date', ''),
            "cause_of_death": record.get('cause_of_death', ''),
            "status": record.get('status', 'Open'),
            "dna_sample_collected": bool(record.get('dna_sample_collected', 0)),
            "dental_records_available": bool(record.get('dental_records_available', 0)),
            "fingerprints_collected": bool(record.get('fingerprints_collected', 0)),
            "profile_photo": record.get('profile_photo', '')
        }
        
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    
    def populate(self):
        """
        Main population function - extract face embeddings and upload to Qdrant
        """
        print("\n" + "="*60)
        print("POPULATE QDRANT WITH FACE EMBEDDINGS")
        print("="*60 + "\n")
        
        # Fetch records
        records = self.fetch_unidentified_bodies()
        if not records:
            print("✗ No records to process")
            return
        
        total = len(records)
        processed = 0
        skipped = 0
        errors = 0
        
        print(f"\nProcessing {total} records...")
        print("-" * 60)
        
        points = []
        
        for record in records:
            try:
                pid = record.get('pid', 'UNKNOWN')
                print(f"\n[{processed + skipped + errors + 1}/{total}] Processing {pid}...")
                
                # Find profile photo
                photo_path = self.find_profile_photo(record)
                if not photo_path:
                    print(f"  ⊘ Skipped: No profile photo found")
                    skipped += 1
                    continue
                
                print(f"  Photo: {photo_path}")
                
                # Extract face embedding
                try:
                    embedding = self.face_extractor.extract_embedding(photo_path, return_normalized=True)
                    print(f"  ✓ Extracted face embedding: {embedding.shape}")
                except Exception as e:
                    print(f"  ✗ Failed to extract face embedding: {e}")
                    errors += 1
                    continue
                
                # Create metadata
                metadata = self.create_metadata(record)
                metadata['photo_path'] = photo_path  # Add photo path to metadata
                
                # Create point
                point = PointStruct(
                    id=record['id'],  # Use database ID as point ID
                    vector=embedding.tolist(),
                    payload=metadata
                )
                
                points.append(point)
                print(f"  ✓ Created point with {len(embedding)} dimensions")
                processed += 1
                
            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                errors += 1
        
        # Upload all points to Qdrant
        if points:
            try:
                print(f"\n\nUploading {len(points)} points to Qdrant...")
                self.qdrant_client.upsert(
                    collection_name=FACE_COLLECTION,
                    points=points
                )
                print(f"✓ Successfully uploaded {len(points)} face embeddings to Qdrant")
            except Exception as e:
                print(f"✗ Error uploading to Qdrant: {e}")
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✓ Successfully processed: {processed}")
        print(f"⊘ Skipped (no photo):    {skipped}")
        print(f"✗ Errors:                {errors}")
        print(f"Total:                   {total}")
        print("="*60 + "\n")
    
    def verify(self):
        """Verify the populated data in Qdrant"""
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60 + "\n")
        
        try:
            # Get collection info
            info = self.qdrant_client.get_collection(FACE_COLLECTION)
            print(f"Collection: {FACE_COLLECTION}")
            print(f"Points count: {info.points_count}")
            print(f"Vectors count: {info.vectors_count}")
            print(f"Status: {info.status}")
            print(f"Vector size: {info.config.params.vectors.size}")
            print(f"Distance metric: {info.config.params.vectors.distance}")
            
            # Sample a few points
            print("\n--- Sample Points ---")
            scroll_result = self.qdrant_client.scroll(
                collection_name=FACE_COLLECTION,
                limit=5,
                with_payload=True,
                with_vectors=False
            )
            
            for idx, point in enumerate(scroll_result[0], 1):
                print(f"\n{idx}. PID: {point.payload.get('pid', 'N/A')}")
                print(f"   Gender: {point.payload.get('gender', 'N/A')}")
                print(f"   Age: {point.payload.get('estimated_age', 'N/A')}")
                print(f"   Location: {point.payload.get('found_address', 'N/A')[:50]}...")
                print(f"   Photo: {point.payload.get('photo_path', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error verifying: {e}")
        
        print("\n" + "="*60)
    
    def close(self):
        """Close database connection"""
        self.db_conn.close()
        print("\n✓ Database connection closed")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("QDRANT FACE EMBEDDING POPULATION SCRIPT")
    print("="*60)
    
    try:
        # Initialize populator
        populator = FaceEmbeddingPopulator(use_gpu=False)  # Set to True if you have CUDA GPU
        
        # Setup collection (recreate=True to start fresh)
        populator.setup_collection(recreate=True)
        
        # Populate Qdrant
        populator.populate()
        
        # Verify
        populator.verify()
        
        # Close
        populator.close()
        
        print("\n✓ Face embedding population complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("  1. Qdrant server is running")
        print("  2. InsightFace is installed (pip install insightface onnxruntime)")
        print("  3. Database file exists: missing_persons.db")
        print("  4. Photos exist in photos/unidentified_bodies/")


if __name__ == "__main__":
    main()
