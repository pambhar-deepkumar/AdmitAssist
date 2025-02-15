@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Function to print messages with timestamp
for /f "tokens=1-2 delims= " %%a in ('echo %DATE% %TIME%') do set "TIMESTAMP=[%%a %%b]"

echo %TIMESTAMP% Starting the development environment setup.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo %TIMESTAMP% Virtual environment not found. Creating ".venv"...
    python -m venv .venv
    if errorlevel 1 (
        echo %TIMESTAMP% ERROR: Failed to create the virtual environment.
        exit /b 1
    )
    echo %TIMESTAMP% Virtual environment ".venv" created successfully.
) else (
    echo %TIMESTAMP% Virtual environment ".venv" already exists. Skipping creation.
)

REM Activate virtual environment
echo %TIMESTAMP% Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo %TIMESTAMP% ERROR: Failed to activate the virtual environment.
    exit /b 1
)
echo %TIMESTAMP% Virtual environment activated.

REM Upgrade pip to the latest version
echo %TIMESTAMP% Upgrading pip...
pip install --upgrade pip
if errorlevel 1 (
    echo %TIMESTAMP% ERROR: Failed to upgrade pip.
    exit /b 1
)
echo %TIMESTAMP% pip upgraded successfully.

REM Install required dependencies
echo %TIMESTAMP% Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo %TIMESTAMP% ERROR: Failed to install dependencies from requirements.txt.
    exit /b 1
)
echo %TIMESTAMP% Dependencies installed from requirements.txt.

echo %TIMESTAMP% Installing development dependencies from requirements-dev.txt...
pip install -r requirements-dev.txt
if errorlevel 1 (
    echo %TIMESTAMP% ERROR: Failed to install development dependencies from requirements-dev.txt.
    exit /b 1
)
echo %TIMESTAMP% Development dependencies installed successfully.

REM Setup pre-commit hooks
echo %TIMESTAMP% Setting up pre-commit hooks...
pre-commit install
if errorlevel 1 (
    echo %TIMESTAMP% ERROR: Failed to set up pre-commit hooks.
    exit /b 1
)
echo %TIMESTAMP% Pre-commit hooks installed successfully.

echo %TIMESTAMP% Development environment setup complete!

REM Launch the Streamlit application
echo %TIMESTAMP% Launching the Streamlit application...
streamlit run main.py
