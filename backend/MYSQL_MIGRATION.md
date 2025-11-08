# MySQL Migration Guide

## Overview
The Missing Persons Database system has been migrated from PostgreSQL to MySQL. This document outlines all the changes made and steps to set up the new MySQL database.

## Changes Made

### 1. Requirements (`requirements.txt`)
- **Removed**: `psycopg2-binary==2.9.9`
- **Added**: `mysql-connector-python==8.2.0`

### 2. Database Schema (`database_schema.sql`)
Converted from PostgreSQL to MySQL syntax:
- Changed `SERIAL` to `INT AUTO_INCREMENT`
- Changed `TIMESTAMP` to `DATETIME`
- Changed `INTEGER` to `INT`
- Moved `DEFAULT` values after column definition
- Added `ON UPDATE CURRENT_TIMESTAMP` for auto-updating timestamps
- Changed `CHECK` constraints to use `CONSTRAINT` syntax
- Removed `CASCADE` from `DROP TABLE` statements
- Removed PostgreSQL triggers (MySQL handles `updated_at` automatically)
- Added `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`
- Changed foreign key syntax from `REFERENCES` to `CONSTRAINT ... FOREIGN KEY`

### 3. Database Helper (`db_helper.py`)
- Changed imports from `psycopg2` to `mysql.connector`
- Updated `DB_CONFIG` structure:
  - `dbname` → `database`
  - `user` → `user` (default changed from `postgres` to `root`)
  - `port` changed from `'5432'` to `3306`
- Changed cursor factory from `RealDictCursor` to `dictionary=True`
- Changed exception handling from `psycopg2.Error` to `Error` (from mysql.connector)
- All SQL queries remain compatible (both use `%s` placeholders)

### 4. Database Setup (`setup_database.py`)
- Changed imports from `psycopg2` to `mysql.connector`
- Simplified database creation (MySQL creates DB directly)
- Updated schema execution to split statements by `;` for MySQL
- Changed verification query from PostgreSQL `information_schema` to MySQL `SHOW TABLES`
- Updated configuration structure to match MySQL

### 5. Population Script (`populate_unidentified_bodies.py`)
- Changed imports from `psycopg2` to `mysql.connector`
- Updated `DB_CONFIG` for MySQL
- Updated connection function and error messages

### 6. Test Connection (`test_db_connection.py`)
- Changed imports from `psycopg2` to `mysql.connector`
- Updated common passwords list (MySQL defaults differ from PostgreSQL)
- Changed table existence check to MySQL syntax
- Updated recovery instructions for MySQL

### 7. Example Scripts
- Updated comments in `example_usage.py` and `example_vector_retrieval.py`
- Changed references from "PostgreSQL" to "MySQL"

## Installation Steps

### 1. Install MySQL
Download and install MySQL Community Server from:
https://dev.mysql.com/downloads/mysql/

During installation:
- Set a root password (remember this!)
- Default port is 3306

### 2. Update Python Dependencies
```bash
cd backend
pip uninstall psycopg2-binary
pip install -r requirements.txt
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Database Connection
Update the password in these files:
- `db_helper.py` (line 17)
- `setup_database.py` (line 13)
- `populate_unidentified_bodies.py` (line 16)
- `test_db_connection.py` (line 20)

```python
DB_CONFIG = {
    'database': 'missing_persons_db',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD_HERE',  # Change this!
    'host': 'localhost',
    'port': 3306
}
```

### 4. Test Connection
```bash
python test_db_connection.py
```

This will try common passwords and help you verify connectivity.

### 5. Create Database and Tables
```bash
python setup_database.py
```

This will:
- Create the `missing_persons_db` database
- Create all three tables (missing_persons, unidentified_bodies, preliminary_uidb_reports)
- Create the photos folder structure
- Verify the setup

### 6. Populate with Sample Data (Optional)
```bash
python populate_unidentified_bodies.py
```

## Key Differences: PostgreSQL vs MySQL

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Auto-increment | SERIAL | INT AUTO_INCREMENT |
| Timestamp | TIMESTAMP | DATETIME |
| Integer | INTEGER | INT |
| Return clause | RETURNING | Uses LAST_INSERT_ID() |
| Boolean | BOOLEAN | BOOLEAN/TINYINT(1) |
| JSON | JSON/JSONB | JSON |
| Dictionary cursor | RealDictCursor | dictionary=True |
| Default port | 5432 | 3306 |
| Default user | postgres | root |

## SQL Compatibility

Most queries are compatible between PostgreSQL and MySQL:
- Both use `%s` for parameter placeholders
- Standard SQL syntax works in both
- JSON operations are similar
- Index creation is identical

## Troubleshooting

### Connection Issues
1. Verify MySQL is running:
   ```bash
   # Windows (PowerShell)
   Get-Service MySQL*
   
   # Or check in Services app (services.msc)
   ```

2. Test with MySQL command line:
   ```bash
   mysql -u root -p
   ```

3. Check firewall settings (port 3306)

### Password Issues
If you forgot your MySQL root password:
1. Stop MySQL service
2. Start MySQL with `--skip-grant-tables`
3. Connect without password and reset
4. Restart MySQL normally

See detailed steps in `test_db_connection.py` output.

### Schema Issues
If tables aren't created:
1. Check `database_schema.sql` for syntax errors
2. Run statements individually in MySQL Workbench
3. Check MySQL error log

## Migration Checklist

- [x] Update requirements.txt
- [x] Convert database_schema.sql
- [x] Update db_helper.py
- [x] Update setup_database.py
- [x] Update populate_unidentified_bodies.py
- [x] Update test_db_connection.py
- [x] Update documentation references
- [ ] Install MySQL
- [ ] Update passwords in config files
- [ ] Run test_db_connection.py
- [ ] Run setup_database.py
- [ ] Test with sample data

## Additional Notes

### Character Set
All tables use `utf8mb4` encoding to support international characters and emojis.

### Storage Engine
All tables use InnoDB for:
- Foreign key support
- Transaction support
- Better performance
- ACID compliance

### Auto-Update Timestamps
MySQL automatically updates `updated_at` timestamps using:
```sql
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

No triggers needed like in PostgreSQL!

## Support

If you encounter issues:
1. Check MySQL error log
2. Verify all passwords are updated
3. Ensure MySQL service is running
4. Check port 3306 is not blocked
5. Review this migration guide

For database-specific issues, consult:
- MySQL Documentation: https://dev.mysql.com/doc/
- MySQL Community Forums: https://forums.mysql.com/
