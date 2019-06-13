from numpy import sqrt, square
from collections import deque

def error(N, f, z):
    z2 = square(z)
    num = f + (z2 / (2 * N)) + z * sqrt((f / N) - (square(f) / N) + (z2 / (4 * square(N))))
    den = 1 + (z2 / N)
    return num / den


def errorBasedPruning(tree, z=0.69):
    groups = tree.groupLeafByParent()
    for parent, childs in groups.items():
        allChilds = tree.getChilds(parent)
        if len(allChilds) == childs:
            if len(childs) > 1:
                errorRates = []
                for chId in childs:
                    node = tree.getNode(chId)
                    maj = node.attr
                    N = node.stat.sum(axis=0)
                    f = node.stat.drop(maj, axis=0).sum(axis=0)
                    errorRates.append(error(N, f, z) / N)
                errorRates = list(filter(lambda x: x == x, errorRates))
                err = sum(errorRates)
                del errorRates
                if err < 0.51:
                    # prune
                    tree.pruneAll(parent, childs)
                    tree._pruneConnect_(parent, childs)
                    tree._pruneBranchStat_(parent, childs)


def pruneMinSamples(tree, minSamples):
    pruned = False
    groups = tree.groupLeafByParent()
    for parent, childs in groups.items():
        wasPrune = False
        for chId in childs:
            node = tree.getNode(chId)
            w = node.stat.sum()
            if w < minSamples:
                tree.prune(parent, chId)
                tree._pruneConnect_(parent, [chId])
                tree._pruneBranchStat_(parent, [chId])
                wasPrune = True
                pruned = True
        if wasPrune:
            newChilds = tree.getChilds(parent)
            if len(newChilds) == 0:
                node = tree.getNode(parent)
                node.attr = node.stat.idxmax()
                node.type = 'leaf'
            elif len(newChilds) == 1:
                grandChilds = tree.getChilds(newChilds[0])
                if len(grandChilds) > 0:
                    if parent == 0:
                        # prune old connections
                        tree._pruneConnect_(0, [newChilds[0]])
                        tree._pruneBranchStat_(0, [newChilds[0]])
                        tree._changeParentConect_(grandChilds, newChilds[0], 0)
                        # remove old root node
                        root = tree.getNode(0)
                        tree.nodes.remove(root)
                        # make node root
                        node = tree.getNode(newChilds[0])
                        node.id = 0
                    else:
                        grandParent = tree.getParentId(parent)
                        tree._pruneConnect_(parent, [newChilds[0]])
                        tree._changeChildConect_(grandParent, parent, newChilds[0])
                        tree._changeStat_((grandParent, parent), (grandParent, newChilds[0]))
                        node = tree.getNode(parent)
                        tree.nodes.remove(node)
                        tree.edges.remove((grandParent, parent))
                        tree.edges.remove((parent, newChilds[0]))
                        tree._addEdge_((grandParent, newChilds[0]))
                else:
                    tree.pruneAll(parent, newChilds)
                    tree._pruneConnect_(parent, newChilds)
                    tree._pruneBranchStat_(parent, newChilds)
        return pruned


def pruneMaxDepth(tree, maxDepth):
    currDepth = 0
    keepVert, last = [0], []
    vert = deque()
    vert.append(0)
    # Find vertexes
    while len(vert) > 0:
        v = vert.popleft()
        childs = tree.getChilds(v)
        keepVert += childs
        currDepth += 1
        for ch in childs:
            vert.append(ch)
        if currDepth == maxDepth:
            last = childs
            break
    # prune nodes
    to_del = []
    for node in tree.nodes:
        if node.id not in keepVert:
            to_del.append(node.id)
            childs = tree.getChilds(node.id)
            tree._pruneConnect_(node.id, childs)
            tree._pruneBranchStat_(node.id, childs)
            for ch in childs:
                edge = (node.id,ch)
                tree.edges.remove(edge)
                tree.nodes.remove(tree.getNode(ch))
            parent = tree.getParentId(node.id)
            tree._pruneConnect_(parent,[node.id])
            tree._pruneBranchStat_(parent, [node.id])
            edge = (parent,node.id)
            tree.edges.remove(edge)
    for id in to_del:
        node = tree.getNode(id)
        tree.nodes.remove(node)
    # Make nodes leafs
    for id in last:
        node = tree.getNode(id)
        node.attr = node.stat.idxmax()
        node.type = 'leaf'