"""Core solver module for Savanty using DSPy."""

import json
import os
from typing import Any

import dspy
from clorm.clingo import Control

from savanty.dspy_modules import (
    InteractiveProblemSolver,
    ProblemSuitabilityCheck,
    SolutionVisualization,
)
from savanty.logging_config import logger

# LLM configuration (lazy initialization)
_lm_instance = None


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass


def _get_configured_lm():
    """Get a configured LLM instance with proper API key validation."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm_model = os.getenv("SAVANTY_LLM_MODEL", "openai/gpt-4o")

    if not openai_api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it: export OPENAI_API_KEY=your_key_here"
        )

    logger.debug(f"Configuring LLM with model: {llm_model}")
    return dspy.LM(llm_model, api_key=openai_api_key)


def _ensure_lm_configured():
    """Ensure the LLM is configured before use."""
    global _lm_instance
    if _lm_instance is None:
        _lm_instance = _get_configured_lm()
        dspy.settings.configure(lm=_lm_instance)
        logger.info("LLM configured successfully")


class ProblemSolverResult:
    """Wrapper class for problem solver results."""

    def __init__(
        self,
        needs_more_info: bool = False,
        questions: list[str] = None,
        solution: str = None,
        asp_code: str = None,
        visualization_html: str = None,
        error: str = None,
        not_suitable: bool = False,
        suggested_tool: str = None,
        suitability_reason: str = None,
    ):
        self.needs_more_info = needs_more_info
        self.questions = questions or []
        self.solution = solution
        self.asp_code = asp_code
        self.visualization_html = visualization_html
        self.error = error
        # New fields for suitability check
        self.not_suitable = not_suitable
        self.suggested_tool = suggested_tool
        self.suitability_reason = suitability_reason


def check_problem_suitability(problem_description: str) -> dict:
    """Check if a problem is suitable for ASP solving."""
    _ensure_lm_configured()
    logger.debug("Checking problem suitability for ASP")
    checker = dspy.Predict(ProblemSuitabilityCheck)
    result = checker(problem_description=problem_description)
    return {
        "is_suitable": result.is_suitable.lower(),
        "problem_type": result.problem_type,
        "reasoning": result.reasoning,
        "suggested_tool": result.suggested_tool,
        "confidence": result.confidence,
    }


def generate_visualization(problem_description: str, solution: str) -> str:
    """Generate an HTML visualization of the solution using DSPy."""
    _ensure_lm_configured()
    try:
        logger.debug("Generating solution visualization")
        visualizer = dspy.Predict(SolutionVisualization)
        result = visualizer(problem_description=problem_description, solution=solution)
        return result.visualization_html
    except Exception as e:
        logger.warning(f"Visualization generation failed: {e}")
        # If visualization fails, return a simple fallback
        return f"""
        <div style="font-family: system-ui, sans-serif; padding: 20px;">
            <h3 style="color: #1e40af; margin-bottom: 16px;">Solution</h3>
            <pre style="background: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap;">{solution}</pre>
            <p style="color: #6b7280; font-size: 12px; margin-top: 12px;">
                <em>Visualization generation failed: {str(e)}</em>
            </p>
        </div>
        """


def generate_clorm_predicates(predicates: list[dict[str, Any]]) -> str:
    """Generate Clorm predicate classes from parsed predicates."""
    predicate_code = ""
    for pred in predicates:
        fields = ", ".join(
            [f"{field} = {field_type}" for field, field_type in pred["fields"].items()]
        )
        predicate_code += f"""
class {pred["name"]}(Predicate):
    {fields}
"""
    return predicate_code


def generate_asp_program(problem_info: dict[str, Any]) -> str:
    """Generate ASP program from parsed problem information."""
    constraints = "\n".join(problem_info["constraints"])
    optimize = problem_info["optimize"]

    return f"""
{constraints}

{optimize}

#show.
"""


def validate_and_parse_problem(description: str, additional_info: str = None) -> dict[str, Any]:
    """Validate and parse the optimization problem using DSPy."""
    _ensure_lm_configured()
    logger.debug("Validating and parsing problem")

    # Create the interactive problem solver
    solver = InteractiveProblemSolver()

    try:
        # Run the DSPy pipeline
        result = solver.forward(problem_description=description, additional_info=additional_info)

        # If the solver needs more information, return the questions
        if result.needs_more_info:
            raise ValueError("NEEDS_MORE_INFO:" + json.dumps(result.questions))

        # Parse the program components
        program_components = json.loads(result.program.program_components)

        return program_components
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse program components: {e}")
        raise ValueError(f"Failed to parse program components from LLM output: {str(e)}") from e
    except Exception as e:
        # Check if this is a "needs more info" error
        if str(e).startswith("NEEDS_MORE_INFO:"):
            raise
        logger.error(f"Error in DSPy processing: {e}")
        raise ValueError(f"Error in DSPy processing: {str(e)}") from e


def solve_optimization_problem(
    problem_description: str, additional_info: str = None
) -> ProblemSolverResult:
    """Solve an optimization problem given its description using DSPy."""
    logger.info("Starting optimization problem solving")
    try:
        # Step 0: Check if problem is suitable for ASP
        suitability = check_problem_suitability(problem_description)

        if suitability["is_suitable"] == "no":
            logger.info(f"Problem not suitable for ASP: {suitability['reasoning']}")
            # Problem is not suitable for ASP - return helpful message
            tool_suggestions = {
                "scipy": "scipy (pip install scipy) - for continuous optimization with gradients",
                "cvxpy": "cvxpy (pip install cvxpy) - for convex optimization problems",
                "calculator": "a simple calculator or spreadsheet",
                "pandas": "pandas (pip install pandas) - for data analysis and aggregation",
                "sklearn": "scikit-learn (pip install sklearn) - for machine learning tasks",
                "none": None,
            }
            suggested = tool_suggestions.get(
                suitability["suggested_tool"], suitability["suggested_tool"]
            )

            return ProblemSolverResult(
                not_suitable=True,
                suggested_tool=suggested,
                suitability_reason=suitability["reasoning"],
                error=f"This problem is better suited for a different tool. {suitability['reasoning']}",
            )

        # Step 1: Validate and parse the problem using DSPy
        logger.debug("Parsing problem description")
        problem_info = validate_and_parse_problem(problem_description, additional_info)

        # Step 2: Generate Clorm predicates
        logger.debug("Generating Clorm predicates")
        predicate_code = generate_clorm_predicates(problem_info["predicates"])
        exec(predicate_code, globals())  # noqa: S102

        # Step 3: Construct the ASP program
        logger.debug("Constructing ASP program")
        asp_program = generate_asp_program(problem_info)

        # Step 4: Solve the optimization problem
        logger.debug("Running Clingo solver")
        ctrl = Control(unifier=[globals()[pred["name"]] for pred in problem_info["predicates"]])

        # Add facts
        for fact in problem_info["facts"]:
            if "(" in fact and ")" in fact:
                predicate_name, *args = fact.split("(")
                args = args[0].rstrip(")").split(",")
                predicate_class = globals()[predicate_name]
                ctrl.add_fact(predicate_class(*args))

        ctrl.add_program(asp_program)

        solution = None
        with ctrl.solve(yield_=True) as sh:
            for model in sh:
                solution = model.facts(atoms=True)

        # Build full ASP code for display
        facts_code = "\n".join([f"{fact}." for fact in problem_info["facts"]])
        full_asp_code = f"% Facts\n{facts_code}\n\n% Rules and Constraints\n{asp_program}"

        solution_str = str(solution) if solution else "No solution found"
        logger.info(f"Problem solved: {solution_str[:100]}...")

        # Generate visualization
        visualization_html = generate_visualization(problem_description, solution_str)

        return ProblemSolverResult(
            solution=solution_str,
            asp_code=full_asp_code,
            visualization_html=visualization_html,
        )
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return ProblemSolverResult(error=str(e))
    except ValueError as e:
        # Check if this is a "needs more info" error
        if str(e).startswith("NEEDS_MORE_INFO:"):
            questions_json = str(e)[16:]  # Remove "NEEDS_MORE_INFO:" prefix
            questions = json.loads(questions_json)
            logger.info(f"Problem needs more info: {len(questions)} questions")
            return ProblemSolverResult(needs_more_info=True, questions=questions)
        else:
            logger.error(f"Validation error: {e}")
            return ProblemSolverResult(error=str(e))
    except Exception as e:
        logger.error(f"Error solving optimization problem: {e}", exc_info=True)
        return ProblemSolverResult(error=f"Error solving optimization problem: {str(e)}")
