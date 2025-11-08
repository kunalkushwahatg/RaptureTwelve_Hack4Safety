# Conda Environment Setup for Missing Persons Database

## Creating a Clean Environment

### Step 1: Create New Conda Environment
```powershell
conda create -n missing_persons_db python=3.11 -y
```

### Step 2: Activate the Environment
```powershell
conda activate missing_persons_db
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Verify Installation
```powershell
python -c "import psycopg2; import qdrant_client; print('All packages installed successfully!')"
```

## Quick Commands

### Activate Environment (Use this every time)
```powershell
conda activate missing_persons_db
```

### Deactivate Environment
```powershell
conda deactivate
```

### Delete Environment (if needed)
```powershell
conda deactivate
conda env remove -n missing_persons_db
```

### List All Environments
```powershell
conda env list
```

## After Environment Setup

Once the environment is created and activated, run:

```powershell
# 1. Configure database credentials
# Edit setup_database.py and db_helper.py with your PostgreSQL credentials

# 2. Run setup
python setup_database.py

# 3. Test with examples
python example_usage.py
```

## Troubleshooting

If you get dependency conflicts:
1. Make sure you're in the conda environment: `conda activate missing_persons_db`
2. Try upgrading pip: `python -m pip install --upgrade pip`
3. Reinstall requirements: `pip install -r requirements.txt --upgrade`

## Environment Information

After activation, you can check:
```powershell
python --version          # Should be Python 3.11.x
pip list                  # List all installed packages
which python              # Location of Python executable
```
