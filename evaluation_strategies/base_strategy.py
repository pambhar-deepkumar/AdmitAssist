from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class BaseEvaluationStrategy(ABC):
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager

    @abstractmethod
    def evaluate(self, documents: Dict[str, Any]) -> Tuple[bool, str]:
        """Implement the evaluation logic"""
        pass
