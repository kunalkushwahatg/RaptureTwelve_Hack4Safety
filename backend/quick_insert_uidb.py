"""
Quick Insert Script - Insert Unidentified Bodies One by One
Useful for debugging and seeing individual record insertion
"""

import json
import psycopg2
from datetime import datetime
import os

# Database configuration
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'postgres',
    'password': 'your_password_here',  # UPDATE THIS
    'host': 'localhost',
    'port': 5432
}

def insert_single_record(conn, record):
    """Insert a single record and return success status"""
    insert_query = """
        INSERT INTO unidentified_bodies (
            pid, police_station, found_date, postmortem_date, 
            estimated_age, gender, height_cm, build, complexion, face_shape,
            hair_color, eye_color, distinguishing_marks, distinctive_features,
            clothing_description, jewelry_description, person_description,
            found_latitude, found_longitude, found_address,
            profile_photo, extra_photos, cause_of_death, estimated_death_time,
            dna_sample_collected, dental_records_available, fingerprints_collected, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s::jsonb, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (pid) DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
        RETURNING pid;
    """
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(insert_query, (
            record['pid'],
            record['police_station'],
            record['found_date'],
            record['postmortem_date'],
            record['estimated_age'],
            record['gender'],
            record['height_cm'],
            record['build'],
            record['complexion'],
            record['face_shape'],
            record['hair_color'],
            record['eye_color'],
            record['distinguishing_marks'],
            record['distinctive_features'],
            record['clothing_description'],
            record['jewelry_description'],
            record['person_description'],
            record['found_latitude'],
            record['found_longitude'],
            record['found_address'],
            record['profile_photo'],
            json.dumps(record['extra_photos']),
            record['cause_of_death'],
            record['estimated_death_time'],
            record['dna_sample_collected'],
            record['dental_records_available'],
            record['fingerprints_collected'],
            record['status']
        ))
        
        pid = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        return True, pid
        
    except Exception as e:
        conn.rollback()
        return False, str(e)

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("QUICK INSERT - Unidentified Bodies (One by One)")
    print("="*60 + "\n")
    
    # Load JSON
    json_file = os.path.join(os.path.dirname(__file__), 'sample_dead.json')
    
    if not os.path.exists(json_file):
        print(f"✗ File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"Loaded {len(records)} records\n")
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to database\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Insert records one by one
    success_count = 0
    fail_count = 0
    
    print("Inserting records:")
    print("-" * 60)
    
    for i, record in enumerate(records, 1):
        success, result = insert_single_record(conn, record)
        
        if success:
            print(f"  {i:2}. ✓ {result} - {record['gender']:6} Age:{record['estimated_age']:2}")
            success_count += 1
        else:
            print(f"  {i:2}. ✗ {record['pid']} - ERROR: {result}")
            fail_count += 1
    
    print("-" * 60)
    print(f"\nResults:")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Total:   {len(records)}")
    
    conn.close()
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
