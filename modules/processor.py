import os
from typing import Tuple

import streamlit as st
from openpyxl import Workbook

from evaluation_strategies.all_strategies import strategies
from evaluation_strategies.comprehensive import ComprehensiveStrategy
from utils.document_processor import convert_pdf_documents


class ApplicationProcessor:
    def __init__(self, strategy_type: str):
        self.strategy = self._get_strategy(strategy_type)

    def _get_strategy(self, strategy_type: str):
        if strategy_type not in strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        print(f"Using strategy: {strategy_type}")
        return strategies[strategy_type]

    def process_application(self, uploaded_files) -> Tuple[bool, Workbook]:
        with st.status("Processing module description file..."):
            module_description = uploaded_files.get("module_description")
            st.text("Checking if module description is a PDF file...")
            if module_description.lower().endswith(".pdf"):
                try:
                    st.text("Module description is a PDF file.")
                    st.text("Converting module description to markdown...")
                    dir_path = os.path.dirname(module_description)
                    path_to_md_file = convert_pdf_documents(dir_path)
                    # Maybe add a happy emoji icon below
                    st.info("Module description converted to markdown.")
                    uploaded_files["module_description"] = path_to_md_file
                except Exception as e:
                    # Maybe add a sad emoji icon below
                    st.error(
                        "An error occurred during conversion for pdf to markdown. Please try again."
                    )
                    st.exception(e)
                    return False, None

        with st.status("Starting evaluation process..."):
            try:
                thisstrategy = ComprehensiveStrategy()
                st.text(f"Using {thisstrategy.name} strategy")
                return thisstrategy.evaluate(uploaded_files)
            except Exception as e:
                st.error(f"An error occurred during processing.")
                st.exception(e)
                return False, None
