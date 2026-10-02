"""
Metamorphic relations for the shortest path program.

Run against the correct version, then switch TARGET to distance_buggy.
    pytest test_shortest_path_mr.py -v
"""

from shortest_path import distance_correct, distance_buggy

TARGET = distance_correct  # <-- Switch to distance_buggy later.


GRAPH = {
    "A": {"B": 1, "C": 10},
    "B": {"A": 1, "C": 2, "D": 7},
    "C": {"A": 10, "B": 2, "D": 3},
    "D": {"B": 7, "C": 3},
}


def scale(graph, k):
    """
    Multiply EVERY edge weight by k.

    Every possible route grows by the same factor k,
    so the ranking of the routes does not change and the shortest route stays the shortest.
    The distance is therefore predictable. It becomes k times the original.
    """

    return {n: {m: w * k for m, w in edges.items()} for n, edges in graph.items()}


def add_constant(graph, k):
    """
    Add k to EVERY edge weight.

    This looks similar to scale() but it behaves very differently.
    A route grows by k times its NUMBER OF EDGES,
    so routes with more edges are punished more heavily and the shortest route can change completely.
    The distance is NOT predictable, so this does not give a valid metamorphic relation.
    """

    return {n: {m: w + k for m, w in edges.items()} for n, edges in graph.items()}


# On an undirected graph, distance(A, D) must equal distance(D, A).
def test_mr1_symmetry():
    assert TARGET(GRAPH, "A", "D") == TARGET(GRAPH, "D", "A")


# Multiplying every weight by k multiplies the distance by k.
def test_mr2_scale_all_weights():
    k = 3
    assert TARGET(scale(GRAPH, k), "A", "D") == k * TARGET(GRAPH, "A", "D")


# Adding a node with no edges cannot change any existing distance.
def test_mr3_isolated_node_added():
    bigger = dict(GRAPH)  # Copy original graph.
    bigger["Z"] = {}  # Add new empty node to new graph
    assert TARGET(bigger, "A", "D") == TARGET(GRAPH, "A", "D")


# C lies on the shortest path from A to D, so the path splits exactly.
def test_mr4_subpath_optimality():
    assert TARGET(GRAPH, "A", "D") == TARGET(GRAPH, "A", "C") + TARGET(GRAPH, "C", "D")


# Going through any node B cannot be cheaper than going direct.
def test_mr5_triangle_inequality():
    assert TARGET(GRAPH, "A", "D") <= TARGET(GRAPH, "A", "B") + TARGET(GRAPH, "B", "D")


# CAREFUL: Is this really a necessary property?
def test_mr6_add_constant_to_all_weights():
    k = 5
    assert TARGET(add_constant(GRAPH, k), "A", "D") == TARGET(GRAPH, "A", "D") + k
