from __future__ import print_function
import matplotlib.pyplot as plt


class AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self):
        self.barriers = []
        self.barriers.append(
            [(2, 4), (2, 5), (2, 6), (3, 6), (4, 6), (5, 6), (5, 5), (5, 4), (5, 3), (5, 2), (4, 2), (3, 2)],
            )
        # self.barriers.append(
        #     [(0, 0), (1, 0), (2, 0)],
        # )
        # self.barriers.append(
        #     [(4, 3), (4, 4), (4, 5)],
        # )
            # [(5, 6), (5, 5), (5, 4), (5, 3), (5, 2), (4, 2), (3, 2)] )

    def heuristic(self, start, goal):
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        # D = 1
        # D2 = 1
        # dx = abs(start[0] - goal[0])
        # dy = abs(start[1] - goal[1])
        # return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
        D = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * (dx + dy)

    def get_vertex_neighbours(self, pos):
        n = []
        # Moves allow link a chess king
        # for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if x2 < 0 or x2 > 7 or y2 < 0 or y2 > 7:
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, a, b):
        for barrier in self.barriers:
            if b in barrier:
                return 100  # Extremely high cost to enter barrier squares
        return 1  # Normal movement cost


def AStarSearch(start, end, graph):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)

    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    while len(openVertices) > 0:
        # Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos

        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            prevTarget = path[0]
            lastTarget = path[-1]
            iterResult = iter(path)
            next(iterResult)
            state = 0
            combinedResults = list()

            delta = 0
            for target in iterResult:
                if target[0] - prevTarget[0] is 0 and state is 0:
                    state = 0
                    delta += target[1] - prevTarget[1]
                elif target[0] - prevTarget[0] is 0 and state is 1:
                    state = 0
                    combinedResults.append((delta, 0))
                    delta = 0
                    delta += target[1] - prevTarget[1]
                elif target[1] - prevTarget[1] is 0 and state is 1:
                    state = 1
                    delta += target[0] - prevTarget[0]
                elif target[1] - prevTarget[1] is 0 and state is 0:
                    state = 1
                    combinedResults.append((0, delta))
                    delta = 0
                    delta += target[0] - prevTarget[0]
                prevTarget = target

            if state is 0:
                combinedResults.append((0, delta))
            elif state is 1:
                combinedResults.append((delta, 0))

            return combinedResults, F[end], path  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in graph.get_vertex_neighbours(current):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + graph.move_cost(current, neighbour)

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex
            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H

    raise RuntimeError("A* failed to find a solution")


if __name__ == "__main__":
    graph = AStarGraph()
    start = (4,5)
    end = (7,7)
    distances, cost, result = AStarSearch(start, end , graph)

    print("route", result)
    print("cost", cost)
    plt.plot([v[0] for v in result], [v[1] for v in result])
    for barrier in graph.barriers:
        plt.plot([v[0] for v in barrier], [v[1] for v in barrier])
    plt.xlim(-7, 8)
    plt.ylim(-7, 8)
    plt.show()