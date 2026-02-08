@echo off
REM Setup script for Codoctopus - Initializes the Keys directory with example files

echo ========================================
echo Codoctopus Security Setup
echo ========================================
echo.

REM Check if Keys directory exists
if exist "Keys\" (
    echo WARNING: Keys directory already exists!
    echo This script will not overwrite existing credential files.
    set /p continue="Do you want to continue and only create missing files? (y/n) "
    if /i not "%continue%"=="y" (
        echo Setup cancelled.
        exit /b 1
    )
) else (
    echo Creating Keys directory...
    mkdir Keys
)

echo.
echo Copying example files to Keys directory...

REM Copy files if they don't exist
if not exist "Keys\openai_key.txt" (
    if exist "Keys.example\openai_key.txt.example" (
        copy "Keys.example\openai_key.txt.example" "Keys\openai_key.txt" >nul
        echo [OK] Created: Keys\openai_key.txt
    )
) else (
    echo [SKIP] Already exists: Keys\openai_key.txt
)

if not exist "Keys\database_uri.txt" (
    if exist "Keys.example\database_uri.txt.example" (
        copy "Keys.example\database_uri.txt.example" "Keys\database_uri.txt" >nul
        echo [OK] Created: Keys\database_uri.txt
    )
) else (
    echo [SKIP] Already exists: Keys\database_uri.txt
)

if not exist "Keys\jwt_secret.txt" (
    if exist "Keys.example\jwt_secret.txt.example" (
        copy "Keys.example\jwt_secret.txt.example" "Keys\jwt_secret.txt" >nul
        echo [OK] Created: Keys\jwt_secret.txt
    )
) else (
    echo [SKIP] Already exists: Keys\jwt_secret.txt
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo WARNING: Next steps:
echo.
echo 1. Edit the files in the Keys\ directory:
echo    - Keys\openai_key.txt     - Add your OpenAI API keys
echo    - Keys\database_uri.txt   - Add your MongoDB connection URI
echo    - Keys\jwt_secret.txt     - Generate a secure JWT secret
echo.
echo 2. Generate secure secrets:
echo    JWT Secret:  python -c "import secrets; print(secrets.token_urlsafe(32))"
echo.
echo 3. See SECURITY.md for complete setup instructions
echo.
echo WARNING: NEVER commit the Keys\ directory to version control!
echo.
pause
