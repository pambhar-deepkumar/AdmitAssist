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
    """Initialize session state variables if they don't exist."""
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
    """Reset session state variables to initial state."""
    st.session_state.processing_started = False
    st.session_state.processing_complete = False
    st.session_state.uploaded_files = None
    st.session_state.evaluation_report = None
    st.session_state.upload_dir = None
    st.session_state.saved_file_paths = {}


def main():
    st.title("Admit Assist")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("Missing required environment variable: OPENAI_API_KEY. Please set this variable before running the application.")
        st.stop()

    initialize_session_state()

    config = load_config()

    st.sidebar.header("Evaluation Options")
    selected_strategy = st.sidebar.selectbox(
        "Select Evaluation Strategy",
        options=list(strategy_options.keys()),
        index=0,
        help="Choose the strategy that fits your application scenario.",
    )
    st.sidebar.info(f"Strategy in use: {selected_strategy}")
    processor = ApplicationProcessor(strategy_options[selected_strategy])

    if not st.session_state.processing_started:
        st.subheader("Upload Your Application Files")

        if st.session_state.upload_dir is None:
            st.session_state.upload_dir = create_upload_directory()

        uploaded_files = {}
        saved_file_paths = {}

        # Create file uploader for each required file input defined in config
        for file_config in config["file_inputs"]:
            uploaded_file = create_file_uploader(file_config)
            uploaded_files[file_config["name"]] = uploaded_file
            if uploaded_file is not None:
                saved_path = save_uploaded_file(
                    uploaded_file, st.session_state.upload_dir
                )
                saved_file_paths[file_config["name"]] = saved_path

        st.divider()

        if st.button(
            "Evaluate Application", help="Click to start evaluating your application"
        ):
            if validate_required_files(uploaded_files, config):
                st.session_state.processing_started = True
                st.session_state.uploaded_files = uploaded_files
                st.session_state.saved_file_paths = saved_file_paths
                st.rerun()
            else:
                st.error(
                    "Missing required files. Please ensure all required documents are uploaded."
                )

    elif (
        st.session_state.processing_started and not st.session_state.processing_complete
    ):
        # Processing screen with visual spinner and clear headings
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
            # Provide download button for the completed evaluation report
            show_download_button(st.session_state.evaluation_report)

            # Button to process another application
            if st.button(
                "Evaluate Another Application", help="Reset and start a new evaluation"
            ):
                reset_session_state()
                st.rerun()


if __name__ == "__main__":
    main()
