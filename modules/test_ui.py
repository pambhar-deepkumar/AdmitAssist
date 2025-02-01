import time

import streamlit as st


def sample_animation():
    with st.spinner("Another Processing..."):
        try:
            time.sleep(5)
            st.text("Done Processing")
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
    with st.spinner("Processing step 2..."):
        try:
            time.sleep(5)
            st.text("Done Processing")
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
    time.sleep(5)
