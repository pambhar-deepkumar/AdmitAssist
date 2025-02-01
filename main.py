import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from evaluation_strategies.all_strategies import strategy_options
from modules.file_handler import (
    create_upload_directory,
    load_config,
    save_uploaded_file,
    validate_required_files,
)
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


def reset_session_state():
    """Reset session state variables to initial state"""
    st.session_state.processing_started = False
    st.session_state.processing_complete = False
    st.session_state.uploaded_files = None
    st.session_state.evaluation_report = None
    st.session_state.upload_dir = None
    st.session_state.saved_file_paths = {}


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

        for file_config in config["file_inputs"]:
            uploaded_file = create_file_uploader(file_config)
            uploaded_files[file_config["name"]] = uploaded_file
            if uploaded_file is not None:
                saved_path = save_uploaded_file(
                    uploaded_file, st.session_state.upload_dir
                )
                saved_file_paths[file_config["name"]] = saved_path

        col1, col2 = st.columns(2)

        # Evaluate button triggers processing
        if col1.button("Evaluate Application"):
            if validate_required_files(uploaded_files, config):
                st.session_state.processing_started = True
                st.session_state.uploaded_files = uploaded_files
                st.session_state.saved_file_paths = saved_file_paths
                st.rerun()  # Force rerun to proceed to the processing step
            else:
                st.error("Please upload all required documents.")

        # Retry button to reset state
        if col2.button("Retry"):
            reset_session_state()
            st.rerun()

    elif (
        st.session_state.processing_started and not st.session_state.processing_complete
    ):
        success, evaluation_report = show_processing_screen(
            st.session_state.saved_file_paths, processor
        )

        if success:
            report_path = os.path.join(
                st.session_state.upload_dir, "evaluation_report.xlsx"
            )
            evaluation_report.save(report_path)

            st.session_state.processing_complete = True
            st.session_state.evaluation_report = evaluation_report
            st.rerun()  # Rerun to show the download button screen

    elif st.session_state.processing_complete:
        show_download_button(st.session_state.evaluation_report)

        if st.button("Evaluate Another Application"):
            reset_session_state()
            st.rerun()


if __name__ == "__main__":
    main()
