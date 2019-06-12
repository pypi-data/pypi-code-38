from collections import Counter


def number_numa_violations(allocations, num_sockets):
    d = len(allocations[0])
    b = d // num_sockets

    violations = 0
    for job in allocations:
        cnt = Counter()
        for ii, e in enumerate(job):
            if e == 1:
                cnt[ii // b] += 1
        top_index = cnt.most_common()[0][0]
        violations += sum(v for k, v in cnt.items() if k != top_index)
    return violations


def number_empty_sockets(allocations, num_sockets):
    d = len(allocations[0])
    b = d // num_sockets
    empty = [True] * num_sockets
    for a in allocations:
        for i, v in enumerate(a):
            empty[i // b] &= v == 0
    return sum(empty)


def number_empty_cores(allocations):
    d = len(allocations[0])
    c = d // 2
    empty = [True] * c
    for a in allocations:
        for i, v in enumerate(a):
            empty[i // 2] &= v == 0
    return sum(empty)


def number_full_cores(allocations):
    d = len(allocations[0])
    c = d // 2
    full = [0] * c
    for a in allocations:
        for i, v in enumerate(a):
            full[i // 2] += v
    return sum([1 if e == 2 else 0 for e in full])


def get_allocation_stats(allocations, num_sockets):
    return [
        number_numa_violations(allocations, num_sockets),
        number_empty_sockets(allocations, num_sockets),
        number_empty_cores(allocations),
        number_full_cores(allocations)
    ]
