# Quick Reference Card - Missing Persons Database

## 🎯 PID Formats
- Missing Persons: `MP-2024-00001`
- Unidentified Bodies: `UIDB-2024-00001`
- Preliminary Reports: `PUIDB-2024-00001`

## 📁 Photo Storage Paths
```
photos/missing_persons/{PID}/profile.jpg
photos/missing_persons/{PID}/photo_01.jpg
photos/unidentified_bodies/{PID}/profile.jpg
photos/preliminary_uidb/{PID}/profile.jpg
```

## 🔧 Common Commands

### Setup
```powershell
pip install -r requirements.txt
python setup_database.py
```

### Add Missing Person
```python
from db_helper import DatabaseHelper
from datetime import datetime

with DatabaseHelper() as db:
    data = {
        'fir_number': 'FIR/2024/001',
        'police_station': 'Station Name',
        'reported_date': datetime.now(),
        'name': 'Person Name',
        'age': 25,
        'gender': 'Male',
        'status': 'Open'
    }
    pid = db.add_missing_person(data, profile_photo_path='photo.jpg')
```

### Search Records
```python
with DatabaseHelper() as db:
    results = db.search_records('missing_persons', {'status': 'Open'})
```

### Get by PID
```python
with DatabaseHelper() as db:
    person = db.get_by_pid('missing_persons', 'MP-2024-00001')
```

### Update Status
```python
with DatabaseHelper() as db:
    db.update_status('missing_persons', 'MP-2024-00001', 'Matched')
```

## 📊 Table Names
- `missing_persons`
- `unidentified_bodies`
- `preliminary_uidb_reports`

## 🎨 Status Values

### Missing Persons & Unidentified Bodies
- `Open` - Active case
- `Matched` - Identity confirmed
- `Closed` - Case resolved

### Preliminary UIDB
- `Pending` - Awaiting postmortem
- `Processed` - Moved to main table
- `Archived` - Stored for records

## 🔑 Required Fields

### Missing Persons
- `fir_number` ✓
- `police_station` ✓
- `reported_date` ✓

### Unidentified Bodies
- `case_number` ✓
- `police_station` ✓
- `reported_date` ✓
- `found_date` ✓

### Preliminary UIDB
- `report_number` ✓
- `police_station` ✓
- `found_date` ✓

## 📝 Text Fields (Unlimited Length)
- `person_description`
- `distinguishing_marks`
- `clothing_description`
- `additional_notes`
- `initial_notes`

## 🗄️ Database Config
```python
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

## 🚨 Important Notes
1. PIDs are auto-generated - don't provide them
2. Photos are stored locally - provide full paths
3. All TEXT fields support unlimited length
4. Timestamps auto-update on modification
5. Extra photos stored as JSON array

## 📞 Quick Help
- Full docs: `DATABASE_README.md`
- Setup guide: `SETUP_SUMMARY.md`
- Examples: `example_usage.py`
