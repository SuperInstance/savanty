# Team Formation

Build teams with optimal skill coverage, balanced experience, and compatible personalities.

## Basic Example: Startup Teams

### Problem Description

```
Form 3 project teams of 4 people each from 12 candidates.

Candidates and skills:
- Alice: Python, ML, leadership
- Bob: Python, backend, databases
- Carol: JavaScript, React, frontend
- Dave: Python, data science, ML
- Eve: JavaScript, Node.js, backend
- Frank: React, CSS, design
- Grace: databases, DevOps, backend
- Henry: ML, research, Python
- Ivy: frontend, React, design
- Jack: backend, databases, DevOps
- Kate: leadership, project management
- Leo: full-stack, Python, JavaScript

Required skills per team:
- At least 1 person with leadership
- At least 1 person with backend
- At least 1 person with frontend
- ML is a plus but not required

Constraints:
1. Each person on exactly one team
2. Alice and Bob work well together - prefer same team
3. Dave and Henry had conflicts - different teams
4. Balance experience levels across teams
```

### Sample Solution

```
Team 1: Alice (lead), Bob, Carol, Grace
  - Leadership: Alice ✓
  - Backend: Bob, Grace ✓
  - Frontend: Carol ✓

Team 2: Kate (lead), Eve, Frank, Jack
  - Leadership: Kate ✓
  - Backend: Eve, Jack ✓
  - Frontend: Frank ✓

Team 3: Leo (lead), Dave, Ivy, Henry
  - Leadership: Leo (full-stack can lead) ✓
  - Backend: Leo ✓
  - Frontend: Ivy ✓
  - ML bonus: Dave, Henry ✓
```

## Advanced Example: Hackathon Teams

### Problem Description

```
Form balanced teams for a 24-hour hackathon.

Participants (40 people):
- 15 developers (various languages/frameworks)
- 10 designers (UI/UX, graphic design)
- 8 data scientists
- 7 product managers/business roles

Skill levels (1-5):
- Each participant rated on: coding, design, data, business

Preferences:
- Each participant listed 3 people they'd like to work with
- Each participant listed 1 person they'd prefer not to work with

Rules:
1. Teams of 4-5 people
2. Each team needs at least:
   - 1 strong coder (coding >= 4)
   - 1 designer (design >= 3)
   - Combined data skill >= 6
3. No team has more than 2 people from same company
4. Maximize preference satisfaction
5. Balance total skill scores across teams
```

### Optimization Goals

**Hard Constraints:** Skill coverage, team size, company diversity

**Soft Constraints:** Preference satisfaction (maximize)

**Objective:** Balance team strength while maximizing happiness

## Variations

### Sports Team Draft

```
Draft 12 players onto 4 teams of 3 players each.

Players and ratings:
- Player A: offense 85, defense 70, teamwork 80
- Player B: offense 90, defense 60, teamwork 75
... (12 players total)

Draft rules:
1. Snake draft order: Team 1, 2, 3, 4, 4, 3, 2, 1, ...
2. Each team's total ratings should be similar
3. Each team needs at least one player with defense >= 75
4. Rival players (A and C) can't be on same team
```

### Committee Assignment

```
Assign 30 board members to 5 committees.

Committees and requirements:
- Finance: needs 2 accountants, 1 lawyer
- Audit: needs 1 accountant, 2 independents
- Compensation: needs 1 HR expert, 2 executives
- Governance: needs 2 lawyers, 1 compliance expert
- Strategy: needs 3 industry experts

Rules:
1. Each member on 1-2 committees
2. No member on both Finance and Audit (conflict)
3. Chair and Vice-Chair of each committee can't both be new members
4. Balance workload (committee sizes)
```

### Study Groups

```
Form study groups for a class of 24 students.

Groups of 4 students each.

Student attributes:
- GPA (indicator of academic strength)
- Preferred study times (morning, afternoon, evening)
- Location (on-campus, off-campus)

Goals:
1. Mix high and low GPA students (peer learning)
2. Group members have overlapping free times
3. At least 2 on-campus students per group (meeting space)
4. Consider past collaboration history
```

## Tips

1. **Define required vs. nice-to-have skills**
2. **Specify team size constraints** - exact, min, max
3. **List compatibility/incompatibility** clearly
4. **Quantify skills** when possible (ratings, years of experience)
5. **State the optimization goal** - balanced teams, max satisfaction, etc.
