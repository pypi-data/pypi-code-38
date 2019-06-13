from unittest import TestCase

from py2neo import Graph

from sekg.graph.accessor import GraphAccessor
from sekg.graph.creator import NodeBuilder
from sekg.graph.factory import GraphInstanceFactory
from sekg.graph.index_accessor import IndexGraphAccessor


class TestGraphAccessor(TestCase):
    test_server_name = "LocalHost"
    test_config_path = "neo4j_config.json"
    test_server_id = 3

    def test_get_graph(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = GraphAccessor(graph=graph)
        self.assertTrue(isinstance(accessor.graph, Graph))

    def test_is_connect(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)
        accessor = GraphAccessor(graph=None)
        self.assertFalse(accessor.is_connect())
        accessor = GraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

    def test_create_or_drop_index_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)

        accessor = IndexGraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        node = accessor.create_or_update_node(node, primary_label="test", primary_property="api id")
        print(node)

        accessor.create_index(label="api class", property_name="api name")
        accessor.drop_index(label="api class", property_name="api name")

        graph.delete(node)
