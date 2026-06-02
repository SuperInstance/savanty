"""DSPy modules for Savanty optimization problem solver."""

import dspy


class ProblemSuitabilityCheck(dspy.Signature):
    """Determine if a problem is suitable for Answer Set Programming (ASP) solving.

    ASP is ideal for:
    - Constraint satisfaction problems (scheduling, timetabling, assignments)
    - Combinatorial optimization (knapsack, bin packing, team formation)
    - Problems with discrete/categorical variables
    - Problems requiring "find all solutions" or "find optimal among valid"
    - Logic puzzles (Sudoku, N-Queens, graph coloring)

    ASP is NOT ideal for:
    - Continuous optimization (use scipy, cvxpy)
    - Statistical/ML problems (use sklearn, pytorch)
    - Simple arithmetic calculations
    - Problems requiring real-time streaming data
    - Numerical simulations
    - Problems with continuous variables and gradients
    """

    problem_description = dspy.InputField(desc="Natural language description of the problem")
    is_suitable = dspy.OutputField(
        desc="'yes' if ASP is the right tool, 'no' if another tool would be better, 'maybe' if unclear"
    )
    problem_type = dspy.OutputField(
        desc="Type of problem: 'constraint_satisfaction', 'combinatorial_optimization', 'continuous_optimization', 'statistical', 'arithmetic', 'simulation', or 'other'"
    )
    reasoning = dspy.OutputField(
        desc="Brief explanation of why this problem is or isn't suitable for ASP"
    )
    suggested_tool = dspy.OutputField(
        desc="If not suitable for ASP, suggest the right tool: 'scipy' for continuous optimization, 'cvxpy' for convex optimization, 'calculator' for simple math, 'pandas' for data analysis, 'none' if ASP is suitable"
    )
    confidence = dspy.OutputField(desc="Confidence level: 'high', 'medium', or 'low'")


class ProblemAnalysis(dspy.Signature):
    """Analyze an optimization problem description and extract structured information."""

    problem_description = dspy.InputField(
        desc="Natural language description of an optimization problem"
    )
    analysis = dspy.OutputField(
        desc="Structured analysis of the problem including domain, variables, constraints, and objective"
    )


class ProblemValidation(dspy.Signature):
    """Validate if a problem description can be converted to a solvable ASP program."""

    problem_description = dspy.InputField(
        desc="Natural language description of an optimization problem"
    )
    is_valid = dspy.OutputField(desc="Boolean indicating if the problem can be solved with ASP")
    reason = dspy.OutputField(
        desc="Explanation of why the problem is or isn't valid for ASP solving"
    )


class GapIdentification(dspy.Signature):
    """Identify gaps and missing information in an optimization problem description."""

    problem_description = dspy.InputField(
        desc="Natural language description of an optimization problem"
    )
    has_gaps = dspy.OutputField(
        desc="Boolean indicating if there are gaps in the problem description"
    )
    gaps = dspy.OutputField(desc="List of specific information gaps in the problem description")
    questions = dspy.OutputField(desc="List of questions to ask the user to fill the gaps")


class ProgramGeneration(dspy.Signature):
    """Generate a complete Answer Set Programming (ASP) encoding from a problem analysis.

    CANONICAL DECISION CONTRACT (mandatory): model every decision as a single relation
    ``assign(Var, Value)`` where each decision variable ``Var`` takes exactly one ``Value``.
    Use a choice rule to generate candidates, e.g. ``1 { assign(V,A); assign(V,B) } 1 :- var(V).``
    Encode every requirement as an integrity constraint (a rule starting with ``:-``).
    The harness appends ``#show assign/2.`` automatically.

    Output STRICT JSON with exactly these keys:
      - "facts":    list of ASP fact strings encoding the problem data (each ends with '.').
      - "rules":    list of ASP rule strings: the choice rule(s) that generate assign/2 AND
                    every integrity constraint (':- ...') that enforces a requirement.
      - "optimize": a single ASP optimization directive string (e.g.
                    "#maximize { W,V,Val : assign(V,Val), objw(V,Val,W) }.") or "" if none.
    Do NOT include '#show'. Use only lowercase constant identifiers for terms.
    """

    analysis = dspy.InputField(desc="Structured analysis of an optimization problem")
    program_components = dspy.OutputField(
        desc='STRICT JSON: {"facts": [...], "rules": [...], "optimize": "..."} using the '
        "assign(Var,Value) contract described above"
    )


class ASPRepair(dspy.Signature):
    """Repair an ASP encoding that failed, using solver-grounded diagnostics.

    You are given the current encoding, the failure type, and targeted feedback derived
    from the clingo solver (e.g. a parse error, or the MINIMAL SET OF CONSTRAINTS that are
    jointly unsatisfiable). Revise the encoding so it solves correctly while still
    faithfully modelling the problem.

    - On 'syntax_error': fix the malformed rule(s) named in the feedback.
    - On 'unsat': the named constraints cannot all hold at once. Decide whether one of them
      MISFORMALIZES the problem (then correct or remove it) or whether the problem is
      genuinely infeasible (then return the encoding unchanged so infeasibility is reported).
    - On 'empty': you did not emit any assign(Var,Value) decision atoms; add the choice rule
      and ensure decisions surface as assign/2.

    Keep the SAME canonical assign(Var,Value) contract and the SAME strict-JSON output
    format as program generation: {"facts": [...], "rules": [...], "optimize": "..."}.
    """

    problem_description = dspy.InputField(desc="The natural-language problem to model")
    current_program_components = dspy.InputField(
        desc='The current encoding as JSON {"facts":[...],"rules":[...],"optimize":"..."}'
    )
    failure_type = dspy.InputField(desc="One of: syntax_error, unsat, empty")
    solver_feedback = dspy.InputField(
        desc="Targeted, solver-grounded diagnostics (parse error or minimal conflicting constraints)"
    )
    repaired_program_components = dspy.OutputField(
        desc='Repaired encoding as STRICT JSON {"facts":[...],"rules":[...],"optimize":"..."}'
    )


class ASPRepairGeneric(dspy.Signature):
    """Repair an ASP encoding given only the raw solver message (Logic-LM-style refinement).

    You are given the current encoding and the solver's raw output/error. Revise the
    encoding so it solves. Keep the same strict-JSON output format as program generation:
    {"facts": [...], "rules": [...], "optimize": "..."}.
    """

    problem_description = dspy.InputField(desc="The natural-language problem to model")
    current_program_components = dspy.InputField(
        desc='The current encoding as JSON {"facts":[...],"rules":[...],"optimize":"..."}'
    )
    solver_feedback = dspy.InputField(desc="The raw solver message / error")
    repaired_program_components = dspy.OutputField(
        desc='Repaired encoding as STRICT JSON {"facts":[...],"rules":[...],"optimize":"..."}'
    )


class ProblemRefinement(dspy.Signature):
    """Refine a problem description with additional information."""

    original_problem = dspy.InputField(desc="Original problem description")
    additional_info = dspy.InputField(desc="Additional information provided by the user")
    refined_problem = dspy.OutputField(
        desc="Refined problem description with additional information incorporated"
    )


class SolutionVisualization(dspy.Signature):
    """Generate an HTML visualization for an optimization solution.

    Create a visually appealing, self-contained HTML snippet that displays the solution
    in an intuitive way. Use appropriate visualizations based on the problem type:
    - Schedules: Use tables/grids with color coding
    - Assignments: Use cards or grouped lists
    - Seating: Use visual table layouts
    - Meal plans: Use calendar-style weekly view
    - Team formation: Use team cards with member details

    The HTML should be self-contained with inline CSS (Tailwind-style classes are fine).
    Use colors meaningfully to distinguish different categories/assignments.
    Make it readable and professional.
    """

    problem_description = dspy.InputField(desc="Original problem description")
    solution = dspy.InputField(desc="The solution output from the ASP solver")
    visualization_html = dspy.OutputField(
        desc="Self-contained HTML snippet visualizing the solution. Use inline styles or simple CSS. Include a title and clear visual representation of the solution."
    )


class InteractiveProblemSolver(dspy.Module):
    """Main module for solving optimization problems using DSPy with interactive gap filling."""

    def __init__(self):
        super().__init__()
        self.analyze = dspy.Predict(ProblemAnalysis)
        self.validate = dspy.Predict(ProblemValidation)
        self.identify_gaps = dspy.Predict(GapIdentification)
        self.generate = dspy.Predict(ProgramGeneration)
        self.refine = dspy.Predict(ProblemRefinement)

    def forward(self, problem_description: str, additional_info: str = None):
        # If we have additional info, refine the problem first
        if additional_info:
            refinement = self.refine(
                original_problem=problem_description, additional_info=additional_info
            )
            problem_description = refinement.refined_problem

        # First validate if the problem makes sense for ASP
        validation = self.validate(problem_description=problem_description)

        if validation.is_valid.lower() != "true":
            # Check if there are gaps we can ask about
            gap_check = self.identify_gaps(problem_description=problem_description)

            if gap_check.has_gaps.lower() == "true":
                # Return the questions to ask the user
                return dspy.Prediction(
                    validation=validation,
                    gap_check=gap_check,
                    needs_more_info=True,
                    questions=gap_check.questions,
                )
            else:
                # Problem is invalid and we can't ask for more info
                raise ValueError(f"Problem cannot be solved with ASP: {validation.reason}")

        # Analyze the problem
        analysis = self.analyze(problem_description=problem_description)

        # Generate program components
        program = self.generate(analysis=analysis.analysis)

        return dspy.Prediction(
            validation=validation, analysis=analysis, program=program, needs_more_info=False
        )
