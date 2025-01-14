@echo off

REM Create virtual environment if it doesn't exist
if not exist .venv (
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Setup pre-commit hooks
pre-commit install

echo Development environment setup complete!
