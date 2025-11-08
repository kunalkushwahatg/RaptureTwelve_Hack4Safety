"""
PostgreSQL Database Setup Script for Missing Persons System
This script creates the database, tables, and photo storage folders
"""

import os
import psycopg2
from psycopg2 import sql
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'postgres',  # Change to your PostgreSQL username
    'password': 'your_password',  # Change to your PostgreSQL password
    'host': 'localhost',
    'port': '5432'
}

# Photo storage folders
PHOTO_FOLDERS = [
    'photos/missing_persons',
    'photos/unidentified_bodies',
    'photos/preliminary_uidb'
]


def create_photo_folders():
    """Create folder structure for storing photos"""
    print("Creating photo storage folders...")
    for folder in PHOTO_FOLDERS:
        folder_path = Path(folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {folder}")
    print("Photo folders created successfully!\n")


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['dbname'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_CONFIG['dbname']}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['dbname'])
                )
            )
            print(f"✓ Database '{DB_CONFIG['dbname']}' created successfully!\n")
        else:
            print(f"Database '{DB_CONFIG['dbname']}' already exists.\n")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        return False


def execute_schema():
    """Execute the SQL schema file to create tables"""
    try:
        # Connect to the newly created database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read and execute the schema file
        schema_file = Path('database_schema.sql')
        if not schema_file.exists():
            print("Error: database_schema.sql not found!")
            return False
        
        print("Executing database schema...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        print("✓ Database schema executed successfully!")
        print("✓ Tables created: missing_persons, unidentified_bodies, preliminary_uidb_reports\n")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error executing schema: {e}")
        return False


def verify_setup():
    """Verify that tables were created successfully"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("Verification - Tables in database:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Error verifying setup: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("Missing Persons Database Setup")
    print("=" * 60)
    print()
    
    # Step 1: Create photo folders
    create_photo_folders()
    
    # Step 2: Create database
    if not create_database():
        print("Failed to create database. Exiting...")
        return
    
    # Step 3: Execute schema
    if not execute_schema():
        print("Failed to execute schema. Exiting...")
        return
    
    # Step 4: Verify setup
    verify_setup()
    
    print()
    print("=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update DB_CONFIG in this file with your PostgreSQL credentials")
    print("2. Use db_helper.py for database operations")
    print("3. Store photos in the 'photos/' folder structure")


if __name__ == "__main__":
    main()
