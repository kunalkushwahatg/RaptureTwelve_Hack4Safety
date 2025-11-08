"""
Database Helper Module for Missing Persons System
Provides utility functions for database operations
"""

import sqlite3
from datetime import datetime
import json
from pathlib import Path
import shutil

# Database configuration
DB_FILE = 'missing_persons.db'  # SQLite database file


class DatabaseHelper:
    """Helper class for database operations"""
    
    def __init__(self, db_file=None):
        """Initialize database connection"""
        self.db_file = db_file or DB_FILE
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    # Missing Persons Operations
    
    def generate_pid(self, table_name):
        """Generate unique PID for a table"""
        prefix_map = {
            'missing_persons': 'MP',
            'unidentified_bodies': 'UIDB',
            'preliminary_uidb_reports': 'PUIDB'
        }
        
        prefix = prefix_map.get(table_name, 'UNK')
        year = datetime.now().year
        
        # Get the latest ID for this year - SQLite uses ? placeholders
        query = f"""
            SELECT pid FROM {table_name} 
            WHERE pid LIKE ? 
            ORDER BY pid DESC 
            LIMIT 1
        """
        self.cursor.execute(query, (f'{prefix}-{year}-%',))
        result = self.cursor.fetchone()
        
        if result:
            # Extract the number and increment
            last_num = int(result['pid'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}-{year}-{new_num:05d}"
    
    def create_person_folder(self, table_name, pid):
        """Create folder structure for a person's photos"""
        folder_map = {
            'missing_persons': 'photos/missing_persons',
            'unidentified_bodies': 'photos/unidentified_bodies',
            'preliminary_uidb_reports': 'photos/preliminary_uidb'
        }
        
        base_folder = folder_map.get(table_name)
        if base_folder:
            person_folder = Path(base_folder) / pid
            person_folder.mkdir(parents=True, exist_ok=True)
            return str(person_folder)
        return None
    
    def save_photo(self, source_path, table_name, pid, is_profile=True, photo_index=None):
        """
        Save a photo to the appropriate folder
        
        Args:
            source_path: Path to the source photo file
            table_name: Name of the table (missing_persons, etc.)
            pid: Person ID
            is_profile: True for profile photo, False for extra photos
            photo_index: Index for extra photos (e.g., 1, 2, 3)
        
        Returns:
            Relative path to the saved photo
        """
        person_folder = self.create_person_folder(table_name, pid)
        if not person_folder:
            return None
        
        source = Path(source_path)
        extension = source.suffix
        
        if is_profile:
            filename = f"profile{extension}"
        else:
            filename = f"photo_{photo_index:02d}{extension}"
        
        dest_path = Path(person_folder) / filename
        shutil.copy2(source, dest_path)
        
        # Return relative path for database storage
        return str(dest_path).replace('\\', '/')
    
    def add_missing_person(self, data, profile_photo_path=None, extra_photo_paths=None):
        """
        Add a new missing person record
        
        Args:
            data: Dictionary containing person data
            profile_photo_path: Path to profile photo file
            extra_photo_paths: List of paths to additional photos
        
        Returns:
            The generated PID if successful, None otherwise
        """
        try:
            # Generate PID
            pid = self.generate_pid('missing_persons')
            
            # Handle photos
            profile_photo = None
            if profile_photo_path:
                profile_photo = self.save_photo(profile_photo_path, 'missing_persons', pid, is_profile=True)
            
            extra_photos = []
            if extra_photo_paths:
                for idx, photo_path in enumerate(extra_photo_paths, 1):
                    saved_path = self.save_photo(photo_path, 'missing_persons', pid, is_profile=False, photo_index=idx)
                    if saved_path:
                        extra_photos.append(saved_path)
            
            # Prepare SQL - SQLite uses ? placeholders and doesn't support RETURNING
            query = """
                INSERT INTO missing_persons (
                    pid, fir_number, police_station, reported_date, name, age, gender,
                    height_cm, build, hair_color, eye_color, distinguishing_marks,
                    clothing_description, person_description, last_seen_date,
                    last_seen_latitude, last_seen_longitude, last_seen_address,
                    profile_photo, extra_photos, reporter_name, reporter_contact,
                    additional_notes, status
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """
            
            data['pid'] = pid
            data['profile_photo'] = profile_photo
            data['extra_photos'] = json.dumps(extra_photos) if extra_photos else None
            
            # Convert data dict to tuple in correct order
            values = (
                data['pid'], data['fir_number'], data['police_station'], data['reported_date'],
                data['name'], data['age'], data['gender'], data['height_cm'], data['build'],
                data['hair_color'], data['eye_color'], data['distinguishing_marks'],
                data['clothing_description'], data['person_description'], data['last_seen_date'],
                data['last_seen_latitude'], data['last_seen_longitude'], data['last_seen_address'],
                data['profile_photo'], data['extra_photos'], data['reporter_name'],
                data['reporter_contact'], data['additional_notes'], data['status']
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            print(f"✓ Missing person added with PID: {pid}")
            return pid
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding missing person: {e}")
            return None
    
    def add_preliminary_uidb(self, data, profile_photo_path=None, extra_photo_paths=None):
        """Add a new preliminary UIDB report"""
        try:
            pid = self.generate_pid('preliminary_uidb_reports')
            
            # Handle photos
            profile_photo = None
            if profile_photo_path:
                profile_photo = self.save_photo(profile_photo_path, 'preliminary_uidb_reports', pid, is_profile=True)
            
            extra_photos = []
            if extra_photo_paths:
                for idx, photo_path in enumerate(extra_photo_paths, 1):
                    saved_path = self.save_photo(photo_path, 'preliminary_uidb_reports', pid, is_profile=False, photo_index=idx)
                    if saved_path:
                        extra_photos.append(saved_path)
            
            query = """
                INSERT INTO preliminary_uidb_reports (
                    pid, report_number, police_station, reported_date, found_date,
                    estimated_age, gender, height_cm, build, hair_color, eye_color,
                    distinguishing_marks, clothing_description, person_description,
                    found_latitude, found_longitude, found_address,
                    profile_photo, extra_photos, initial_notes, status
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
            """
            
            data['pid'] = pid
            data['profile_photo'] = profile_photo
            data['extra_photos'] = json.dumps(extra_photos) if extra_photos else None
            
            values = (
                data['pid'], data['report_number'], data['police_station'], data['reported_date'],
                data['found_date'], data['estimated_age'], data['gender'], data['height_cm'],
                data['build'], data['hair_color'], data['eye_color'], data['distinguishing_marks'],
                data['clothing_description'], data['person_description'], data['found_latitude'],
                data['found_longitude'], data['found_address'], data['profile_photo'],
                data['extra_photos'], data['initial_notes'], data['status']
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            print(f"✓ Preliminary UIDB report added with PID: {pid}")
            return pid
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding preliminary UIDB: {e}")
            return None
    
    def add_unidentified_body(self, data, profile_photo_path=None, extra_photo_paths=None):
        """Add a new unidentified body record"""
        try:
            pid = self.generate_pid('unidentified_bodies')
            
            # Handle photos
            profile_photo = None
            if profile_photo_path:
                profile_photo = self.save_photo(profile_photo_path, 'unidentified_bodies', pid, is_profile=True)
            
            extra_photos = []
            if extra_photo_paths:
                for idx, photo_path in enumerate(extra_photo_paths, 1):
                    saved_path = self.save_photo(photo_path, 'unidentified_bodies', pid, is_profile=False, photo_index=idx)
                    if saved_path:
                        extra_photos.append(saved_path)
            
            query = """
                INSERT INTO unidentified_bodies (
                    pid, case_number, police_station, reported_date, found_date,
                    postmortem_date, estimated_age, gender, height_cm, build,
                    hair_color, eye_color, distinguishing_marks, clothing_description,
                    person_description, found_latitude, found_longitude, found_address,
                    profile_photo, extra_photos, cause_of_death, postmortem_report_url,
                    dna_sample_collected, dental_records_available, fingerprints_collected,
                    additional_notes, status
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """
            
            data['pid'] = pid
            data['profile_photo'] = profile_photo
            data['extra_photos'] = json.dumps(extra_photos) if extra_photos else None
            
            values = (
                data['pid'], data['case_number'], data['police_station'], data['reported_date'],
                data['found_date'], data['postmortem_date'], data['estimated_age'], data['gender'],
                data['height_cm'], data['build'], data['hair_color'], data['eye_color'],
                data['distinguishing_marks'], data['clothing_description'], data['person_description'],
                data['found_latitude'], data['found_longitude'], data['found_address'],
                data['profile_photo'], data['extra_photos'], data['cause_of_death'],
                data['postmortem_report_url'], data['dna_sample_collected'],
                data['dental_records_available'], data['fingerprints_collected'],
                data['additional_notes'], data['status']
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            print(f"✓ Unidentified body added with PID: {pid}")
            return pid
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding unidentified body: {e}")
            return None
    
    def get_by_pid(self, table_name, pid):
        """Get a record by PID"""
        try:
            query = f"SELECT * FROM {table_name} WHERE pid = ?"
            self.cursor.execute(query, (pid,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching record: {e}")
            return None
    
    def search_records(self, table_name, filters=None, limit=100):
        """
        Search records with filters
        
        Args:
            table_name: Name of the table to search
            filters: Dictionary of field:value pairs to filter by
            limit: Maximum number of results
        
        Returns:
            List of matching records
        """
        try:
            query = f"SELECT * FROM {table_name}"
            params = []
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    conditions.append(f"{field} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(conditions)
            
            query += f" ORDER BY created_at DESC LIMIT {limit}"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error searching records: {e}")
            return []
    
    def update_status(self, table_name, pid, new_status):
        """Update the status of a record"""
        try:
            query = f"UPDATE {table_name} SET status = ? WHERE pid = ?"
            self.cursor.execute(query, (new_status, pid))
            self.conn.commit()
            print(f"✓ Status updated for {pid}: {new_status}")
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating status: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Example: Add a missing person
    with DatabaseHelper() as db:
        missing_person_data = {
            'fir_number': 'FIR/2024/001',
            'police_station': 'Central Police Station',
            'reported_date': datetime.now(),
            'name': 'John Doe',
            'age': 25,
            'gender': 'Male',
            'height_cm': 175,
            'build': 'Athletic',
            'hair_color': 'Black',
            'eye_color': 'Brown',
            'distinguishing_marks': 'Scar on left arm',
            'clothing_description': 'Blue jeans, white t-shirt',
            'person_description': 'Athletic build, short black hair, clean shaven',
            'last_seen_date': datetime.now(),
            'last_seen_latitude': 28.6139,
            'last_seen_longitude': 77.2090,
            'last_seen_address': 'Connaught Place, New Delhi',
            'reporter_name': 'Jane Doe',
            'reporter_contact': '+91-9999999999',
            'additional_notes': 'Was wearing glasses',
            'status': 'Open'
        }
        
        # Uncomment to add (make sure to provide actual photo paths)
        # pid = db.add_missing_person(
        #     missing_person_data,
        #     profile_photo_path='path/to/profile.jpg',
        #     extra_photo_paths=['path/to/photo1.jpg', 'path/to/photo2.jpg']
        # )
        # print(f"Created missing person with PID: {pid}")
