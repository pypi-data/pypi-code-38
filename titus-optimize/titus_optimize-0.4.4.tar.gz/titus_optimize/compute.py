from collections import defaultdict

import cvxpy as cp
import numpy as np

IP_SOLUTION_OPTIMAL = 'optimal'
IP_SOLUTION_TIME_BOUND = 'time_bound'


def optimize_ip(requested_cus, total_available_cus, num_sockets, previous_allocation=None,
        unavailable_cus=None, reverse_numbering=False, verbose=False,
        max_runtime_secs=2, solver='GLPK_MI'):
    """
    This function will find the optimal placement of workloads on the compute units of the instance,
    potentially starting from an initial allocation state (in which case it will also try to minimize
    the changes required to the current placement to satisfy the new request).

    Arguments:
        - requested_cus: array of integers representing the number of compute units requested by each workload. Ex: [2,4,8,4]
        - total_available_cus: total # of compute units on the instance
        - num_sockets: # of NUMA sockets on the instance
        - previous allocation: array of assignment vectors from a previous placement
        - verbose: flag to turn on verbose output of the MIP solver
        - max_runtime_secs: the maximum runtime allowed to compute a solution (if supported by the solver)
        - solver: which MIP solver backend to use

    Returns:
        - an array of binary assignment vectors. For example: [[0, 1, 0, 0], [1, 0, 1, 0]] could be a possible
          return value for a call where requested_cus=[1, 2] and total_available_cus=4
          This would mean that the first workload was assigned the compute unit with index 1, and that
          the second workload was assigned the compute units with indices 0 and 3
        - status of the solution ("optimal" or "time_bound")
    """

    d = total_available_cus
    n = num_sockets
    c = d // 2  # number of physical cores
    b = total_available_cus // n  # number of CUs per socket
    k = len(requested_cus)

    if sum(requested_cus) > d:
        raise ValueError("The total # of compute units requested is higher than the total available on the instance.")
    if total_available_cus % 2 != 0:
        raise ValueError("Odd number of compute units on the instance not allowed."
                         " we assume that there always are 2 hyper-threads per physical core.")

    ALPHA_NU = 1000.0
    ALPHA_LLC = 10.0
    ALPHA_L12 = 100.0
    ALPHA_ORDER = 1.0
    ALPHA_PREV = 1000.0

    r = np.array(requested_cus)

    V = np.zeros((d, k), dtype=np.int32)
    for i in range(d):
        for j in range(k):
            if not reverse_numbering:
                V[i, j] = (i + 1) * (j + 1) * (i // b + 1)
            else:
                V[i, j] = (d-1-i + 1) * (k-1-j + 1) * ((d-1-i) // b + 1)
    sV = np.sum(V)

    prev_M = None
    if previous_allocation is not None:
        prev_M = np.zeros((d, k), dtype=np.int32)
        for j, v in enumerate(previous_allocation):
            if j == k:  # means that previous one was bigger, we removed a task
                break
            for i in range(d):
                if v[i] > 0.5:
                    prev_M[i, j] = 1

    # Optimal boolean assignment matrix we wish to find
    M = cp.Variable((d, k), boolean=True)

    # Auxiliary variables needed
    X = cp.Variable((n, k), integer=True)
    Y = cp.Variable(c, integer=True)
    U = cp.Variable(1, integer=True)

    # 1) Penalize placements where workloads span multiple sockets
    cost_NU = -(ALPHA_NU / (n * k)) * cp.sum(X)

    # 2) Try to even the # of busy CPUs per socket
    cost_LLC = (ALPHA_LLC / n) * sum([cp.abs(U - cp.sum(M[t * b: (t + 1) * b, :])) for t in range(n)])

    # 3) Penalize empty cores (because it means more L1/L2 trashing)
    cost_L12 = (ALPHA_L12 / c) * cp.sum(Y)

    # 4) Favor contiguous indexing for:
    # - better affinity of hyperthreads to jobs on the same core
    # - more organized placement
    cost_ordering = (ALPHA_ORDER / (d * k * sV)) * cp.sum(cp.multiply(V, M))

    cost = cost_NU + cost_LLC + cost_L12 + cost_ordering

    # 5) [optional] if starting from a previous allocation,
    # penalize placements that move assignements too much
    # compared to reference placement.
    if prev_M is not None:
        cost += (ALPHA_PREV / (d * k)) * cp.sum(cp.abs(M - prev_M))

    # The placement has to satisfy the requested # of units for each workload
    CM1 = [M.T * np.ones((d,)) == r]
    # Each compute unit can only be assigned to a single workload
    CM2 = [M * np.ones((k, 1)) <= np.ones((d, 1))]

    CM3 = None
    if unavailable_cus is not None:
        CM3 = [cp.sum(M[cu_id,:]) == 0 for cu_id in unavailable_cus]

    # Extra variables constraints (coming from linearization of min/-max operators)
    CX1 = [X[t, j] <= (1.0 / max(r[j], 1)) * cp.sum(M[t * b: (t + 1) * b, j]) for t in range(n) for j in range(k)]
    CX2 = [X <= 1]

    CY1 = [Y[l] >= -1 + cp.sum(M[2 * l, :]) + cp.sum(M[2 * l + 1, :]) for l in range(c)]
    CY2 = [Y >= 0]

    constraints = CM1 + CM2 + CY1 + CY2 + CX1 + CX2
    if CM3 is not None:
        constraints += CM3

    prob = cp.Problem(cp.Minimize(cost), constraints)

    if verbose:
        print("Number of scalar variables in problem: ", prob.size_metrics.num_scalar_variables)

    try:
        extra_args = {} if solver != 'GLPK_MI' else {"tm_lim": int(1000 * max_runtime_secs)}
        prob.solve(solver=solver, verbose=verbose, **extra_args)
    except Exception as e:
        msg = "Solver crashed. (requested_cus=%s , previous_allocation=%s)" % (
            requested_cus, previous_allocation)
        raise Exception(msg).with_traceback(e.__traceback__)

    if prob.status not in ('optimal', 'optimal_inaccurate'):
        raise Exception("Could not solve the integer program: `%s`" % (prob.status,))

    status = IP_SOLUTION_OPTIMAL if prob.status == 'optimal' else IP_SOLUTION_TIME_BOUND

    res = [None] * len(requested_cus)
    for i, e in enumerate(M.value.T):
        res[i] = [1 if u > 0.5 else 0 for u in e]

    return res, status


def optimize_greedy(requested_cus, total_available_cus, num_sockets):
    """
    This function simulates the greedy algorithm implemented in titus-isolate.
    Only used for benchmarking purposes.
    """
    try:
        from titus_isolate.isolate.cpu import assign_threads
        from titus_isolate.model.processor.cpu import Cpu
        from titus_isolate.model.processor.package import Package
        from titus_isolate.model.processor.core import Core
        from titus_isolate.model.processor.thread import Thread
        from titus_isolate.model.workload import Workload
        from titus_isolate.docker.constants import STATIC
    except ImportError:
        raise Exception("You need titus-isolate for this function.")

    workloads = []

    for i, req in enumerate(requested_cus):
        w = Workload(str(i), req, STATIC)
        workloads.append(w)

    workloads.sort(key=lambda workload: workload.get_thread_count(), reverse=True)

    b = total_available_cus // num_sockets
    c = b // 2
    sockets = []
    for i in range(num_sockets):
        cores = []
        for j in range(c):
            core = Core(j, [Thread(b * i + 2 * j), Thread(b * i + 2 * j + 1)])
            cores.append(core)
        sockets.append(Package(i, cores))
    cpu = Cpu(sockets)
    cpu.clear()

    for w in workloads:
        assign_threads(cpu, w)

    ids_per_workload = defaultdict(list)

    for t in cpu.get_threads():
        if t.is_claimed():
            ids_per_workload[t.get_workload_id()] = ids_per_workload[t.get_workload_id()] + [t.get_id()]

    allocations = []
    for i in range(len(requested_cus)):
        assignments = [0] * total_available_cus
        for j in ids_per_workload[str(i)]:
            assignments[j] = 1
        allocations.append(assignments)

    return allocations
