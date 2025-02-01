import io
import os

import streamlit as st

from .test_ui import sample_animation


def create_file_uploader(file_config):
    return st.file_uploader(
        f"{file_config['display_name']} {'(Required)' if file_config['required'] else '(Optional)'}",
        type=[ext.replace(".", "") for ext in file_config["allowed_extensions"]],
        help=file_config["description"],
    )


def show_processing_screen(uploaded_files, processor):
    st.header("Application Processing")

    st.subheader("Uploaded Files:")
    for file_name, file_path in uploaded_files.items():
        if file_path:
            uploaded_file_name = os.path.basename(file_path)
            st.text(f"✓ {file_name}: {uploaded_file_name}")

    st.divider()

    with st.spinner("Please wait while your application is being processed..."):
        try:
            st.text("Processing starting...")
            return processor.process_application(uploaded_files)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            return False, None


def show_download_button(evaluation_report):
    st.success("Evaluation completed successfully!")

    buffer = io.BytesIO()
    evaluation_report.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="Download Evaluation Report",
        data=buffer,
        file_name="evaluation_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
