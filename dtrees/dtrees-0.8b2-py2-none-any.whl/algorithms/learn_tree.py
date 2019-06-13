from dtrees.core.graph import Graph, Node
from dtrees.algorithms.criterions import *
from numpy import round
from dtrees.utils.help_functions import groupSameElements
from operator import itemgetter
from multiprocessing import Process, Manager
import numpy as np

def _getPartition_(data, attr):
    num = data.loc[data[attr].notnull()]['__W__'].sum()
    den = data['__W__'].sum()
    return round(num / den, 3)


class Tree(Graph):

    def __init__(self, data, target, attrProp, attrTypes, params=None):
        Graph.__init__(self)
        self.target = target
        self.data = data
        self.branchStat = pd.DataFrame(columns=[lbl for lbl in attrProp[target]])
        self.data['__W__'] = [1.0 for _ in range(len(data))]
        self.attrributeProperties = attrProp
        self.attrributeTypes = attrTypes
        self.connectionProp = []
        self.nClasses = len(attrProp[target])
        self.targetLbls = [lbl for lbl in attrProp[target]]
        self.minObj = 2
        if params is None:
            self.params = {'criterion': 'entropy'}
        else:
            self.params = params
            if 'minSamples' in params:
                ms = float(params['minSamples'])
                if ms < 1:
                    self.minObj = round(data.shape[0] * ms, 3)
                else:
                    self.minObj = ms

    def _id3_(self, data, currId, parentId):

        node = Node(id=currId)

        # Check if all target values are equal
        if len(data[self.target].unique()) == 1:
            node.type = 'leaf'
            label = data.iloc[0][self.target]
            if not isinstance(label, str):
                if label.dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                    label = int(label)
            node.attr = label
            self.addNode(node, parentId)
        # If only target
        elif len(data.columns) == 1:
            node.type = 'leaf'
            most_freq = data[self.target].value_counts().idxmax()
            if not isinstance(most_freq, str):
                if most_freq.dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                    most_freq = int(most_freq)
            node.attr = most_freq
            self.addNode(node, parentId)
        else:
            # initial_entropy = info(data, self.target, self.target)
            gain = {}
            for attr in data.columns:
                if (attr != self.target) and (attr != '__W__'):
                    I = entropy(data, self.target, attr)
                    gain[attr] = round(I, 3)
                    # gain[attr] = round(initial_entropy - I, 3)

            best_attr = max(gain, key=gain.get)

            node.attr = best_attr
            node.type = 'inner'

            if node.id == 0:
                self.setRootNode(node)
            else:
                self.addNode(node, parentId=parentId)

            for prop in self.attrributeProperties[best_attr]:
                sub = data.loc[data[best_attr] == prop, data.columns != best_attr]
                self.connectionProp.append({(node.id, self._next_id()): prop})
                self._id3_(sub, currId=self._next_id(), parentId=node.id)
        return self

    def _usefullAttribute_(self, d):
        vals = []
        for v in d.values():
            vals.append(v)
        if max(vals) == 0:
            return False
        else:
            return True

    def _c45_(self, data, currId, parentId):

        node = Node(id=currId)

        # Check if all target values are equal
        if len(data[self.target].unique()) == 1:
            node.type = 'leaf'
            label = data.iloc[0][self.target]
            if not isinstance(label, str):
                if label.dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                    label = int(label)
            node.attr = label
            node.stat = self._getStat_(data)
            self.addNode(node, parentId)
            return self
        # If only target
        elif len(data.columns) == 1:
            node = self._leafNode_(node, data)
            self.addNode(node, parentId)
            return self
        enough, mostFreq = self._enoughInstances_(data)
        if not enough:
            node.type = 'leaf'
            node.attr = mostFreq
            node.stat = self._getStat_(data)
            self.addNode(node, parentId)
            return self
        else:

            def _attributeFinding_(attr):
                if self.attrributeTypes[attr] == 1:
                    # categorical attribute
                    if self.params['criterion'] == 'entropy':
                        # attrEst[attr] = self._handleCategorial_(data, attr)
                        attrEst[attr] = gainRatio(data, self.target, attr)
                    elif self.params['criterion'] == 'Gini':
                        attrEst[attr] = gini(data, self.target, attr)
                    elif self.params['criterion'] == 'D':
                        attrEst[attr] = D(data, self.target, attr)
                    elif self.params['criterion'] == 'Tsallis':
                        attrEst[attr] = tsallis(data, self.target, attr, alpha=self.params['alpha'])
                    elif self.params['criterion'] == 'Renyi':
                        attrEst[attr] = renyi(data, self.target, attr, alpha=self.params['alpha'])
                else:
                    # continous attribute
                    if self.params['criterion'] == 'entropy':
                        # gr, thrsh = self._handleNumerical_(data, attr)
                        gr, thrsh = entropyCont(data, self.target, attr)
                        attrEst[attr] = gr
                        attrThrsh[attr] = thrsh
                    elif self.params['criterion'] == 'Gini':
                        g, thrsh = giniCont(data, self.target, attr)
                        attrEst[attr] = g
                        attrThrsh[attr] = thrsh
                    elif self.params['criterion'] == 'D':
                        d, thrsh = D_cont(data, self.target, attr)
                        attrEst[attr] = d
                        attrThrsh[attr] = thrsh
                    elif self.params['criterion'] == 'Tsallis':
                        t, thrsh = tsallisCont(data, self.target, attr, self.params['alpha'])
                        attrEst[attr] = t
                        attrThrsh[attr] = thrsh
                    elif self.params['criterion'] == 'Renyi':
                        r, thrsh = renyiCont(data, self.target, attr, self.params['alpha'])
                        attrEst[attr] = r
                        attrThrsh[attr] = thrsh

            manager = Manager()
            attrEst, attrThrsh = manager.dict(), manager.dict()
            jobs = []
            for attr in data.columns:
                if (attr != self.target) and (attr != '__W__'):
                    # proc = Process(target=self._attributeFinding_, args=(attr, attrEst, attrThrsh, data,))
                    proc = Process(target=_attributeFinding_, args=(attr,))
                    jobs.append(proc)
                    proc.start()
            for proc in jobs:
                proc.join()

            attrEst, attrThrsh = dict(attrEst), dict(attrThrsh)
            best_attr = max(attrEst, key=attrEst.get)

            node.attr = best_attr
            node.type = 'inner'
            node.stat = self._getStat_(data)

            if node.id == 0:
                if not self._usefullAttribute_(attrEst):
                    node.type = 'leaf'
                    node.attr = mostFreq
                    self.setRootNode(node)
                    return self
                else:
                    self.setRootNode(node)
            else:
                if not self._usefullAttribute_(attrEst):
                    node.type = 'leaf'
                    node.attr = mostFreq
                    self.addNode(node, parentId=parentId)
                    return self
                else:
                    self.addNode(node, parentId=parentId)

            N = data.loc[data[best_attr].notnull()]['__W__'].sum()
            if self.attrributeTypes[best_attr] == 0:
                thrsh = attrThrsh[best_attr]
                thrsh = set_threshold(self.data[best_attr], thrsh)
                lessOrEq = data.loc[data[best_attr] <= thrsh]
                great = data.loc[data[best_attr] > thrsh]
                if lessOrEq.empty or great.empty:
                    return self
                nextId = self._next_id()
                self._addBranchStat_(lessOrEq, (node.id, nextId))
                self.connectionProp.append({(node.id, self._next_id()): '<= {}'.format(thrsh)})
                self._c45_(lessOrEq, currId=self._next_id(), parentId=node.id)
                nextId = self._next_id()
                self._addBranchStat_(great, (node.id, nextId))
                self.connectionProp.append({(node.id, self._next_id()): '> {}'.format(thrsh)})
                self._c45_(great, currId=self._next_id(), parentId=node.id)
            else:
                notEmpty = [not data.loc[data[best_attr] == prop].empty for prop in
                            self.attrributeProperties[best_attr]]
                if sum(notEmpty) <= 1:
                    return self
                for prop in self.attrributeProperties[best_attr]:
                    sub = data.loc[data[best_attr] == prop, data.columns != best_attr]
                    if sub.empty:
                        continue
                    w = round(sub['__W__'].sum() / N, 3)
                    unknown = data.loc[data[best_attr].isnull(), data.columns != best_attr].copy()
                    unknown['__W__'] = [w for _ in range(unknown.shape[0])]
                    sub = pd.concat([sub, unknown], sort=False)
                    nextId = self._next_id()
                    self._addBranchStat_(sub, (node.id, nextId))
                    self.connectionProp.append({(node.id, nextId): prop})
                    self._c45_(sub, currId=nextId, parentId=node.id)
        return self

    def _attributeFinding_(self, attr, attrEst, attrThrsh, data):
        if self.attrributeTypes[attr] == 1:
            # categorical attribute
            if self.params['criterion'] == 'entropy':
                # attrEst[attr] = self._handleCategorial_(data, attr)
                attrEst[attr] = gainRatio(data, self.target, attr)
            elif self.params['criterion'] == 'Gini':
                attrEst[attr] = gini(data, self.target, attr)
            elif self.params['criterion'] == 'D':
                attrEst[attr] = D(data, self.target, attr)
            elif self.params['criterion'] == 'Tsallis':
                attrEst[attr] = tsallis(data, self.target, attr, alpha=self.params['alpha'])
            elif self.params['criterion'] == 'Renyi':
                attrEst[attr] = renyi(data, self.target, attr, alpha=self.params['alpha'])
        else:
            # continous attribute
            if self.params['criterion'] == 'entropy':
                # gr, thrsh = self._handleNumerical_(data, attr)
                gr, thrsh = entropyCont(data, self.target, attr)
                attrEst[attr] = gr
                attrThrsh[attr] = thrsh
            elif self.params['criterion'] == 'Gini':
                g, thrsh = giniCont(data, self.target, attr)
                attrEst[attr] = g
                attrThrsh[attr] = thrsh
            elif self.params['criterion'] == 'D':
                d, thrsh = D_cont(data, self.target, attr)
                attrEst[attr] = d
                attrThrsh[attr] = thrsh
            elif self.params['criterion'] == 'Tsallis':
                t, thrsh = tsallisCont(data, self.target, attr, self.params['alpha'])
                attrEst[attr] = t
                attrThrsh[attr] = thrsh
            elif self.params['criterion'] == 'Renyi':
                r, thrsh = renyiCont(data, self.target, attr, self.params['alpha'])
                attrEst[attr] = r
                attrThrsh[attr] = thrsh

    def _enoughInstances_(self, data):
        W = data['__W__'].sum()
        mostFreq = data[self.target].value_counts().idxmax()
        if not isinstance(mostFreq, str):
            if mostFreq.dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                mostFreq = int(mostFreq)
        N = data.loc[data[self.target] == mostFreq]['__W__'].sum()
        if (W > 2 * self.minObj) & (W > N):
            return True, mostFreq
        else:
            return False, mostFreq

    def _addBranchStat_(self, data, conn):
        row = pd.DataFrame(columns=self.branchStat.columns, index=[conn])
        for col in self.branchStat:
            w = data.loc[data[self.target] == col]['__W__'].sum()
            row[col] = [w]
        self.branchStat = self.branchStat.append(row, ignore_index=False)

    def _getStat_(self, data):
        names, weights = [], []
        # weights per class
        for T in self.attrributeProperties[self.target]:
            w = data.loc[data[self.target] == T]['__W__'].sum()
            names.append(T)
            weights.append(w)
        weightsPerClass = pd.Series(data=weights, index=names)
        del names, weights
        return weightsPerClass

    def _leafNode_(self, node, data):
        node.type = 'leaf'
        label = data[self.target].value_counts().idxmax()
        if not isinstance(label, str):
            if label.dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                label = int(label)
        most_freq = label
        node.attr = most_freq
        node.stat = self._getStat_(data)
        return node

    def _pruneConnect_(self, parent, chId):
        for id in chId:
            edge = (parent, id)
            for conn in self.connectionProp:
                if edge in conn:
                    self.connectionProp.remove(conn)
                    break

    def _multipleConnect(self, parent, chId):
        dst = (parent, chId[0])
        for id in chId[1:]:
            edge = (parent, id)
            for conn in self.connectionProp:
                if edge in conn:
                    val = None
                    for v in conn.values():
                        val = v
                    self.connectionProp.remove(conn)
                    self.connectionProp.append({dst: val})
                    break

    def _pruneBranchStat_(self, parent, chId):
        for id in chId:
            edge = (parent, id)
            self.branchStat.drop(edge, axis=0, inplace=True)

    def _changeChildConect_(self, parent, id1, id2):
        """
        :param parent: common parent id
        :param id1: old id
        :param id2: new id
        """
        oldEdge = (parent, id1)
        newEdge = (parent, id2)
        for conn in self.connectionProp:
            if oldEdge in conn:
                val = conn[oldEdge]
                conn[newEdge] = val
                del conn[oldEdge]
                break

    def _changeParentConect_(self, childs, oldParent, newParent):
        """
        :param parent: common parent id
        :param id1: old id
        :param id2: new id
        """
        for ch in childs:
            oldEdge = (oldParent, ch)
            newEdge = (newParent, ch)
            for conn in self.connectionProp:
                if oldEdge in conn:
                    val = conn[oldEdge]
                    conn[newEdge] = val
                    del conn[oldEdge]
                    break

    def _changeStat_(self, oldIndex, newIndex):
        bStat = self.branchStat.loc[[oldIndex]]
        row = bStat
        row.index = [newIndex]
        self.branchStat = self.branchStat.append(row, ignore_index=False)
        self.branchStat.drop(oldIndex, axis=0, inplace=True)

    def _mergeNodes_(self, parent, chId):
        allProp = []
        for id in chId:
            edge = (parent, id)
            for conn in self.connectionProp:
                if edge in conn:
                    allProp.append(conn[edge])

    def _mergeBranchStat_(self, parent, chId):
        edges = [(parent, id) for id in chId]
        data = self.branchStat.loc[edges]
        edge = (parent, chId[0])
        merged = pd.DataFrame(data.sum(axis=0)).T
        data = data.append(merged)
        data.drop(edges, inplace=True)
        data.index = [edge]

    def _pruneSameChild_(self):
        prune = False
        groups = self.groupLeafByParent()
        for parent, childs in groups.items():
            if len(childs) > 1:
                allChilds = self.getChilds(parent)
                labels = [self.getNode(id).attr for id in childs]
                sameLbls = groupSameElements(labels)
                if (len(sameLbls) > 1) or (len(allChilds) > len(childs)):
                    for leafs in sameLbls:
                        if len(leafs) > 1:
                            ind_leafs = groups[parent]
                            ind_leafs = itemgetter(*leafs)(ind_leafs)
                            self._makeOneNode_(parent, ind_leafs)
                            self._multipleConnect(parent, ind_leafs)
                            self._mergeBranchStat_(parent, ind_leafs)
                            prune = True
                else:
                    # prune leafs
                    for eq in sameLbls:
                        chId = [childs[i] for i in eq]
                        self.pruneAll(parent, chId)
                        self._pruneConnect_(parent, chId)
                        self._pruneBranchStat_(parent, chId)
                        prune = True
        return prune

    def _getConnections_(self, id):
        return [conn for conn in self.connectionProp for edge in conn.keys() if edge[0] == id]

    def _prob_(self, parentStat, edges):
        W = parentStat.sum()
        P = self.branchStat.loc[edges].sum(axis=0)
        return P.divide(W).round(3)

    def _predict_(self, example, node):
        if node.type == 'leaf':
            res = pd.DataFrame(columns=self.targetLbls)
            for lbl in self.targetLbls:
                res[lbl] = [float(0) if lbl != node.attr else float(1)]
            return res
        else:
            test = node.attr
            val = example[test]
            connections = self._getConnections_(node.id)
            nextNode = None
            if not ((val is None) or (val is np.nan)):
                if self.attrributeTypes[test] == 1:
                    # handle categorial
                    for connect in connections:
                        if nextNode is not None:
                            break
                        for k, v in connect.items():
                            if v == val:
                                nextNode = self.getNode(k[1])
                                break
                else:
                    # handle numerical
                    for connect in connections:
                        if nextNode is not None:
                            break
                        for k, v in connect.items():
                            if '<=' in v:
                                testVal = float(v[3:])
                                if val <= testVal:
                                    nextNode = self.getNode(k[1])
                                    break
                            else:
                                testVal = float(v[2:])
                                if val > testVal:
                                    nextNode = self.getNode(k[1])
                                    break
                if nextNode is not None:
                    return self._predict_(example, nextNode)
                else:
                    edges = [edge for conn in connections for edge in conn.keys()]
                    prob = self._prob_(node.stat, edges)
                    prob = pd.DataFrame(prob).T
                    return prob
            else:
                edges = [edge for conn in connections for edge in conn.keys()]
                prob = self._prob_(node.stat, edges)
                prob = pd.DataFrame(prob).T
                return prob
