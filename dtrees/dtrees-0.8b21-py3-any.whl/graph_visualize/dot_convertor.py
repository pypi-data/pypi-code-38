from dtrees.algorithms.learn_tree import Tree


def make_node(node, writeId, writeSamples, writeProb):
    label = ''
    if node.type == 'inner':
        if writeId:
            label += "{}\n".format(node.id)
        label += "{}\n".format(node.attr)
        if writeSamples:
            label += 'Samples = {}\n'.format(round(node.stat.sum(),3))
        dot_instance = '{}[label="{}", fillcolor="#ffffff"];\n'.format(node.id, label)
    else:
        if writeId:
            label += "{}\n".format(node.id)
        if writeSamples:
            label += 'Samples = {}\n'.format(round(node.stat.sum(),3))
        if writeProb:
            P = node.stat[node.attr] / node.stat.sum()
            label += "P = {:.2f}\n".format(P)
        label += "{}\n".format(node.attr)
        dot_instance = '{}[label="{}", fillcolor="#c6cbd3"];\n'.format(node.id, label)
    return dot_instance


def make_connection(connect):
    nodes = tuple(connect.keys())[0]
    prop = list(connect.values())[0]
    conn = '{} -> {} [label="{}", fontsize=10]'.format(nodes[0], nodes[1], prop)
    return conn


def export2dot(name, tree, writeId=False, writeSamples=True, writeProb=True, write=False):
    if isinstance(tree, Tree):
        dot_graph = 'digraph Tree { \n\tnode [shape=box, style="filled, rounded", color="black", fontname=helvetica] ; edge [fontname=helvetica];\n'
        graph_nodes, connections, ids = [], [], []
        for connection in tree.connectionProp:
            nodes = tuple(connection.keys())[0]
            node = tree.getNode(nodes[0])
            if node.id not in ids:
                dot_graph += make_node(node, writeId, writeSamples,writeProb)
                ids.append(node.id)
            node = tree.getNode(nodes[1])
            if node.id not in ids:
                dot_graph += make_node(node, writeId, writeSamples,writeProb)
                ids.append(node.id)
            dot_graph += make_connection(connection)
        dot_graph += '}'

        if write:
            with open(name + ".dot", "w") as output:
                output.write(dot_graph)
                output.close()
            return None
        else:
            return dot_graph

# dot -Tpng test/zenit/zenitID3.dot -o test/zenit/zenit.png