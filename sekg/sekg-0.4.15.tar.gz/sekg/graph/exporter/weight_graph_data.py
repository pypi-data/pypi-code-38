from sekg.graph.exporter.graph_data import GraphData
from sekg.util.vector_util import VectorUtil


import math
import numpy as np
from sekg.graph.exporter.graph_data import GraphData
from sekg.graph.exporter.graph_data import GraphIndexCollection
from sekg.graph.metadata_accessor import MetadataGraphAccessor
import networkx as nx
from networkx import MultiGraph

from gensim.utils import SaveLoad

"""
this package is used to get a weight graph
"""


class WeightGraphData(SaveLoad):
    """
    the store of a weight undirected graph data.

    each node is represent as a dict of node info named 'node_json',
    Example Format for 'node_json':

     {
        "id": 1,
        "properties": {"name":"bob","age":1},
        "labels": ["entity","man"]
    }

    """

    DEFAULT_KEY_NODE_ID = "id"  # the key name for the node id, every node must have it.
    DEFAULT_KEY_NODE_PROPERTIES = "properties"  # the key name for the node properties, every node must have it.
    DEFAULT_KEY_NODE_LABELS = "labels"  # the key name for the node labels, every node must have it.

    DEFAULT_KEYS = [DEFAULT_KEY_NODE_ID, DEFAULT_KEY_NODE_PROPERTIES, DEFAULT_KEY_NODE_LABELS]
    UNASSIGNED_NODE_ID = -1  # a node without a id specify, a newly created node, its id is -1

    DEFAULT_KEY_RELATION_START_ID = "startId"
    DEFAULT_KEY_RELATION_TYPE = "relationType"
    DEFAULT_KEY_RELATION_END_ID = "endId"

    DEFAULT_KEY_PROPERTY_QUALIFIED_NAME = "qualified_name"
    DEFAULT_KEY_PROPERTY_ALIAS = "alias"

    def __init__(self):
        self.graph = MultiGraph()
        self.max_node_id = 0
        self.label_to_ids_map = {}
        self.index_collection = GraphIndexCollection()
        self.relation_type_weight_dict = {}
        self.node_weight_dict = {}
        self.r_weights = {}

    '''
    init the undirected graph from directed graph and get the node weight dict
    :param graph_data: MulDiGraph
    '''
    def init_from_directed_graph(self, graph_data, weight="weight"):
        if not isinstance(graph_data, GraphData):
            # todo alert an Error info
            return
        print("Transfer undirected graph to weight graph data")
        self.label_to_ids_map = graph_data.label_to_ids_map
        computer = WeightGraphDataComputer(graph_data)
        self.graph = computer.generate_weight_graph(weight_type=weight)

    def get_relation_num(self):
        return len(self.graph.edges)

    def get_node_ids(self):
        return set(self.graph.nodes)

    def get_node_label_by_id(self, node_id):
        pass


    # todo: fix the weight graphdata training
    # def precompute_weight(self):
    #     relation_count = self.graph_data.get_relation_num()
    #     relation_type_count = {}
    #
    #     node_degree_dict = {}
    #
    #     for node_id in self.graph_data.get_node_ids():
    #         # get the out degree of a node
    #         out_relation_list = self.graph_data.get_all_out_relations(node_id=node_id)
    #         # get the in degree of a node
    #         in_relation_list = self.graph_data.get_all_in_relations(node_id=node_id)
    #
    #         # get the degree of a node
    #         node_degree_dict[node_id] = len(out_relation_list) + len(in_relation_list)
    #
    #         for start_id, relation_type, end_id in out_relation_list:
    #             if relation_type not in relation_type_count.keys():
    #                 relation_type_count[relation_type] = 0
    #             relation_type_count[relation_type] = relation_type_count[relation_type] + 1
    #
    #     self.relation_type_weight_dict = VectorUtil.compute_idf_weight_dict(total_num=relation_count,
    #                                                                         number_dict=relation_type_count)
    #     print(self.relation_type_weight_dict)
    #     self.node_weight_dict = VectorUtil.compute_idf_weight_dict(total_num=relation_count * 2,
    #                                                                number_dict=node_degree_dict)

    def get_node_weight(self, node_id):
        if node_id not in self.node_weight_dict.keys():
            return 1
        return self.node_weight_dict[node_id]

    def get_relation_type_weight(self, relation_type):
        if relation_type not in self.relation_type_weight_dict.keys():
            return 1
        return self.relation_type_weight_dict[relation_type]

    def get_relation_tuple_weight(self, start_node_id, end_node_id, relation_name):
        start_w = self.get_node_weight(start_node_id)
        end_w = self.get_node_weight(end_node_id)
        r_w = self.get_relation_type_weight(relation_name)

        return start_w * end_w * r_w

    def get_all_in_relations(self, node_id):
        if node_id not in self.graph.nodes:
            return set()
        return {(r[0], r[2], r[1]) for r in self.graph.edges(node_id, keys=True)}


class WeightGraphDataComputer:
    """
    this class is to get a weight graph Data"""

    def __init__(self, graph_data):
        if isinstance(graph_data, GraphData):
            self.graph_data = graph_data
        else:
            self.graph_data = None

        self.undirected_graph = None
        self.max_w_r_type_dict = {}
        self.node_id_to_weight_map = {}
        self.r_weights = {}

    '''
    weight_type == "weight" or weight_type == "distance"
    :param weight_type: 
    :return: 
    '''
    def generate_weight_graph(self, weight_type="weight"):
        r_weights, max_w_r_type_dict = self.compute_r_weight(self.graph_data)
        self.max_w_r_type_dict = max_w_r_type_dict
        self.r_weights = r_weights

        graph_data: GraphData = self.graph_data
        undirected_graph = graph_data.graph.to_undirected()
        node_id_to_weight_map = self.compute_node_weight(undirected_graph)
        self.node_id_to_weight_map = node_id_to_weight_map

        r_list = []
        r_weight_list = []
        r_type_list = []
        for start_id, end_id, relation_type in undirected_graph.edges(keys=True):
            r_list.append((start_id, end_id))
            r_type_list.append(relation_type)
            start_w = node_id_to_weight_map[start_id]
            end_w = node_id_to_weight_map[end_id]
            r_weight = r_weights[(start_id, end_id)]
            weight = (start_w + end_w) * r_weight

            r_weight_list.append(weight)

        np_r_weight = np.array(r_weight_list)
        w_min = np_r_weight.min()
        w_max = np_r_weight.max()
        normal_r_weight = (np_r_weight - w_min) / (w_max - w_min)
        normal_r_weight = np.abs(1 - normal_r_weight)
        undirected_graph = nx.MultiGraph()

        for (start_id, end_id), weight, normal_w, relation_type in zip(r_list, r_weight_list, normal_r_weight, r_type_list):
            if weight_type == "weight":
                undirected_graph.add_edge(start_id, end_id, weight=1 - normal_w, key=relation_type)
            else:
                undirected_graph.add_edge(start_id, end_id, weight=normal_w, key=relation_type)

        self.undirected_graph = undirected_graph
        return undirected_graph

    @staticmethod
    def compute_r_weight(graph_data):
        relation_count = graph_data.get_relation_num()
        print("relation count=%d" % relation_count)
        relation_statics = {}
        # get the num of relation type and count for every node
        node_id_to_relation_type_count = {}
        r_to_relation_types_map = {}

        def _count_node_r_weight(node_id, relation_type):
            if node_id not in node_id_to_relation_type_count:
                node_id_to_relation_type_count[node_id] = dict()

            if relation_type not in node_id_to_relation_type_count[node_id]:
                node_id_to_relation_type_count[node_id][relation_type] = 0
            node_id_to_relation_type_count[node_id][relation_type] += 1

        for start_id, relation_type, end_id in graph_data.get_relation_pairs_with_type():
            if relation_type.startswith("operation_"):
                relation_type = "operation"
            if relation_type.startswith("mention "):
                relation_type = "mention"

            _count_node_r_weight(start_id, relation_type)
            _count_node_r_weight(end_id, relation_type)
            if relation_type not in relation_statics:
                relation_statics[relation_type] = 0

            relation_statics[relation_type] += 1
            if (start_id, end_id) not in r_to_relation_types_map:
                r_to_relation_types_map[(start_id, end_id)] = set([])
            if (end_id, start_id) not in r_to_relation_types_map:
                r_to_relation_types_map[(end_id, start_id)] = set([])
            r_to_relation_types_map[(start_id, end_id)].add(relation_type)
            r_to_relation_types_map[(end_id, start_id)].add(relation_type)

        r_weights = {}
        for node_id in node_id_to_relation_type_count.keys():
            for r in node_id_to_relation_type_count[node_id].keys():
                node_id_to_relation_type_count[node_id][r] = 1.0 / (math.log10(
                    node_id_to_relation_type_count[node_id][r]) + 1)

        max_w_r_type_dict = {}
        for (start_id, end_id), relation_types in r_to_relation_types_map.items():
            r_weights[(start_id, end_id)] = 0
            for r in relation_types:
                w = node_id_to_relation_type_count[start_id][r] + node_id_to_relation_type_count[end_id][r]
                if w > r_weights[(start_id, end_id)]:
                    r_weights[(start_id, end_id)] = w
                    max_w_r_type_dict[(start_id, end_id)] = r
        return r_weights, max_w_r_type_dict

    @staticmethod
    def compute_node_weight(undirected_graph):
        node_id_list = []
        node_degree_list = []
        edge_num = undirected_graph.number_of_edges()
        node_id_to_weight_map = {}
        for node_id in undirected_graph.nodes():
            node_id_list.append(node_id)
            node_degree_list.append(undirected_graph.degree(node_id))
        node_weight_list = np.log10((edge_num + 1) / (np.array(node_degree_list) + 1))
        for node_id, weight in zip(node_id_list, node_weight_list):
            node_id_to_weight_map[node_id] = weight
        return node_id_to_weight_map

    def save(self, edge_path):
        # print([e for e in self.undirected_graph.edges.data('weight', default=1)])
        with open(edge_path, "w+") as f:
            f.writelines([
                " ".join([str(item) for item in e]) for e in self.undirected_graph.edges.data('weight', default=1)
            ])

    def get_distance(self, start_id, end_id):
        if start_id not in self.undirected_graph.nodes:
            return -1
        elif end_id not in self.undirected_graph.nodes:
            return -1
        for adj in self.undirected_graph.edges.data('weight', default=1):
            if (start_id == adj[0] and end_id == adj[1]) or (start_id == adj[1] and end_id == adj[0]):
                return adj[2]
        return -1

    def get_weight(self, start_id, end_id):
        if start_id not in self.undirected_graph.nodes:
            return -1
        elif end_id not in self.undirected_graph.nodes:
            return -1
        for adj in self.undirected_graph.edges.data('weight', default=1):
            if (start_id == adj[0] and end_id == adj[1]) or (start_id == adj[1] and end_id == adj[0]):
                return 1 - adj[2]
        return -1


if __name__ == "__main__":
    graph_path = "E:\PycharmProjects\KGFeatureLocation\output\graph\jedite-4.3\jedite-4.3.v3.graph"
    c = WeightGraphDataComputer(GraphData.load(graph_path))
    c.generate_weight_graph(weight_type="weight")
    print(c.get_weight(40153, 40154))
