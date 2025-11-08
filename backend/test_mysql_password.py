"""
Interactive MySQL Password Finder
This script helps you find and test your MySQL password
"""

import mysql.connector
from getpass import getpass

def test_password(password):
    """Test if a password works"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            port=3306
        )
        conn.close()
        return True
    except:
        return False

def main():
    print("=" * 60)
    print("MySQL Password Finder")
    print("=" * 60)
    
    # Test common passwords first
    print("\nTesting common passwords...")
    common_passwords = ['', 'root', 'mysql', 'admin', 'password', '123456', 'hello']
    
    for pwd in common_passwords:
        pwd_display = '(empty)' if pwd == '' else pwd
        print(f"Trying: {pwd_display}...", end=' ')
        if test_password(pwd):
            print("✓ SUCCESS!")
            print(f"\n{'='*60}")
            print(f"Your MySQL root password is: '{pwd}'" if pwd else "Your MySQL root password is EMPTY")
            print(f"{'='*60}")
            
            # Ask if user wants to update config files
            response = input("\nUpdate all config files with this password? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                print(f"\nPlease tell the AI assistant: 'My password is {pwd}'")
                print("The assistant will update all files for you.")
            return
        else:
            print("✗ Failed")
    
    print("\n" + "=" * 60)
    print("Common passwords didn't work. Let's try manual entry.")
    print("=" * 60)
    
    # Manual password entry
    while True:
        print("\nEnter your MySQL root password (or 'quit' to exit):")
        password = getpass("Password: ")
        
        if password.lower() == 'quit':
            print("Exiting...")
            break
        
        print("Testing password...", end=' ')
        if test_password(password):
            print("✓ SUCCESS!")
            print(f"\n{'='*60}")
            print("Password verified successfully!")
            print(f"{'='*60}")
            print(f"\nTell the AI assistant: 'My password is {password}'")
            print("The assistant will update all config files for you.")
            break
        else:
            print("✗ Failed - Incorrect password. Try again.")

if __name__ == "__main__":
    main()
