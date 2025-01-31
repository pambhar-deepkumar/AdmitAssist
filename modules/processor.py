import os
from typing import Tuple

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
        print("Processing application...")
        print("self.strategy", self.strategy)

        module_description = uploaded_files.get("module_description")

        if module_description.lower().endswith(".pdf"):
            print("Converting module description to markdown...")
            dir_path = os.path.dirname(module_description)
            path_to_md_file = convert_pdf_documents(dir_path)
            uploaded_files["module_description"] = path_to_md_file
        try:
            print("Evaluating application...")
            # Print the name of the class of the strategy
            print("Strategy class:", self.strategy.__init__())
            strategy = ComprehensiveStrategy()
            return strategy.evaluate(uploaded_files)
        except Exception as e:
            return False, f"Evaluation failed: {str(e)}"
