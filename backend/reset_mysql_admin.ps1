# ============================================================
# MySQL Password Reset - PowerShell Commands (Run as Admin)
# ============================================================

# STEP 1: Stop MySQL Service
Write-Host "`nSTEP 1: Stopping MySQL Service..." -ForegroundColor Yellow
net stop MySQL80

# STEP 2: Create temporary password reset file
Write-Host "`nSTEP 2: Creating password reset file..." -ForegroundColor Yellow
@"
ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword123';
FLUSH PRIVILEGES;
"@ | Out-File -FilePath "$env:TEMP\mysql-init.txt" -Encoding ASCII

Write-Host "Created file at: $env:TEMP\mysql-init.txt" -ForegroundColor Green

# STEP 3: Navigate to MySQL bin directory
Write-Host "`nSTEP 3: Navigating to MySQL directory..." -ForegroundColor Yellow
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

# STEP 4: Start MySQL with the init file
Write-Host "`nSTEP 4: Starting MySQL with password reset..." -ForegroundColor Yellow
Write-Host "IMPORTANT: Wait until you see 'ready for connections', then press Ctrl+C" -ForegroundColor Red
Write-Host ""

Start-Process mysqld -ArgumentList "--init-file=`"$env:TEMP\mysql-init.txt`"" -NoNewWindow -Wait

# STEP 5: Start MySQL service normally
Write-Host "`nSTEP 5: Starting MySQL service normally..." -ForegroundColor Yellow
net start MySQL80

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "PASSWORD RESET COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Your new MySQL root password is: newpassword123" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Write-Host "`nNext: Tell the AI 'My password is newpassword123'" -ForegroundColor Yellow
Write-Host "The AI will update all config files automatically." -ForegroundColor Yellow
