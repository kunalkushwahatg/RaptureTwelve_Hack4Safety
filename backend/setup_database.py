"""
SQLite Database Setup Script for Missing Persons System
"""
import os
import sqlite3
from pathlib import Path

DB_FILE = 'missing_persons.db'
PHOTO_FOLDERS = ['photos/missing_persons', 'photos/unidentified_bodies', 'photos/preliminary_uidb']

def create_photo_folders():
    print("Creating photo storage folders...")
    for folder in PHOTO_FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f" Created: {folder}")
    print("Photo folders created!\n")

def execute_schema():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        schema_file = Path('database_schema_sqlite.sql')
        if not schema_file.exists():
            print("Error: database_schema_sqlite.sql not found!")
            return False
        print(f"Creating database: {DB_FILE}")
        with open(schema_file, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        conn.commit()
        print(" Database created successfully!\n")
        cursor.close()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False

def main():
    print("="*60)
    print("Missing Persons Database Setup (SQLite)")
    print("="*60 + "\n")
    create_photo_folders()
    if execute_schema():
        print("="*60)
        print("Setup completed!")
        print("="*60)
        print(f"\nDatabase: {DB_FILE}")
        print("No password needed - SQLite is file-based!")
    else:
        print("Setup failed!")

if __name__ == "__main__":
    main()
