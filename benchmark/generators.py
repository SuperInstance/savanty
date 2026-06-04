"""Parametric generators for the Savanty constraint-reasoning benchmark.

Each generator emits problem ``spec`` dicts that pair a faithful natural-language
description with a machine-checkable specification (over the canonical ``assign/2``
relation).  Three variants stress different failure modes:

- ``feasible``  : clearly worded and solvable (the common case).
- ``infeasible``: clearly worded but over-constrained -> correct behaviour is to report
                  UNSAT (probes *false-feasible* hallucination + repair restraint).
- ``tight``     : solvable but numerically tight (capacity == demand, k == chromatic
                  number) -> probes *spurious-UNSAT* from over-formalisation.

Descriptions state every constraint in the spec, so a model is never penalised for
information it was not given; under-constraint failures arise naturally when a model
*omits* a stated constraint and are caught by the oracle.

Generation is deterministic (fixed structures, no RNG) so the dataset is reproducible.
Feasibility / optimum labels are filled in by ``benchmark.reference.ground_truth``.
"""

from __future__ import annotations


def _spec(id, domain, size, variant, nl, variables, domains, constraints, objective=None):
    return {
        "id": id,
        "domain": domain,
        "size": size,
        "variant": variant,
        "nl_description": nl.strip(),
        "variables": variables,
        "domains": domains,
        "constraints": constraints,
        "objective": objective,
    }


# --- graph colouring ----------------------------------------------------------------


def _coloring(id, variant, n, edges, k, nl_extra=""):
    nodes = [f"n{i}" for i in range(1, n + 1)]
    colors = [f"c{i}" for i in range(1, k + 1)]
    cons = [{"type": "not_equal", "a": f"n{a}", "b": f"n{b}"} for a, b in edges]
    edge_txt = ", ".join(f"({a},{b})" for a, b in edges)
    nl = f"""
We must colour {n} regions, numbered n1..n{n}, using at most {k} colours (c1..c{k}).
Two regions that share a border must get different colours.
Bordering pairs (by region number): {edge_txt}.
Assign exactly one colour to each region. {nl_extra}
"""
    return _spec(id, "graph_coloring", n, variant, nl, nodes,
                 dict.fromkeys(nodes, colors), cons)


def graph_coloring_instances():
    out = []
    # Feasible: paths and even cycles (2-colourable), given 3 colours -> easy.
    out.append(_coloring("color_path5_k3", "feasible", 5,
                         [(1, 2), (2, 3), (3, 4), (4, 5)], 3))
    out.append(_coloring("color_cycle6_k3", "feasible", 6,
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)], 3))
    out.append(_coloring("color_star7_k3", "feasible", 7,
                         [(1, i) for i in range(2, 8)], 3))
    # Tight: odd cycle needs exactly 3 colours; clique K3 needs exactly 3.
    out.append(_coloring("color_cycle5_k3_tight", "tight", 5,
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)], 3))
    out.append(_coloring("color_k4_k4_tight", "tight", 4,
                         [(a, b) for a in range(1, 5) for b in range(a + 1, 5)], 4))
    # Infeasible: clique K4 with only 3 colours; odd cycle with 2 colours.
    out.append(_coloring("color_k4_k3_infeasible", "infeasible", 4,
                         [(a, b) for a in range(1, 5) for b in range(a + 1, 5)], 3))
    out.append(_coloring("color_cycle5_k2_infeasible", "infeasible", 5,
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)], 2))
    # Larger / more discriminating instances.
    k5 = [(a, b) for a in range(1, 6) for b in range(a + 1, 6)]
    out.append(_coloring("color_cycle8_k3", "feasible", 8,
                         [(i, i % 8 + 1) for i in range(1, 9)], 3))
    out.append(_coloring("color_k5_k5_tight", "tight", 5, k5, 5))
    out.append(_coloring("color_k5_k4_infeasible", "infeasible", 5, k5, 4))
    # Wheel W5 (5-cycle + hub n6): chromatic number 4.
    wheel = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)] + [(6, i) for i in range(1, 6)]
    out.append(_coloring("color_wheel5_k4_tight", "tight", 6, wheel, 4))
    out.append(_coloring("color_wheel5_k3_infeasible", "infeasible", 6, wheel, 3))
    return out


# --- knapsack (optimisation) --------------------------------------------------------


def _knapsack(id, variant, weights, values, cap):
    items = [f"item{i}" for i in range(1, len(weights) + 1)]
    w = {it: weights[i] for i, it in enumerate(items)}
    v = {it: values[i] for i, it in enumerate(items)}
    lines = "; ".join(f"{it} (weight {w[it]}, value {v[it]})" for it in items)
    nl = f"""
A knapsack holds at most {cap} units of weight. Choose a subset of the following items
to put 'in' the knapsack (the rest stay 'out') so the total weight is within {cap} and
the total value is as large as possible.
Items: {lines}.
For each item decide 'in' or 'out'.
"""
    return _spec(
        id, "knapsack", len(weights), variant, nl, items,
        {it: ["in", "out"] for it in items},
        [{"type": "weighted_capacity", "weights": w, "selected_value": "in", "bound": cap}],
        {"sense": "max", "weights": {it: {"in": v[it], "out": 0} for it in items}},
    )


def knapsack_instances():
    out = []
    out.append(_knapsack("knap4_c10", "feasible", [5, 4, 6, 2], [10, 7, 12, 3], 10))
    out.append(_knapsack("knap5_c14", "feasible", [3, 5, 7, 2, 4], [4, 6, 9, 2, 5], 14))
    out.append(_knapsack("knap6_c20", "feasible", [6, 8, 3, 9, 5, 4],
                         [10, 13, 4, 14, 7, 6], 20))
    # Tight: capacity equals the weight of the best single feasible packing.
    out.append(_knapsack("knap5_c8_tight", "tight", [3, 5, 7, 2, 4], [4, 6, 9, 2, 5], 8))
    out.append(_knapsack("knap6_c12_tight", "tight", [6, 8, 3, 9, 5, 4],
                         [10, 13, 4, 14, 7, 6], 12))
    out.append(_knapsack("knap7_c25", "feasible", [7, 3, 9, 5, 6, 2, 8],
                         [12, 5, 15, 8, 10, 3, 13], 25))
    out.append(_knapsack("knap8_c30", "feasible", [7, 3, 9, 5, 6, 2, 8, 4],
                         [12, 5, 15, 8, 10, 3, 13, 6], 30))
    out.append(_knapsack("knap4_c6_tight", "tight", [5, 4, 6, 2], [10, 7, 12, 3], 6))
    out.append(_knapsack("knap7_c14_tight", "tight", [7, 3, 9, 5, 6, 2, 8],
                         [12, 5, 15, 8, 10, 3, 13], 14))
    return out


# --- team assignment (people -> teams, capacities, separations) ---------------------


def _assignment(id, variant, n_people, teams, cap, separations, forbidden=None):
    people = [f"p{i}" for i in range(1, n_people + 1)]
    cons = []
    for t in teams:
        cons.append({"type": "capacity", "value": t, "max": cap})
    for a, b in separations:
        cons.append({"type": "not_equal", "a": f"p{a}", "b": f"p{b}"})
    for var, val in (forbidden or []):
        cons.append({"type": "forbidden", "var": f"p{var}", "value": val})
    sep_txt = ", ".join(f"(p{a},p{b})" for a, b in separations) or "none"
    forb_txt = ", ".join(f"p{var}!={val}" for var, val in (forbidden or [])) or "none"
    nl = f"""
Assign {n_people} people (p1..p{n_people}) to the teams {teams}. Each team can hold at
most {cap} people. The following pairs must NOT be on the same team: {sep_txt}.
Forbidden person/team placements: {forb_txt}. Give each person exactly one team.
"""
    return _spec(id, "team_assignment", n_people, variant, nl, people,
                 {p: list(teams) for p in people}, cons)


def assignment_instances():
    out = []
    out.append(_assignment("team6_2x3", "feasible", 6, ["alpha", "beta"], 3,
                           [(1, 2)], [(3, "beta")]))
    out.append(_assignment("team9_3x3", "feasible", 9, ["alpha", "beta", "gamma"], 3,
                           [(1, 2), (3, 4)]))
    out.append(_assignment("team8_2x4_tight", "tight", 8, ["alpha", "beta"], 4,
                           [(1, 2), (3, 4), (5, 6)]))
    # Infeasible: 7 people, 2 teams, cap 3 -> capacity 6 < 7.
    out.append(_assignment("team7_2x3_infeasible", "infeasible", 7, ["alpha", "beta"], 3,
                           []))
    out.append(_assignment("team10_2x5", "feasible", 10, ["alpha", "beta"], 5,
                           [(1, 2), (3, 4)]))
    out.append(_assignment("team12_3x4", "feasible", 12, ["alpha", "beta", "gamma"], 4,
                           [(1, 2), (3, 4), (5, 6)]))
    out.append(_assignment("team6_2x3_tight", "tight", 6, ["alpha", "beta"], 3,
                           [(1, 2), (3, 4)]))
    # Infeasible: 10 people, 3 teams, cap 3 -> capacity 9 < 10.
    out.append(_assignment("team10_3x3_infeasible", "infeasible", 10,
                           ["alpha", "beta", "gamma"], 3, []))
    # Infeasible: 3 mutually-separated people but only 2 teams.
    out.append(_assignment("team8_2x4_sep_infeasible", "infeasible", 8, ["alpha", "beta"], 4,
                           [(1, 2), (1, 3), (2, 3)]))
    return out


# --- seating (guests -> tables, capacities, must/cannot sit together) ---------------


def _seating(id, variant, n_guests, tables, cap, together, apart):
    guests = [f"g{i}" for i in range(1, n_guests + 1)]
    cons = []
    for t in tables:
        cons.append({"type": "capacity", "value": t, "max": cap})
    for a, b in together:
        cons.append({"type": "equal", "a": f"g{a}", "b": f"g{b}"})
    for a, b in apart:
        cons.append({"type": "not_equal", "a": f"g{a}", "b": f"g{b}"})
    tog = ", ".join(f"(g{a},g{b})" for a, b in together) or "none"
    apt = ", ".join(f"(g{a},g{b})" for a, b in apart) or "none"
    nl = f"""
Seat {n_guests} guests (g1..g{n_guests}) at tables {tables}, each seating at most {cap}.
These pairs must sit at the SAME table: {tog}. These pairs must sit at DIFFERENT
tables: {apt}. Assign every guest to exactly one table.
"""
    return _spec(id, "seating", n_guests, variant, nl, guests,
                 {g: list(tables) for g in guests}, cons)


def seating_instances():
    out = []
    out.append(_seating("seat8_2x4", "feasible", 8, ["t1", "t2"], 4,
                        [(1, 2)], [(3, 4)]))
    out.append(_seating("seat9_3x3", "feasible", 9, ["t1", "t2", "t3"], 3,
                        [(1, 2), (4, 5)], [(1, 3)]))
    out.append(_seating("seat6_2x3_tight", "tight", 6, ["t1", "t2"], 3,
                        [(1, 2), (3, 4)], [(1, 5)]))
    # Infeasible: 3 guests must be mutually apart but only 2 tables.
    out.append(_seating("seat5_2x4_infeasible", "infeasible", 5, ["t1", "t2"], 4,
                        [], [(1, 2), (2, 3), (1, 3)]))
    out.append(_seating("seat12_3x4", "feasible", 12, ["t1", "t2", "t3"], 4,
                        [(1, 2), (3, 4)], [(1, 5)]))
    out.append(_seating("seat10_2x5_tight", "tight", 10, ["t1", "t2"], 5,
                        [(1, 2), (3, 4)], [(1, 5)]))
    # Infeasible: 7 guests, 2 tables, cap 3 -> 6 < 7.
    out.append(_seating("seat7_2x3_infeasible", "infeasible", 7, ["t1", "t2"], 3, [], []))
    return out


# --- timetabling (courses -> slots; shared-resource courses need distinct slots) ----


def _timetable(id, variant, n_courses, slots, conflicts, forbidden=None):
    courses = [f"course{i}" for i in range(1, n_courses + 1)]
    cons = [{"type": "not_equal", "a": f"course{a}", "b": f"course{b}"} for a, b in conflicts]
    for var, val in (forbidden or []):
        cons.append({"type": "forbidden", "var": f"course{var}", "value": val})
    conf = ", ".join(f"(course{a},course{b})" for a, b in conflicts) or "none"
    forb = ", ".join(f"course{var}!={val}" for var, val in (forbidden or [])) or "none"
    nl = f"""
Schedule {n_courses} courses (course1..course{n_courses}) into time slots {slots}.
Courses that share students or a room cannot be in the same slot. Conflicting pairs:
{conf}. Forbidden course/slot placements: {forb}. Give each course exactly one slot.
"""
    return _spec(id, "timetabling", n_courses, variant, nl, courses,
                 {c: list(slots) for c in courses}, cons)


def timetable_instances():
    out = []
    out.append(_timetable("tt5_3slot", "feasible", 5, ["mon", "tue", "wed"],
                         [(1, 2), (2, 3), (4, 5)]))
    out.append(_timetable("tt6_4slot", "feasible", 6, ["s1", "s2", "s3", "s4"],
                         [(1, 2), (2, 3), (3, 4), (5, 6)], [(1, "s4")]))
    out.append(_timetable("tt4_3slot_tight", "tight", 4, ["s1", "s2", "s3"],
                         [(1, 2), (1, 3), (2, 3), (2, 4)]))
    # Infeasible: K4 conflict among 4 courses but only 3 slots.
    out.append(_timetable("tt4_3slot_infeasible", "infeasible", 4, ["s1", "s2", "s3"],
                         [(a, b) for a in range(1, 5) for b in range(a + 1, 5)]))
    k4 = [(a, b) for a in range(1, 5) for b in range(a + 1, 5)]
    out.append(_timetable("tt7_4slot", "feasible", 7, ["s1", "s2", "s3", "s4"],
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]))
    out.append(_timetable("tt5_3slot_tight", "tight", 5, ["s1", "s2", "s3"],
                         [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]))
    # Infeasible: K4 among courses 1-4 but only 3 slots (with an extra course).
    out.append(_timetable("tt5_3slot_infeasible", "infeasible", 5, ["s1", "s2", "s3"],
                         k4 + [(4, 5)]))
    return out


# --- scheduling-lite (workers -> shift per day; coverage + rest) --------------------


def _schedule(id, variant, workers, days, min_on, max_on):
    # var = w{worker}_d{day}; values = on/off; >= min_on workers ON each day,
    # each worker ON at most max_on days.
    variables, domains, cons = [], {}, []
    for d in range(1, days + 1):
        scope = []
        for w in range(1, workers + 1):
            var = f"w{w}_d{d}"
            variables.append(var)
            domains[var] = ["on", "off"]
            scope.append(var)
        cons.append({"type": "min_count", "value": "on", "min": min_on, "vars": scope})
    for w in range(1, workers + 1):
        scope = [f"w{w}_d{d}" for d in range(1, days + 1)]
        cons.append({"type": "capacity", "value": "on", "max": max_on, "vars": scope})
    nl = f"""
Build a {days}-day duty roster for {workers} workers (w1..w{workers}). For each worker
and each day decide 'on' or 'off' (variable w<worker>_d<day>). At least {min_on} workers
must be 'on' each day. No worker may work more than {max_on} days in total.
"""
    return _spec(id, "scheduling", workers * days, variant, nl, variables, domains, cons)


def schedule_instances():
    out = []
    out.append(_schedule("sched4w3d", "feasible", 4, 3, 2, 3))
    out.append(_schedule("sched5w4d", "feasible", 5, 4, 2, 3))
    out.append(_schedule("sched3w3d_tight", "tight", 3, 3, 2, 2))
    # Infeasible: need 3 on each of 3 days (9 worker-shifts) but 3 workers * max 2 = 6.
    out.append(_schedule("sched3w3d_infeasible", "infeasible", 3, 3, 3, 2))
    out.append(_schedule("sched6w5d", "feasible", 6, 5, 2, 4))
    out.append(_schedule("sched5w5d", "feasible", 5, 5, 2, 3))
    # Tight: 2 on each of 4 days = 8 on-slots; 4 workers * max 2 = 8 capacity.
    out.append(_schedule("sched4w4d_tight", "tight", 4, 4, 2, 2))
    # Infeasible: 3 on each of 4 days = 12; 4 workers * max 2 = 8 < 12.
    out.append(_schedule("sched4w4d_infeasible", "infeasible", 4, 4, 3, 2))
    return out


# --- latin-square-lite (all_different rows & columns) -------------------------------


def _latin(id, variant, n):
    cells = [f"r{r}c{c}" for r in range(1, n + 1) for c in range(1, n + 1)]
    digits = [f"d{i}" for i in range(1, n + 1)]
    cons = []
    for r in range(1, n + 1):
        cons.append({"type": "all_different", "vars": [f"r{r}c{c}" for c in range(1, n + 1)]})
    for c in range(1, n + 1):
        cons.append({"type": "all_different", "vars": [f"r{r}c{c}" for r in range(1, n + 1)]})
    nl = f"""
Fill an {n}x{n} grid (cell r<row>c<col>) with symbols d1..d{n} so that every row contains
all {n} symbols once and every column contains all {n} symbols once (a Latin square).
Assign exactly one symbol to each cell.
"""
    return _spec(id, "latin_square", n, variant, nl, cells,
                 dict.fromkeys(cells, digits), cons)


def latin_instances():
    out = []
    out.append(_latin("latin3", "feasible", 3))
    out.append(_latin("latin4", "feasible", 4))
    out.append(_latin("latin5", "tight", 5))
    return out


# --- stress tier: large instances (trivial for a solver, hard to reason through) ---
# Tagged variant="stress" (must be feasible/solvable; validated by the reference solver).
# These probe the scale crossover: chain-of-thought must track many simultaneous
# constraints, while Savanty's encoding stays compact and clingo remains complete.


def _kpartite_coloring(id, n_per_group, k, density):
    """k-partite graph (k-colourable by construction) with many cross-group edges."""
    n = n_per_group * k
    edges, cnt = [], 0
    for a in range(1, n + 1):
        for b in range(a + 1, n + 1):
            if (a - 1) // n_per_group != (b - 1) // n_per_group:  # different groups
                cnt += 1
                if cnt % density == 0:
                    edges.append((a, b))
    spec = _coloring(id, "stress", n, edges, k)
    return spec


def stress_instances():
    out = []
    # Large graph colouring (guaranteed k-colourable, dense cross-group edges).
    out.append(_kpartite_coloring("stress_color_g3x7_k3", 7, 3, 2))   # 21 nodes
    out.append(_kpartite_coloring("stress_color_g3x9_k3", 9, 3, 3))   # 27 nodes
    out.append(_kpartite_coloring("stress_color_g4x6_k4", 6, 4, 3))   # 24 nodes, 4 colours
    # Large knapsacks (optimisation): CoT tends to find a feasible but sub-optimal pack.
    w1 = [7, 3, 9, 5, 6, 2, 8, 4, 7, 3, 5, 9, 2, 6, 8, 4, 5, 7]
    v1 = [12, 5, 15, 8, 10, 3, 13, 6, 11, 4, 9, 14, 3, 10, 12, 7, 8, 11]
    out.append(_knapsack("stress_knap18_c40", "stress", w1, v1, 40))
    out.append(_knapsack("stress_knap18_c30", "stress", w1, v1, 30))
    # Large scheduling (feasible): 8 workers x 7 days, >=3 on/day, <=5 days/worker.
    out.append(_schedule("stress_sched8w7d", "stress", 8, 7, 3, 5))
    out.append(_schedule("stress_sched7w6d", "stress", 7, 6, 3, 4))
    # Large seating / team / timetable (feasible).
    out.append(_seating("stress_seat20_5x4", "stress", 20, ["t1", "t2", "t3", "t4", "t5"], 4,
                        [(1, 2), (3, 4), (5, 6)], [(1, 7), (2, 8)]))
    out.append(_assignment("stress_team18_3x6", "stress", 18,
                           ["alpha", "beta", "gamma"], 6, [(1, 2), (3, 4), (5, 6), (7, 8)]))
    out.append(_timetable("stress_tt12_5slot", "stress", 12,
                         ["s1", "s2", "s3", "s4", "s5"],
                         [(i, i + 1) for i in range(1, 12)] + [(1, 3), (2, 4), (5, 7)]))
    out.append(_latin("stress_latin6", "stress", 6))
    # Large infeasible (probes false-feasible hallucination at scale).
    k4 = [(a, b) for a in range(1, 5) for b in range(a + 1, 5)]  # K4 needs 4 colours
    out.append(_coloring("stress_color20_k3_infeasible", "infeasible", 20,
                         k4 + [(i, i + 1) for i in range(4, 20)], 3))
    return out


# --- XL tier: very large FEASIBLE instances (clingo-trivial, CoT-breaking) ----------
# Only feasibility-style problems: clingo finds one model in <0.1s even at 60-120 vars,
# while chain-of-thought must track 60-120 simultaneous decisions. (Large numeric
# optimisation like knapsack is excluded — ASP cannot certify those optima quickly.)


def xl_instances():
    out = []
    out.append(_kpartite_coloring("xl_color_g3x20_k3", 20, 3, 2))   # 60 nodes
    out.append(_kpartite_coloring("xl_color_g4x15_k4", 15, 4, 3))   # 60 nodes, 4 colours
    out.append(_kpartite_coloring("xl_color_g3x30_k3", 30, 3, 3))   # 90 nodes
    out.append(_schedule("xl_sched12x10", "xl", 12, 10, 2, 8))      # 120 vars
    out.append(_schedule("xl_sched10x8", "xl", 10, 8, 2, 6))        # 80 vars
    out.append(_seating("xl_seat40_10x5", "xl", 40, [f"t{i}" for i in range(1, 11)], 5,
                        [(1, 2), (3, 4), (5, 6)], [(1, 7), (2, 8)]))
    out.append(_assignment("xl_team30_5x8", "xl", 30, [f"grp{i}" for i in range(1, 6)], 8,
                           [(1, 2), (3, 4), (5, 6), (7, 8)]))
    out.append(_latin("xl_latin8", "xl", 8))   # 64 cells
    out.append(_latin("xl_latin9", "xl", 9))   # 81 cells
    out.append(_timetable("xl_tt20_6slot", "xl", 20, [f"s{i}" for i in range(1, 7)],
                          [(i, i + 1) for i in range(1, 20)] + [(1, 3), (2, 5), (4, 7)]))
    # tag the k-partite colourings (built with variant "stress") as xl
    for s in out:
        if s["variant"] == "stress":
            s["variant"] = "xl"
    return out


def all_instances():
    out = []
    for fn in (
        graph_coloring_instances,
        knapsack_instances,
        assignment_instances,
        seating_instances,
        timetable_instances,
        schedule_instances,
        latin_instances,
        stress_instances,
        xl_instances,
    ):
        out.extend(fn())
    return out
