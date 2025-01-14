import streamlit as st
import pandas as pd
from pathlib import Path
import os
import time

def list_uploaded_files(section_name):
    files = []
    directory = Path(f"uploads/{section_name}")
    if directory.exists():
        files = list(directory.glob("*"))
    return files

def create_upload_section(section_name, allowed_types):
    st.header(section_name)
    uploaded_file = st.file_uploader(
        f"Upload {section_name}", 
        type=allowed_types,
        key=section_name
    )
    
    if uploaded_file is not None:
        save_dir = Path(f"uploads/{section_name}")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Saved {uploaded_file.name} in {section_name} section!")
        
        # Preview based on file type
        if uploaded_file.type.startswith('image/'):
            st.image(uploaded_file)
        elif uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
        elif uploaded_file.type == 'application/pdf':
            st.write("PDF file uploaded successfully!")

def show_file_listing(sections):
    st.header("File Listing")
    
    # Create tabs for each section
    tabs = st.tabs(sections.keys())
    
    for tab, section_name in zip(tabs, sections.keys()):
        with tab:
            files = list_uploaded_files(section_name)
            if files:
                for file in files:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"📄 {file.name}")
                    with col2:
                        st.write(f"{file.stat().st_size/1024:.1f} KB")
                    with col3:
                        if st.button("Delete", key=f"delete_{file.name}"):
                            file.unlink()
                            st.rerun()
            else:
                st.info(f"No files uploaded in {section_name} section")

def simulate_processing():
    """Simulate some processing with a progress bar"""
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        progress_text.text(f"Processing... {i+1}%")
        time.sleep(0.05)  # Simulate work being done
    
    progress_text.text("Processing Complete!")
    time.sleep(1)
    progress_bar.empty()
    progress_text.empty()

def main():
    st.set_page_config(page_title="File Upload Portal", layout="wide")
    
    st.title("File Upload Portal")
    
    # Define your sections and allowed file types
    sections = {
        "Images": ["jpg", "jpeg", "png"],
        "Documents": ["pdf", "docx"],
        "Data Files": ["csv", "xlsx"],
    }
    
    # Create columns for different sections
    cols = st.columns(len(sections))
    
    # Create upload sections
    for col, (section_name, allowed_types) in zip(cols, sections.items()):
        with col:
            create_upload_section(section_name, allowed_types)
    
    # Evaluate button with spinner and progress bar
    if st.button("Evaluate Files", type="primary"):
        with st.spinner('Processing files...'):
            simulate_processing()
            
            # Show file listing after processing
            show_file_listing(sections)
            
            # Optional: Add your actual evaluation logic here
            st.success("Evaluation Complete!")
            
            # Example metrics display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Files", value=sum(len(list_uploaded_files(section)) for section in sections))
            with col2:
                st.metric(label="Processing Time", value="2.5s")
            with col3:
                st.metric(label="Status", value="Complete")

if __name__ == "__main__":
    main()
