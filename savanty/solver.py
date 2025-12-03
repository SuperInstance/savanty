"""Core solver module for Savanty using DSPy."""

import os
import json
from typing import Dict, Any, Optional, List
from clorm import Predicate, ConstantField, IntegerField
from clorm.clingo import Control
import dspy
from savanty.dspy_modules import InteractiveProblemSolver, SolutionVisualization, ProblemSuitabilityCheck


# Configure DSPy with LLM
openai_api_key = os.getenv("OPENAI_API_KEY")
llm_model = os.getenv("SAVANTY_LLM_MODEL", "openai/gpt-4o")
# Use a placeholder if no API key is provided (will fail at runtime if actually needed)
lm = dspy.LM(llm_model, api_key=openai_api_key or "YOUR_API_KEY_HERE")
dspy.settings.configure(lm=lm)


class ProblemSolverResult:
    """Wrapper class for problem solver results."""

    def __init__(self, needs_more_info: bool = False, questions: List[str] = None,
                 solution: str = None, asp_code: str = None,
                 visualization_html: str = None, error: str = None,
                 not_suitable: bool = False, suggested_tool: str = None,
                 suitability_reason: str = None):
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
    checker = dspy.Predict(ProblemSuitabilityCheck)
    result = checker(problem_description=problem_description)
    return {
        'is_suitable': result.is_suitable.lower(),
        'problem_type': result.problem_type,
        'reasoning': result.reasoning,
        'suggested_tool': result.suggested_tool,
        'confidence': result.confidence
    }


def generate_visualization(problem_description: str, solution: str) -> str:
    """Generate an HTML visualization of the solution using DSPy."""
    try:
        visualizer = dspy.Predict(SolutionVisualization)
        result = visualizer(
            problem_description=problem_description,
            solution=solution
        )
        return result.visualization_html
    except Exception as e:
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


def generate_clorm_predicates(predicates: list) -> str:
    """Generate Clorm predicate classes from parsed predicates."""
    predicate_code = ""
    for pred in predicates:
        fields = ", ".join([f"{field} = {type}" for field, type in pred['fields'].items()])
        predicate_code += f"""
class {pred['name']}(Predicate):
    {fields}
"""
    return predicate_code


def generate_asp_program(problem_info: Dict[str, Any]) -> str:
    """Generate ASP program from parsed problem information."""
    constraints = "\n".join(problem_info['constraints'])
    optimize = problem_info['optimize']
    
    return f"""
{constraints}

{optimize}

#show.
"""


def validate_and_parse_problem(description: str, additional_info: str = None) -> Dict[str, Any]:
    """Validate and parse the optimization problem using DSPy."""
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
        raise ValueError(f"Failed to parse program components from LLM output: {str(e)}")
    except Exception as e:
        # Check if this is a "needs more info" error
        if str(e).startswith("NEEDS_MORE_INFO:"):
            raise
        raise ValueError(f"Error in DSPy processing: {str(e)}")


def solve_optimization_problem(problem_description: str, additional_info: str = None) -> ProblemSolverResult:
    """Solve an optimization problem given its description using DSPy."""
    try:
        # Step 0: Check if problem is suitable for ASP
        suitability = check_problem_suitability(problem_description)

        if suitability['is_suitable'] == 'no':
            # Problem is not suitable for ASP - return helpful message
            tool_suggestions = {
                'scipy': 'scipy (pip install scipy) - for continuous optimization with gradients',
                'cvxpy': 'cvxpy (pip install cvxpy) - for convex optimization problems',
                'calculator': 'a simple calculator or spreadsheet',
                'pandas': 'pandas (pip install pandas) - for data analysis and aggregation',
                'sklearn': 'scikit-learn (pip install sklearn) - for machine learning tasks',
                'none': None
            }
            suggested = tool_suggestions.get(suitability['suggested_tool'], suitability['suggested_tool'])

            return ProblemSolverResult(
                not_suitable=True,
                suggested_tool=suggested,
                suitability_reason=suitability['reasoning'],
                error=f"This problem is better suited for a different tool. {suitability['reasoning']}"
            )

        # Step 1: Validate and parse the problem using DSPy
        problem_info = validate_and_parse_problem(problem_description, additional_info)
        
        # Step 2: Generate Clorm predicates
        predicate_code = generate_clorm_predicates(problem_info['predicates'])
        exec(predicate_code, globals())
        
        # Step 3: Construct the ASP program
        asp_program = generate_asp_program(problem_info)
        
        # Step 4: Solve the optimization problem
        ctrl = Control(unifier=[globals()[pred['name']] for pred in problem_info['predicates']])
        
        # Add facts
        for fact in problem_info['facts']:
            if '(' in fact and ')' in fact:
                predicate_name, *args = fact.split('(')
                args = args[0].rstrip(')').split(',')
                predicate_class = globals()[predicate_name]
                ctrl.add_fact(predicate_class(*args))
        
        ctrl.add_program(asp_program)

        solution = None
        with ctrl.solve(yield_=True) as sh:
            for model in sh:
                solution = model.facts(atoms=True)

        # Build full ASP code for display
        facts_code = "\n".join([f"{fact}." for fact in problem_info['facts']])
        full_asp_code = f"% Facts\n{facts_code}\n\n% Rules and Constraints\n{asp_program}"

        solution_str = str(solution) if solution else "No solution found"

        # Generate visualization
        visualization_html = generate_visualization(problem_description, solution_str)

        return ProblemSolverResult(
            solution=solution_str,
            asp_code=full_asp_code,
            visualization_html=visualization_html
        )
    except ValueError as e:
        # Check if this is a "needs more info" error
        if str(e).startswith("NEEDS_MORE_INFO:"):
            questions_json = str(e)[16:]  # Remove "NEEDS_MORE_INFO:" prefix
            questions = json.loads(questions_json)
            return ProblemSolverResult(needs_more_info=True, questions=questions)
        else:
            return ProblemSolverResult(error=str(e))
    except Exception as e:
        return ProblemSolverResult(error=f"Error solving optimization problem: {str(e)}")