# Event Seating

Arrange guests at tables for weddings, conferences, or dinners while respecting relationship constraints and preferences.

## Basic Example: Wedding Reception

### Problem Description

```
Arrange seating for a wedding reception with 8 tables of 8 seats each.

Guests (64 total):
- Bride's family: Alice, Bob, Carol, Dave, Eve, Frank (6 people)
- Groom's family: Grace, Henry, Ivy, Jack, Kate, Leo, Mary (7 people)
- Bride's friends: Nancy, Oscar, Paula, Quinn (4 people)
- Groom's friends: Rachel, Sam, Tom, Uma, Victor (5 people)
- Work colleagues: Will, Xena, Yuki, Zach, and 38 others

Constraints:
1. Bride's parents (Alice, Bob) sit at Table 1 with Groom's parents (Grace, Henry)
2. Carol and Dave are divorced - cannot sit at same table
3. Eve and Frank are dating - prefer same table
4. Bride's friends should sit together
5. No table should have only one person from a group
6. Wheelchair user (Will) needs accessible table (Table 1 or 8)
```

### What Savanty Does

1. **Groups** guests by their relationships and categories
2. **Encodes** must-separate and prefer-together constraints
3. **Assigns** each guest to exactly one seat
4. **Balances** groups across tables while respecting constraints

### Sample Solution

```
Table 1 (Head Table):
  Alice, Bob, Grace, Henry, [Bride], [Groom], Will, Xena

Table 2:
  Carol, Eve, Frank, Nancy, Oscar, Paula, Quinn, Yuki

Table 3:
  Dave, Rachel, Sam, Tom, Uma, Victor, [Guest], [Guest]
...
```

## Advanced Example: Corporate Conference

### Problem Description

```
Seat 120 attendees at a corporate conference dinner.

Round tables: 15 tables with 8 seats each

Attendee categories:
- Executives (12 people): spread across tables for networking
- Sales team (30 people): mix with other departments
- Engineering (40 people): can sit together
- Marketing (25 people): should network with Sales
- Support (13 people): no special requirements

Special constraints:
1. No more than 2 executives per table
2. Each table should have at least 2 different departments
3. CEO (exec) and CTO (exec) should not sit together (they talk all day)
4. New hires (tagged) should sit with at least one mentor (tagged)
5. Vegetarian meals at tables 1-5 only - seat vegetarians there
6. Speaker table (Table 1) reserved for keynote speakers
```

### Key Features

**Diversity:** Mix departments for networking

**Limits:** Cap executives per table

**Dietary:** Match guests to meal-compatible tables

**Special Roles:** Speakers, mentors, new hires

## Variations

### Classroom Seating

```
Arrange 30 students in a classroom with 5 rows of 6 desks.

Constraints:
1. Talking pairs (Alice-Bob, Carol-Dave) must be separated by at least 2 seats
2. Students needing visual aids sit in rows 1-2
3. Left-handed students (Eve, Frank) need left-side seats
4. Study partners can sit adjacent for group work
```

### Theater/Auditorium

```
Assign 200 guests to a theater with:
- 10 rows, 20 seats per row
- VIP section: rows 1-3 (60 seats)
- Standard section: rows 4-10 (140 seats)

Rules:
1. Groups (families) sit together in consecutive seats
2. VIP ticket holders in VIP section only
3. Wheelchair spaces at aisle ends
4. Keep aisles (seats 10-11) clear
```

### Dinner Party (Small Scale)

```
Seat 12 guests at a rectangular dinner table.

Seats: 6 on each long side, heads reserved for hosts

Guests:
- Hosts: Michael and Sarah (at heads)
- Couples: (A,B), (C,D), (E,F)
- Singles: G, H, I, J

Rules:
1. Couples sit across from or next to each other
2. Alternate genders along each side
3. G and H had an argument - not adjacent
4. I speaks only Japanese - sit near Sarah (translator)
```

## Tips

1. **Define table shapes** - round, rectangular, U-shaped
2. **Specify seat positions** if adjacency matters
3. **Categorize constraints:**
   - Must: hard requirements
   - Should: preferences (soft)
   - Must not: separations
4. **Handle special needs** - accessibility, dietary, roles
