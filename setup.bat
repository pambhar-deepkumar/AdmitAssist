@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Function to create timestamp
call :CreateTimestamp
goto :Main

:CreateTimestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set "DATETIME=%%I"
set "TIMESTAMP=[%DATETIME:~0,4%-%DATETIME:~4,2%-%DATETIME:~6,2% %DATETIME:~8,2%:%DATETIME:~10,2%:%DATETIME:~12,2%]"
exit /b 0

:LogMessage
echo %TIMESTAMP% %~1
exit /b 0

:CheckPythonVersion
python --version > nul 2>&1
if errorlevel 1 (
    call :LogMessage "ERROR: Python is not installed or not in PATH."
    exit /b 1
)
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%I"
if "%PYTHON_VERSION:~0,1%" neq "3" (
    call :LogMessage "ERROR: Python 3.x is required, found version %PYTHON_VERSION%"
    exit /b 1
)
exit /b 0

:CheckRequirements
if not exist "requirements.txt" (
    call :LogMessage "ERROR: requirements.txt not found."
    exit /b 1
)
if not exist "main.py" (
    call :LogMessage "ERROR: main.py not found."
    exit /b 1
)
exit /b 0

:CreateVirtualEnv
if not exist ".venv" (
    call :LogMessage "Virtual environment not found. Creating '.venv'..."
    python -m venv .venv
    if errorlevel 1 (
        call :LogMessage "ERROR: Failed to create virtual environment."
        exit /b 1
    )
    call :LogMessage "Virtual environment created successfully."
) else (
    call :LogMessage "Virtual environment '.venv' already exists. Skipping creation."
)
exit /b 0

:ActivateVirtualEnv
if not exist ".venv\Scripts\activate.bat" (
    call :LogMessage "ERROR: Virtual environment activation script not found."
    exit /b 1
)
call :LogMessage "Activating virtual environment..."
call .venv\Scripts\activate.bat
if errorlevel 1 (
    call :LogMessage "ERROR: Failed to activate virtual environment."
    exit /b 1
)
call :LogMessage "Virtual environment activated."
exit /b 0

:UpgradePip
call :LogMessage "Upgrading pip..."
python -m pip install --upgrade pip
if errorlevel 1 (
    call :LogMessage "ERROR: Failed to upgrade pip."
    exit /b 1
)
call :LogMessage "pip upgraded successfully."
exit /b 0

:InstallDependencies
call :LogMessage "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if errorlevel 1 (
    call :LogMessage "ERROR: Failed to install dependencies."
    exit /b 1
)
call :LogMessage "Dependencies installed successfully."
exit /b 0


:CheckStreamlit
where streamlit > nul 2>&1
if errorlevel 1 (
    call :LogMessage "ERROR: Streamlit is not installed."
    exit /b 1
)
exit /b 0

:LaunchStreamlit
call :LogMessage "Launching Streamlit application..."
streamlit run main.py
if errorlevel 1 (
    call :LogMessage "ERROR: Failed to launch Streamlit application."
    exit /b 1
)
exit /b 0

:Main
call :LogMessage "Starting development environment setup."

REM Perform initial checks
call :CheckPythonVersion || exit /b 1
call :CheckRequirements || exit /b 1

REM Setup virtual environment
call :CreateVirtualEnv || exit /b 1
call :ActivateVirtualEnv || exit /b 1

REM Install dependencies
call :UpgradePip || exit /b 1
call :InstallDependencies || exit /b 1

REM Setup pre-commit and launch applicationß
call :CheckStreamlit || exit /b 1
call :LaunchStreamlit

endlocal
exit /b 0
