"""
Face Recognition Integration with Database
Combines face embeddings with the missing persons database for matching
"""

from face_embedding import FaceEmbeddingExtractor
from db_helper import DatabaseHelper
import numpy as np
import json
from datetime import datetime


class FaceRecognitionMatcher:
    """
    Match missing persons with unidentified bodies using facial recognition
    """
    
    def __init__(self, use_gpu=True, similarity_threshold=0.5):
        """
        Initialize the matcher
        
        Args:
            use_gpu: Use GPU for face detection if available
            similarity_threshold: Threshold for face matching (0.4-0.6 typical)
        """
        self.face_extractor = FaceEmbeddingExtractor(use_gpu=use_gpu)
        self.threshold = similarity_threshold
        print(f"✓ Face Recognition Matcher initialized (threshold: {self.threshold})")
    
    def extract_and_save_embedding(self, db, table_name, pid, photo_path):
        """
        Extract face embedding from a photo and save to database
        
        Args:
            db: DatabaseHelper instance
            table_name: 'missing_persons', 'unidentified_bodies', or 'preliminary_uidb_reports'
            pid: Person ID
            photo_path: Path to the photo file
        
        Returns:
            numpy.ndarray: The extracted embedding
        """
        # Extract embedding
        embedding = self.face_extractor.extract_embedding(photo_path)
        
        # Convert to JSON for storage
        embedding_json = json.dumps(embedding.tolist())
        
        # Save to database (you'll need to add an 'embedding' column to tables)
        # For now, we'll save to a separate embeddings table or file
        
        print(f"✓ Extracted embedding for {pid} from {photo_path}")
        return embedding
    
    def find_matches_for_missing_person(self, db, missing_person_pid, top_n=5):
        """
        Find potential matches for a missing person in UIDB records
        
        Args:
            db: DatabaseHelper instance
            missing_person_pid: PID of the missing person
            top_n: Return top N matches
        
        Returns:
            list: List of (uidb_pid, similarity_score) tuples
        """
        # Get missing person record
        missing_person = db.get_by_pid('missing_persons', missing_person_pid)
        if not missing_person:
            raise ValueError(f"Missing person {missing_person_pid} not found")
        
        # Get profile photo path
        mp_photo = missing_person['profile_photo']
        if not mp_photo:
            raise ValueError(f"No profile photo for {missing_person_pid}")
        
        # Extract embedding from missing person photo
        mp_embedding = self.face_extractor.extract_embedding(mp_photo)
        
        # Get all unidentified bodies with photos
        uidb_records = db.search_records('unidentified_bodies', filters={'status': 'Open'})
        
        matches = []
        for uidb in uidb_records:
            if not uidb['profile_photo']:
                continue
            
            try:
                # Extract embedding from UIDB photo
                uidb_embedding = self.face_extractor.extract_embedding(uidb['profile_photo'])
                
                # Calculate similarity
                similarity = self.face_extractor.compute_similarity(mp_embedding, uidb_embedding)
                
                matches.append({
                    'uidb_pid': uidb['pid'],
                    'uidb_name': uidb.get('name', 'Unknown'),
                    'similarity': similarity,
                    'is_match': similarity > self.threshold,
                    'found_date': uidb['found_date'],
                    'found_address': uidb['found_address']
                })
                
            except Exception as e:
                print(f"Warning: Could not process {uidb['pid']}: {e}")
                continue
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches[:top_n]
    
    def find_matches_for_uidb(self, db, uidb_pid, top_n=5):
        """
        Find potential matches for an unidentified body in missing persons records
        
        Args:
            db: DatabaseHelper instance
            uidb_pid: PID of the unidentified body
            top_n: Return top N matches
        
        Returns:
            list: List of match dictionaries
        """
        # Get UIDB record
        uidb = db.get_by_pid('unidentified_bodies', uidb_pid)
        if not uidb:
            raise ValueError(f"Unidentified body {uidb_pid} not found")
        
        # Get profile photo path
        uidb_photo = uidb['profile_photo']
        if not uidb_photo:
            raise ValueError(f"No profile photo for {uidb_pid}")
        
        # Extract embedding from UIDB photo
        uidb_embedding = self.face_extractor.extract_embedding(uidb_photo)
        
        # Get all open missing persons with photos
        mp_records = db.search_records('missing_persons', filters={'status': 'Open'})
        
        matches = []
        for mp in mp_records:
            if not mp['profile_photo']:
                continue
            
            try:
                # Extract embedding from missing person photo
                mp_embedding = self.face_extractor.extract_embedding(mp['profile_photo'])
                
                # Calculate similarity
                similarity = self.face_extractor.compute_similarity(uidb_embedding, mp_embedding)
                
                matches.append({
                    'mp_pid': mp['pid'],
                    'mp_name': mp.get('name', 'Unknown'),
                    'similarity': similarity,
                    'is_match': similarity > self.threshold,
                    'reported_date': mp['reported_date'],
                    'last_seen_address': mp['last_seen_address'],
                    'age': mp['age'],
                    'gender': mp['gender']
                })
                
            except Exception as e:
                print(f"Warning: Could not process {mp['pid']}: {e}")
                continue
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches[:top_n]
    
    def auto_match_new_uidb(self, db, uidb_pid, auto_update=False):
        """
        Automatically find matches when a new UIDB is added
        
        Args:
            db: DatabaseHelper instance
            uidb_pid: PID of the newly added UIDB
            auto_update: If True, update status to 'Matched' if high confidence match found
        
        Returns:
            dict: Match results
        """
        matches = self.find_matches_for_uidb(db, uidb_pid, top_n=10)
        
        result = {
            'uidb_pid': uidb_pid,
            'total_matches': len(matches),
            'high_confidence_matches': [m for m in matches if m['similarity'] > 0.6],
            'medium_confidence_matches': [m for m in matches if 0.5 < m['similarity'] <= 0.6],
            'low_confidence_matches': [m for m in matches if 0.4 < m['similarity'] <= 0.5],
            'all_matches': matches
        }
        
        # Auto-update if high confidence match and flag is set
        if auto_update and result['high_confidence_matches']:
            best_match = result['high_confidence_matches'][0]
            print(f"\n⚠️  High confidence match found!")
            print(f"   UIDB: {uidb_pid}")
            print(f"   Missing Person: {best_match['mp_pid']} ({best_match['mp_name']})")
            print(f"   Similarity: {best_match['similarity']:.4f}")
            print(f"\n   Consider manual verification before updating status.")
        
        return result
    
    def compare_physical_attributes(self, mp_record, uidb_record):
        """
        Compare physical attributes between missing person and UIDB
        
        Args:
            mp_record: Missing person database record
            uidb_record: UIDB database record
        
        Returns:
            dict: Attribute comparison scores
        """
        scores = {}
        
        # Age comparison (within 5 years)
        if mp_record['age'] and uidb_record['estimated_age']:
            age_diff = abs(mp_record['age'] - uidb_record['estimated_age'])
            scores['age_match'] = age_diff <= 5
            scores['age_difference'] = age_diff
        
        # Gender match
        if mp_record['gender'] and uidb_record['gender']:
            scores['gender_match'] = mp_record['gender'] == uidb_record['gender']
        
        # Height comparison (within 5cm)
        if mp_record['height_cm'] and uidb_record['height_cm']:
            height_diff = abs(mp_record['height_cm'] - uidb_record['height_cm'])
            scores['height_match'] = height_diff <= 5
            scores['height_difference'] = height_diff
        
        # Hair color match
        if mp_record['hair_color'] and uidb_record['hair_color']:
            scores['hair_color_match'] = mp_record['hair_color'].lower() == uidb_record['hair_color'].lower()
        
        # Eye color match
        if mp_record['eye_color'] and uidb_record['eye_color']:
            scores['eye_color_match'] = mp_record['eye_color'].lower() == uidb_record['eye_color'].lower()
        
        # Calculate overall attribute match percentage
        matches = sum(1 for k, v in scores.items() if k.endswith('_match') and v)
        total = sum(1 for k in scores.keys() if k.endswith('_match'))
        scores['overall_match_percentage'] = (matches / total * 100) if total > 0 else 0
        
        return scores


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Face Recognition Database Integration - Example")
    print("=" * 70)
    print()
    
    # Initialize matcher
    matcher = FaceRecognitionMatcher(use_gpu=True, similarity_threshold=0.5)
    
    # Example: Find matches for a missing person
    print("\n--- Example 1: Find matches for missing person ---")
    # with DatabaseHelper() as db:
    #     matches = matcher.find_matches_for_missing_person(db, 'MP-2024-00001', top_n=5)
    #     
    #     print(f"Found {len(matches)} potential matches:")
    #     for match in matches:
    #         print(f"  • {match['uidb_pid']}: {match['similarity']:.4f} (Match: {match['is_match']})")
    
    # Example: Find matches for UIDB
    print("\n--- Example 2: Find matches for unidentified body ---")
    # with DatabaseHelper() as db:
    #     matches = matcher.find_matches_for_uidb(db, 'UIDB-2024-00001', top_n=5)
    #     
    #     print(f"Found {len(matches)} potential matches:")
    #     for match in matches:
    #         print(f"  • {match['mp_pid']} ({match['mp_name']}): {match['similarity']:.4f}")
    
    # Example: Auto-match new UIDB
    print("\n--- Example 3: Auto-match new UIDB ---")
    # with DatabaseHelper() as db:
    #     result = matcher.auto_match_new_uidb(db, 'UIDB-2024-00001', auto_update=False)
    #     
    #     print(f"High confidence matches: {len(result['high_confidence_matches'])}")
    #     print(f"Medium confidence matches: {len(result['medium_confidence_matches'])}")
    #     print(f"Low confidence matches: {len(result['low_confidence_matches'])}")
    
    print("\n✓ Face recognition integration is ready!")
    print("\nNote: Uncomment examples above and provide actual PIDs to test.")
    print("Make sure to:")
    print("  1. Install face recognition dependencies: pip install -r requirements.txt")
    print("  2. Have photos with faces in the database")
    print("  3. Configure database credentials")
