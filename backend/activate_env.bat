@echo off
REM Activate conda environment and display setup instructions

echo ================================================
echo Missing Persons Database - Environment Activator
echo ================================================
echo.

call conda activate hsf

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment 'hsf'
    echo.
    echo Please create the environment first:
    echo   conda create -n hsf python=3.11 -y
    echo   conda activate hsf
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Conda environment 'hsf' activated!
echo.
echo Next Steps:
echo   1. Configure database credentials in setup_database.py and db_helper.py
echo   2. Run: python setup_database.py
echo   3. Test: python example_usage.py
echo.
echo ================================================

cmd /k
