import json
from copy import deepcopy
from typing import TypeVar, Optional, List, Dict, Any, Union, Set

from pydgraph import DgraphClient

import grapl_analyzerlib.entity_queries as entity_queries
import grapl_analyzerlib.file as file


P = TypeVar("P", bound="ProcessView")
PQ = TypeVar("PQ", bound="ProcessQuery")


class ProcessQuery(object):
    def __init__(self) -> None:
        # Properties
        self._node_key = None  # type: Optional[entity_queries.Cmp]
        self._process_name = []  # type: List[List[entity_queries.Cmp]]
        self._process_command_line = []  # type: List[List[entity_queries.Cmp]]
        self._process_guid = []  # type: List[List[entity_queries.Cmp]]
        self._process_id = []  # type: List[List[entity_queries.Cmp]]
        self._created_timestamp = []  # type: List[List[entity_queries.Cmp]]
        self._terminated_timestamp = []  # type: List[List[entity_queries.Cmp]]
        self._last_seen_timestamp = []  # type: List[List[entity_queries.Cmp]]

        # Edges
        self._parent = None  # type: Optional[PQ]
        self._bin_file = None  # type: Optional[FQ]
        self._children = None  # type: Optional[PQ]
        self._deleted_files = None  # type: Optional[FQ]

        # Meta
        self._first = None  # type: Optional[int]

    def with_node_key(self, node_key: Optional[str]=None):
        if node_key:
            self._node_key = entity_queries.Eq('node_key', node_key)
        else:
            self._node_key = entity_queries.Has('node_key')
        return self

    def only_first(self, first: int) -> PQ:
        self._first = first
        return self

    def get_count(self, dgraph_client: DgraphClient):
        raise NotImplementedError

    def _get_var_block(self, binding_num: int, root: Any, already_converted: Set[Any]) -> str:
        if self in already_converted:
            return ""
        already_converted.add(self)

        filters = self._filters()

        parent = entity_queries.get_var_block(
            self._parent, "~children", binding_num, root, already_converted
        )

        children = entity_queries.get_var_block(
            self._children, "children", binding_num, root, already_converted
        )

        deleted_files = entity_queries.get_var_block(
            self._deleted_files, "deleted_files", binding_num, root, already_converted
        )

        block = f"""
            {filters} {{
                {parent}
                {children}
                {deleted_files}
            }}
            """

        return block

    def _get_var_block_root(self, binding_num: int, root: Any, node_key: str) -> str:
        already_converted = {self}
        root_var = ""
        if self == root:
            root_var = f"Binding{binding_num} as "

        filters = self._filters()

        parent = entity_queries.get_var_block(
            self._parent, "~children", binding_num, root, already_converted
        )

        children = entity_queries.get_var_block(
            self._children, "children", binding_num, root, already_converted
        )

        deleted_files = entity_queries.get_var_block(
            self._deleted_files, "deleted_files", binding_num, root, already_converted
        )

        bin_file = entity_queries.get_var_block(
            self._bin_file, "bin_file", binding_num, root, already_converted
        )

        block = f"""
            {root_var} var(func: eq(node_key, "{node_key}")) {filters} {{
                {parent}
                {children}
                {deleted_files}
                {bin_file}
            }}
            """

        return block

    def get_neighbors(self) -> List[Any]:
        neighbors = [self._parent, self._bin_file, self._children, self._deleted_files]

        return [n for n in neighbors if n]

    def with_process_name(
            self,
            eq: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            contains: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            ends_with: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._process_name.extend( entity_queries._str_cmps("process_name", eq, contains, ends_with))
        return self

    def with_process_command_line(
            self,
            eq: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            contains: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            ends_with: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._process_command_line.extend(
             entity_queries._str_cmps("process_command_line", eq, contains, ends_with)
        )
        return self

    def with_process_guid(
            self,
            eq: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            contains: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            ends_with: Optional[Union[str, List[str],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._process_guid.extend( entity_queries._str_cmps("process_guid", eq, contains, ends_with))
        return self

    def with_process_id(
            self,
            eq: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            gt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            lt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._process_id.extend(entity_queries._int_cmps("process_id", eq, gt, lt))
        return self

    def with_created_timestamp(
            self,
            eq: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            gt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            lt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._created_timestamp.extend(entity_queries._int_cmps("created_timestamp", eq, gt, lt))
        return self

    def with_terminated_timestamp(
            self,
            eq: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            gt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            lt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._terminated_timestamp.extend(entity_queries._int_cmps("terminated_timestamp", eq, gt, lt))
        return self

    def with_last_seen_timestamp(
            self,
            eq: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            gt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
            lt: Optional[Union[str, List[int],  entity_queries.Not, List[ entity_queries.Not]]] = None,
    ) -> PQ:
        self._last_seen_timestamp.extend(entity_queries._int_cmps("last_seen_timestamp", eq, gt, lt))
        return self

    def _filters(self) -> str:
        inner_filters = (
            entity_queries._generate_filter(self._process_name),
            entity_queries._generate_filter(self._process_command_line),
            entity_queries._generate_filter(self._process_guid),
            entity_queries._generate_filter(self._process_id),
        )

        inner_filters = [i for i in inner_filters if i]
        if not inner_filters:
            return ""
        return f"@filter({'AND'.join(inner_filters)})"

    def with_parent(self, process: PQ) -> PQ:
        process = deepcopy(process)
        process._children = self
        self._parent = process
        return self

    def with_bin_file(self, file: file.FQ) -> PQ:
        file = deepcopy(file)
        file._spawned_from = self
        self._bin_file = file
        return self

    def with_deleted_files(self, file: file.FQ) -> PQ:
        file = deepcopy(file)
        file._deleter = self
        self._deleted_files = file
        return self

    def with_children(self, children: PQ) -> PQ:
        children = deepcopy(children)
        children._parent = self
        self._children = children
        return self

    def _to_query(self, first: int) -> str:

        return ""

    def query_first(
            self, dgraph_client, contains_node_key=None
    ) -> Optional[P]:
        if contains_node_key:
            query_str = entity_queries.get_queries(self, node_key=contains_node_key)
        else:
            query_str = self._to_query(first=True)

        raw_views = json.loads(dgraph_client.txn(read_only=True).query(query_str).json)[
            "res"
        ]

        if not raw_views:
            return None

        return P.from_dict(dgraph_client, raw_views[0])



class ProcessView(node.NodeView):
    def __init__(
            self,
            dgraph_client: DgraphClient,
            node_key: str,
            uid: Optional[str],
            image_name: Optional[str],
            bin_file: Optional[F],
            parent: Optional[P],
            children: Optional[List[P]],
            deleted_files: Optional[List[F]],
            create_time: Optional[int],
            terminate_time: Optional[int],
    ) -> None:
        self.dgraph_client = dgraph_client  # type: DgraphClient
        self.node_key = node_key  # type: str
        self.uid = uid  # type: Optional[str]
        self.image_name = image_name  # type: Optional[str]
        self.bin_file = bin_file  # type: Optional[F]
        self.children = children  # type: Optional[List[P]]
        self.parent = parent  # type: Optional[P]
        self.deleted_files = deleted_files  # type: Optional[List[F]]
        self.create_time = create_time  # type: Optional[int]
        self.terminate_time = terminate_time  # type: Optional[int]

    @staticmethod
    def from_dict(dgraph_client: DgraphClient, d: Dict[str, Any]) -> P:
        raw_bin_file = d.get("bin_file", None)

        bin_file = None

        if raw_bin_file:
            bin_file = file.FileView.from_dict(dgraph_client, raw_bin_file)

        raw_parent = d.get("~children", None)

        parent = None

        if raw_parent:
            parent = ProcessView.from_dict(dgraph_client, raw_parent)

        raw_deleted_files = d.get("deleted_files", None)

        deleted_files = None

        if raw_deleted_files:
            deleted_files = [
                file.FileView.from_dict(dgraph_client, f) for f in d["deleted_files"]
            ]

        raw_children = d.get("children", None)

        children = None  # type: Optional[List[P]]
        if raw_children:
            children = [
                ProcessView.from_dict(dgraph_client, child) for child in d["children"]
            ]

        return ProcessView(
            dgraph_client=dgraph_client,
            node_key=d["node_key"],
            uid=d.get("uid", None),
            image_name=d.get("image_name", None),
            bin_file=bin_file,
            children=children,
            parent=parent,
            create_time=d.get("create_time", None),
            deleted_files=deleted_files,
            terminate_time=d.get("terminate_time", None),
        )

    def get_image_name(self) -> Optional[str]:
        if self.image_name:
            return self.image_name

        self_process = (
            ProcessQuery()
            .with_node_key(self.node_key)
            .with_process_name()
            .query_first(dgraph_client=self.dgraph_client)
        )

        if not self_process:
            return None

        self.image_name = self_process[0].image_name
        return self.image_name

    def get_parent(self) -> Optional[P]:
        if self.parent:
            return self.parent

        parent = (
            ProcessQuery()
            .with_children(ProcessQuery().with_node_key(self.node_key))
            .query_first(self.dgraph_client)
        )

        if not parent:
            return None

        self.parent = parent
        return self.parent

    def get_uid(self):
        # type: () -> str
        if self.uid:
            return self.uid

        process = (
            ProcessQuery()
            .with_node_key(self.node_key)
            .with_uid()
            .query_first(self.dgraph_client)
        )

        assert process
        self.uid = process.uid
        return process.uid

    def get_bin_file(self) -> Optional[F]:
        if self.bin_file:
            return self.bin_file

        query = (
            ProcessQuery()
                .with_node_key(self.node_key)
                .with_bin_file(file.FileQuery())
                .to_query()
        )

        res = json.loads(self.dgraph_client.txn(read_only=True).query(query).json)

        bin_file = res["q0"]["bin_file"]
        self.bin_file = file.FileView.from_dict(self.dgraph_client, bin_file)
        return self.bin_file

    def get_deleted_files(self) -> Optional[List[F]]:
        if self.deleted_files:
            return self.deleted_files

        deleted_files = (
            ProcessQuery()
            .with_node_key(self.node_key)
            .with_deleted_files(file.FileQuery().with_node_key())
            .query()
        )

        if not deleted_files:
            return None

        self.deleted_files = deleted_files[0].deleted_files
        return self.deleted_files
