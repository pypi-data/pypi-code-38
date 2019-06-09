"""
visitor.visit() calls a visitor function for each node in a tree, in either
pre- or post-order.

A visitor function takes three arguments (parent, key, node), where `parent`
is the containing node (or None if this is the top node), and `key` is a
key for the child within parent (which might be a string, integer or some
other sort of thing)

"""


def simple_children(node):
    if isinstance(node, dict):
        return node.items()

    if isinstance(node, (tuple, list)):
        return enumerate(node)

    return ()


def visit(root, visitor, pre=False, get_children=simple_children):
    """
    Call a function on each node in the tree.

    Arguments
      root: the root of the tree

      visitor_fn: the visitor function

      pre: if True, call the visitor function on a node before all subnodes;
          otherwise call the visitor function after all subnodes

      get_children: a function that returns an iterator of (key, child)
          pairs from a node

    """

    def recurse(parent, key, node):
        pre and visitor(parent, key, node)

        for child_key, child_node in list(get_children(node)):
            recurse(node, child_key, child_node)

        pre or visitor(parent, key, node)

    recurse(None, None, root)
