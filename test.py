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
