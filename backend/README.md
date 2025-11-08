# RaptureTwelve_Hack4Safety

## Missing Persons & Unidentified Bodies Database System

A comprehensive PostgreSQL-based system for managing missing persons reports and unidentified bodies, with support for facial recognition and geolocation.

## 🎯 Features

- **3 Database Tables**: Missing Persons, Unidentified Bodies, and Preliminary Reports
- **Unique PID System**: Auto-generated unique identifiers (MP-2024-00001, UIDB-2024-00001, etc.)
- **Photo Management**: Profile photos + multiple additional photos stored locally
- **Unlimited Text Fields**: Detailed descriptions without length limits
- **Geolocation Support**: Latitude/longitude tracking for last seen/found locations
- **Status Tracking**: Open, Matched, Closed status for each case
- **Auto-timestamps**: Automatic creation and update timestamps
- **Python Helper Library**: Easy-to-use database operations

## 📁 Project Structure

```
RaptureTwelve_Hack4Safety/
├── photos/                      # Photo storage
│   ├── missing_persons/        
│   ├── unidentified_bodies/    
│   └── preliminary_uidb/       
├── database_schema.sql          # PostgreSQL schema
├── setup_database.py            # Database setup script
├── db_helper.py                 # Database operations library
├── example_usage.py             # Usage examples
├── vectordb.py                  # Vector database for facial recognition
├── DATABASE_README.md           # Detailed database documentation
├── SETUP_SUMMARY.md            # Quick setup guide
└── requirements.txt             # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Database
Edit `setup_database.py` and `db_helper.py` with your PostgreSQL credentials:
```python
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

### 3. Run Setup
```powershell
python setup_database.py
```

### 4. Test Installation
```powershell
python example_usage.py
```

## 📊 Database Tables

### Missing Persons
- Unique PID (MP-2024-XXXXX)
- FIR details and police station
- Physical description (unlimited text)
- Photos (profile + extras)
- Last seen location (geo-tagged)
- Reporter information

### Unidentified Bodies
- Unique PID (UIDB-2024-XXXXX)
- Postmortem details
- Physical description (unlimited text)
- Photos (profile + extras)
- Found location (geo-tagged)
- Forensic evidence tracking (DNA, dental, fingerprints)

### Preliminary UIDB Reports
- Unique PID (PUIDB-2024-XXXXX)
- Initial observations before postmortem
- Links to main UIDB table after processing
- Status: Pending/Processed/Archived

## 💻 Usage Example

```python
from db_helper import DatabaseHelper
from datetime import datetime

with DatabaseHelper() as db:
    # Add a missing person
    data = {
        'fir_number': 'FIR/2024/001',
        'police_station': 'Central Police Station',
        'reported_date': datetime.now(),
        'name': 'John Doe',
        'age': 25,
        'gender': 'Male',
        'height_cm': 175,
        'person_description': 'Athletic build, black hair, brown eyes...',
        'last_seen_address': 'Connaught Place, New Delhi',
        'status': 'Open'
    }
    
    pid = db.add_missing_person(
        data,
        profile_photo_path='path/to/profile.jpg',
        extra_photo_paths=['path/to/photo1.jpg', 'path/to/photo2.jpg']
    )
    
    print(f"Created missing person: {pid}")
    
    # Search records
    results = db.search_records('missing_persons', filters={'status': 'Open'})
    for person in results:
        print(f"{person['pid']}: {person['name']}")
```

## 📖 Documentation

- **[SETUP_SUMMARY.md](SETUP_SUMMARY.md)** - Complete setup guide
- **[DATABASE_README.md](DATABASE_README.md)** - Detailed database documentation
- **[database_schema.sql](database_schema.sql)** - Full SQL schema

## 🔐 Security

- Photos stored locally in organized folders
- Database credentials managed via configuration
- `.gitignore` excludes sensitive data
- `.env.example` provided for environment variables

## 🛠️ Technologies

- **PostgreSQL** - Primary database
- **Python 3.x** - Backend language
- **psycopg2** - PostgreSQL adapter
- **Qdrant** - Vector database for facial recognition

## 📝 License

This project is part of Hack4Safety initiative.

## 👥 Contributors

- RaptureTwelve Team