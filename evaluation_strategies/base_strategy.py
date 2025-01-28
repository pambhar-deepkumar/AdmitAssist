from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class BaseEvaluationStrategy(ABC):
    def __init__(self, llm_manager, final_report: str):
        self.llm_manager = llm_manager
        self.final_report = final_report

    @abstractmethod
    def evaluate(self, documents: Dict[str, Any]) -> Tuple[bool, str]:
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
