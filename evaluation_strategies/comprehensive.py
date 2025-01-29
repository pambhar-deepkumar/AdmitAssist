import openpyxl

from ..utils.document_processor import DocumentProcessor
from .base_strategy import BaseEvaluationStrategy

# from utils.markdown_parser import MarkdownLLMHelper


class ComprehensiveStrategy(BaseEvaluationStrategy):
    def evaluate(self, documents):
        print("Evaluating application with comprehensive strategy...")

        """
        Comprehensive evaluation combining:
        1. Academic performance
        2. Research potential
        3. Motivation and fit
        4. Additional qualifications
        """
        # Implementation...

        # Creates a parser for the LLM to retreive relevant content
        # markdownParser = MarkdownLLMHelper(documents["curriculum_analysis"])

        return openpyxl.open(documents["curriculum_analysis"]), True

    def retrieveCourse(self, courseName):
        pass
