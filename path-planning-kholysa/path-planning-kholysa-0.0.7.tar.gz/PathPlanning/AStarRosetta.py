from __future__ import print_function
from decimal import Decimal
from numpy import round, subtract
import matplotlib.pyplot as plt



class AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self, walls, stepSize):
        self.barriers = []
        self.stepSize = stepSize
        for wall in walls:
            self.barriers.append(wall)

    def heuristic(self, start, goal):
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        D = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * (dx + dy)

    def get_vertex_neighbours(self, pos):
        n = []
        # Moves allow link a chess king
        # for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        for dx, dy in [(self.stepSize, 0), (-self.stepSize, 0), (0, self.stepSize), (0, -self.stepSize)]:
            x2 = round(pos[0] + dx, 2)
            y2 = round(pos[1] + dy, 2)
            n.append((x2, y2))
        return n

    def move_cost(self, a, b):
        b = (round(b[0], 2), round(b[1], 2))
        for barrier in self.barriers:
            if b in barrier:
                import numpy as np
                return 100000000000000  # Extremely high cost to enter barrier squares
        return 1  # Normal movement cost


def AStarSearch(start, end, graph, stepSize, display=False):

    difference = subtract(end, start)
    if not (difference[0]/stepSize).is_integer() or not (difference[1]/stepSize).is_integer():
        raise Exception("The goal is not reachable from the starting position given the step size")

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
        if round(current[0],2) == round(end[0],2) and round(current[1],2) == round(end[1],2):
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            prevTarget = path[0]
            iterResult = iter(path)
            next(iterResult)
            state = 0
            combinedResults = list()

            delta = 0
            for target in iterResult:
                if target[0] - prevTarget[0] == 0 and state is 0:
                    state = 0
                    delta += target[1] - prevTarget[1]
                elif target[0] - prevTarget[0] == 0 and state is 1:
                    state = 0
                    combinedResults.append((delta, 0))
                    delta = 0
                    delta += target[1] - prevTarget[1]
                elif target[1] - prevTarget[1] == 0 and state is 1:
                    state = 1
                    delta += target[0] - prevTarget[0]
                elif target[1]  - prevTarget[1] == 0 and state is 0:
                    state = 1
                    combinedResults.append((0, delta))
                    delta = 0
                    delta += target[0] - prevTarget[0]
                prevTarget = target

            if state is 0:
                combinedResults.append((0, delta))
            elif state is 1:
                combinedResults.append((delta, 0))

            if display:
                plt.plot([v[0] for v in path], [v[1] for v in path])
                for barrier in graph.barriers:
                    plt.plot([v[0] for v in barrier], [v[1] for v in barrier])
                plt.xlim(-1, 8)
                plt.ylim(-1, 8)
                plt.show()

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
    barriers = list()
    barrierA = list()
    barrierB = list()
    barrierC = list()
    stepSizeBarriers = 0.1
    for i in range(21):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierA.append((stepSize, 5.0))

    for i in range(21):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierB.append((4.0, 3 + stepSize))

    for i in range(21):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierC.append((2.0, 4 + stepSize))

    for i in range(31):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierC.append((2 + stepSize, 6.0))

    for i in range(41):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierC.append((5.0, 6 - stepSize))

    for i in range(21):
        stepSize = round(i * stepSizeBarriers, 2)
        barrierC.append((3 + stepSize, 2.0))

    barriers.append(barrierA)
    barriers.append(barrierB)
    barriers.append(barrierC)

    stepSize = 0.5
    # graph = AStarGraph([    [(2, 5), (1, 5), (0, 5)],
    #
    #                         [(4, 3), (4, 4), (4, 5)],
    #
    #                         [(2, 4), (2, 5), (2, 6),
    #                          (3, 6), (4, 6), (5, 6),
    #                          (5, 5), (5, 4), (5, 3), (5, 2),
    #                          (4, 2), (3, 2)]
    #                     ])
    graph = AStarGraph(barriers, stepSize)
    start = (3.5,5)
    end = (7.5,7.5)
    distances, cost, result = AStarSearch(start, end, graph, stepSize, True)

    print("route", distances)
    print("coordiantes ", result)
    print("cost", cost)
