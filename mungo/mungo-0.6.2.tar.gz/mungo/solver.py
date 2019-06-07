import re
from collections import namedtuple
from functools import partial
from typing import Dict, Callable, List, Tuple, DefaultDict, Set

from fastcache import lru_cache
from igraph import *
from pulp import *
from pulp import LpProblem, LpMinimize, LpStatusOptimal, LpStatus
from tqdm import tqdm

from mungo.common import vparse, BFMT, QUIET
from mungo.repositorydata import get_repository_data, merge_repository_data, RepositoryData

Version = namedtuple("Version", "version build")


def equal_compare(y):
    p = re.compile(y.replace(".*", "*").replace("*", r"(\D.*)??\Z"))
    return lambda x: bool(p.match(x.version))


@lru_cache(maxsize=None)
def geq(x: Version, y: Version) -> bool:
    return vparse(x.version) >= vparse(y.version)


# @lru_cache(maxsize=None)
def gt(x: Version, y: Version) -> bool:
    return vparse(x.version) > vparse(y.version)


# @lru_cache(maxsize=None)
def leq(x: Version, y: Version) -> bool:
    return vparse(x.version) <= vparse(y.version)


# @lru_cache(maxsize=None)
def lt(x: Version, y: Version) -> bool:
    return vparse(x.version) < vparse(y.version)


# @lru_cache(maxsize=None)
def eq(x: Version, y: Version) -> bool:
    return vparse(x.version) == vparse(y.version)


# @lru_cache(maxsize=None)
def neq(x: Version, y: Version) -> bool:
    return ~(vparse(x.version) == vparse(y.version)) and (vparse(x.version) < vparse(y.version, ".99999999999999"))


operator_function: Dict[str, Callable[[Version, Version], bool]] = {
    ">=": geq,
    ">": gt,
    "<=": leq,
    "<": lt,
    "!=": neq,
    "==": eq,
    #    "=": lambda x, y: (vparse(x.version) >= vparse(y.version))
    #                      and (vparse(x.version) < vparse(y.version, ".99999999999999")),
}


def build_comp(x: Version, constraint: Version) -> bool:
    xb, yb = x.build, constraint.build
    rs = re.search(r'_[0-9]*$', yb)
    if rs is not None:
        yb = yb[:-len(rs.group(0))]

    return xb == yb \
           or yb.endswith("*") and xb.startswith(yb.rstrip("*")) \
           or yb == "*"


class Node:
    def __init__(self, name: str, version, p):
        self.name = name
        self.version = version
        self.distance_root = -1
        self._in_nodes = []
        self._out_nodes = defaultdict(list)
        self._x = None
        self.p = p
        self._mass_low = None
        self._mass_high = None
        self.invalid = False

    def add_in_node(self, n: 'Node'):
        self._in_nodes.append(n)

    def remove_in_node(self, n: 'Node'):
        self._in_nodes.remove(n)

    def add_out_node(self, n: 'Node'):
        self._out_nodes[n.name].append(n)

    def remove_out_node(self, n: 'Node'):
        self._out_nodes[n.name].remove(n)

    @property
    def channel_name(self) -> str:
        if self.p is None or "channel" not in self.p:
            return ""
        return self.p['channel'].split('/')[-2]

    @property
    def installed(self) -> bool:
        if self.p is None:
            return False
        # print(self.name, self.version, "installed" in self.p)
        return "installed" in self.p and self.p["installed"]

    @property
    def in_nodes(self) -> List['Node']:
        return self._in_nodes

    @property
    def out_nodes(self) -> List['Node']:
        for nodes in self._out_nodes.values():
            for n in nodes:
                yield n

    @property
    def x(self) -> LpVariable:
        # create LP variable, if not exist
        if self._x is None:
            self._x = LpVariable("{name}-{version}".format(name=self.name, version=self.version), 0, 1, LpInteger)
        return self._x

    def delete(self):
        for n in self.in_nodes:
            n.remove_out_node(self)
        for n in self.out_nodes:
            n.remove_in_node(self)


PackageNodeDict = DefaultDict[str, Dict[str, Vertex]]
DependencyNodeDict = Dict[tuple, Vertex]


@lru_cache(maxsize=None)
def valid_packages(ls: list, repodata: dict):
    # print(ls)
    all_valids = []
    for s in ls:
        name, is_valid = _valid_packages_function(s)
        all_valids.append(is_valid)

    # all_valid = lambda x: reduce((lambda a, b: a(x) and b(x)), all_valids)
    all_valid = lambda x: any(f(x) for f in all_valids)  # TODO: any or all?
    ret = [(name, x) for x in repodata.d[name] if all_valid(Version(*x))]
    return ret


def split_package_constraint(s: str) -> Tuple[str, List[List[List[str]]]]:
    or_split = s.split("|")
    ret = []
    name = None

    for o in or_split:
        term = []
        for x in o.split(","):
            res = re.split('(==|!=|>=|<=|=|<|>| )', x)
            res = [y for y in res if y != " " and len(y) > 0]
            if name is None:
                name = res.pop(0)
            term.append(res)
        ret.append(term)
    return name, ret  # foo, [[]]


#print(split_package_constraint("pysocks 4 rc3"))
#print(split_package_constraint("_r-mutex 1.* anacondar_1"))

# print(split_package_constain("pysocks >=1.5.6,<2.0,!=1.5.7"))
# print(split_package_constain("pysocks>=   1.5.6,  <  2.0,!= 1.5.7"))
# print(split_package_constain("pysocks 1=4"))
# f()

def _valid_packages_function(s: str) -> Tuple[str, Callable[[Version], bool]]:
    name, or_constraints = split_package_constraint(s)

    and_valids = []

    for constraints in or_constraints:
        is_valids = []  # lambda x: True

        for c in constraints:
            len_c = len(c)
            if len_c == 0:
                # no version constraint
                pass
            elif len_c == 1:
                # version constraint without operator (equals ==)
                version = c[0]
                is_valids.append(equal_compare(y=version))
            elif len_c == 2:
                # version constraint
                operator, v = c
                version = Version(v, "*")
                if operator == "=":
                    is_valids.append(equal_compare(y=v))
                elif operator in [">=", ">", "<=", "<", "!=", "=="]:
                    is_valids.append(partial(operator_function[operator], y=version))
                else:
                    # version build constraint with no operator
                    version = Version(*c)
                    if version.version != "*":
                        is_valids.append(equal_compare(y=version.version))
                    is_valids.append(partial(build_comp, constraint=version))
            elif len_c == 3:
                # operator version build
                operator, v, b = c
                version = Version(v, b)
                if operator == "=":
                    is_valids.append(equal_compare(y=v))
                elif operator in [">=", ">", "<=", "<", "!=", "=="]:
                    is_valids.append(partial(operator_function[operator], y=version))
                is_valids.append(partial(build_comp, constraint=version))
            else:
                raise Exception("invalid version constraint", s)

        def all_valids(x, is_valids=is_valids):
            return all(f(x) for f in is_valids)

        and_valids.append(all_valids)
    or_valid = lambda x: any(f(x) for f in and_valids)
    return name, or_valid


def reduce_dependency_graph(g: Graph, all_package_nodes: PackageNodeDict, channels: List[str]) -> Graph:
    channel_order = dict()
    for priority, channel in enumerate(reversed(channels)):
        if channel == "defaults":
            channel_order['main'] = priority
            channel_order['free'] = priority
            channel_order['pro'] = priority
            channel_order['r'] = priority
        else:
            channel_order[channel] = priority
        channel_order[""] = priority + 1  # highest priority for local installed packages

    nodes_to_remove = set()
    for name, versions in tqdm(all_package_nodes.items(), desc="Pruning dependency graph", position=4,
                               bar_format=BFMT, disable=QUIET):
        if name == "root":
            continue
        seen_keys = set()

        # if name == "ca-certificates":
        #     print(list(sorted(versions.keys(), key=lambda v: (channel_order[versions[v].channel_name] + versions[v].is_installed * (priority + 1), vparse(v)), reverse=True)))
        #     exit()

        # TODO the following line is also used in "base" and should be some kind of function import
        for v in sorted(versions.keys(),
                        key=lambda x: (channel_order[versions[x]["channel"]]
                                       + versions[x]["installed"] * (priority + 1), vparse(x[0])),
                        reverse=True):
            current_node = versions[v]

            # in_node_key = tuple(sorted([(n.name, n.version) for n in current_node.in_nodes]))
            # out_node_key = tuple(sorted([(n.name, n.version) for n in current_node.out_nodes]))
            in_key = tuple(sorted(set(g.neighbors(current_node, mode="in"))))
            out_key = tuple(sorted(set(g.neighbors(current_node, mode="out"))))
            key = (in_key, out_key)

            # if current_node.version[0] == "3.6.8":
            # print(current_node.channel_name, current_node.is_installed, current_node.name, current_node.version, key in seen_keys)

            if key in seen_keys:
                # the in-node out-node combination exist in a higher version of the same package
                # thus the higher version is ALWAYS preferable and this version can be removed
                nodes_to_remove.add(current_node)
            else:
                seen_keys.add(key)

    # remove the identified nodes
    g.delete_vertices(nodes_to_remove)
    # # optional: ony keep main connected component, i.e. the one containing the root vertex 0
    # main_component = next(filter(lambda x: 0 in x, g.components(mode="WEAK")))
    # g = g.induced_subgraph(main_component)
    return g


def distances_dependency_graph(g: Graph, root: Vertex):
    return g.shortest_paths(source=root, mode="out")[0]


def add_node_to_igraph(g: Graph) -> Vertex:
    global VERTEX_COUNT
    if VERTEX_COUNT >= len(g.vs):
        g.add_vertices(len(g.vs))
        g.vs[VERTEX_COUNT:]["name"] = ""
    VERTEX_COUNT += 1
    # print(VERTEX_COUNT)
    return g.vs[VERTEX_COUNT - 1]


def create_dependency_node(g: Graph,
                           dependency: List[str],
                           pname: str,
                           repodata: RepositoryData,
                           all_package_nodes: PackageNodeDict = defaultdict(dict),
                           all_dependency_nodes: DependencyNodeDict = dict(),
                           debug: bool = False,
                           edges: List[Tuple[Vertex, Vertex]] = [],
                           t: tqdm = None) -> Vertex:
    dependency = tuple(dependency)

    if dependency in all_dependency_nodes:
        return all_dependency_nodes[dependency]

    node = add_node_to_igraph(g)
    node["name"] = f"{dependency}"
    node["pname"] = pname,
    node["type"] = "dependency"
    t.total = g.vcount()
    t.update(1)

    all_dependency_nodes[dependency] = node

    valid = False
    for p_name, p_version in valid_packages(tuple(dependency), repodata):
        p_node = create_package_node(g, p_name, p_version, repodata, all_package_nodes=all_package_nodes,
                                     all_dependency_nodes=all_dependency_nodes, debug=debug, edges=edges, t=t)
        edges.append((node, p_node))
        valid = True

    if not valid:  # no versions were found for a dependency
        print_missing_package(dependency, debug=debug)
    node["invalid"] = not valid

    return node


global VERTEX_COUNT
VERTEX_COUNT = 0


def channel_name(data) -> str:
    if data is None or "channel" not in data:
        return ""
    return data['channel'].split('/')[-2]


def installed(data) -> bool:
    if data is None:
        return False
    # print(self.name, self.version, "installed" in self.p)
    return "installed" in data and data["installed"]


def create_package_node(g: Graph,
                        name: str,
                        version: str,
                        repodata: RepositoryData,
                        all_package_nodes: PackageNodeDict = defaultdict(dict),
                        all_dependency_nodes: DependencyNodeDict = dict(),
                        override_dependencies: List[str] = None,
                        debug: bool = False,
                        edges: List[Tuple[Vertex, Vertex]] = [],
                        t: tqdm = None) -> Vertex:
    if version in all_package_nodes[name]:
        return all_package_nodes[name][version]

    # create new node
    data = repodata.d[name].get(version, None)

    node = add_node_to_igraph(g)
    node["name"] = f"{name}-{version}"
    node["pname"] = name
    node["version"] = version
    node["data"] = data
    node["type"] = "package"
    node["channel"] = channel_name(data)
    node["installed"] = installed(data)
    node["mass_low"] = None
    node["mass_high"] = None

    t.total = g.vcount()
    t.update(1)

    all_package_nodes[name][version] = node

    if override_dependencies is not None:
        dependencies = override_dependencies
    else:
        dependencies = data["depends"]

    grouped_dependencies = defaultdict(list)

    for dependency in dependencies:
        dependency_name = split_package_constraint(dependency)[0]
        grouped_dependencies[dependency_name].append(dependency)

    # print(grouped_dependencies)

    for dependency in grouped_dependencies.values():
        # create dependency node
        d_node = create_dependency_node(g, dependency, name, repodata, all_package_nodes=all_package_nodes,
                                        all_dependency_nodes=all_dependency_nodes, debug=debug, edges=edges, t=t)
        edges.append((node, d_node))

    return node


def create_dependency_graph(channels: List[str],
                            packages: Set[str],
                            local_repodata: List[RepositoryData],
                            njobs: int = 8,
                            offline: bool = False,
                            force_download: bool = False,
                            debug: bool = False) -> Graph:
    repodata_chunks = get_repository_data(channels, njobs, offline, force_download)

    repodata = merge_repository_data(local_repodata + repodata_chunks)

    # create dependency_graph
    g = Graph(1000, directed=True)
    edges = []
    all_package_nodes = defaultdict(dict)
    with tqdm(total=1, desc="Building dependency graph", position=3, bar_format=BFMT, disable=QUIET) as t:
        root = create_package_node(g, "root", ("0", "0"), repodata, all_package_nodes=all_package_nodes,
                                   override_dependencies=packages, debug=debug, edges=edges, t=t)
        t.total = VERTEX_COUNT
    g.add_edges(edges)
    g = reduce_dependency_graph(g, all_package_nodes, channels)
    return g


def solve(g: Graph, channels: List[str]) -> List[Vertex]:
    root = g.vs[0]
    distances = distances_dependency_graph(g, root)

    # create new reduced all_package_nodes
    all_package_nodes = defaultdict(dict)
    for vertex in g.vs.select(type="package"):
        all_package_nodes[vertex["pname"]][vertex["version"]] = vertex
        vertex["x"] = LpVariable(vertex["name"], 0, 1, LpInteger)

    channel_order = dict()
    for priority, channel in enumerate(reversed(channels)):
        if channel == "defaults":
            channel_order['main'] = priority
            channel_order['free'] = priority
            channel_order['pro'] = priority
            channel_order['r'] = priority
        else:
            channel_order[channel] = priority
        channel_order[""] = priority + 1  # highest priority for local installed packages

    # create ILP problem
    prob = LpProblem("DependencySolve", LpMinimize)

    # build LP on the reduced dependency_graph
    objective = []

    prob += root["x"] == 1

    # n.p['channel'].split('/')[-2]

    # create brother information
    for name, versions in all_package_nodes.items():
        big_brother = None
        # small hack to make local always be the highest

        for v in sorted(versions.keys(),
                        key=lambda x: (channel_order[versions[x]["channel"]]
                                       + versions[x]["installed"] * (priority + 1), vparse(x[0])),
                        reverse=True):
            parent = versions[v]
            parent["big_brother"] = big_brother
            big_brother = parent

    def mass(v: Vertex):
        if v is None:
            return 0, 0

        #        if n.name == "attrs" and n.version == ('15.2.0', 'py36'):
        #            for children in n._out_nodes.values():
        #                print([(c.name, c.version) for c in children])
        #        print("\tmass", n.name, n.version)

        if v["mass_low"] is None:
            # n._mass_low = 0  # temporarily set mass to 0 for loops in dependency_graph
            # n._mass_high = 0  # temporarily set mass to 0 for loops in dependency_graph
            v["mass_low"] = 1
            v["mass_high"] = 1
            m_low = 0
            m_high = 0
            # print(n.name, n.distance_root)

            for dependency in v.neighbors(mode="out"):
                children = dependency.neighbors(mode="out")
                children_masses = [mass(c) for c in children if distances[c.index] > distances[v.index]]
                if len(children_masses) > 0:
                    m_low += min([c for c, _ in children_masses])
                    m_high += max([c for _, c in children_masses])
                else:
                    m_low = 0
                    m_high = 1
            # n._mass_low = m_low + 1 + mass(n.big_brother)[1]
            # n._mass_high = m_high + 1 + mass(n.big_brother)[1]
            v["mass_high"] = m_high - m_low + 1 + mass(v["big_brother"])[1]
            v["mass_low"] = 1 + mass(v["big_brother"])[1]
        return v["mass_low"], v["mass_high"]

    # for name, versions in all_nodes.items():
    #     for version, n in versions.items():
    #         print(name, version, mass(n))

    # breadth first search
    seen = [root]
    current_index = 0
    while current_index < len(seen):
        e = seen[current_index]
        for c in e.neighbors(mode="out"):
            if c not in seen:
                seen.append(c)
        current_index += 1

    #    for n in reversed(seen):
    #        print(n.name, n.version)
    #        mass(n)
    #    exit()

    # create ILP
    constraints = []
    foo = list(all_package_nodes.items())
    for name, versions in tqdm(foo, total=len(foo), desc="Formulating constraints",
                               position=5, bar_format=BFMT, disable=QUIET):
        # constraint: install at most one version of a package
        constraints.append(pulp.lpSum(n["x"] for n in versions.values()) <= 1)

        # constraint: if a parent is installed, one version of each dependency must be installed too
        for parent in versions.values():
            for dependency in parent.neighbors(mode="out"):
                if dependency["invalid"]:
                    constraints.append(parent["x"] == 0)
                    continue
                constraints.append(pulp.lpSum([d["x"] for d in dependency.neighbors(mode="out")]) >= parent["x"])

        # storing the objectives
        objective.extend([mass(n)[0] * n["x"] for n in versions.values()])

    prob.setObjective(pulp.lpSum(objective))
    prob.extend(constraints)
    prob.writeLP("WhiskasModel.lp")
    solvers = [GUROBI,
               GUROBI_CMD,
               GLPK_CMD,
               PYGLPK,
               PULP_CBC_CMD,
               CPLEX_DLL,
               CPLEX_CMD,
               CPLEX_PY,
               COIN_CMD,
               COINMP_DLL,
               XPRESS,
               YAPOSIB]
    solver = next(s for s in solvers if s().available())
    with tqdm(desc=f"Solving ILP (using {solver.__name__})", bar_format=BFMT, position=6, total=1, disable=QUIET) as t:
        prob.solve(solver(msg=False))
        t.update()

    if prob.status != LpStatusOptimal:
        if not QUIET:
            print('\n' * 7)
        print(f"ERROR: Solution is not optimal (status: {LpStatus[prob.status]}).\nAborting.", file=sys.stderr)
        exit(1)

    # for v in prob.variables():
    #     print(v.name, v.varValue)

    # collect all install nodes
    install_nodes = []
    dep_nodes = []
    for _, versions in sorted(all_package_nodes.items()):
        for n in versions.values():
            # print(n.name, n.version, n.x.varValue, "installed" in n.p)
            if n == root:  # skip root
                dep_nodes.extend(n.neighbors(mode="out"))
                continue
            x = n["x"]
            if x.varValue == 1.0:
                install_nodes.append(n)
                dep_nodes.extend(n.neighbors(mode="out"))
    return install_nodes, dep_nodes


missing_dependencies = set()


def print_missing_package(dependency: list, debug=False):
    if not debug:
        return
    # print missing package information for a dependency constraint
    # only print once by remembering
    dependency = tuple(dependency)
    if dependency not in missing_dependencies:
        print("WARNING:", "no packages found for", *dependency, file=sys.stderr)
        missing_dependencies.add(dependency)
