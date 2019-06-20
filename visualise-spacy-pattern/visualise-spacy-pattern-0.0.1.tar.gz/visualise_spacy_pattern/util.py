def get_node_name(pattern_element):
    node_name = pattern_element['SPEC']['NODE_NAME']
    return node_name


def get_feature_dict(pattern_element):
    feature_dict = pattern_element['PATTERN']
    return feature_dict


def get_nbor_name(pattern_element):
    try:
        nbor_name = pattern_element['SPEC']['NBOR_NAME']
    except KeyError:
        nbor_name = None
    return nbor_name


def get_rel(pattern_element):
    try:
        rel = pattern_element['SPEC']['NBOR_RELOP']
    except KeyError:
        rel = None
    return rel
