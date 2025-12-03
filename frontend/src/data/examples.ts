import type { ProblemExample } from '@/types'

export const examples: ProblemExample[] = [
  {
    id: 'shift-scheduling',
    name: 'Staff Shift Scheduling',
    category: 'Workforce',
    description: 'Schedule nurses across shifts with complex constraints',
    problem_description: `Schedule nurses for next week at City Hospital's Emergency Department.

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

Create a fair schedule that covers all shifts while respecting preferences and constraints.`,
  },
  {
    id: 'course-timetabling',
    name: 'University Timetabling',
    category: 'Education',
    description: 'Schedule courses avoiding conflicts for students and professors',
    problem_description: `Create a fall semester timetable for the Computer Science department.

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

Find an optimal timetable with no conflicts.`,
  },
  {
    id: 'meal-planning',
    name: 'Weekly Meal Planning',
    category: 'Lifestyle',
    description: 'Plan nutritious meals respecting dietary needs and budget',
    problem_description: `Plan dinners for a family of 4 for the upcoming week.

Family members:
- Dad: no restrictions, prefers hearty meals
- Mom: vegetarian
- Teen (14): picky eater, only likes chicken/pasta/pizza, needs 2500 cal
- Child (8): no spicy food, allergic to nuts

Available recipes:
- Grilled Chicken & Veggies: $15, 600cal, contains meat
- Vegetable Stir Fry: $12, 400cal, vegetarian, mildly spicy
- Pasta Primavera: $10, 550cal, vegetarian, kid-friendly
- Homemade Pizza: $14, 700cal, can be made half-veggie, kid-friendly
- Salmon with Rice: $20, 500cal, contains fish
- Bean Tacos: $8, 450cal, vegetarian, mildly spicy
- Mac and Cheese: $7, 600cal, vegetarian, kid-friendly
- Chicken Parmesan: $16, 650cal, contains meat, kid-friendly
- Veggie Lasagna: $13, 580cal, vegetarian, contains nuts (pesto)
- Grilled Cheese & Soup: $9, 500cal, vegetarian, kid-friendly

Constraints:
- Weekly budget: $90 maximum
- Don't repeat the same meal within the week
- At least 3 vegetarian dinners (for Mom)
- Teen must have chicken or pasta at least 3 times
- No nut-containing dishes (child's allergy)
- No spicy food more than once per week
- Include at least 2 "fancy" meals (salmon, chicken parm, lasagna) for variety

Plan Monday through Sunday dinners.`,
  },
  {
    id: 'wedding-seating',
    name: 'Wedding Seating Chart',
    category: 'Event Planning',
    description: 'Arrange guests at tables considering relationships',
    problem_description: `Create a seating arrangement for Sarah & Tom's wedding reception.

Tables available: 6 round tables, 8 seats each (48 total seats for 42 guests)

Guest groups and relationships:
- Bride's family (8): Parents + grandparents MUST sit together, Aunt Martha and Aunt Rose had a fight (separate tables!)
- Groom's family (7): Parents, 2 siblings with partners, grandma (needs accessible seating near exit)
- College friends (8): Group wants to sit together, Jake and Emma are exes (separate tables)
- Work colleagues (6): Boss should sit near front, interns can sit anywhere
- Couple's mutual friends (6): Everyone gets along
- Extended family (7): Cousin Mike is very loud (not near elderly), Great-uncle Bob needs quiet table

Special requirements:
- Head table (Table 1): Bride, Groom, Best Man, Maid of Honor, and parents (8 seats) - already assigned
- Table 2 must be near the exit (for grandma with mobility issues)
- Table 6 is near the band (loud - good for young people)
- Keep feuding family members at least 2 tables apart
- Couples should sit together
- Try to keep friend groups together when possible
- Balance tables to have 6-8 people each

Create a harmonious seating arrangement that minimizes drama!`,
  },
  {
    id: 'conference-schedule',
    name: 'Tech Conference Schedule',
    category: 'Events',
    description: 'Schedule talks across rooms and time slots',
    problem_description: `Schedule talks for a 1-day AI/ML conference.

Talks submitted (speaker, duration, topic track):
- "GPT-5 Architecture Deep Dive" - Dr. Chen, 45min, LLM track, keynote
- "Practical RAG Systems" - Sarah Miller, 30min, LLM track
- "Computer Vision in Healthcare" - Prof. Patel, 30min, CV track
- "Diffusion Models Explained" - Mike Ross, 45min, CV track
- "MLOps Best Practices" - Lisa Wang, 30min, Engineering track
- "Scaling ML Pipelines" - James Liu, 30min, Engineering track
- "Ethics in AI" - Dr. Johnson, 45min, General track, keynote
- "Real-time Object Detection" - Emma Davis, 30min, CV track
- "Fine-tuning LLMs on Custom Data" - Alex Kim, 30min, LLM track
- "ML Model Monitoring" - Chris Brown, 30min, Engineering track

Rooms: Main Hall (300 capacity), Room A (100), Room B (80)

Time slots: 9:00, 9:45, 10:30, 11:15, 12:00 (lunch), 1:30, 2:15, 3:00, 3:45, 4:30

Constraints:
- Keynotes must be in Main Hall
- No two talks from same track at the same time (attendees want to see full track)
- Dr. Chen must present before 11am (early flight)
- Prof. Patel arrives at 10am (can't present at 9:00 or 9:45)
- 45-minute talks can only start at :00 times (9:00, 10:00, 11:00, 1:30, 3:00)
- Lunch is 12:00-1:30, no talks during this time
- Ethics keynote should be the closing talk (4:30 Main Hall)
- Leave 15-minute gaps between talks in same room for transitions

Create a schedule that maximizes room usage and avoids conflicts.`,
  },
  {
    id: 'team-formation',
    name: 'Startup Team Formation',
    category: 'Business',
    description: 'Form balanced project teams with complementary skills',
    problem_description: `Form 3 product teams from 12 available engineers for a startup.

Engineers and their skills:
- Alice: Frontend (expert), Backend (basic), Leadership (yes)
- Bob: Frontend (intermediate), Mobile (expert)
- Carol: Backend (expert), DevOps (intermediate), Leadership (yes)
- David: Backend (intermediate), ML (expert)
- Eve: Frontend (expert), Design (expert)
- Frank: DevOps (expert), Backend (basic)
- Grace: ML (expert), Backend (intermediate)
- Henry: Mobile (expert), Frontend (intermediate)
- Iris: Design (expert), Frontend (basic)
- Jack: Backend (expert), DevOps (basic), Leadership (yes)
- Kate: ML (intermediate), Backend (intermediate)
- Leo: Mobile (intermediate), DevOps (intermediate)

Team requirements:
- Each team needs exactly 4 engineers
- Each team must have at least one person with Leadership
- Each team needs at least one Frontend expert or intermediate
- Each team needs at least one Backend expert or intermediate
- At least one team needs ML capability for the AI product

Preferences:
- Alice and Bob work great together (prefer same team)
- Carol and Frank had conflicts (prefer different teams)
- Balance expertise levels (don't put all experts on one team)
- Each team should have at least 3 different skill areas covered

Form balanced teams that can each independently deliver a full product.`,
  },
  // === Real-world examples where guaranteed correctness matters ===
  {
    id: 'delivery-routes',
    name: 'Delivery Route Planning',
    category: 'Logistics',
    description: 'Optimize delivery stops with time windows and vehicle capacity',
    problem_description: `Plan today's delivery routes for a small bakery with 2 delivery vans.

Orders to deliver (with delivery time windows):
- Order 1: Downtown Cafe, 10 boxes, must arrive 7:00-8:00 AM
- Order 2: Hotel & Suites, 25 boxes, must arrive 6:30-7:30 AM
- Order 3: Corner Bistro, 8 boxes, must arrive 8:00-9:00 AM
- Order 4: City Hospital cafeteria, 30 boxes, must arrive 6:00-7:00 AM
- Order 5: Tech Campus, 15 boxes, must arrive 7:30-8:30 AM
- Order 6: Airport Lounge, 20 boxes, must arrive 6:00-8:00 AM
- Order 7: Train Station Kiosk, 5 boxes, must arrive 7:00-9:00 AM

Vehicle capacity: 50 boxes each
Bakery opens for loading: 5:30 AM

Travel times between locations (minutes):
- Bakery to Downtown: 15, to Hotel: 20, to Bistro: 10, to Hospital: 25, to Campus: 30, to Airport: 40, to Station: 12
- Downtown to Hotel: 8, to Bistro: 5, to Hospital: 15, to Campus: 20, to Airport: 35, to Station: 7

Create routes that deliver all orders within their time windows using minimum vehicles.

LLMs often miss time window conflicts or exceed capacity. This needs exact constraint checking.`,
  },
  {
    id: 'retail-scheduling',
    name: 'Retail Staff Scheduling',
    category: 'Business',
    description: 'Schedule part-time retail workers with labor law compliance',
    problem_description: `Create next week's schedule for a retail store.

Employees:
- Maria: Available Mon-Fri, max 25 hrs/week (student), trained on register + floor
- Jake: Available any day, max 40 hrs/week, trained on register + stock room + floor
- Emma: Available Tue-Sun, max 30 hrs/week, trained on register + floor, requests Sat morning off
- Tyler: Available Wed-Sun, max 20 hrs/week (student), trained on floor + stock room
- Aisha: Available Mon-Sat, max 35 hrs/week, trained on all positions, team lead

Shifts needed daily:
- Morning (9am-2pm): 2 floor staff + 1 register
- Afternoon (2pm-7pm): 2 floor staff + 1 register + 1 stock room
- Evening (5pm-9pm, weekdays only): 1 floor + 1 register

Labor rules:
- No one works more than 8 hours in a day
- At least 10 hours between shifts
- Team lead (Aisha) must be present during at least one shift per day
- Weekend shifts pay 1.5x (minimize weekend hours for budget)
- Each employee works at least 2 shifts per week (for benefits eligibility)

Create a compliant schedule that minimizes weekend labor costs.`,
  },
  {
    id: 'moving-day',
    name: 'Moving Day Packing',
    category: 'Consumer',
    description: 'Pack household items into moving boxes and truck space',
    problem_description: `Help me pack for my apartment move. I'm renting a 10-foot truck.

Items to move (dimensions in cubic feet, weight in lbs):
- Couch: 40 cu ft, 150 lbs, FRAGILE, must go in last (first out)
- Mattress: 35 cu ft, 80 lbs, can stand on side
- Dresser: 20 cu ft, 120 lbs, has 3 drawers that could hold small items
- Desk: 15 cu ft, 60 lbs, legs removable
- 4 dining chairs: 3 cu ft each, 15 lbs each, stackable
- Dining table: 12 cu ft, 70 lbs, legs removable
- 6 moving boxes (books): 2 cu ft each, 50 lbs each, HEAVY
- 4 moving boxes (clothes): 3 cu ft each, 20 lbs each
- 3 moving boxes (kitchen): 2.5 cu ft each, 35 lbs each, FRAGILE
- TV (55"): 8 cu ft, 40 lbs, FRAGILE, must stay upright
- Bicycle: 10 cu ft, 25 lbs, awkward shape

Truck capacity: 400 cu ft, max 3000 lbs
Rules:
- Heavy items on bottom
- Fragile items protected and accessible
- Maximize space usage
- Items needed first should load last

How should I pack the truck?`,
  },
  {
    id: 'sports-league',
    name: 'Youth Soccer League',
    category: 'Community',
    description: 'Schedule games ensuring fairness and field availability',
    problem_description: `Create an 8-week schedule for our youth soccer league.

Teams: Lightning, Thunder, Rockets, Comets, Wolves, Eagles (6 teams)

Available fields and times (Saturdays only):
- Main Field: 9am, 10:30am, 12pm slots
- Practice Field: 9am, 10:30am slots only (smaller, no lights)

League rules:
- Each team plays every other team once (round-robin)
- Each team plays exactly one game per week
- No team plays at the same time slot more than twice
- Balance home/away for each team (roughly equal)

Special requests:
- Lightning coach requests no 9am games (works early Saturdays)
- Rockets and Comets are siblings - never schedule at same time (parents)
- Eagles have a player with mobility issues - prefer Main Field
- Thunder requested 2 home games in weeks 1-3 (fundraiser)
- Week 5 is holiday weekend - try to use Main Field only (volunteers limited)

Create a fair schedule that accommodates these constraints.`,
  },
  {
    id: 'appointment-booking',
    name: 'Salon Appointment Scheduler',
    category: 'Small Business',
    description: 'Book overlapping appointments across multiple stylists',
    problem_description: `Schedule tomorrow's appointments for a hair salon.

Stylists working tomorrow:
- Anna: 9am-5pm, can do: cuts, color, styling, extensions
- Ben: 10am-6pm, can do: cuts, styling, beard trims
- Carla: 9am-3pm, can do: cuts, color, styling (senior stylist, complex color only)

Services (duration):
- Basic cut: 30 min
- Cut & style: 45 min
- Full color: 90 min
- Highlights: 120 min (needs senior stylist)
- Extensions: 180 min
- Beard trim: 20 min

Appointment requests (in order received):
1. Mrs. Chen: highlights, prefers morning, only available until 1pm
2. Jake: cut & beard, anytime
3. Emma: extensions, needs to finish by 4pm
4. Sofia: full color, prefers Anna, after 11am
5. Mike: basic cut, lunch break only (12-1pm)
6. Twins Ava & Mia: both need cuts, same time slot (different stylists)
7. David: cut & style, first appointment of day requested
8. Nina: full color, anytime
9. Tom: beard trim only, after 3pm

Equipment constraints:
- Only 2 color mixing stations
- Extensions need special chair (only 1)

Schedule all appointments respecting constraints, or identify which can't be accommodated.`,
  },
]
