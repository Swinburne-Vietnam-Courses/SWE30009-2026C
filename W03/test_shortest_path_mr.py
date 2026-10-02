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
    return {n: {m: w * k for m, w in edges.items()} for n, edges in graph.items()}


def add_constant(graph, k):
    return {n: {m: w + k for m, w in edges.items()} for n, edges in graph.items()}
