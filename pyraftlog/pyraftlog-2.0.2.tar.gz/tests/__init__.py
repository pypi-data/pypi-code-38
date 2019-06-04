import pyraftlog


def get_node(node_type, node_name, neighbourhood, log_reduction=False):
    """ Get a node """
    node = pyraftlog.Node(node_type, node_name, neighbourhood, pyraftlog.Storage(),
                          election_timeout=0.3, heartbeat_timeout=0.1, vote_timeout=0.3)
    node.state.log_reduction = log_reduction
    return node
