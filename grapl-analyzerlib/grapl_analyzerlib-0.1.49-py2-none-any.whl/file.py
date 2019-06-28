from copy import deepcopy
from typing import TypeVar, Optional, List, Dict, Any

from pydgraph import DgraphClient

import grapl_analyzerlib.entity_queries as entity_queries
import grapl_analyzerlib.node as node
import grapl_analyzerlib.process as process

F = TypeVar("F", bound="FileView")
FQ = TypeVar("FQ", bound="FileQuery")


class FileQuery(object):
    def __init__(self) -> None:
        # Attributes
        self._node_key = None  # type: Optional[entity_queries.Cmp]
        self._file_name = []  # type: List[List[entity_queries.Cmp]]
        self._file_path = []  # type: List[List[entity_queries.Cmp]]
        self._file_extension = []  # type: List[List[entity_queries.Cmp]]
        self._file_mime_type = []  # type: List[List[entity_queries.Cmp]]
        self._file_size = []  # type: List[List[entity_queries.Cmp]]
        self._file_version = []  # type: List[List[entity_queries.Cmp]]
        self._file_description = []  # type: List[List[entity_queries.Cmp]]
        self._file_product = []  # type: List[List[entity_queries.Cmp]]
        self._file_company = []  # type: List[List[entity_queries.Cmp]]
        self._file_directory = []  # type: List[List[entity_queries.Cmp]]
        self._file_inode = []  # type: List[List[entity_queries.Cmp]]
        self._file_hard_links = []  # type: List[List[entity_queries.Cmp]]
        self._md5_hash = []  # type: List[List[entity_queries.Cmp]]
        self._sha1_hash = []  # type: List[List[entity_queries.Cmp]]
        self._sha256_hash = []  # type: List[List[entity_queries.Cmp]]

        # Edges
        self._creator = None  # type: Optional[process.PQ]
        self._deleter = None  # type: Optional[process.PQ]
        self._writers = None  # type: Optional[process.PQ]
        self._readers = None  # type: Optional[process.PQ]
        self._spawned_from = None  # type: Optional[process.PQ]

    def with_node_key(self, node_key: Optional[str]=None):
        if node_key:
            self._node_key = entity_queries.Eq('node_key', node_key)
        else:
            self._node_key = entity_queries.Has('node_key')
        return self

    def with_file_name(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_name.extend(entity_queries._str_cmps("file_name", eq, contains, ends_with))
        return self

    def with_file_path(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_path.extend(entity_queries._str_cmps("file_path", eq, contains, ends_with))
        return self

    def with_file_extension(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_extension.extend(
            entity_queries._str_cmps("file_extension", eq, contains, ends_with)
        )
        return self

    def with_file_mime_type(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_mime_type.extend(
            entity_queries._str_cmps("file_mime_type", eq, contains, ends_with)
        )
        return self

    def with_file_size(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_size.extend(entity_queries._str_cmps("file_size", eq, contains, ends_with))
        return self

    def with_file_version(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_version.extend(entity_queries._str_cmps("file_version", eq, contains, ends_with))
        return self

    def with_file_description(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_description.extend(
            entity_queries._str_cmps("file_description", eq, contains, ends_with)
        )
        return self

    def with_file_product(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_product.extend(entity_queries._str_cmps("file_product", eq, contains, ends_with))
        return self

    def with_file_company(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_company.extend(entity_queries._str_cmps("file_company", eq, contains, ends_with))
        return self

    def with_file_directory(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_directory.extend(
            entity_queries._str_cmps("file_directory", eq, contains, ends_with)
        )
        return self

    def with_file_inode(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_inode.extend(entity_queries._str_cmps("file_inode", eq, contains, ends_with))
        return self

    def with_file_hard_links(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._file_hard_links.extend(
            entity_queries._str_cmps("file_hard_links", eq, contains, ends_with)
        )
        return self

    def with_md5_hash(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._md5_hash.extend(entity_queries._str_cmps("md5_hash", eq, contains, ends_with))
        return self

    def with_sha1_hash(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._sha1_hash.extend(entity_queries._str_cmps("sha1_hash", eq, contains, ends_with))
        return self

    def with_sha256_hash(self, eq=None, contains=None, ends_with=None) -> FQ:
        self._sha256_hash.extend(entity_queries._str_cmps("sha256_hash", eq, contains, ends_with))
        return self

    def with_creator(self, creator: process.PQ) -> FQ:
        creator = deepcopy(creator)
        self._creator = creator
        return self

    def with_deleter(self, deleter: process.PQ) -> FQ:
        deleter = deepcopy(deleter)
        self._deleter = deleter
        deleter._deleted_files = self
        return self

    def with_writers(self, writers: process.PQ) -> FQ:
        writers = deepcopy(writers)
        self._writers = writers
        return self

    def with_readers(self, readers: process.PQ) -> FQ:
        readers = deepcopy(readers)
        self._readers = readers
        readers._read_files = self
        return self

    def _get_var_block(self, binding_num, root, already_converted) -> str:
        if self in already_converted:
            return ""
        already_converted.add(self)

        filters = self._filters()

        creator = entity_queries.get_var_block(
            self._creator, "~created_files", binding_num, root, already_converted
        )

        deleter = entity_queries.get_var_block(
            self._deleter, "~deleted_files", binding_num, root, already_converted
        )

        writers = entity_queries.get_var_block(
            self._writers, "~wrote_files", binding_num, root, already_converted
        )

        readers = entity_queries.get_var_block(
            self._readers, "~read_files", binding_num, root, already_converted
        )

        block = f"""
            @cascade {filters} {{
                {creator}
                {deleter}
                {writers}
                {readers}
            }}
            """

        return block

    def _get_var_block_root(self, binding_num, root, node_key):
        already_converted = {self}
        root_var = ""
        if self == root:
            root_var = f"Binding{binding_num} as "

        filters = self._filters()

        creator = entity_queries.get_var_block(
            self._creator, "~created_files", binding_num, root, already_converted
        )

        deleter = entity_queries.get_var_block(
            self._deleter, "~deleted_files", binding_num, root, already_converted
        )

        writers = entity_queries.get_var_block(
            self._writers, "~wrote_files", binding_num, root, already_converted
        )

        readers = entity_queries.get_var_block(
            self._readers, "~read_files", binding_num, root, already_converted
        )

        spawned_from = entity_queries.get_var_block(
            self._spawned_from, "~bin_file", binding_num, root, already_converted
        )

        block = f"""
            {root_var} var(func: entity_queries.Eq(node_key, "{node_key}")) @cascade {filters} {{
                {creator}
                {deleter}
                {writers}
                {readers}
                {spawned_from}
            }}
            """

        return block

    def _filters(self) -> str:
        inner_filters = (
             entity_queries._generate_filter(self._file_name),
             entity_queries._generate_filter(self._file_path),
             entity_queries._generate_filter(self._file_extension),
             entity_queries._generate_filter(self._file_mime_type),
             entity_queries._generate_filter(self._file_size),
             entity_queries._generate_filter(self._file_version),
             entity_queries._generate_filter(self._file_description),
             entity_queries._generate_filter(self._file_product),
             entity_queries._generate_filter(self._file_company),
             entity_queries._generate_filter(self._file_directory),
             entity_queries._generate_filter(self._file_inode),
             entity_queries._generate_filter(self._file_hard_links),
             entity_queries._generate_filter(self._md5_hash),
             entity_queries._generate_filter(self._sha1_hash),
             entity_queries._generate_filter(self._sha256_hash),
        )

        inner_filters = [i for i in inner_filters if i]
        if not inner_filters:
            return ""

        return f"@filter({'AND'.join(inner_filters)})"

    def get_neighbors(self) -> List[Any]:
        neighbors = [
            self._creator,
            self._deleter,
            self._writers,
            self._readers,
            self._spawned_from,
        ]

        return [n for n in neighbors if n]


class FileView(node.NodeView):
    def __init__(
            self,
            dgraph_client: DgraphClient,
            node_key: str,
            uid: Optional[str],
            path: Optional[str],
    ) -> None:
        self.dgraph_client = dgraph_client  # type: DgraphClient
        self.node_key = node_key  # type: Optional[str]
        self.uid = uid  # type: Optional[str]
        self.path = path  # type: Optional[str]

    @staticmethod
    def from_dict(dgraph_client: DgraphClient, d: Dict[str, Any]) -> F:
        return FileView(
            dgraph_client=dgraph_client,
            node_key=d["node_key"],
            uid=d.get("uid"),
            path=d.get("path"),
        )
