"""
Quick Insert with Password Input
Prompts for PostgreSQL password instead of hardcoding it
"""

import json
import psycopg2
from psycopg2.extras import execute_values
import os
import getpass

def main():
    print("\n" + "="*60)
    print("UNIDENTIFIED BODIES - BULK INSERT")
    print("="*60 + "\n")
    
    # Get password from user
    print("Database: missing_persons_db")
    print("User: postgres")
    password = getpass.getpass("Enter PostgreSQL password: ")
    
    # Database configuration
    DB_CONFIG = {
        'dbname': 'missing_persons_db',
        'user': 'postgres',
        'password': password,
        'host': 'localhost',
        'port': 5432
    }
    
    # JSON file path
    json_file = os.path.join(os.path.dirname(__file__), 'sample_dead.json')
    
    if not os.path.exists(json_file):
        print(f"✗ JSON file not found: {json_file}")
        return
    
    # Load JSON data
    print("\nStep 1: Loading JSON data...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        print(f"✓ Loaded {len(records)} records")
    except Exception as e:
        print(f"✗ Error loading JSON: {e}")
        return
    
    # Connect to database
    print("\nStep 2: Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\n⚠ Please check your password and try again")
        return
    
    # Prepare insert query
    insert_query = """
        INSERT INTO unidentified_bodies (
            pid, police_station, found_date, postmortem_date, 
            estimated_age, gender, height_cm, build, complexion, face_shape,
            hair_color, eye_color, distinguishing_marks, distinctive_features,
            clothing_description, jewelry_description, person_description,
            found_latitude, found_longitude, found_address,
            profile_photo, extra_photos, cause_of_death, estimated_death_time,
            dna_sample_collected, dental_records_available, fingerprints_collected, status
        ) VALUES %s
        ON CONFLICT (pid) DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
        RETURNING pid;
    """
    
    # Prepare records
    print("\nStep 3: Inserting records...")
    prepared_records = []
    for record in records:
        prepared_records.append((
            record.get('pid'),
            record.get('police_station'),
            record.get('found_date'),
            record.get('postmortem_date'),
            record.get('estimated_age'),
            record.get('gender'),
            record.get('height_cm'),
            record.get('build'),
            record.get('complexion'),
            record.get('face_shape'),
            record.get('hair_color'),
            record.get('eye_color'),
            record.get('distinguishing_marks'),
            record.get('distinctive_features'),
            record.get('clothing_description'),
            record.get('jewelry_description'),
            record.get('person_description'),
            record.get('found_latitude'),
            record.get('found_longitude'),
            record.get('found_address'),
            record.get('profile_photo'),
            json.dumps(record.get('extra_photos', [])),
            record.get('cause_of_death'),
            record.get('estimated_death_time'),
            record.get('dna_sample_collected'),
            record.get('dental_records_available'),
            record.get('fingerprints_collected'),
            record.get('status', 'Open')
        ))
    
    try:
        cursor = conn.cursor()
        execute_values(cursor, insert_query, prepared_records)
        inserted_pids = cursor.fetchall()
        conn.commit()
        print(f"✓ Successfully inserted/updated {len(inserted_pids)} records")
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"✗ Error inserting records: {e}")
        conn.close()
        return
    
    # Verify insertion
    print("\nStep 4: Verifying insertion...")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM unidentified_bodies;")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT pid, gender, estimated_age, police_station 
            FROM unidentified_bodies 
            ORDER BY created_at DESC 
            LIMIT 5;
        """)
        sample_records = cursor.fetchall()
        cursor.close()
        
        print(f"\n{'='*60}")
        print("Database Verification")
        print(f"{'='*60}")
        print(f"Total records in database: {total_count}")
        print(f"\nSample records (latest 5):")
        print(f"{'-'*60}")
        for record in sample_records:
            pid, gender, age, station = record
            print(f"  {pid} | {gender:6} | Age: {age:2} | {station[:30]}")
        print(f"{'-'*60}")
        
    except Exception as e:
        print(f"✗ Error verifying: {e}")
    
    conn.close()
    print("\n" + "="*60)
    print("Process completed successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
