def ancestors(g, O):
    """
    Extract ancestors nodes from an starting node
    :param g: starting node name
    :param O: Graph
    :return: a set with node names
    """
    result = {g}
    for o in O.successors(g):
        result.update(ancestors(o, O))
    return result
