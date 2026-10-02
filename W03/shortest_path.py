"""
Shortest path on an undirected weighted graph.

The graph is a dict: {node: {neighbour: weight, ...}, ...}
"""
import heapq


# Dijkstra.
# Returns the shortest total weight, or None if unreachable.
def distance_correct(graph, start, end):
    best = {start: 0}
    queue = [(0, start)]
    done = set()
    while queue:
        d, node = heapq.heappop(queue)
        if node in done:
            continue
        done.add(node)
        if node == end:
            return d
        for neighbour, weight in graph.get(node, {}).items():
            nd = d + weight
            if nd < best.get(neighbour, float("inf")):
                best[neighbour] = nd
                heapq.heappush(queue, (nd, neighbour))
    return None


"""
Same idea, but it returns as soon as `end` is first RELAXED,
instead of waiting until `end` is POPPED from the queue.

A very common mistake. The first path found is not always the shortest.
"""
def distance_buggy(graph, start, end):
    best = {start: 0}
    queue = [(0, start)]
    done = set()
    while queue:
        d, node = heapq.heappop(queue)
        if node in done:
            continue
        done.add(node)
        for neighbour, weight in graph.get(node, {}).items():
            nd = d + weight
            if nd < best.get(neighbour, float("inf")):
                best[neighbour] = nd
                if neighbour == end:
                    return nd          # <-- The bug.
                heapq.heappush(queue, (nd, neighbour))
    return best.get(end)