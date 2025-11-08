"""
Populate Qdrant Vector Database with Unidentified Bodies Data
Converts database records to textual paragraphs and stores embeddings
"""

import sqlite3
import json
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from text_embedder import TextEmbedder
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_FILE = 'missing_persons.db'

# Qdrant configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
TEXT_COLLECTION = "text_embeddings"


class QdrantPopulator:
    """Populate Qdrant with unidentified bodies data"""
    
    def __init__(self):
        """Initialize database connections and embedder"""
        # SQLite connection
        self.db_conn = sqlite3.connect(DB_FILE)
        self.db_conn.row_factory = sqlite3.Row
        
        # Qdrant client
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Text embedder
        self.embedder = TextEmbedder()
        
        # OpenAI client for generating descriptions
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        print("✓ Initialized QdrantPopulator")
    
    def setup_collection(self, recreate: bool = False):
        """Setup Qdrant collection for text embeddings"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            exists = TEXT_COLLECTION in collection_names
            
            if recreate and exists:
                self.qdrant_client.delete_collection(TEXT_COLLECTION)
                print(f"✓ Deleted existing collection: {TEXT_COLLECTION}")
                exists = False
            
            if not exists:
                self.qdrant_client.create_collection(
                    collection_name=TEXT_COLLECTION,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-3-small
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Created collection: {TEXT_COLLECTION}")
            else:
                print(f"✓ Collection already exists: {TEXT_COLLECTION}")
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
    
    def generate_description(self, record: Dict) -> str:
        """
        Generate a 30-40 word paragraph description using LLM
        
        Args:
            record: Database record dict
            
        Returns:
            Textual description paragraph
        """
        # Create structured input for LLM
        prompt = f"""Convert this unidentified body record into a natural 30-40 word paragraph description for search purposes.

Record Data:
- PID: {record.get('pid', 'N/A')}
- Gender: {record.get('gender', 'Unknown')}
- Age: {record.get('estimated_age', 'Unknown')} years
- Height: {record.get('height_cm', 'Unknown')} cm
- Build: {record.get('build', 'Unknown')}
- Complexion: {record.get('complexion', 'Unknown')}
- Face Shape: {record.get('face_shape', 'Unknown')}
- Hair: {record.get('hair_color', 'Unknown')}
- Eyes: {record.get('eye_color', 'Unknown')}
- Distinguishing Marks: {record.get('distinguishing_marks', 'None')}
- Distinctive Features: {record.get('distinctive_features', 'None')}
- Clothing: {record.get('clothing_description', 'Not described')}
- Jewelry: {record.get('jewelry_description', 'None')}
- Location Found: {record.get('found_address', 'Unknown')}
- Police Station: {record.get('police_station', 'Unknown')}
- Found Date: {record.get('found_date', 'Unknown')}

Generate a concise, searchable paragraph (30-40 words) describing this person. Focus on physical characteristics and location."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, searchable descriptions of missing persons and unidentified bodies. Keep descriptions factual and objective, exactly 30-40 words."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            description = response.choices[0].message.content.strip()
            return description
        except Exception as e:
            print(f"  ✗ Error generating description for {record.get('pid')}: {e}")
            # Fallback to manual description
            return self.create_fallback_description(record)
    
    def create_fallback_description(self, record: Dict) -> str:
        """Create a simple fallback description if LLM fails"""
        parts = []
        
        if record.get('gender'):
            parts.append(record['gender'])
        if record.get('estimated_age'):
            parts.append(f"{record['estimated_age']} years old")
        if record.get('complexion'):
            parts.append(f"{record['complexion']} complexion")
        if record.get('build'):
            parts.append(f"{record['build']} build")
        if record.get('height_cm'):
            parts.append(f"{record['height_cm']}cm tall")
        if record.get('hair_color'):
            parts.append(f"{record['hair_color']} hair")
        if record.get('distinctive_features'):
            parts.append(f"{record['distinctive_features']}")
        if record.get('found_address'):
            parts.append(f"Found at {record['found_address']}")
        
        description = ". ".join(parts[:8]) + "."
        return description
    
    def create_metadata(self, record: Dict) -> Dict:
        """
        Create metadata payload for Qdrant point
        
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
            "fingerprints_collected": bool(record.get('fingerprints_collected', 0))
        }
        
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    
    def populate(self, batch_size: int = 10):
        """
        Main population function
        
        Args:
            batch_size: Number of records to process in each batch
        """
        print("\n" + "="*60)
        print("POPULATE QDRANT WITH UNIDENTIFIED BODIES")
        print("="*60 + "\n")
        
        # Fetch records
        records = self.fetch_unidentified_bodies()
        if not records:
            print("✗ No records to process")
            return
        
        total = len(records)
        processed = 0
        errors = 0
        
        print(f"\nProcessing {total} records in batches of {batch_size}...")
        print("-" * 60)
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            batch_points = []
            
            for record in batch:
                try:
                    pid = record.get('pid', 'UNKNOWN')
                    print(f"\n[{processed + 1}/{total}] Processing {pid}...")
                    
                    # Generate description
                    description = self.generate_description(record)
                    print(f"  Description: {description}")
                    
                    # Get embedding
                    embedding = self.embedder.get_embedding(description)
                    
                    # Create metadata
                    metadata = self.create_metadata(record)
                    metadata['description'] = description  # Store description in metadata
                    
                    # Create point
                    point = PointStruct(
                        id=record['id'],  # Use database ID as point ID
                        vector=embedding.tolist(),
                        payload=metadata
                    )
                    
                    batch_points.append(point)
                    print(f"  ✓ Created point with {len(embedding)} dimensions")
                    processed += 1
                    
                except Exception as e:
                    print(f"  ✗ Error processing {record.get('pid', 'unknown')}: {e}")
                    errors += 1
            
            # Upload batch to Qdrant
            if batch_points:
                try:
                    self.qdrant_client.upsert(
                        collection_name=TEXT_COLLECTION,
                        points=batch_points
                    )
                    print(f"\n  ✓ Uploaded batch of {len(batch_points)} points to Qdrant")
                except Exception as e:
                    print(f"\n  ✗ Error uploading batch: {e}")
                    errors += len(batch_points)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✓ Successfully processed: {processed}")
        print(f"✗ Errors: {errors}")
        print(f"Total: {total}")
        print("="*60 + "\n")
    
    def verify(self):
        """Verify the populated data in Qdrant"""
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60 + "\n")
        
        try:
            # Get collection info
            info = self.qdrant_client.get_collection(TEXT_COLLECTION)
            print(f"Collection: {TEXT_COLLECTION}")
            print(f"Points count: {info.points_count}")
            print(f"Vectors count: {info.vectors_count}")
            print(f"Status: {info.status}")
            
            # Sample a few points
            print("\n--- Sample Points ---")
            scroll_result = self.qdrant_client.scroll(
                collection_name=TEXT_COLLECTION,
                limit=3,
                with_payload=True,
                with_vectors=False
            )
            
            for idx, point in enumerate(scroll_result[0], 1):
                print(f"\n{idx}. PID: {point.payload.get('pid', 'N/A')}")
                print(f"   Description: {point.payload.get('description', 'N/A')}")
                print(f"   Gender: {point.payload.get('gender', 'N/A')}")
                print(f"   Age: {point.payload.get('estimated_age', 'N/A')}")
                print(f"   Location: {point.payload.get('found_address', 'N/A')[:50]}...")
            
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
    print("QDRANT POPULATION SCRIPT")
    print("="*60)
    
    try:
        # Initialize populator
        populator = QdrantPopulator()
        
        # Setup collection (recreate=True to start fresh)
        populator.setup_collection(recreate=True)
        
        # Populate Qdrant
        populator.populate(batch_size=10)
        
        # Verify
        populator.verify()
        
        # Close
        populator.close()
        
        print("\n✓ Qdrant population complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. Qdrant server is running (docker run -p 6333:6333 qdrant/qdrant)")
        print("  2. OpenAI API key is set in .env file")
        print("  3. Database file exists: missing_persons.db")


if __name__ == "__main__":
    main()
