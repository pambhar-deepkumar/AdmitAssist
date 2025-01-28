from typing import Tuple

from openpyxl import Workbook

from evaluation_strategies.all_strategies import strategies
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
        try:
            return self.strategy.evaluate(uploaded_files)
        except Exception as e:
            return False, f"Evaluation failed: {str(e)}"
