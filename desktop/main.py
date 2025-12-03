#!/usr/bin/env python3
"""
Savanty Desktop Application
AI Planning Agent using Slint UI
"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Check for slint dependency and provide helpful error
try:
    import slint
except ImportError:
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  Savanty Desktop requires the 'slint' package                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Install with:                                                   ║
║    pip install savanty[desktop]                                  ║
║                                                                  ║
║  Or run directly with uvx:                                       ║
║    uvx --from 'savanty[desktop]' savanty-desktop                 ║
║                                                                  ║
║  Or with uv:                                                     ║
║    uv tool install 'savanty[desktop]'                            ║
║    savanty-desktop                                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    sys.exit(1)

# Add parent directory to path for savanty imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from savanty.solver import solve_optimization_problem

# Example problems
EXAMPLES = [
    {
        "name": "Staff Shift Scheduling",
        "category": "Workforce",
        "description": "Schedule nurses across shifts with complex constraints",
        "problem": """Schedule nurses for next week at City Hospital's Emergency Department.

Staff:
- Sarah (senior, prefers day shifts, cannot work Wed)
- Mike (senior, any shift, must have 2 days off)
- Emma (junior, needs supervision, prefers nights)
- James (junior, any shift, cannot work weekends)
- Lisa (senior, nights only, max 4 shifts/week)

Requirements:
- Each shift needs at least 1 senior nurse
- Night shifts need minimum 2 nurses
- Day shifts need minimum 3 nurses
- No nurse works more than 5 shifts per week
- No nurse works more than 2 night shifts in a row
- Junior nurses must work with at least one senior

Shifts: Day (7am-3pm), Evening (3pm-11pm), Night (11pm-7am)
Days: Monday through Sunday

Create a fair schedule that covers all shifts while respecting preferences and constraints.""",
    },
    {
        "name": "University Timetabling",
        "category": "Education",
        "description": "Schedule courses avoiding conflicts",
        "problem": """Create a fall semester timetable for the Computer Science department.

Courses to schedule:
- CS101 Intro to Programming (Prof. Smith, 120 students, needs computer lab)
- CS201 Data Structures (Prof. Smith, 80 students, regular room)
- CS301 Algorithms (Prof. Johnson, 45 students, regular room)
- CS350 Databases (Prof. Lee, 60 students, needs computer lab)
- CS401 Machine Learning (Prof. Johnson, 35 students, needs computer lab)
- CS450 Security (Prof. Lee, 40 students, regular room)

Rooms available:
- Room A: capacity 150, regular classroom
- Room B: capacity 100, computer lab
- Room C: capacity 50, regular classroom
- Room D: capacity 60, computer lab

Time slots: 9am, 11am, 2pm, 4pm (Mon/Wed or Tue/Thu)

Constraints:
- No professor teaches two courses at the same time
- CS201 requires CS101 as prerequisite (many students take both - avoid conflicts)
- CS301 and CS350 share many students - don't schedule at same time
- Prof. Johnson is unavailable Tuesday mornings
- Computer lab courses must be in rooms B or D
- Room capacity must accommodate enrolled students

Find an optimal timetable with no conflicts.""",
    },
    {
        "name": "Weekly Meal Planning",
        "category": "Lifestyle",
        "description": "Plan nutritious meals respecting dietary needs",
        "problem": """Plan dinners for a family of 4 for the upcoming week.

Family members:
- Dad: no restrictions, prefers hearty meals
- Mom: vegetarian
- Teen (14): picky eater, only likes chicken/pasta/pizza
- Child (8): no spicy food, allergic to nuts

Available recipes:
- Grilled Chicken & Veggies: $15, contains meat
- Vegetable Stir Fry: $12, vegetarian, mildly spicy
- Pasta Primavera: $10, vegetarian, kid-friendly
- Homemade Pizza: $14, can be made half-veggie, kid-friendly
- Salmon with Rice: $20, contains fish
- Mac and Cheese: $7, vegetarian, kid-friendly
- Chicken Parmesan: $16, contains meat, kid-friendly
- Grilled Cheese & Soup: $9, vegetarian, kid-friendly

Constraints:
- Weekly budget: $90 maximum
- Don't repeat the same meal within the week
- At least 3 vegetarian dinners (for Mom)
- Teen must have chicken or pasta at least 3 times
- No nut-containing dishes (child's allergy)

Plan Monday through Sunday dinners.""",
    },
    {
        "name": "Wedding Seating Chart",
        "category": "Event Planning",
        "description": "Arrange guests at tables considering relationships",
        "problem": """Create a seating arrangement for a wedding reception.

Tables: 6 round tables, 8 seats each (48 total seats for 42 guests)

Guest groups:
- Bride's family (8): Parents + grandparents MUST sit together
- Groom's family (7): Parents, siblings, grandma (needs accessible seating)
- College friends (8): Jake and Emma are exes (separate tables)
- Work colleagues (6): Boss should sit near front
- Mutual friends (6): Everyone gets along
- Extended family (7): Cousin Mike is loud (not near elderly)

Special requirements:
- Head table (Table 1): Bride, Groom, Best Man, Maid of Honor, parents
- Table 2 must be near exit (for grandma with mobility issues)
- Keep feuding family members at least 2 tables apart
- Couples should sit together
- Balance tables to have 6-8 people each

Create a harmonious seating arrangement!""",
    },
    {
        "name": "Tech Conference Schedule",
        "category": "Events",
        "description": "Schedule talks across rooms and time slots",
        "problem": """Schedule talks for a 1-day AI/ML conference.

Talks (speaker, duration, track):
- "GPT-5 Architecture" - Dr. Chen, 45min, LLM track, keynote
- "Practical RAG Systems" - Sarah Miller, 30min, LLM track
- "Computer Vision in Healthcare" - Prof. Patel, 30min, CV track
- "Diffusion Models" - Mike Ross, 45min, CV track
- "MLOps Best Practices" - Lisa Wang, 30min, Engineering
- "Scaling ML Pipelines" - James Liu, 30min, Engineering
- "Ethics in AI" - Dr. Johnson, 45min, keynote

Rooms: Main Hall (300), Room A (100), Room B (80)
Time slots: 9:00, 10:00, 11:00, 1:30, 2:30, 3:30, 4:30

Constraints:
- Keynotes in Main Hall
- No two talks from same track at same time
- Dr. Chen must present before 11am
- Ethics keynote should close the conference
- 15-minute gaps between talks in same room

Create a schedule that maximizes attendance.""",
    },
    {
        "name": "Startup Team Formation",
        "category": "Business",
        "description": "Form balanced teams with complementary skills",
        "problem": """Form 3 product teams from 12 engineers.

Engineers and skills:
- Alice: Frontend (expert), Leadership (yes)
- Bob: Frontend (intermediate), Mobile (expert)
- Carol: Backend (expert), Leadership (yes)
- David: Backend (intermediate), ML (expert)
- Eve: Frontend (expert), Design (expert)
- Frank: DevOps (expert)
- Grace: ML (expert), Backend (intermediate)
- Henry: Mobile (expert), Frontend (intermediate)
- Iris: Design (expert)
- Jack: Backend (expert), Leadership (yes)
- Kate: ML (intermediate), Backend (intermediate)
- Leo: Mobile (intermediate), DevOps (intermediate)

Requirements:
- Each team: exactly 4 engineers
- Each team must have Leadership capability
- Each team needs Frontend + Backend
- At least one team needs ML for AI product

Preferences:
- Alice and Bob work well together
- Carol and Frank had conflicts (different teams)
- Balance expertise across teams

Form balanced, capable teams.""",
    },
]


@dataclass
class AppState:
    """Application state"""
    problem_text: str = ""
    additional_info: str = ""
    is_loading: bool = False


class SavantyApp:
    """Main application class"""

    def __init__(self):
        # Load the Slint component
        ui_path = Path(__file__).parent / "ui" / "app.slint"
        components = slint.load_file(str(ui_path))
        self.window = components.AppWindow()

        # Set up callbacks
        self.window.solve = self.on_solve
        self.window.reset = self.on_reset
        self.window.submit_info = self.on_submit_info
        self.window.select_example = self.on_select_example

        # Store state
        self._current_problem = ""
        self._additional_info = ""

    def on_select_example(self, index):
        """Handle example selection"""
        index = int(index)  # Slint passes numbers as floats
        if 0 <= index < len(EXAMPLES):
            example = EXAMPLES[index]
            # Use the function to update TextEdit (workaround for Slint binding issue)
            self.window.set_problem_text(example["problem"])
            self._current_problem = example["problem"]
            # Clear previous results
            self.window.has_solution = False
            self.window.needs_info = False
            self.window.not_suitable = False
            self.window.error_message = ""
            self.window.questions = slint.ListModel([])

    def on_reset(self):
        """Reset the application state"""
        self.window.set_problem_text("")  # Use function for TextEdit
        self.window.solution_text = ""
        self.window.asp_code = ""
        self.window.visualization_html = ""
        self.window.questions = slint.ListModel([])
        self.window.error_message = ""
        self.window.is_loading = False
        self.window.needs_info = False
        self.window.has_solution = False
        self.window.not_suitable = False
        self.window.suggested_tool = ""
        self.window.suitability_reason = ""
        self.window.additional_info = ""
        self.window.selected_tab = 0
        self._current_problem = ""
        self._additional_info = ""

    def on_submit_info(self, info: str):
        """Handle submission of additional info"""
        self._additional_info = info
        self.window.additional_info = ""
        self._do_solve()

    def on_solve(self):
        """Handle solve button click"""
        self._current_problem = self.window.problem_text
        self._additional_info = ""
        self._do_solve()

    def _do_solve(self):
        """Execute the solver"""
        self.window.is_loading = True
        self.window.has_solution = False
        self.window.needs_info = False
        self.window.not_suitable = False
        self.window.error_message = ""

        try:
            # Call the solver
            result = solve_optimization_problem(
                self._current_problem,
                additional_info=self._additional_info if self._additional_info else None
            )

            if result.not_suitable:
                self.window.not_suitable = True
                self.window.suggested_tool = result.suggested_tool or ""
                self.window.suitability_reason = result.suitability_reason or ""
            elif result.needs_more_info:
                self.window.needs_info = True
                self.window.questions = slint.ListModel(result.questions or [])
            elif result.error:
                self.window.error_message = result.error
            else:
                self.window.has_solution = True
                self.window.solution_text = result.solution or ""
                self.window.asp_code = result.asp_code or ""
                self.window.visualization_html = result.visualization_html or ""
                self.window.selected_tab = 0

        except Exception as e:
            self.window.error_message = f"Error: {str(e)}"
        finally:
            self.window.is_loading = False

    def run(self):
        """Run the application"""
        self.window.run()


def main():
    """Entry point"""
    app = SavantyApp()
    app.run()


if __name__ == "__main__":
    main()
