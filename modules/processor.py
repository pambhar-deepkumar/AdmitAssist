import os
from typing import Tuple

from openpyxl import Workbook

from evaluation_strategies.all_strategies import strategies
from utils.document_processor import convert_pdf_documents
from utils.llm_manager import LLMManager


class ApplicationProcessor:
    def __init__(self, strategy_type: str):
        self.llm_manager = LLMManager()
        self.strategy = self._get_strategy(strategy_type)

    def _get_strategy(self, strategy_type: str):
        if strategy_type not in strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        return strategies[strategy_type](self.llm_manager)

    def process_application(self, uploaded_files) -> Tuple[bool, Workbook]:
        module_description = uploaded_files.get("module_description")
        if module_description:
            if module_description.lower().endswith(".pdf"):
                dir_path = os.path.dirname(module_description)
                path_to_md_file = convert_pdf_documents(dir_path)
                uploaded_files["module_description"] = path_to_md_file
            elif module_description.lower().endswith(".md"):
                pass
            else:
                raise ValueError(
                    "Unsupported module description format. Only PDF and Markdown are accepted."
                )

        try:
            # Execute evaluation strategy with processed documents
            return self.strategy.evaluate(uploaded_files)
        except Exception as e:
            return False, f"Evaluation failed: {str(e)}"
