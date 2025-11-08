"""
Quick Database Connection Test
Tests MySQL connection with common passwords
"""

import mysql.connector
import sys

# Common default passwords to try
COMMON_PASSWORDS = [
    '',  # Empty password
    'root',
    'admin',
    'password',
    '123456',
]

DB_CONFIG = {
    'database': 'missing_persons_db',
    'user': 'root',
    'host': 'localhost',
    'port': 3306
}

def test_connection(password):
    """Test connection with a specific password"""
    try:
        config = DB_CONFIG.copy()
        config['password'] = password
        conn = mysql.connector.connect(**config)
        return conn
    except:
        return None

def main():
    print("\n" + "="*60)
    print("DATABASE CONNECTION TEST")
    print("="*60 + "\n")
    
    print("Testing common passwords...")
    print("-"*60)
    
    successful_conn = None
    successful_password = None
    
    for password in COMMON_PASSWORDS:
        password_display = '(empty)' if password == '' else password
        print(f"Trying password: {password_display}...", end=" ")
        
        conn = test_connection(password)
        if conn:
            print("✓ SUCCESS!")
            successful_conn = conn
            successful_password = password
            break
        else:
            print("✗ Failed")
    
    if successful_conn:
        print("\n" + "="*60)
        print("CONNECTION SUCCESSFUL!")
        print("="*60)
        print(f"\nWorking password: {successful_password if successful_password else '(empty)'}")
        
        # Test database
        try:
            cursor = successful_conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name = 'unidentified_bodies'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                print("✓ Table 'unidentified_bodies' exists")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM unidentified_bodies;")
                count = cursor.fetchone()[0]
                print(f"✓ Total records: {count}")
                
                if count > 0:
                    # Show sample record
                    cursor.execute("""
                        SELECT pid, gender, estimated_age, police_station, found_date
                        FROM unidentified_bodies
                        LIMIT 1;
                    """)
                    sample = cursor.fetchone()
                    print(f"\nSample record:")
                    print(f"  PID: {sample[0]}")
                    print(f"  Gender: {sample[1]}")
                    print(f"  Age: {sample[2]}")
                    print(f"  Police Station: {sample[3]}")
                    print(f"  Found Date: {sample[4]}")
                else:
                    print("\n⚠ Table is empty - no records found")
            else:
                print("✗ Table 'unidentified_bodies' does not exist")
                print("\n→ Run: python setup_database.py to create tables")
            
            cursor.close()
            successful_conn.close()
            
            # Update the populate script with working password
            print("\n" + "="*60)
            print("NEXT STEP")
            print("="*60)
            print(f"\nUpdate populate_unidentified_bodies.py line 17:")
            print(f"'password': '{successful_password if successful_password else ''}',")
            
        except Exception as e:
            print(f"\n✗ Database test error: {e}")
            successful_conn.close()
    else:
        print("\n" + "="*60)
        print("ALL PASSWORDS FAILED")
        print("="*60)
        print("\nOptions to recover:")
        print("\n1. Use MySQL Workbench or phpMyAdmin:")
        print("   - Open MySQL Workbench")
        print("   - Connect to server (it might remember password)")
        print("   - Manage users and reset password")
        
        print("\n2. Reset MySQL root password:")
        print("   - Stop MySQL service")
        print("   - Start MySQL with --skip-grant-tables option")
        print("   - Connect and reset password")
        print("   - Restart MySQL normally")
        
        print("\n3. Reinstall MySQL:")
        print("   - Backup your data first")
        print("   - Uninstall and reinstall with known password")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
