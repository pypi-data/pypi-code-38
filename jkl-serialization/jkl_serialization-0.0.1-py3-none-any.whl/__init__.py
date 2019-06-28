name = 'jkl_serialization'
from typing import NewType, List, Dict, Tuple
from collections import deque

Node = NewType('Node', str)
ParentSetScore = NewType("ParentSetScore", Tuple[int, List[Node]])
JKL_Object = NewType('JKL_Object', Dict[Node, List[ParentSetScore]])


def deserialize_jkl(jkl: str) -> JKL_Object:
    d = {}
    q = deque(jkl.split('\n'))
    nodes = int(q.popleft())

    while len(q) and q[0]:
        node, lines = tuple(q.popleft().split(' '))
        scores = []
        for i in range(int(lines)):
            line = deque(q.popleft().split(' '))
            score = line.popleft()
            n_parents = line.popleft()
            parents = list(line)
            scores.append((score, parents))
        d[node] = scores
    return d


def serialize_jkl(jkl: JKL_Object) -> str:
    number_of_vars = len(jkl.keys())
    result = f"{number_of_vars}\n"
    for node, parent_list in jkl.items():
        result += f"{node} {len(parent_list)}\n"
        for score, parent_set in parent_list:
            if len(parent_set) > 0:
                result += f"{score} {len(parent_set)} {' '.join(parent_set)}\n"
            else:
                result += f"{score} 0\n"
    return result
