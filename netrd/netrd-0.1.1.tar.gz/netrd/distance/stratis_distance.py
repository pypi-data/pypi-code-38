"""
stratis_distance.py
--------------------------

author: Stefan McCabe
email:
Submitted as part of the 2019 NetSI Collabathon.

"""

from functools import partial
import networkx as nx
import numpy as np
from scipy.optimize import minimize
import cvxpy as cv
from .base import BaseDistance


class StratisDistance(BaseDistance):
    # def dist(self, G1, G2):
    #     A1 = nx.to_numpy_array(G1)
    #     A2 = nx.to_numpy_array(G2)

    #     N = A1.shape[0]
    #     vals1, vecs1 = np.linalg.eigh(A1)
    #     vals2, vecs2 = np.linalg.eigh(A2)

    #     v1 = np.diag(vals1)
    #     v2 = np.diag(vals2)

    #     I1 = np.eye(N)
    #     I2 = np.eye(N)

    #     P = vecs1 @ (I1.T @ I2) @ vecs2.T

    #     def objective(x, P, n):
    #         m = x.reshape((n,n))
    #         return -np.trace(m + P.T + 0.001 * np.random.rand(n, n))

    #     def objective_2(x, P, n):
    #         m = x.reshape((n, n))
    #         return - np.trace(m + P.T)

    #     FP_init = np.eye(N).flatten()
    #     bounds = tuple([(0, 1) for _ in range(len(FP_init))])

    #     rows = [np.array(list(range(k*N, (k+1)*N))) for k in range(N)]
    #     cols = [np.linspace(0+i, N**2+i, N, endpoint=False, dtype=int) for i in range(N)]
    #     indices = rows+cols

    #     def constraint(x, idx):
    #         return 1 - x[idx].sum()

    #     constraints = [
    #         {'type': 'eq', 'fun': partial(constraint, idx=idx)} for idx in indices
    #     ]

    #     results = minimize(objective, FP_init, method='SLSQP', bounds=bounds,
    #                        constraints=constraints, args=(P, N))

    #     # def constraint_1(x):
    #     #     return x

    #     # def constraint_2(x):
    #     #     return 1 - x

    #     def constraint_3(x):

    #         return 1 - np.sum(x, axis=0)

    #     def constraint_4(x):
    #         return 1 - np.sum(x, axis=1)

    #     constraints = [
    #         # {'type': 'ineq', 'fun': constraint_1},
    #         # {'type': 'ineq', 'fun': constraint_2},
    #         {'type': 'eq', 'fun': constraint_3},
    #         {'type': 'eq', 'fun': constraint_4},
    #     ]

    #     self.results['dist'] = dist
    #     return dist

    def dist(self, G1, G2):
        A = nx.to_numpy_array(G1)
        B = nx.to_numpy_array(G2)
        N = A.shape[0]
        P = np.array([1 / N for _ in range(N ** 2)])

        a = cv.Constant(A)
        b = cv.Constant(B)
        p = cv.Variable((N, N))
        constraint = [p >= 0, cp.sum(p, axis=0) == 1, cp.sum(p, axis=1) == 1]
        obj = cp.Minimize(cp.norm(a * p - p * b, "fro"))

        prob = cp.Problem(obj, constraint)
        prob.solve()

        P = p.value

        dist = np.linalg.norm(A.dot(P) - P.dot(B))

        def objective(P, A, B):
            N = int(np.sqrt(len(P)))
            P = P.reshape((N, N))
            return np.linalg.norm(A @ P - P @ B)

        bounds = tuple([(0, np.inf) for _ in range(len(P))])

        rows = [np.array(list(range(k * N, (k + 1) * N))) for k in range(N)]
        cols = [
            np.linspace(0 + i, N ** 2 + i, N, endpoint=False, dtype=int)
            for i in range(N)
        ]
        indices = rows + cols

        def constraint(x, idx):
            return 1 - x[idx].sum()

        constraints = [
            {"type": "eq", "fun": partial(constraint, idx=idx)} for idx in indices
        ]

        results = minimize(
            objective,
            P,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            args=(A, B),
        )

        return dist
