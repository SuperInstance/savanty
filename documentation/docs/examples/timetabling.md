# Timetabling

Create schedules for courses, exams, or events with room assignments, instructor availability, and conflict avoidance.

## Basic Example: University Courses

### Problem Description

```
Schedule 6 courses across 5 days with 4 time slots per day.

Courses:
- CS101 (Intro Programming): 3 sessions/week, Prof. Alice
- CS201 (Data Structures): 2 sessions/week, Prof. Bob
- CS301 (Algorithms): 2 sessions/week, Prof. Alice
- MATH101 (Calculus): 3 sessions/week, Prof. Carol
- MATH201 (Linear Algebra): 2 sessions/week, Prof. Carol
- PHYS101 (Physics): 3 sessions/week, Prof. Dave

Rooms:
- Room A: capacity 50, has projector
- Room B: capacity 30, has computers
- Room C: capacity 100, lecture hall

Constraints:
1. CS courses need computers (Room B)
2. Prof. Alice unavailable Monday mornings
3. Prof. Carol unavailable Fridays
4. Students taking CS101 often take MATH101 - avoid conflicts
5. Each professor teaches max 2 consecutive slots
```

### Sample Solution

| Time | Monday | Tuesday | Wednesday | Thursday | Friday |
|------|--------|---------|-----------|----------|--------|
| 9am  | MATH101 (C) | CS101 (B) | MATH101 (C) | CS101 (B) | CS201 (B) |
| 11am | CS201 (B) | MATH201 (A) | CS301 (B) | MATH201 (A) | PHYS101 (C) |
| 2pm  | PHYS101 (C) | CS301 (B) | PHYS101 (C) | MATH101 (C) | - |
| 4pm  | CS101 (B) | - | - | - | - |

## Advanced Example: Exam Scheduling

### Problem Description

```
Schedule final exams for 20 courses over 5 days.

Constraints:
1. Each exam is 3 hours
2. Time slots: 9am-12pm, 2pm-5pm (2 per day)
3. Available rooms: 5 exam halls (capacity 100-300)

Rules:
1. No student has 2 exams at the same time
2. No student has more than 2 exams in one day
3. Large courses (>200 students) need Hall A or B
4. Courses with shared students should have at least 1 day gap
5. Core courses (CS101, MATH101, PHYS101) spread across different days

Student enrollment data provided showing course overlaps.
```

### Conflict Detection

Savanty analyzes enrollment to find:

- **Direct conflicts:** Same student in both courses
- **Load conflicts:** Too many exams in one day for a student
- **Spread requirements:** Related courses need gaps

## Variations

### Conference Scheduling

```
Schedule 30 talks across 3 days at a tech conference.

Tracks:
- Track A (Main Hall): keynotes and popular talks
- Track B (Room 1): technical deep-dives
- Track C (Room 2): workshops

Time: 9am-5pm, 1-hour slots with 15-min breaks

Constraints:
1. Keynotes at 9am in Track A
2. Speaker X has 2 talks - at least 3 hours apart
3. Workshop Y needs 2 consecutive slots
4. "Intro to X" before "Advanced X" on same or earlier day
5. Attendee interest data - minimize schedule conflicts
```

### School Timetable

```
Create weekly timetable for a middle school.

Classes: 6A, 6B, 7A, 7B, 8A, 8B
Subjects: Math, English, Science, History, Art, PE
Teachers: 10 teachers with subject specialties

Period: 8 periods per day, 5 days

Rules:
1. Each class has each subject 4-5 times per week
2. PE and Art only in periods 5-8 (after lunch)
3. No teacher has more than 5 consecutive periods
4. Class can't have same subject twice in one day
5. Science needs lab (only 2 labs available)
```

### Meeting Scheduler

```
Schedule 15 recurring weekly meetings for a company.

Meeting rooms: 4 rooms with different capacities/equipment

Meetings and requirements:
- Team standup (daily, 15 min, needs any room)
- Sprint planning (weekly, 2 hours, needs large room)
- 1:1s (weekly, 30 min each, 8 different pairs)
- All-hands (weekly, 1 hour, needs largest room)
- Board call (weekly, 1 hour, needs video conferencing)

Constraints:
1. No room double-booked
2. Key people's conflicts: CEO has external calls Mon/Wed 2-4pm
3. Standup before other meetings each day
4. Buffer time between meetings for room transitions
```

## Tips

1. **Specify time granularity** - hours, 30-min slots, etc.
2. **List all resources** - rooms, equipment, instructors
3. **Provide conflict data** - who can't overlap with whom
4. **Define hard vs. soft constraints**
5. **Include prerequisites** - what must come before what
