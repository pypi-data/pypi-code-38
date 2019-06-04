# -*- coding: utf-8 -*-


class QueriesStore(object):

    def __init__(self):
        self.__queries = []

    def add_query(self, query, volume_id):
        query_obj = QueryObj(query, volume_id)
        self._add_query_obj(query_obj)

    def _add_query_obj(self, query_obj):
        if not self._was_query_added(query_obj):
            self.__queries.append(query_obj)

    def add_query_objects(self, query_objects):
        for query_obj in query_objects:
            self._add_query_obj(query_obj)

    def _was_query_added(self, query_obj):
        return any(existing == query_obj for existing in self.__queries)

    def get_all_query_obj(self):
        return self.__queries

    def _get_first_query_obj(self):
        return self.__queries and self.__queries[0]

    def get_all(self):
        return [q.dump_without_version() for q in self.__queries]

    def get_first(self):
        first = self._get_first_query_obj()
        return first and first.dump_without_version()

    @property
    def is_empty(self):
        return len(self.__queries) == 0


class QueryObj(object):

    def __init__(self, query, volume_id):
        self.query = query
        self.volume_id = volume_id

    def __eq__(self, other):
        return self.query == other.query and self.volume_id == other.volume_id

    def dump_without_version(self):
        query_without_version, version = self.remove_version_part(self.query)
        return {
            'query': query_without_version,
            'version': version,
            'volume_id': self.volume_id,
        }

    @classmethod
    def remove_version_part(cls, query):
        from missinglink.legit.scam import LuceneTreeTransformer, QueryParser, resolve_tree, FunctionVersion
        from missinglink.legit.scam.luqum.tree import AndOperation, OrOperation

        # noinspection PyClassicStyleClass
        class RemoveVersionTransformer(LuceneTreeTransformer):
            def __init__(self):
                self.version = None

            def visit_operation(self, klass, node, _parents):
                new_node = klass(*list(self.__enum_children(node)))
                return new_node

            def __enum_children(self, node):
                for child in node.children:
                    if isinstance(child, FunctionVersion):
                        self.version = child.version
                        continue

                    yield child

            def visit_and_operation(self, node, parents=None):
                return self.visit_operation(AndOperation, node, parents)

            def visit_or_operation(self, node, parents=None):
                return self.visit_operation(OrOperation, node, parents)

            def __call__(self, query_tree):
                return self.visit(query_tree)

        transformer = RemoveVersionTransformer()
        parsed_tree = QueryParser().parse_query(query)
        resolved_tree = resolve_tree(parsed_tree)
        resolved_tree = transformer(resolved_tree)

        query_without_version = str(resolved_tree)

        return query_without_version, transformer.version
