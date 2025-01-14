# Strategy selection in sidebar
from .comprehensive import ComprehensiveStrategy
from .step_by_step import StepByStepStrategy

strategy_options = {"Step by step": "step_by_step", "Comprehensive": "comprehensive"}
strategies = {
    "comprehensive": ComprehensiveStrategy,
    "step_by_step": StepByStepStrategy,
}
