# PostgreSQL Password Reset Guide

## ✅ EASIEST METHOD: Trust Authentication

Follow these steps to reset your PostgreSQL password:

### Step 1: Edit pg_hba.conf

1. **Open the file as Administrator:**
   ```
   C:\Program Files\PostgreSQL\13\data\pg_hba.conf
   ```
   
2. **Find this line:**
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

3. **Change `scram-sha-256` to `trust`:**
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            trust
   ```

4. **Save the file** (you need Administrator privileges)

### Step 2: Restart PostgreSQL Service

**Option A - Using Services GUI:**
1. Press `Win + R`, type `services.msc`, press Enter
2. Find `postgresql-x64-13`
3. Right-click → Restart

**Option B - Using PowerShell (as Admin):**
```powershell
Restart-Service postgresql-x64-13
```

### Step 3: Connect and Reset Password

Open PowerShell/CMD and run:

```cmd
"C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -d postgres
```

It will connect WITHOUT asking for password!

Then run this SQL command:
```sql
ALTER USER postgres PASSWORD 'your_new_password';
\q
```

### Step 4: Revert pg_hba.conf

1. **Open pg_hba.conf again**

2. **Change `trust` back to `scram-sha-256`:**
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

3. **Restart PostgreSQL service again**

### Step 5: Test New Password

```powershell
python test_db_connection.py
```

---

## 🔧 Alternative: Use pgAdmin

1. Open **pgAdmin 4** from Start Menu
2. It might have your password saved
3. If it connects:
   - Right-click on "PostgreSQL 13"
   - Properties → Connection
   - Click "Change Password"
   - Enter new password

---

## 📝 Update Your Scripts

After resetting, update the password in:

1. `backend/populate_unidentified_bodies.py` (line 17)
2. `backend/db_helper.py` (line 17)
3. `backend/setup_database.py` (line 17)

Change:
```python
'password': 'your_password',  # ← Put your new password here
```

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **Always change `trust` back to `scram-sha-256`** after resetting password
2. **Never leave trust authentication enabled** - it allows anyone to connect
3. **Use a strong password** for production systems
4. **Store password in .env file**, not in code (we have .env set up)

---

## 🚨 If All Else Fails

Windows password might be stored in:
- **pgAdmin saved passwords:** `%APPDATA%\pgAdmin\`
- **pgpass file:** `%APPDATA%\postgresql\pgpass.conf`

Check these files, password might be there!
