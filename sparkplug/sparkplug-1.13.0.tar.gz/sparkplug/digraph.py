import collections


class CyclicGraphError(Exception):
    pass


class Digraph(object):
    """An acyclic, directed graph.
    
        >>> g = Digraph()
        >>> g.add_edge('a', 'b')
        >>> g.add_edge('a', 'c')
        >>> g.add_edge('b', 'c')

    You can use a digraph to compute topological orderings (eg. for
    dependencies):

        >>> g.sorted()
        ['a', 'b', 'c']

    Graphs can contain unconnected nodes:
    
        >>> g.add_node('d')
        >>> 'd' in g.sorted()
        True

    """
    def __init__(self, nodes=None, edges=None):
        self.outbound_edges = collections.defaultdict(set)
        self.inbound_edges = collections.defaultdict(set)
        self.nodes = set()
        if nodes is not None:
            self.nodes.update(nodes)
        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, outbound, inbound):
        self.add_node(inbound)
        self.add_node(outbound)
        self.outbound_edges[outbound].add(inbound)
        self.inbound_edges[inbound].add(outbound)

    def remove_edge(self, outbound, inbound):
        self.outbound_edges[outbound].remove(inbound)
        self.inbound_edges[inbound].remove(outbound)

    def edges(self):
        for node, outbounds in self.outbound_edges.items():
            for outbound in outbounds:
                yield (node, outbound)

    def outbound_from(self, node):
        return set(self.outbound_edges[node])

    def inbound_to(self, node):
        return set(self.inbound_edges[node])

    def dup(self):
        return type(self)(self.nodes, self.edges())

    def sorted(self):
        # Following topological sort taken from:
        # Kahn, Arthur B. (1962), "Topological sorting of large networks",
        # Communications of the ACM 5 (11): 558-562, doi:10.1145/368996.369025.

        # Scratch space, so we don't invalidate _this_ graph
        graph = self.dup()

        nodes = []
        roots = set(
            node for node in graph.nodes if not graph.inbound_to(node)
        )

        while roots:
            next_node = roots.pop()
            nodes.append(next_node)
            for node in graph.outbound_from(next_node):
                graph.remove_edge(next_node, node)
                if not graph.inbound_to(node):
                    roots.add(node)

        assert not list(graph.edges())
        return nodes
