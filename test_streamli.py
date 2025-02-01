import time

import streamlit as st

with st.spinner("Please wait while your application is being processed..."):
    with st.status("Downloading data..."):
        st.write("Searching for data...")
        time.sleep(1)
        st.write("Found URL.")
        time.sleep(1)
        st.write("Downloading data...")
        st.info("Download complete.")
        time.sleep(1)
    st.write("Data downloaded.")
    with st.status("processing data..."):
        st.write("Searching for data...")
        time.sleep(1)
        st.write("Found URL.")
        time.sleep(1)
        st.write("Downloading data...")
        st.info("Download complete.")
        time.sleep(1)
    st.write("Data downloaded.")

st.warning("This is a warning")
