from unittest import TestCase

from py2neo import Graph

from sekg.graph.accessor import GraphAccessor
from sekg.graph.metadata_accessor import MetadataGraphAccessor
from sekg.graph.creator import NodeBuilder
from sekg.graph.factory import GraphInstanceFactory
from sekg.graph.index_accessor import IndexGraphAccessor


class TestMetadataAccessor(TestCase):
    test_server_name = "LocalHost"
    test_config_path = "neo4j_config.json"
    test_server_id = 3

    def test_get_max_id_for_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result = accessor.get_max_id_for_node()
        print(result)

    def test_get_max_id_for_relation(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result = accessor.get_max_id_for_relation()
        print(result)

    def test_get_node_num(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result_1 = accessor.get_node_num()
        print("all nodes: ", result_1)
        result_2 = accessor.get_node_num("api method")
        print("api method: ", result_2)

    def test_get_relation_num(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result = accessor.get_relation_num()
        print(result)

    def test_count_relation_type(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result = accessor.count_relation_type()
        print(result)

    def test_expand_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = MetadataGraphAccessor(graph=graph)
        result = accessor.expand_node(2226, 10)
        print(result)
