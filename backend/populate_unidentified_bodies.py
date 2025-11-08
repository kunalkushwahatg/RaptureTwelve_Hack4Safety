"""
Populate unidentified_bodies table from JSON file
Reads sample_dead.json and inserts records into SQLite database
"""

import json
import sqlite3
from datetime import datetime
import os

# Database configuration
DB_FILE = 'missing_persons.db'

def connect_db():
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        print("✓ Connected to database successfully")
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return None

def load_json_data(json_file):
    """Load data from JSON file"""
    try:
        # Try both locations - root and fixed filename
        if os.path.exists(json_file):
            file_path = json_file
        elif os.path.exists(f"../{json_file}"):
            file_path = f"../{json_file}"
        elif os.path.exists("../sample_dead_fixed.json"):
            file_path = "../sample_dead_fixed.json"
        else:
            print(f"✗ JSON file not found: {json_file}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} records from {file_path}")
        return data
    except Exception as e:
        print(f"✗ Error loading JSON: {e}")
        return None

def insert_unidentified_body(conn, record):
    """Insert a single unidentified body record"""
    cursor = conn.cursor()
    
    insert_query = """
    INSERT OR IGNORE INTO unidentified_bodies (
        pid, case_number, police_station, reported_date, found_date, postmortem_date,
        estimated_age, gender, height_cm, build, complexion, face_shape,
        hair_color, eye_color, distinguishing_marks, distinctive_features,
        clothing_description, jewelry_description, person_description,
        found_latitude, found_longitude, found_address,
        profile_photo, extra_photos, cause_of_death, estimated_death_time,
        dna_sample_collected, dental_records_available, fingerprints_collected, status
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?
    )
    """
    
    try:
        # Convert extra_photos list to JSON string if it's a list
        if isinstance(record.get('extra_photos'), list):
            record['extra_photos'] = json.dumps(record['extra_photos'])
        
        # Generate case_number from PID if not present
        case_number = record.get('case_number', f"CASE-{record.get('pid', 'UNKNOWN')}")
        
        # Use found_date as reported_date if reported_date not present
        reported_date = record.get('reported_date', record.get('found_date'))
        
        # Create tuple of values in the correct order
        values = (
            record.get('pid'),
            case_number,
            record.get('police_station'),
            reported_date,
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
            record.get('extra_photos'),
            record.get('cause_of_death'),
            record.get('estimated_death_time'),
            record.get('dna_sample_collected', False),
            record.get('dental_records_available', False),
            record.get('fingerprints_collected', False),
            record.get('status', 'Open')
        )
        
        cursor.execute(insert_query, values)
        
        # Check if row was inserted (rowcount > 0 means insert happened)
        if cursor.rowcount > 0:
            print(f"  ✓ Inserted: {record['pid']}")
            return True
        else:
            print(f"  ⊘ Skipped (already exists): {record['pid']}")
            return False
    except Exception as e:
        print(f"  ✗ Error inserting {record.get('pid', 'unknown')}: {e}")
        return False

def populate_database(json_file='sample_dead.json'):
    """Main function to populate the database"""
    print("\n" + "="*60)
    print("POPULATE UNIDENTIFIED BODIES TABLE")
    print("="*60 + "\n")
    
    # Connect to database
    conn = connect_db()
    if not conn:
        return
    
    # Load JSON data
    data = load_json_data(json_file)
    if not data:
        conn.close()
        return
    
    # Insert records
    print(f"\nInserting {len(data)} records...")
    print("-"*60)
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        for i, record in enumerate(data, 1):
            print(f"\n[{i}/{len(data)}] Processing {record.get('pid', 'unknown')}...")
            
            result = insert_unidentified_body(conn, record)
            if result:
                inserted_count += 1
            else:
                skipped_count += 1
        
        # Commit all changes
        conn.commit()
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✓ Successfully inserted: {inserted_count}")
        print(f"⊘ Skipped (duplicates):  {skipped_count}")
        print(f"✗ Errors:                {error_count}")
        print(f"Total processed:         {len(data)}")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Transaction failed: {e}")
    finally:
        conn.close()
        print("✓ Database connection closed\n")

def verify_insertion():
    """Verify the inserted records"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60 + "\n")
    
    # Count total records
    cursor.execute("SELECT COUNT(*) FROM unidentified_bodies;")
    total = cursor.fetchone()[0]
    print(f"Total records in unidentified_bodies: {total}")
    
    # Show latest 5 records
    cursor.execute("""
        SELECT pid, gender, estimated_age, police_station, found_date
        FROM unidentified_bodies
        ORDER BY created_at DESC
        LIMIT 5;
    """)
    
    print("\nLatest 5 records:")
    print("-"*60)
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | Age: {row[2]} | {row[3][:30]}...")
    
    conn.close()
    print("\n")

if __name__ == "__main__":
    """
    Run the population script
    """
    
    # Check if using sample_dead.json or sample_dead_fixed.json
    # Check in current directory (backend folder)
    if os.path.exists("sample_dead_fixed.json"):
        json_file = "sample_dead_fixed.json"
        print("\n✓ Using sample_dead_fixed.json (corrected format)")
    elif os.path.exists("sample_dead.json"):
        json_file = "sample_dead.json"
        print("\n⚠ WARNING: Using sample_dead.json (original format)")
        print("  Note: This file may need corrections. Use sample_dead_fixed.json if available.\n")
    # Check in parent directory
    elif os.path.exists("../sample_dead_fixed.json"):
        json_file = "../sample_dead_fixed.json"
        print("\n✓ Using ../sample_dead_fixed.json (corrected format)")
    elif os.path.exists("../sample_dead.json"):
        json_file = "../sample_dead.json"
        print("\n⚠ WARNING: Using ../sample_dead.json (original format)\n")
    else:
        print("\n✗ No JSON file found!")
        print("  Searched for:")
        print("    - sample_dead_fixed.json (in backend/)")
        print("    - sample_dead.json (in backend/)")
        print("    - ../sample_dead_fixed.json (in project root)")
        print("    - ../sample_dead.json (in project root)")
        exit(1)
    
    # Populate database
    populate_database(json_file)
    
    # Verify insertion
    verify_insertion()
    
    print("="*60)
    print("Done! Check the output above for any errors.")
    print("="*60 + "\n")
