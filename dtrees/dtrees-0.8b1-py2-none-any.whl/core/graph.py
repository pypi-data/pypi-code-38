import pandas as pd


class Node():

    def __init__(self, id, nodeType='leaf'):
        self.id = id
        self.type = nodeType
        self.stat = None
        self.attr = None

    def nodeStat(self, stat):
        self.stat = stat


class Graph():

    def __init__(self):
        self.nodes = []
        self.edges = []
        self._initialized = False

    def addNode(self, node, parentId):
        if isinstance(node, Node) or hasattr(node, 'id'):
            if isinstance(parentId, int):
                self._addEdge_((parentId, node.id))
                self.nodes.append(node)

    def setRootNode(self, node):
        if isinstance(node, Node) or hasattr(node, 'id'):
            if node.id != 0:
                node.id = 0
            self.nodes.append(node)
            self._initialized = True

    def getNode(self, id):
        for node in self.nodes:
            if node.id == id:
                return node

    def getChilds(self, id):
        childs = [edge[1] for edge in self.edges if edge[0] == id]
        return childs

    def _next_id(self):
        if len(self.nodes) == 0:
            return 0
        else:
            max_id = max([node.id for node in self.nodes])
            return max_id + 1

    def _addEdge_(self, edge):
        if edge is not None:
            if isinstance(edge, list) or isinstance(edge, tuple):
                if len(edge) == 2:
                    self.edges.append(tuple(edge))

    def getParentId(self, id):
        """
        :param id: int id of leaf node
        :return: parent node id
        """
        for edge in self.edges:
            if edge[1] == id:
                return edge[0]

    def groupLeafByParent(self):
        leafInd = [node.id for node in self.nodes if node.type == 'leaf']
        parents = [self.getParentId(id) for id in leafInd]
        group = {}
        for i, id in enumerate(leafInd):
            if parents[i] not in group:
                group[parents[i]] = [id]
            else:
                group[parents[i]].append(id)
        del leafInd, parents
        return group

    def _makeOneNode_(self, parentId, nodesId):
        # merge to node 0
        nodes = [self.getNode(id) for id in nodesId]
        stats = [node.stat for node in nodes]
        res = pd.concat(stats, axis=1, sort=False)
        res['W'] = res.sum(axis=1)
        res.drop(columns=[name for name in res.columns[:-1]], axis=1, inplace=True)
        res.columns = ['Weight']
        for node in nodes[1:]:
            edge = (parentId, node.id)
            self.edges.remove(edge)
            self.nodes.remove(node)
        del nodes
        node = self.getNode(nodesId[0])
        node.stat = res.squeeze()

    def _replace_(self, id1, id2):
        node1 = self.getNode(id1)
        stat = node1.stat
        node2 = self.getNode(id2)
        node2.stat = stat
        self.nodes.remove(node1)
        parent = self.getParentId(id1)
        edge = (parent, id1)
        self.edges.remove(edge)
        newEdge = (parent, id2)
        self._addEdge_(newEdge)

    def pruneAll(self, parentId, childs):
        for id in childs:
            edge = (parentId, id)
            self.edges.remove(edge)
            node = self.getNode(id)
            self.nodes.remove(node)
        node = self.getNode(parentId)
        node.attr = node.stat.idxmax()
        node.type = 'leaf'

    def prune(self, parentId, childId):
        edge = (parentId, childId)
        self.edges.remove(edge)
        node = self.getNode(childId)
        self.nodes.remove(node)
