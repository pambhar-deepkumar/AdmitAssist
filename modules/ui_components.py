import io

import streamlit as st


def create_file_uploader(file_config):
    return st.file_uploader(
        f"{file_config['display_name']} {'(Required)' if file_config['required'] else '(Optional)'}",
        type=[ext.replace(".", "") for ext in file_config["allowed_extensions"]],
        help=file_config["description"],
    )


def show_processing_screen(uploaded_files, processor):
    st.header("Processing Application")

    # Display uploaded files
    st.subheader("Uploaded Files")
    for file_name, file in uploaded_files.items():
        if file:
            st.text(f"✓ {file_name}: {file.name}")

    # Indefinite processing indicator using spinner and status updates
    with st.spinner("Processing..."):
        # status_text = st.empty()  # Placeholder for dynamic status updates

        try:
            # What shoudl this return is file path to the saved report ok ?
            # convert 'module_description' if pdf
            #
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
