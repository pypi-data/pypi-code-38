from math import factorial

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from deap import base, creator, tools
from deap import benchmarks

np.random.seed(333)

PROBLEM = "dtlz2"
NOBJ = 3
K = 10
NDIM = NOBJ + K - 1
P = 12
H = factorial(NOBJ + P - 1) / (factorial(P) * factorial(NOBJ - 1))
MU = int(H + (4 - H % 4))
NGEN = 400
BOUND_LOW, BOUND_UP = 0.0, 1.0

creator.create("FitnessMin", base.Fitness, weights=(-1,)*NOBJ)
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr", np.random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, n=NDIM)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

dtlz2 = lambda x: benchmarks.dtlz2(x, NOBJ)

pop = toolbox.population(2*MU)
fitnesses = map(dtlz2, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit

fronts = tools.sortLogNondominated(pop, MU)

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection="3d")

# the coordinate origin (black + sign)
ax.scatter(0, 0, 0, c="k", marker="+", s=100)

for i, f in enumerate(fronts):
    p = np.array([ind.fitness.values for ind in f])
    ax.scatter(p[:, 0], p[:, 1], p[:, 2], marker="o", s=48, label="Level {}".format(i))

ax.view_init(elev=11, azim=-25)
ax.autoscale(tight=True)
plt.tight_layout()
plt.legend()
plt.show()