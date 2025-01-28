import os
from datetime import datetime
from pathlib import Path

import yaml


def create_upload_directory():
    """
    Creates a timestamped directory within ./user_data for storing uploaded files.
    Returns the path to the created directory.
    """
    # Create base user_data directory if it doesn't exist
    base_dir = "./user_data"
    os.makedirs(base_dir, exist_ok=True)

    # Create timestamped directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = os.path.join(base_dir, f"upload_{timestamp}")
    os.makedirs(upload_dir, exist_ok=True)

    return upload_dir


def save_uploaded_file(uploaded_file, directory):
    """
    Saves an uploaded file to the specified directory.
    """
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def load_config():
    config_path = Path("config/upload_config.yaml")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def validate_file_extension(file, allowed_extensions):
    if file is None:
        return False
    file_extension = Path(file.name).suffix.lower()
    return file_extension in allowed_extensions


def validate_required_files(uploaded_files, config):
    required_files = [f for f in config["file_inputs"] if f["required"]]
    for req_file in required_files:
        if (
            req_file["name"] not in uploaded_files
            or uploaded_files[req_file["name"]] is None
        ):
            return False
    return True
