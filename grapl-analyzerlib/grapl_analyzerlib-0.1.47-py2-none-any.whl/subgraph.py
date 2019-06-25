from typing import TypeVar, Dict, List, Any, Iterator

from grapl_analyzerlib import graph_description_pb2
from grapl_analyzerlib.file import F
from grapl_analyzerlib.node import NodeView, EdgeView
from grapl_analyzerlib.process import P

S = TypeVar("S", bound="SubgraphView")


class SubgraphView(object):
    def __init__(
            self, nodes: Dict[str, NodeView], edges: Dict[str, List[EdgeView]]
    ) -> None:
        self.nodes = nodes
        self.edges = edges

    @staticmethod
    def from_proto(s: bytes) -> S:
        subgraph = graph_description_pb2.GraphDescription()
        subgraph.ParseFromString(s)

        nodes = {key: NodeView.from_key(key) for key in subgraph.subgraph.nodes}
        return SubgraphView(nodes, subgraph.subgraph.edges)

    def process_iter(self) -> Iterator[P]:
        for node in self.nodes.values():
            maybe_node = node.as_process_view()
            if maybe_node:
                yield maybe_node

    def file_iter(self) -> Iterator[F]:
        for node in self.nodes.values():
            maybe_node = node.as_file_view()
            if maybe_node:
                yield maybe_node

