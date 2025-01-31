from evaluation_strategies.comprehensive import ComprehensiveStrategy

if __name__ == "__main__":
    docuements = {
        "curriculum_analysis": "D:\GenAI\git\AdmitAssist\data\example_1\example_1_MIE_Curricularanalyse.xlsx",
        "module_description": "D:\GenAI\git\AdmitAssist\data\example_1\output\example_1_course_catalogue_LMU_BSc_Informatics.md",
        "essay": None,
        "motivation_letter": None,
    }
    v = ComprehensiveStrategy()
    v.evaluate(docuements)

# from abc import ABC, abstractmethod

# class BaseEvaluationStrategy(ABC):
#     def __init__(self, name: str):
#         self.name = name

#     @abstractmethod
#     def evaluate(self, documents):
#         pass

# class ComprehensiveStrategy(BaseEvaluationStrategy):
#     def __init__(self):
#         super().__init__("Comprehensive Strategy")
#         print("Initializing ComprehensiveStrategy")

#     def evaluate(self, documents):
#         print("Evaluating application with comprehensive strategy...")
#         # Add evaluation logic here

# # Instantiate and use ComprehensiveStrategy
# if __name__ == "__main__":
#     documents = {
#         'curriculum_analysis': 'path_to_curriculum_analysis.xlsx',
#         'module_description': 'path_to_module_description.md',
#         'essay': None,
#         'motivation_letter': None,
#     }
#     v = ComprehensiveStrategy()
#     v.evaluate(documents)
