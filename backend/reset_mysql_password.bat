@echo off
echo ================================================
echo MySQL Password Reset Script for Windows
echo ================================================
echo.

echo Step 1: Stopping MySQL service...
net stop MySQL80
echo.

echo Step 2: Creating temporary init file...
echo ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword123'; > %TEMP%\mysql-init.txt
echo FLUSH PRIVILEGES; >> %TEMP%\mysql-init.txt
echo.

echo Step 3: Starting MySQL with skip-grant-tables...
echo Please wait while MySQL restarts...
echo.

echo Navigate to: C:\Program Files\MySQL\MySQL Server 8.0\bin
echo Then run:
echo mysqld --init-file=%TEMP%\mysql-init.txt
echo.

echo ================================================
echo INSTRUCTIONS:
echo ================================================
echo 1. This will reset your password to: newpassword123
echo 2. After MySQL starts, press Ctrl+C to stop it
echo 3. Then run: net start MySQL80
echo 4. Your new password will be: newpassword123
echo ================================================
pause
