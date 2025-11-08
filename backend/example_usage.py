"""
Example Usage Script for Missing Persons Database
This demonstrates how to use the database helper functions
"""

from db_helper import DatabaseHelper
from datetime import datetime, timedelta
import random

def create_sample_missing_person(db):
    """Create a sample missing person record"""
    print("\n--- Adding Sample Missing Person ---")
    
    missing_person_data = {
        'fir_number': f'FIR/2024/{random.randint(1000, 9999)}',
        'police_station': 'Central Police Station',
        'reported_date': datetime.now(),
        'name': 'John Doe',
        'age': 25,
        'gender': 'Male',
        'height_cm': 175,
        'build': 'Athletic',
        'hair_color': 'Black',
        'eye_color': 'Brown',
        'distinguishing_marks': 'Scar on left arm (5cm long), small tattoo on right shoulder (star shape), birthmark on left cheek',
        'clothing_description': 'Blue denim jeans, white cotton t-shirt, black sneakers, brown leather jacket',
        'person_description': '''Athletic build with well-defined muscles. Short black hair, neatly combed to the side. 
        Clean shaven face with sharp jawline. Fair complexion. Wears prescription glasses with thin black frames. 
        Approximately 175cm tall and weighs around 70kg. Has a confident walking style.''',
        'last_seen_date': datetime.now() - timedelta(days=2),
        'last_seen_latitude': 28.6139,
        'last_seen_longitude': 77.2090,
        'last_seen_address': 'Connaught Place, New Delhi, Near Central Park',
        'reporter_name': 'Jane Doe',
        'reporter_contact': '+91-9999999999',
        'additional_notes': 'Was wearing prescription glasses. Has a medical condition (diabetes). Carries a brown leather wallet with photo ID. May be confused or disoriented.',
        'status': 'Open'
    }
    
    # Note: In real usage, provide actual photo paths
    # pid = db.add_missing_person(
    #     missing_person_data,
    #     profile_photo_path='path/to/profile.jpg',
    #     extra_photo_paths=['path/to/photo1.jpg', 'path/to/photo2.jpg']
    # )
    
    # For demo without photos:
    pid = db.add_missing_person(missing_person_data)
    
    if pid:
        print(f"✓ Successfully created missing person: {pid}")
        return pid
    else:
        print("✗ Failed to create missing person")
        return None


def create_sample_preliminary_uidb(db):
    """Create a sample preliminary UIDB report"""
    print("\n--- Adding Sample Preliminary UIDB Report ---")
    
    preliminary_data = {
        'report_number': f'TEMP/2024/{random.randint(1000, 9999)}',
        'police_station': 'West District Police Station',
        'reported_date': datetime.now(),
        'found_date': datetime.now() - timedelta(hours=6),
        'estimated_age': 30,
        'gender': 'Male',
        'height_cm': 170,
        'build': 'Medium',
        'hair_color': 'Brown',
        'eye_color': 'Unknown',
        'distinguishing_marks': 'Large scar on forehead, tattoo on left arm (appears to be a name)',
        'clothing_description': 'Grey suit, white shirt, black tie, formal shoes',
        'person_description': '''Medium build male, approximately 30 years old. Brown hair, slightly disheveled. 
        Wearing formal business attire. Face shows signs of stress or exhaustion.''',
        'found_latitude': 28.5355,
        'found_longitude': 77.3910,
        'found_address': 'Noida Sector 62, Near Metro Station',
        'initial_notes': 'Body found near metro station. No visible injuries. Appears to be recent. Awaiting postmortem examination.',
        'status': 'Pending'
    }
    
    pid = db.add_preliminary_uidb(preliminary_data)
    
    if pid:
        print(f"✓ Successfully created preliminary UIDB report: {pid}")
        return pid
    else:
        print("✗ Failed to create preliminary UIDB report")
        return None


def demonstrate_search(db):
    """Demonstrate search functionality"""
    print("\n--- Searching Records ---")
    
    # Search all open missing persons cases
    print("\nOpen Missing Persons Cases:")
    results = db.search_records('missing_persons', filters={'status': 'Open'}, limit=10)
    for person in results:
        print(f"  - {person['pid']}: {person['name']} (Age: {person['age']}, Last seen: {person['last_seen_address']})")
    
    # Search pending preliminary reports
    print("\nPending Preliminary UIDB Reports:")
    results = db.search_records('preliminary_uidb_reports', filters={'status': 'Pending'}, limit=10)
    for report in results:
        print(f"  - {report['pid']}: Found at {report['found_address']} on {report['found_date']}")


def demonstrate_get_by_pid(db, pid):
    """Demonstrate getting a record by PID"""
    print(f"\n--- Getting Record by PID: {pid} ---")
    
    record = db.get_by_pid('missing_persons', pid)
    if record:
        print(f"Found record:")
        print(f"  PID: {record['pid']}")
        print(f"  Name: {record['name']}")
        print(f"  Age: {record['age']}")
        print(f"  Gender: {record['gender']}")
        print(f"  Status: {record['status']}")
        print(f"  Description: {record['person_description'][:100]}...")
    else:
        print(f"No record found with PID: {pid}")


def demonstrate_update_status(db, pid):
    """Demonstrate updating a record's status"""
    print(f"\n--- Updating Status for {pid} ---")
    
    success = db.update_status('missing_persons', pid, 'Matched')
    if success:
        print(f"✓ Status updated successfully")
        
        # Verify the update
        record = db.get_by_pid('missing_persons', pid)
        if record:
            print(f"  New status: {record['status']}")


def main():
    """Main demonstration function"""
    print("=" * 70)
    print("Missing Persons Database - Example Usage")
    print("=" * 70)
    
    try:
        with DatabaseHelper() as db:
            # Create sample records
            mp_pid = create_sample_missing_person(db)
            pu_pid = create_sample_preliminary_uidb(db)
            
            # Demonstrate search
            demonstrate_search(db)
            
            # Demonstrate get by PID
            if mp_pid:
                demonstrate_get_by_pid(db, mp_pid)
            
            # Demonstrate status update
            if mp_pid:
                demonstrate_update_status(db, mp_pid)
            
            print("\n" + "=" * 70)
            print("✓ All operations completed successfully!")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to:")
        print("1. Update DB_CONFIG in db_helper.py with your PostgreSQL credentials")
        print("2. Run setup_database.py first to create the database")


if __name__ == "__main__":
    main()
