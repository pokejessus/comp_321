#!/usr/bin/env python3
"""Test-case generator for "Awkward-Free Photo".

The generator only produces INPUTS. The .ans files are produced afterwards by running
the accepted solution

Graph families (all are "cycles with trees hanging off them"):
  fixed      an explicit list a_1..a_n written by hand
  cycles     given cycle lengths, remaining guests attach as trees with a chosen shape:
               random   to a random earlier vertex          (bushy random trees)
               chain    to the previous vertex              (one very long path)
               star     to a random cycle vertex            (huge stars on the cycle)
               deep     to one of the 5 newest vertices     (long thin deep trees)
               cater    alternately extend a spine / add a leaf (caterpillar)
"""
import os
import random
import sys

MAX_N = 10 ** 5


# --------------------------------------------------------------------------- builders
def build_cycles(n, lens, attach, rng):
    """Cycles of the given lengths (labels shuffled), remaining guests are trees."""
    assert sum(lens) <= n and all(L >= 2 for L in lens)
    nodes = list(range(1, n + 1))
    rng.shuffle(nodes)
    a = [0] * (n + 1)
    idx = 0
    for L in lens:
        c = nodes[idx:idx + L]
        for j in range(L):
            a[c[j]] = c[(j + 1) % L]
        idx += L
    cyc_nodes = nodes[:idx]
    placed = list(cyc_nodes)
    spine = placed[-1]
    toggle = True
    for v in nodes[idx:]:
        if attach == "random":
            p = rng.choice(placed)
        elif attach == "chain":
            p = placed[-1]
        elif attach == "star":
            p = rng.choice(cyc_nodes)
        elif attach == "deep":
            p = rng.choice(placed[-5:])
        elif attach == "cater":
            p = spine
            if toggle:
                spine = v
            toggle = not toggle
        else:
            raise ValueError(attach)
        a[v] = p
        placed.append(v)
    return a[1:]


def random_lens(n, rng, lo, hi, frac, odd_only=False):
    budget = max(lo, int(n * frac))
    lens = []
    while budget >= lo:
        L = rng.randint(lo, min(hi, budget))
        if odd_only and L % 2 == 0:
            L = L - 1 if L - 1 >= lo else L + 1
        if L > budget:
            break
        lens.append(L)
        budget -= L
    return lens or [lo]


def pure_cycle(n):
    return [i % n + 1 for i in range(1, n + 1)]  # i gives to i+1, n gives to 1


# --------------------------------------------------------------------------- cases
def case_random(n, seed):
    rng = random.Random(seed)
    lens = random_lens(n, rng, 2, max(2, n // 2), rng.choice([0.2, 0.5, 0.9]))
    return build_cycles(n, lens, rng.choice(["random", "deep", "star"]), rng)


def case_cycles(n, seed, lens_fn, attach):
    rng = random.Random(seed)
    return build_cycles(n, lens_fn(n, rng), attach, rng)


TRICKY_12 = [10, 7, 6, 7, 4, 5, 4, 2, 11, 12, 3, 10]  # found by search; answer 7

# (name, builder, description)
SAMPLES = [
    ("1", lambda: [2, 1, 2, 3, 4],
     "Sample 1: mutual pair (a 2-cycle) with a chain attached. Answer 3."),
    ("2", lambda: [2, 3, 1, 1, 1, 2],
     "Sample 2: triangle with leaves hanging off two of its vertices (the figure in the statement). Answer 4."),
    ("3", lambda: [2, 3, 4, 1],
     "Sample 3: a pure even cycle of length 4. Answer 2."),
]

SECRET = [
    ("01_edge_min_n2", lambda: [2, 1],
     "Edge case: smallest allowed input, n = 2, the two guests give to each other. Answer 1."),
    ("02_edge_triangle", lambda: pure_cycle(3),
     "Edge case: pure triangle (odd cycle, no trees). Answer 1; a solution that forgets the wrap-around edge answers 2."),
    ("03_edge_odd_cycle_5", lambda: pure_cycle(5),
     "Edge case: pure odd cycle of length 5. Answer 2; catches 'cycle treated as a path' and 'graph is bipartite' solutions."),
    ("04_edge_all_mutual_pairs", lambda: [2, 1, 4, 3, 6, 5, 8, 7, 10, 9],
     "Edge case: five disjoint 2-cycles (several components, every cycle has length 2). Answer 5."),
    ("05_edge_star_into_2cycle", lambda: [2, 1] + [1] * 6,
     "Edge case: six leaves all giving to the same guest of a mutual pair (a star). Answer 7."),
    ("06_handcrafted_tricky_12", lambda: TRICKY_12,
     "Hand-crafted: 12 guests with several cycle/tree interactions, found by search. Answer 7. Sorting guests once by initial degree and greedily picking gives only 6, so heuristics fail here."),
    ("07_small_random_a", lambda: case_random(12, 101),
     "Small random functional graph (n = 12), mixed tree shapes and cycle lengths."),
    ("08_small_random_b", lambda: case_random(16, 102),
     "Small random functional graph (n = 16); small enough for exponential brute force."),
    ("09_small_odd_cycles", lambda: case_cycles(
        21, 103, lambda n, r: [3, 5, 3], "random"),
     "Small: three odd cycles (3, 5, 3) with trees attached; several components."),
    ("10_medium_random", lambda: case_random(2000, 104),
     "Normal random case, n = 2000. Mixed cycle lengths and tree shapes."),
    ("11_medium_odd_cycles", lambda: case_cycles(
        3000, 105, lambda n, r: random_lens(n, r, 3, 9, 0.6, odd_only=True), "random"),
     "Medium: many small odd cycles with random trees. Exposes solutions that ignore the cycle closing edge."),
    ("12_large_cycle_even", lambda: pure_cycle(100000),
     "Large: one pure cycle of length 100000 (no trees). Answer 50000. Exposes O(L^2) cycle handling."),
    ("13_large_cycle_odd", lambda: case_cycles(99999, 106, lambda n, r: [n], "random"),
     "Large: one pure cycle of odd length 99999 with shuffled labels. Answer 49999."),
    ("14_large_chain_2cycle", lambda: case_cycles(100000, 107, lambda n, r: [2], "chain"),
     "Worst case for recursion: a mutual pair with a path of 99998 guests attached. Depth ~1e5: breaks recursive DFS and non-memoized DP."),
    ("15_large_chain_triangle", lambda: case_cycles(100000, 108, lambda n, r: [3], "chain"),
     "Deep chain attached to a triangle instead of a 2-cycle. Recursion-depth and Fibonacci-blowup test."),
    ("16_large_star_triangle", lambda: case_cycles(100000, 109, lambda n, r: [3], "star"),
     "Large: a triangle whose three vertices receive ~33000 leaves each (huge stars). Tests aggregation over many children."),
    ("17_large_big_cycle_trees", lambda: case_cycles(100000, 110, lambda n, r: [70001], "random"),
     "Large: one odd cycle of 70001 guests with 29999 guests in random trees. Tests the cycle DP with non-trivial in/out values."),
    ("18_large_deep_thin_trees", lambda: case_cycles(100000, 111, lambda n, r: [2], "deep"),
     "Large: a mutual pair with long, thin, deep trees (each guest attaches to one of the 5 newest). Deep recursion with branching."),
    ("19_large_many_small_cycles", lambda: case_cycles(
        100000, 112, lambda n, r: random_lens(n, r, 2, 5, 0.6), "random"),
     "Large: tens of thousands of tiny cycles (length 2..5), each a separate component. Tests summing over components."),
    ("20_large_random_a", lambda: case_random(100000, 113),
     "Large complicated random case (mixed cycle lengths and tree shapes), n = 100000."),
    ("21_large_random_b", lambda: case_random(100000, 114),
     "Large complicated random case with a different seed, n = 100000."),
    ("22_large_odd_cycles", lambda: case_cycles(
        100000, 115, lambda n, r: random_lens(n, r, 3, 15, 0.8, odd_only=True), "random"),
     "Large: many odd cycles of length 3..15 with random trees; wrap-around edge matters in every component."),
    ("23_large_caterpillar", lambda: case_cycles(100000, 116, lambda n, r: [2], "cater"),
     "Large: caterpillar (a long spine with a leaf on every second spine vertex) hanging off a mutual pair. Greedy and DP both stressed."),
    ("24_large_two_odd_cycles_deep", lambda: case_cycles(
        100000, 117, lambda n, r: [30001, 30001], "deep"),
     "Large: two big odd cycles plus deep thin trees; mixes long cycles with deep trees."),
]


# --------------------------------------------------------------------------- io + checks
def check_valid(a):
    n = len(a)
    assert 2 <= n <= MAX_N, "n out of range"
    for i, x in enumerate(a, start=1):
        assert 1 <= x <= n and x != i, "invalid a_%d = %d" % (i, x)


def write_case(folder, name, a):
    check_valid(a)
    with open(os.path.join(folder, name + ".in"), "w") as f:
        f.write("%d\n%s\n" % (len(a), " ".join(map(str, a))))


def clean(folder):
    os.makedirs(folder, exist_ok=True)
    for fn in os.listdir(folder):
        if fn.endswith((".in", ".ans")):
            os.remove(os.path.join(folder, fn))


def generate(data_dir):
    sample_dir = os.path.join(data_dir, "sample")
    secret_dir = os.path.join(data_dir, "secret")
    clean(sample_dir)
    clean(secret_dir)
    lines = ["Description of the test cases", "=" * 29, "",
             "SAMPLE (data/sample)", "-" * 20]
    for name, make, desc in SAMPLES:
        a = make()
        write_case(sample_dir, name, a)
        lines.append("%s.in  (n=%d): %s" % (name, len(a), desc))
    lines += ["", "SECRET (data/secret)", "-" * 20]
    for name, make, desc in SECRET:
        a = make()
        write_case(secret_dir, name, a)
        lines.append("%s.in  (n=%d): %s" % (name, len(a), desc))
    with open(os.path.join(data_dir, "Description.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %d sample and %d secret cases to %s" % (len(SAMPLES), len(SECRET), data_dir))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data")
    generate(out)
