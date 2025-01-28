import time

import streamlit as st


def create_file_uploader(file_config):
    return st.file_uploader(
        f"{file_config['display_name']} {'(Required)' if file_config['required'] else '(Optional)'}",
        type=[ext.replace(".", "") for ext in file_config["allowed_extensions"]],
        help=file_config["description"],
    )


def show_processing_screen(uploaded_files, config, processor):
    st.header("Processing Application")

    # Display uploaded files
    st.subheader("Uploaded Files")
    for file_config in config["file_inputs"]:
        file = uploaded_files.get(file_config["name"])
        if file:
            st.text(f"✓ {file_config['display_name']}: {file.name}")

    # Instead of dummy I would now like to call the processor.evaluate method and pass the uploaded_files dictionary to it as an argument to start the evaluation process.
    # Also if possible suign the processing I would like to display the progress of the evaluation process.
    # But I am not sure how to do that. Can you help me with that?

    # Processing progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_duration = sum(step["duration"] for step in config["processing_steps"])
    current_progress = 0

    for step in config["processing_steps"]:
        status_text.text(f"Current step: {step['name']}...")
        for _ in range(step["duration"]):
            current_progress += 1
            progress_bar.progress(current_progress / total_duration)
            time.sleep(1)

    status_text.text("Processing complete!")
    return True


def show_download_button():
    st.success("Evaluation completed successfully!")
    # In a real scenario, you would generate this report
    dummy_report = b"This is a dummy report content"
    st.download_button(
        label="Download Evaluation Report",
        data=dummy_report,
        file_name="evaluation_report.pdf",
        mime="application/pdf",
    )
