from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from openpyxl import Workbook


class BaseEvaluationStrategy(ABC):
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager

    @abstractmethod
    def evaluate(self, documents: Dict[str, Any]) -> Tuple[bool, Workbook]:
        """
        Implement the evaluation logic
        You will have access to the uploaded documents in the documents dictionary
        Structure of the documents dictionary:
        {
            'curriculum_analysis': '<file_path_to_curriculum_analysis>',
            'module_description': '<file_path_to_module_description>',
            'essay': '<file_path_to_essay>',
            'motivation_letter': '<file_path_to_motivation_letter>'
        }
        Store the document in the final report path
        """
        pass
