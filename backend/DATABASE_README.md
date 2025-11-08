# Database Setup Instructions

This project uses PostgreSQL to manage missing persons and unidentified bodies data.

## Database Schema

The database contains 3 main tables:

1. **missing_persons** - Records of missing persons reported by police
2. **unidentified_bodies** - Complete records after postmortem examination
3. **preliminary_uidb_reports** - Initial reports before postmortem (temporary)

### Key Features

- **Unique PID System**: Each record gets a unique Person ID (PID)
  - Missing Persons: `MP-2024-00001`
  - Unidentified Bodies: `UIDB-2024-00001`
  - Preliminary Reports: `PUIDB-2024-00001`

- **Photo Management**:
  - `profile_photo` - Main identification photo
  - `extra_photos` - JSON array of additional photos
  - Photos stored locally in organized folders

- **Unlimited Text Fields**:
  - `person_description` - Detailed physical description
  - `distinguishing_marks` - Scars, tattoos, birthmarks, etc.
  - `additional_notes` - Any other relevant information

- **Auto-updating Timestamps**: `updated_at` field automatically updates on record modification

## Setup Instructions

### 1. Install PostgreSQL

Download and install PostgreSQL from: https://www.postgresql.org/download/

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Database Credentials

Edit the `DB_CONFIG` in both `setup_database.py` and `db_helper.py`:

```python
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'your_postgres_username',
    'password': 'your_postgres_password',
    'host': 'localhost',
    'port': '5432'
}
```

### 4. Run Setup Script

```powershell
python setup_database.py
```

This will:
- Create photo storage folders
- Create the database
- Create all tables with indexes and triggers
- Verify the setup

## Folder Structure

```
RaptureTwelve_Hack4Safety/
├── photos/
│   ├── missing_persons/
│   │   ├── MP-2024-00001/
│   │   │   ├── profile.jpg
│   │   │   ├── photo_01.jpg
│   │   │   └── photo_02.jpg
│   │   └── MP-2024-00002/
│   ├── unidentified_bodies/
│   │   └── UIDB-2024-00001/
│   └── preliminary_uidb/
│       └── PUIDB-2024-00001/
├── database_schema.sql
├── setup_database.py
├── db_helper.py
├── vectordb.py
└── requirements.txt
```

## Using the Database Helper

### Example: Add a Missing Person

```python
from db_helper import DatabaseHelper
from datetime import datetime

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
        'distinguishing_marks': 'Scar on left arm, tattoo on right shoulder',
        'clothing_description': 'Blue jeans, white t-shirt',
        'person_description': 'Athletic build, short black hair, clean shaven, approximately 175cm tall',
        'last_seen_date': datetime.now(),
        'last_seen_latitude': 28.6139,
        'last_seen_longitude': 77.2090,
        'last_seen_address': 'Connaught Place, New Delhi',
        'reporter_name': 'Jane Doe',
        'reporter_contact': '+91-9999999999',
        'additional_notes': 'Was wearing glasses, has a medical condition',
        'status': 'Open'
    }
    
    pid = db.add_missing_person(
        missing_person_data,
        profile_photo_path='path/to/profile.jpg',
        extra_photo_paths=['path/to/photo1.jpg', 'path/to/photo2.jpg']
    )
    print(f"Created missing person with PID: {pid}")
```

### Example: Search Records

```python
with DatabaseHelper() as db:
    # Search for open cases
    results = db.search_records(
        'missing_persons',
        filters={'status': 'Open'},
        limit=50
    )
    
    for person in results:
        print(f"{person['pid']}: {person['name']}")
```

### Example: Update Status

```python
with DatabaseHelper() as db:
    db.update_status('missing_persons', 'MP-2024-00001', 'Matched')
```

### Example: Get by PID

```python
with DatabaseHelper() as db:
    person = db.get_by_pid('missing_persons', 'MP-2024-00001')
    if person:
        print(f"Found: {person['name']}")
```

## Database Operations

### Direct SQL Access

You can also access the database directly:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname='missing_persons_db',
    user='postgres',
    password='your_password',
    host='localhost'
)

cursor = conn.cursor(cursor_factory=RealDictCursor)
cursor.execute("SELECT * FROM missing_persons WHERE status = 'Open'")
results = cursor.fetchall()

cursor.close()
conn.close()
```

## Common Queries

### Get all open missing persons cases
```sql
SELECT * FROM missing_persons WHERE status = 'Open' ORDER BY reported_date DESC;
```

### Get all pending preliminary reports
```sql
SELECT * FROM preliminary_uidb_reports WHERE status = 'Pending' ORDER BY found_date DESC;
```

### Get cases from a specific police station
```sql
SELECT * FROM missing_persons WHERE police_station = 'Central Police Station';
```

### Get cases reported in a date range
```sql
SELECT * FROM missing_persons 
WHERE reported_date BETWEEN '2024-01-01' AND '2024-12-31';
```

## Notes

- All TEXT fields (descriptions, notes, marks) support unlimited length
- Photos are stored locally in the `photos/` folder structure
- PIDs are automatically generated in format: `PREFIX-YEAR-XXXXX`
- The `updated_at` timestamp automatically updates on any record modification
- Use the DatabaseHelper class for safe, easy database operations
- Extra photos are stored as JSON array in the database

## Security Recommendations

1. Never commit `DB_CONFIG` with real passwords to version control
2. Use environment variables for sensitive data
3. Implement proper access controls on the PostgreSQL database
4. Regularly backup the database and photos folder
5. Encrypt sensitive data if required by regulations
