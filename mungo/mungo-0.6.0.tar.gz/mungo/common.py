from igraph import Graph
from tqdm import _tqdm, tqdm
from fastcache import lru_cache

from mungo.conda.models.version import VersionOrder

mungoversion = "0.6.0"

PBAR_FMT = "{desc:<40}{percentage:3.0f}%| {bar} {n_fmt:>5}/{total_fmt:>5} [{elapsed}] {postfix}"


def format_interval(t):
    return '{0:.2f}s'.format(t)


_tqdm.format_interval = format_interval
tqdm.format_interval = format_interval


@lru_cache(maxsize=None)
def vparse(x: str, add: str = "") -> VersionOrder:
    # TODO: remove strip?
    if x != "*":
        x = x.strip("*").strip(".")
    return VersionOrder(f"{x}{add}")


def print_dag(packages: list, g: Graph, to_install: list, dep_nodes: list, installed: dict = None):
    # all_nodes = to_install + dep_nodes
    # sg = g.subgraph(all_nodes)
    # layout = sg.layout("fr")
    # color_map = {'dependency': 'blue', 'package': 'orange'}
    # style = {'vertex_label': [(v["pname"] + str(v["version"])) if v["type"] == "package" else v["name"] for v in sg.vs],
    #          'vertex_shape': 'rectangle',
    #          'vertex_size': 60,
    #          'vertex_color': [color_map[t] for t in sg.vs["type"]],
    #          'bbox': (1280, 1280),
    #          'margin': 50,
    #          }
    # p = plot(sg, layout=layout, **style)
    from graphviz import Digraph
    dot = Digraph()
    # dot.attr("graph", splines="false")

    # ugly, but sufficient for the time being
    to_install2 = {node['data']['name']: node['data'] for node in to_install if node['type'] == 'package'}
    installed_keys = installed.keys() if installed is not None else {}
    changed = installed_keys & to_install2.keys()
    local_versions = {name: list(installed[name].values())[0] for name in changed}
    remote_versions = {name: data for name, data in to_install2.items() if name in changed}
    version_changes = {package: (local_versions[package], remote_versions[package]) for package in changed}
    upgrades = {package: (p_from, p_to)
                for (package, (p_from, p_to)) in version_changes.items()
                # if vparse(([p_from['version'], p_from['build']])) < vparse(([p_to['version'], p_to['build']]))
                if vparse(p_from['version']) < vparse(p_to['version'])
                }
    downgrades = {package: (p_from, p_to)
                  for (package, (p_from, p_to)) in version_changes.items()
                  if vparse(p_from['version']) > vparse(p_to['version'])
                  # if vparse(([p_from['version'], p_from['build']])) > vparse(([p_to['version'], p_to['build']]))}
                  }
    # nodes
    sg = g.subgraph(to_install + dep_nodes)
    out_nodes = set()
    for vertex in sg.vs.select(type='package'):
        # color = "white" if v.name not in changed else "red"
        requested = vertex['pname'] in packages
        upgrade = vertex['pname'] in upgrades
        downgrade = vertex['pname'] in downgrades
        local = vertex['pname'] in installed_keys
        kwargs = {
            # 'shape': "house" if upgrade else "invhouse" if downgrade else "folder" if local else "note",
            'shape': "folder" if local else "note",
            'fillcolor': "#C0E2E7" if requested else "#CFE7C0" if upgrade else "#E7C6C0" if downgrade else "white",
            'style': 'filled',
            'fontname': 'Fira Sans',
        }
        dot.node(f"{vertex['pname']}_{vertex['version']}",
                 f"{vertex['pname']}\n{vertex['version'][0]} {vertex['version'][1]}", **kwargs)
        out_nodes.add(vertex)

    # edges
    for vertex in sg.vs.select(type='package'):
        deps = vertex.neighbors(mode='out')
        for dep in deps:
            pkgs = dep.neighbors(mode='out')
            for pkg in pkgs:
                if pkg in out_nodes:
                    kwargs = {
                        'fontname': 'Fira Sans',
                    }
                    from_label = f"{vertex['pname']}_{vertex['version']}"
                    to_label = f"{pkg['pname']}_{pkg['version']}"
                    dot.edge(from_label, to_label,
                             label='\n'.join(dep['name'].strip('()\',').split(' ')),
                             **kwargs)
    dot.render('graph.tmp', view=True)
    # print(dot.source)
