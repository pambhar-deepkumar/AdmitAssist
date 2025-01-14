from pathlib import Path

import yaml


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
