from unittest import TestCase

from py2neo import Graph, Node

from sekg.graph.factory import GraphInstanceFactory


class TestGraphInstanceFactory(TestCase):

    def test_create_py2neo_graph_by_server_name(self):
        factory = GraphInstanceFactory("neo4j_config.json")
        graph2 = factory.create_py2neo_graph_by_server_id(2)
        self.assertIsNotNone(graph2)
        self.assertTrue(type(graph2) == Graph)

        graph3 = factory.create_py2neo_graph_by_server_id(3)
        self.assertIsNone(graph3)

        graphDysD3 = factory.create_py2neo_graph_by_server_name("DysD3")
        self.assertIsNotNone(graphDysD3)
        self.assertTrue(type(graphDysD3) == Graph)

        graphDysD3 = factory.create_py2neo_graph_by_server_name("DysD3Wrong")
        self.assertIsNone(graphDysD3)

    def test___init__(self):
        factory = GraphInstanceFactory("neo4j_neo4j_config.json")
        configs = [
            {'server_name': 'LocalHostServer', 'server_id': 1, 'host': 'localhost', 'user': 'neo4j',
             'password': '123456', 'http_port': 7474, 'https_port': 7473, 'bolt_port': 7687},
            {'server_name': 'DysD3', 'server_id': 2, 'host': '10.141.221.87', 'user': 'neo4j',
             'password': '123456', 'http_port': 7474, 'https_port': 7473, 'bolt_port': 7687}
        ]
        self.assertEqual("neo4j_config.json",
                         factory.get_config_file_path())
        self.assertEqual(configs,
                         factory.get_configs())

    def test_get_node_id(self):
        factory = GraphInstanceFactory("neo4j_config.json")
        graphDysD3 = factory.create_py2neo_graph_by_server_name("DysD3")

        node = graphDysD3.evaluate("Match (n:entity) where id(n)=4 return n")
        self.assertTrue(type(node) == Node)
        print(node)
        self.assertEqual(node.identity, 4)

        new_node = Node("person", a=1, name="harry")
        print(new_node)
        print(new_node.identity)
