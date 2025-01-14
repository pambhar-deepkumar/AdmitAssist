import os
import sys

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
        uploaded_files = {}

        # Create file uploaders based on config
        for file_config in config["file_inputs"]:
            uploaded_files[file_config["name"]] = create_file_uploader(file_config)

        # Evaluate button
        if st.button("Evaluate Application"):
            if validate_required_files(uploaded_files, config):
                st.session_state.processing_started = True
                st.session_state.uploaded_files = uploaded_files
                st.experimental_rerun()
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
            st.session_state.processing_complete = True
            st.session_state.evaluation_report = evaluation_report
            st.experimental_rerun()

    # Download section
    elif st.session_state.processing_complete:
        show_download_button(st.session_state.evaluation_report)

        # Add reset button
        if st.button("Evaluate Another Application"):
            st.session_state.processing_started = False
            st.session_state.processing_complete = False
            st.session_state.uploaded_files = None
            st.session_state.evaluation_report = None
            st.experimental_rerun()


if __name__ == "__main__":
    main()
