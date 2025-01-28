from utils.document_processor import DocumentProcessor

from .base_strategy import BaseEvaluationStrategy


class ComprehensiveStrategy(BaseEvaluationStrategy):
    def evaluate(self, documents):
        print(documents)
        documentProcessor = DocumentProcessor(llm_manager=self.llm_manager)
        documentProcessor.process_documents(documents)

        """
        Comprehensive evaluation combining:
        1. Academic performance
        2. Research potential
        3. Motivation and fit
        4. Additional qualifications
        """
        # Implementation...

    def retrieveCourse(self, courseName):
        pass
