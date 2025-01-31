from enum import Enum


class TestResult(Enum):
    """
    Enum representing the possible evaluation results.
    """

    PASSED = "passed"
    NOT_PASSED = "not passed"
    NOT_FOUND = "not found"

    def __str__(self):
        return super().__str__()
