import time
from unittest import TestCase

from py2neo import Graph

from sekg.graph.accessor import GraphAccessor
from sekg.graph.creator import NodeBuilder
from sekg.graph.factory import GraphInstanceFactory


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

    def test_create_or_update_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)

        accessor = GraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        node = accessor.create_or_update_node(node, primary_label="test", primary_property="api id")
        print(node)

        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api class", "entity"})
        self.assertEqual(node["api name"], "java.lang.Object")
        self.assertEqual(node["api id"], 4)

        graph.delete(node)

    def test_update_remote_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)

        accessor = GraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        node = accessor.create_or_update_node(node, primary_label="test", primary_property="api id")
        print(node)

        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api class", "entity"})
        self.assertEqual(node["api name"], "java.lang.Object")
        self.assertEqual(node["api id"], 4)

        node = accessor.update_remote_node(remote_node=node, property_dict={"api id": 5, "version": "1.0"},
                                           labels={"api interface", "api", "entity"})

        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api interface", "api", "entity"})
        self.assertEqual(node["api name"], "java.lang.Object")
        self.assertEqual(node["api id"], 5)
        self.assertEqual(node["version"], '1.0')

        graph.delete(node)

    def test_find_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_name(self.test_server_name)
        accessor = GraphAccessor(graph=graph)
        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        accessor.create_or_update_node(node, primary_label="api class", primary_property="api id")
        node = accessor.find_node(primary_label="api class", primary_property="api id", primary_property_value=4)
        self.assertIsNotNone(node)
        graph.delete(node)
        node = accessor.find_node(primary_label="api class", primary_property="api id", primary_property_value=4)
        self.assertIsNone(node)

    def test_find_relation_by_id(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_name(self.test_server_name)
        accessor = GraphAccessor(graph=graph)

        start_node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                              property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        start_node = accessor.create_or_update_node(start_node, primary_label="api class", primary_property="api id")
        end_node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                            property_value=6).add_one_property(
            property_name="api name", property_value="java.lang.String").build()
        end_node = accessor.create_or_update_node(end_node, primary_label="api class", primary_property="api id")

        relation = accessor.create_relation_without_duplicate(start_node=start_node, end_node=end_node,
                                                              relation_str="call by")
        self.assertIsNotNone(relation)
        self.assertEqual(accessor.get_relation_type_string(relation), "call by")

        found_relation = accessor.find_relation_by_id(relation.identity)
        self.assertIsNotNone(found_relation)

        self.assertEqual(found_relation.identity, relation.identity)
        old_relation_id = relation.identity
        graph.delete(relation)
        found_relation = accessor.find_relation_by_id(old_relation_id)

        self.assertIsNone(found_relation)

    def test_create_relation_without_duplicate(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_name(self.test_server_name)
        accessor = GraphAccessor(graph=graph)

        start_node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                              property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        start_node = accessor.create_or_update_node(start_node, primary_label="api class", primary_property="api id")
        end_node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                            property_value=6).add_one_property(
            property_name="api name", property_value="java.lang.String").build()
        end_node = accessor.create_or_update_node(end_node, primary_label="api class", primary_property="api id")

        relation = accessor.create_relation_without_duplicate(start_node=start_node, end_node=end_node,
                                                              relation_str="call by")
        self.assertIsNotNone(relation)
        self.assertEqual(accessor.get_relation_type_string(relation), "call by")
        graph.delete(relation)

    def test_update_metadata(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_name(self.test_server_name)
        accessor = GraphAccessor(graph=graph)
        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        node = accessor.create_or_update_node(node, primary_label="api class", primary_property="api id")

        create_time = node["_create_time"]
        update_time = node["_update_time"]
        modify_version = node["_modify_version"]

        self.assertIsNotNone(create_time)
        self.assertIsNotNone(update_time)
        self.assertIsNotNone(modify_version)

        time.sleep(1)

        accessor.update_metadata(node)

        self.assertEqual(modify_version + 1, node["_modify_version"])
        self.assertEqual(create_time, node["_create_time"])
        self.assertNotEqual(update_time, node["_update_time"])

    def test_update_remote_node_by_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)

        accessor = GraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        node = accessor.create_or_update_node(node, primary_label="test", primary_property="api id")

        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api class", "entity"})
        self.assertEqual(node["api name"], "java.lang.Object")
        self.assertEqual(node["api id"], 4)

        node = accessor.update_remote_node(remote_node=node, property_dict={"api id": 5, "version": "1.0"},
                                           labels={"api interface", "api", "entity"})

        modify_node = NodeBuilder().add_entity_label().add_label("api").add_label("api interface").add_one_property(
            property_name="api id",
            property_value=5).add_one_property(
            property_name="version", property_value="1.0").build()

        accessor.update_remote_node_by_node(remote_node=node, source_node=modify_node)
        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api interface", "api", "entity"})
        self.assertEqual(node["api name"], "java.lang.Object")
        self.assertEqual(node["api id"], 5)
        self.assertEqual(node["version"], '1.0')

        graph.delete(node)

    def test_find_node_by_id(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_name(self.test_server_name)
        accessor = GraphAccessor(graph=graph)
        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=4).add_one_property(
            property_name="api name", property_value="java.lang.Object").build()

        accessor.create_or_update_node(node, primary_label="api class", primary_property="api id")
        node = accessor.find_node(primary_label="api class", primary_property="api id", primary_property_value=4)
        self.assertIsNotNone(node)

        node = accessor.find_node_by_id(node_id=node.identity)
        self.assertIsNotNone(node)
        graph.delete(node)

    def test_create_node(self):
        factory = GraphInstanceFactory(self.test_config_path)
        graph = factory.create_py2neo_graph_by_server_id(self.test_server_id)

        accessor = GraphAccessor(graph=graph)
        self.assertTrue(accessor.is_connect())

        node = accessor.find_node(primary_label="api class", primary_property="api id", primary_property_value=8)
        self.assertIsNone(node)

        node = NodeBuilder().add_entity_label().add_label("api class").add_one_property(property_name="api id",
                                                                                        property_value=8).add_one_property(
            property_name="api name", property_value="java.lang.String").add_one_property(property_name="type",
                                                                                          property_value="int").build()

        node = accessor.create_node(node)

        self.assertTrue(accessor.is_remote(node))
        self.assertEqual(node.labels, {"api class", "entity"})
        self.assertEqual(node["api name"], "java.lang.String")
        self.assertEqual(node["api id"], 8)
        self.assertEqual(node["type"], "int")

        graph.delete(node)
