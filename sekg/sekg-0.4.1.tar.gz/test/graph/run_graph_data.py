#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sekg.graph.exporter.graph_data import GraphData

graph_data = GraphData()

graph_data.add_node({"method"}, {"qualified_name": "ArrayList.add"})
graph_data.add_node({"override method"}, {"qualified_name": "ArrayList.pop"})
graph_data.add_node({"method"}, {"qualified_name": "ArrayList.remove"})
graph_data.add_node({"method"}, {"qualified_name": "ArrayList.clear"})

# print(graph_data.find_nodes_by_property_value_starts_with("qualified_name", "ArrayList"))

# print(graph_data.get_node_ids())
# print(graph_data.get_relation_pairs_with_type())

graph_data.add_relation(1, "related to", 2)
graph_data.add_relation(1, "related to", 3)
graph_data.add_relation(1, "related to", 4)
graph_data.add_relation(2, "related to", 3)
graph_data.add_relation(3, "related to", 4)

print(graph_data.get_relations(1, "related to"))
print("get relation by type")
print(graph_data.get_relations(relation_type="related to"))

graph_data.remove_node(node_id=1)

# print(graph_data.get_node_ids())
# print(graph_data.get_relation_pairs_with_type())

# print("#" * 50)
# graph_data.merge_two_nodes_by_id(1, 2)

# print(graph_data.get_node_ids())
# print(graph_data.get_relation_pairs_with_type())

print("full graph----------")
graph_data.print_graph_info()


print("subgraph----------")
left_graph=graph_data.subgraph(set([1,2,3]))
left_graph.print_graph_info()


print("old graph----------")
graph_data.print_graph_info()

