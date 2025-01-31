import json
from dataclasses import dataclass

import openpyxl
from enums import TestResult
from openpyxl.utils.cell import range_boundaries


@dataclass
class RowData:
    """
    Data class representing a row in the Excel sheet.

    Attributes:
    - name: str, the name of the course/module
    - credits: float, the number of credits
    - evaluation: str, the evaluation result
    - comment: str, a comment regarding the evaluation
    - eval_cell: str, the cell reference for the evaluation result
    - comment_cell: str, the cell reference for the comment

    The evaluation and comment attributes are optional and can be set later.
    """

    name: str
    credits: float
    evaluation: TestResult = None
    comment: str = None
    eval_cell: str = None
    comment_cell: str = None

    def set_evaluation(self, evaluation: TestResult, comment: str):
        self.evaluation = evaluation
        self.comment = comment


class ModuleData:
    """
    Data class representing a module in the Excel sheet.

    Attributes:
    - name: str, the name of the module
    - rows: list[RowData], the rows of the module

    Implements the __iter__ and __next__ methods to allow iteration over the rows.
    """

    def __init__(
        self, name: str, content: str, learnOut: str, maxCred: int, rows: list[RowData]
    ):
        self.name = name
        self.content = content
        self.learnOut = learnOut
        self.maxCred = maxCred
        self.rows = rows

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        while self._index < len(self.rows):
            row = self.rows[self._index]
            self._index += 1
            if row.name is not None:
                return row
        raise StopIteration


class AssessmentManager:
    """
    Class to manage the assessment data for multiple modules in an Excel sheet.

    Attributes:
    - data: dict, the assessment data loaded from a JSON file
    - wb: Workbook, the Excel workbook
    - ws: Worksheet, the active worksheet

    Methods:
    - _process_modules: Processes the modules from the JSON data
    - _create_module_rows: Creates RowData objects for each row in a module
    - _get_cell_references: Returns a list of cell references from a given range
    - save: Saves all evaluations and comments back to the Excel file
    - get_wb: Returns the Excel workbook
    - __iter__: Iterates over all modules
    - __next__: Returns the next module
    """

    def __init__(self, json_file, excel_file):
        with open(json_file, "r") as f:
            self.data = json.load(f)

        self.wb = openpyxl.load_workbook(excel_file)
        self.ws = self.wb.active
        self.modules = []
        self._process_modules()

    def _process_modules(self):
        for section in self.data.values():
            modules = section.get("Modules") or section.get("modules") or []
            for module in modules:
                module_name = module["Course"]
                module_content = module["Content"]
                module_learning_outcome = module["Learning Outcome"]
                module_max_credit = module["Minimum Credits"]
                rows = self._create_module_rows(module)
                self.modules.append(
                    ModuleData(
                        module_name,
                        module_content,
                        module_learning_outcome,
                        module_max_credit,
                        rows,
                    )
                )

    def _create_module_rows(self, module):
        """
        Creates RowData objects for each row in the module's ranges.
        """
        name_cells = self._get_cell_references(module["Name Location"])
        credit_cells = self._get_cell_references(module["Credits Location"])
        eval_cells = self._get_cell_references(module["Evaluation Result Location"])
        comment_cells = self._get_cell_references(module["Comments Location"])

        return [
            RowData(
                name=self.ws[name].value,
                credits=self.ws[credit].value,
                eval_cell=eval,
                comment_cell=comment,
            )
            for name, credit, eval, comment in zip(
                name_cells, credit_cells, eval_cells, comment_cells
            )
        ]

    def _get_cell_references(self, cell_range):
        """
        Returns a list of cell references (e.g., ['B32', 'B33', ...]) from a given range.
        """
        min_col, min_row, max_col, max_row = range_boundaries(cell_range)
        return [
            f"{openpyxl.utils.get_column_letter(min_col)}{row}"
            for row in range(min_row, max_row + 1)
        ]

    def save(self):
        """
        Saves all evaluations and comments back to their respective locations in the Excel file.
        """
        for module in self.modules:
            for row in module:
                if row.eval_cell and row.evaluation:
                    self.ws[row.eval_cell] = row.evaluation.value
                if row.comment_cell and row.comment:
                    self.ws[row.comment_cell] = row.comment
        self.wb.save("updated_assessment.xlsx")

    def get_wb(self):
        for module in self.modules:
            for row in module:
                if row.eval_cell and row.evaluation:
                    self.ws[row.eval_cell] = row.evaluation.value
                if row.comment_cell and row.comment:
                    self.ws[row.comment_cell] = row.comment
        return self.wb

    def __iter__(self):
        """
        Iterates over all modules.
        """
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.modules):
            module = self.modules[self._index]
            self._index += 1
            return module
        raise StopIteration


# Example usage:
if __name__ == "__main__":
    manager = AssessmentManager(
        "D:\\GenAI\\git\\AdmitAssist\\data\\course_requirements\\Assessment Format.json",
        "D:\\GenAI\\git\\AdmitAssist\\data\\course_requirements\\MIE_Curricularanalyse_Information_Engineering_Template.xlsx",
    )

    # Iterate through modules and rows
    for module in manager:
        print(f"\nModule: {module.name}")
        for row in module:
            print(f"Processing: {row.name} ({row.credits} ECTS)")
            # Set evaluation and comment for this row if applicable
            if "Informatik" in (row.name or ""):
                row.set_evaluation(True, "Excellent performance")

    # Save all changes to a new Excel file
    manager.save()
