from typing import TypeVar, Union, Optional

import grapl_analyzerlib.file as file
import grapl_analyzerlib.process as process


N = TypeVar("N", bound="NodeView")

class NodeView(object):
    def from_key(self, node_key: str) -> N:
        raise NotImplementedError

    def as_process_view(self) -> Optional[process.P]:
        if isinstance(self, process.ProcessView):
            return self
        return None

    def as_file_view(self) -> Optional[file.F]:
        if isinstance(self, file.FileView):
            return self
        return None


class EdgeView(object):
    def __init__(
        self, from_neighbor_key: str, to_neighbor_key: str, edge_name: str
    ) -> None:
        self.from_neighbor_key = from_neighbor_key
        self.to_neighbor_key = to_neighbor_key
        self.edge_name = edge_name
