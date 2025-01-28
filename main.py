import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from evaluation_strategies.all_strategies import strategy_options
from modules.file_handler import load_config, validate_required_files
from modules.processor import ApplicationProcessor
from modules.ui_components import (
    create_file_uploader,
    show_download_button,
    show_processing_screen,
)


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None
    if "evaluation_report" not in st.session_state:
        st.session_state.evaluation_report = None
    if "upload_dir" not in st.session_state:
        st.session_state.upload_dir = None
    if "saved_file_paths" not in st.session_state:
        st.session_state.saved_file_paths = {}


def create_upload_directory():
    """Creates a timestamped directory for storing uploaded files"""
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_data"
    )
    os.makedirs(base_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = os.path.join(base_dir, f"upload_{timestamp}")
    os.makedirs(upload_dir, exist_ok=True)

    return upload_dir


def save_uploaded_file(uploaded_file, directory):
    """Saves an uploaded file to the specified directory"""
    if uploaded_file is None:
        return None

    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def main():
    st.title("Application Evaluation System")

    # Initialize session state
    initialize_session_state()

    # Load configuration
    config = load_config()

    selected_strategy = st.sidebar.selectbox(
        "Select Evaluation Strategy", options=list(strategy_options.keys()), index=0
    )

    # Display strategy information
    st.sidebar.write(f"Using: {selected_strategy} Strategy")

    # Initialize processor with selected strategy
    processor = ApplicationProcessor(strategy_options[selected_strategy])

    # File upload section
    if not st.session_state.processing_started:
        # Create new upload directory for this session if not exists
        if st.session_state.upload_dir is None:
            st.session_state.upload_dir = create_upload_directory()

        uploaded_files = {}
        saved_file_paths = {}

        # Create file uploaders based on config
        for file_config in config["file_inputs"]:
            uploaded_file = create_file_uploader(file_config)
            uploaded_files[file_config["name"]] = uploaded_file
            # Save the file if it was uploaded
            if uploaded_file is not None:
                saved_path = save_uploaded_file(
                    uploaded_file, st.session_state.upload_dir
                )
                saved_file_paths[file_config["name"]] = saved_path

        # Evaluate button
        if st.button("Evaluate Application"):
            if validate_required_files(uploaded_files, config):
                st.session_state.processing_started = True
                st.session_state.uploaded_files = uploaded_files
                st.session_state.saved_file_paths = saved_file_paths
                processor.process_application(saved_file_paths)
            else:
                st.error("Please upload all required documents.")

    # Processing section
    elif (
        st.session_state.processing_started and not st.session_state.processing_complete
    ):
        success, evaluation_report = show_processing_screen(
            st.session_state.uploaded_files, config, processor
        )
        if success:
            # Save evaluation report to the upload directory
            report_path = os.path.join(
                st.session_state.upload_dir, "evaluation_report.json"
            )
            with open(report_path, "w") as f:
                f.write(evaluation_report)

            st.session_state.processing_complete = True
            st.session_state.evaluation_report = evaluation_report
            st.experimental_rerun()

    # Download section
    elif st.session_state.processing_complete:
        show_download_button(st.session_state.evaluation_report)

        # Add reset button
        if st.button("Evaluate Another Application"):
            # Reset all session state variables
            st.session_state.processing_started = False
            st.session_state.processing_complete = False
            st.session_state.uploaded_files = None
            st.session_state.evaluation_report = None
            st.session_state.upload_dir = None
            st.session_state.saved_file_paths = {}
            st.experimental_rerun()


if __name__ == "__main__":
    main()
