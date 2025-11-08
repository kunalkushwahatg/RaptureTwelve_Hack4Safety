# 🚀 Getting Started - Complete Guide

## ✅ Environment Setup Complete!

Your conda environment `hsf` has been created and all dependencies are installed successfully.

## 📋 What's Been Done

- ✅ Conda environment `hsf` created with Python 3.11
- ✅ All dependencies installed (psycopg2-binary, python-dotenv, qdrant-client)
- ✅ No dependency conflicts
- ✅ Photo folders created
- ✅ Database schema ready

## 🎯 Next Steps

### 1. Configure PostgreSQL Credentials

You need to update the database configuration in two files:

#### File 1: `setup_database.py`
Find this section (around line 16-22):
```python
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'postgres',          # ← Change to your PostgreSQL username
    'password': 'your_password',  # ← Change to your PostgreSQL password
    'host': 'localhost',
    'port': '5432'
}
```

#### File 2: `db_helper.py`
Find this section (around line 12-18):
```python
DB_CONFIG = {
    'dbname': 'missing_persons_db',
    'user': 'postgres',          # ← Change to your PostgreSQL username
    'password': 'your_password',  # ← Change to your PostgreSQL password
    'host': 'localhost',
    'port': '5432'
}
```

### 2. Run Database Setup

Open PowerShell and run:

```powershell
# Activate environment
conda activate hsf

# Run setup (creates database and tables)
python setup_database.py
```

This will:
- Create the `missing_persons_db` database
- Create all 3 tables (missing_persons, unidentified_bodies, preliminary_uidb_reports)
- Set up indexes and triggers
- Verify the setup

### 3. Test the Setup

```powershell
# Still in hsf environment
python example_usage.py
```

This will demonstrate:
- Adding sample missing person records
- Adding preliminary UIDB reports
- Searching records
- Getting records by PID
- Updating status

## 📁 Quick Reference

### Activate Environment (Every Time)
```powershell
conda activate hsf
```

Or double-click: `activate_env.bat`

### Deactivate Environment
```powershell
conda deactivate
```

### Check Installed Packages
```powershell
conda activate hsf
pip list
```

### Verify Setup
```powershell
conda activate hsf
python -c "import psycopg2; print('Ready!')"
```

## 💻 Usage Example

Once setup is complete, you can use the database like this:

```python
from db_helper import DatabaseHelper
from datetime import datetime

# Always run this with hsf environment activated!
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
        'person_description': 'Athletic build, black hair...',
        'status': 'Open'
    }
    
    pid = db.add_missing_person(
        data,
        profile_photo_path='C:/path/to/profile.jpg',
        extra_photo_paths=['C:/path/to/photo1.jpg']
    )
    
    print(f"Created: {pid}")  # Output: MP-2024-00001
```

## 🗂️ Project Structure

```
RaptureTwelve_Hack4Safety/
├── photos/                    # Photo storage (auto-organized)
│   ├── missing_persons/
│   ├── unidentified_bodies/
│   └── preliminary_uidb/
├── setup_database.py         # RUN THIS FIRST (after config)
├── db_helper.py              # Main database library
├── example_usage.py          # Usage examples
├── database_schema.sql       # SQL schema
├── activate_env.bat          # Quick environment activator
└── requirements.txt          # Dependencies (already installed)
```

## 🔧 Troubleshooting

### Issue: "conda: command not found"
**Solution:** Install Anaconda or Miniconda first
- Download: https://www.anaconda.com/download

### Issue: "psycopg2 connection error"
**Solution:** Make sure PostgreSQL is installed and running
- Download: https://www.postgresql.org/download/
- Check if running: `pg_ctl status`

### Issue: "Permission denied"
**Solution:** Run PowerShell as Administrator

### Issue: "Wrong environment"
**Solution:** Make sure you activated the environment
```powershell
conda activate hsf
```

## 📚 Documentation Files

- `README.md` - Project overview
- `DATABASE_README.md` - Detailed database documentation
- `SETUP_SUMMARY.md` - Complete setup summary
- `QUICK_REFERENCE.md` - Quick command reference
- `CONDA_SETUP.md` - Conda environment guide
- `GETTING_STARTED.md` - This file

## ✨ You're All Set!

Your environment is ready. Just:
1. Configure PostgreSQL credentials (see step 1 above)
2. Run `python setup_database.py`
3. Start building!

## 🎓 Learning Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- Python Database Programming: https://docs.python.org/3/library/sqlite3.html

---

**Need help?** Check the other documentation files or review the example scripts.

**Environment:** `hsf` (Python 3.11)  
**Status:** ✅ Ready to use  
**Dependencies:** ✅ Installed  
**Next:** Configure PostgreSQL credentials and run setup
