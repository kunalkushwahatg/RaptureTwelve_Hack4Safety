# Complete MySQL Fix and Reset Script
# Run this in Admin PowerShell

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MySQL Complete Fix and Reset" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Stop MySQL if running
Write-Host "Step 1: Stopping MySQL service..." -ForegroundColor Yellow
net stop MySQL80 2>$null

# Go to MySQL bin directory
Write-Host "Step 2: Navigating to MySQL directory..." -ForegroundColor Yellow
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Backup old data directory if exists
$dataDir = "C:\Program Files\MySQL\MySQL Server 8.0\data"
$backupDir = "C:\Program Files\MySQL\MySQL Server 8.0\data_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

if (Test-Path $dataDir) {
    Write-Host "Step 3: Backing up old data directory..." -ForegroundColor Yellow
    Move-Item -Path $dataDir -Destination $backupDir -Force
    Write-Host "  Backup created at: $backupDir" -ForegroundColor Green
}

# Initialize new data directory with NO password
Write-Host "Step 4: Initializing new data directory (NO password)..." -ForegroundColor Yellow
.\mysqld --initialize-insecure --console

Write-Host ""
Write-Host "Step 5: Starting MySQL service..." -ForegroundColor Yellow
net start MySQL80

# Wait a moment for MySQL to fully start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "MySQL root password is now: EMPTY (no password)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing connection..." -ForegroundColor Yellow

# Test connection
$testResult = & .\mysql -u root -e "SELECT 'Connection successful!' AS status;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Connection test SUCCESSFUL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step:" -ForegroundColor Yellow
    Write-Host "Tell the AI: 'My password is empty'" -ForegroundColor Cyan
    Write-Host "The AI will update all config files." -ForegroundColor Cyan
} else {
    Write-Host "✗ Connection test failed" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
