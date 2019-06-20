class node(object):
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []
        self.dockerfile = None

    def append_child(self, node):
        node.parent = self
        self.children.append(node)

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def upstream_nodes(self):
        if self.parent is None:
            return []
        return self.parent.upstream_nodes() + [self.parent]

    def downstream_nodes(self):
        result = [self]
        for child in self.children:
            result += child.downstream_nodes()
        return result

    def __repr__(self):
        return '<tree node representation>'

def get_node(n, value):
    if n.value == value:
        return n
    for c in n.children:
        v = get_node(c, value)
        if v is not None:
            return v
    return None