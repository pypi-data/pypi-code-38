#-*- coding:utf-8 -*-
import networkx as nx
import copy as cp
import random as rd
import matplotlib.pyplot as plt
import numpy as np
class snode:
    def __init__(self,index,cpu,position):
        self.index=index
        self.position=position
        self.cpu=cpu
        self.lastcpu=cpu
        self.vnodeindexs = []
        self.open=False
        self.mappable_flag=False
        self.baseEnergy=0
        self.maxEnergy=0
        self.classflag=0
    def msg(self):
        print('snode', self.index, 'cpu', self.cpu, 'lastcpu', self.lastcpu,'vnodeindexs',self.vnodeindexs,'position', self.position)

class sedege:
    def __init__(self,index,bandwidth,a_t_b,delay):
        self.index = index;
        self.nodeindex = [int(a_t_b[0]),int(a_t_b[1])]
        self.bandwidth = bandwidth
        self.lastbandwidth = bandwidth;
        self.vedegeindexs = []
        self.delay = delay
        self.open=False
        self.mappable_flag = False
        self.baseEnergy=0
        self.classflag = 0
    def msg(self):
        print('sedege', self.index, 'bandwidth', self.bandwidth,'lastbandwidth',self.lastbandwidth, 'nodeindex', self.nodeindex,'vedegeindexs',self.vedegeindexs)
class SN:
    def __init__(self, snfilepath):
        self.id = 0
        self.snode = []
        self.sedege = []
        self.p = 0
        self.t = 0
        with open(snfilepath) as filevnr:
            lines = filevnr.readline()
            p_tmp = [float(value) for value in lines.split()]
            snodenumber = int(p_tmp[0])
            sedegenumber = int(p_tmp[1])
            for i in range(snodenumber):
                lines = filevnr.readline()
                if not lines:
                    break
                    pass
                p_tmp = [float(value) for value in lines.split()]
                sno = snode(i, p_tmp[2], p_tmp[0:2])
                self.snode.append(sno)

            for i in range(sedegenumber):
                lines = filevnr.readline()
                if not lines:
                    break
                    pass
                p_tmp = [float(value) for value in lines.split()]
                sedge = sedege(i, p_tmp[2], p_tmp[0:2], p_tmp[3])
                self.sedege.append(sedge)
    def nodemapping(self, vnr, v2sindex):
        vn = len(v2sindex)
        for i in range(vn):
            if self.snode[v2sindex[i]].lastcpu < self.snode[v2sindex[i]].lastcpu - vnr.vnode[i].cpu:
                raise Exception("CPU约束不满足，无法映射虚拟节点")
            self.snode[v2sindex[i]].lastcpu = self.snode[v2sindex[i]].lastcpu - vnr.vnode[i].cpu
            self.snode[v2sindex[i]].vnodeindexs.append([vnr.id, vnr.vnode[i].index])
            self.snode[v2sindex[i]].open = True
        print('map  vnr  ', vnr.id, ' success')
    def nodemapping2(self, vnr, v2sindex):
        # v2sindex=[[v,s],[]...]
        vn = len(v2sindex)
        for i in range(vn):
            if self.snode[v2sindex[i][1]].lastcpu < vnr.vnode[v2sindex[i][0]].cpu and vnr.id not in [id_vnode[0] for id_vnode in self.snode[v2sindex[i][1]].vnodeindexs]:
                raise Exception("CPU约束不满足，无法映射虚拟节点 或者同一个虚拟节点映射到同一个物理节点上")
            self.snode[v2sindex[i][1]].lastcpu = self.snode[v2sindex[i][1]].lastcpu - vnr.vnode[v2sindex[i][0]].cpu
            self.snode[v2sindex[i][1]].vnodeindexs.append([vnr.id, vnr.vnode[v2sindex[i][0]].index])
            self.snode[v2sindex[i][1]].open = True
        print('map  vnr node  ', vnr.id, ' success')

    def removenodemapping(self, vnr):
        sn = len(self.snode)
        for i in range(sn):
            xtemp = []
            for x in self.snode[i].vnodeindexs:
                if vnr.id == x[0]:
                    self.snode[i].lastcpu = self.snode[i].lastcpu + vnr.vnode[x[1]].cpu
                    xtemp.append(x)
                    # self.snode[i].vnodeindexs.remove(x)
            for x in xtemp:
                self.snode[i].vnodeindexs.remove(x)
            if not self.snode[i].vnodeindexs:
                self.snode[i].open = False

        print('remove vnr node ', vnr.id, ' success')
    def edegemapping(self, vnr, ve2seindex):
        i = 0
        for path in ve2seindex:
            for e in path:
                if self.sedege[e].lastbandwidth < vnr.vedege[i].bandwidth:
                    raise Exception("带宽约束不满足,无法映射链路")
                self.sedege[e].lastbandwidth = self.sedege[e].lastbandwidth - vnr.vedege[i].bandwidth
                self.sedege[e].vedegeindexs.append([vnr.id, vnr.vedege[i].index])
                self.sedege[e].open = True
            i = i + 1
        print('map vnr edege ', vnr.id, ' success')

    def removeedegemapping(self, vnr):
        en = len(self.sedege)
        for e in range(en):
            tempx = []
            for x in self.sedege[e].vedegeindexs:
                if vnr.id == x[0]:
                    self.sedege[e].lastbandwidth = self.sedege[e].lastbandwidth + vnr.vedege[x[1]].bandwidth
                    tempx.append(x)
            for x in tempx:
                self.sedege[e].vedegeindexs.remove(x)
            if not self.sedege[e].vedegeindexs:
                self.sedege[e].open = False
        print('remove vnr edege ', vnr.id, ' success')

    def openstate(self):
        nodeopen = 0
        for snode in self.snode:
            if snode.open:
                nodeopen = nodeopen + 1
        sedegeopen = 0
        for sedege in self.sedege:
            if sedege.open:
                sedegeopen = sedegeopen + 1
        return nodeopen, sedegeopen

    def node_edege_util_rate(self):
        nodeutilrate = 0
        edegeutilrate = 0
        a = 0
        b = 0
        for snode in self.snode:
            if snode.open:
                a = a + snode.cpu
                b = b + snode.lastcpu
                # nodeutilrate.append((snode.cpu-snode.lastcpu)/snode.cpu)
        if a is 0:
            nodeutilrate = 0
        else:
            nodeutilrate = (a - b) / a
        a = 0
        b = 0
        for edege in self.sedege:
            if edege.open:
                a = a + edege.bandwidth
                b = b + edege.lastbandwidth
                # edegeutilrate.append((edege.bandwidth-edege.lastbandwidth)/edege.bandwidth)
        if a is 0:
            edegeutilrate = 0
        else:
            edegeutilrate = (a - b) / a
        return nodeutilrate, edegeutilrate

    def power(self, time):
        totalp = 0
        for snode in self.snode:
            if snode.open:
                totalp = totalp + (snode.maxEnergy - snode.baseEnergy) * (
                            snode.cpu - snode.lastcpu) / snode.cpu + snode.baseEnergy
        for sedege in self.sedege:
            if sedege.open:
                totalp = totalp + sedege.baseEnergy
        dtenergy = self.p * (time - self.t)
        self.t = time
        self.p = totalp
        return dtenergy

    def Sn2_networkxG(self, bandlimit=0):
        g = nx.Graph()
        for snod in self.snode:
            g.add_node(snod.index,cpu=snod.cpu,lastcpu=snod.lastcpu,classflag=snod.classflag,open=snod.open)
        en = len(self.sedege)
        for i in range(en):
            if self.sedege[i].lastbandwidth > bandlimit:
                g.add_edge(self.sedege[i].nodeindex[0], self.sedege[i].nodeindex[1],lastbandwidth= self.sedege[i].lastbandwidth,bandwidth=self.sedege[i].bandwidth,classflag=self.sedege[i].classflag,open=self.sedege[i].open)
        return g

    def getnodeneighbors(self, n):
        g = self.Sn2_networkxG()
        iternode = g.neighbors(n)
        nodes = [x for x in iternode]
        return nodes

    def getedege(self, sourcenode, targetnode):
        for i in range(len(self.sedege)):
            for j in range(len(self.sedege[i].nodeindex)):
                if (sourcenode == self.sedege[i].nodeindex[0] and targetnode == self.sedege[i].nodeindex[1]) or (
                        sourcenode == self.sedege[i].nodeindex[1] and targetnode == self.sedege[i].nodeindex[0]):
                    return self.sedege[i].index
        return []

    # 最小数调用
    def getedege2(self, sourcenode, targetnode):
        for i in range(len(self.sedege)):
            for j in range(len(self.sedege[i].nodeindex)):
                if (sourcenode == self.sedege[i].nodeindex[0] and targetnode == self.sedege[i].nodeindex[1]) or (
                        sourcenode == self.sedege[i].nodeindex[1] and targetnode == self.sedege[i].nodeindex[0]):
                    return self.sedege[i]
        return []

    def get_vnr_edege(self, vnr, sourcenode, targetnode):
        for i in range(len(vnr.vedege)):
            if (sourcenode == vnr.vedege[i].nodeindex[0] and targetnode == vnr.vedege[i].nodeindex[1]) or (
                    sourcenode == vnr.vedege[i].nodeindex[1] and targetnode == vnr.vedege[i].nodeindex[0]):
                return vnr.vedege[i].index
        return [None]

    def nodecpu(self, nodeindex=[], isdraw=False):
        if not nodeindex:
            cpu = [[x.index, x.lastcpu] for x in self.snode]
            print(cpu)
            if isdraw:
                plt.hist([x[1] for x in cpu])
                plt.show()
            return cpu
        else:
            cpu = []
            for i in nodeindex:
                cpu.append([self.snode[i].index, self.snode[i].lastcpu])
            print(cpu)
            if isdraw:
                plt.hist([x[1] for x in cpu])
                plt.show()
            return cpu

    def edegebandwidth(self, edegeindex=[], isdraw=False):
        if not edegeindex:
            bandwidth = [[x.index, x.lastbandwidth] for x in self.sedege]
            print(bandwidth)
            if isdraw:
                plt.hist([x[1] for x in bandwidth])
                plt.show()
            return bandwidth
        else:
            bandwidth = []
            for i in edegeindex:
                bandwidth.append([self.sedege[i].index, self.sedege[i].lastbandwidth])
            print(bandwidth)
            if isdraw:
                plt.hist([x[1] for x in bandwidth])
                plt.show()
            return bandwidth

    def changedistributioneNergy(self, Pb, Pm, Pn):
        n = len(self.snode)
        for i in range(n):
            self.snode[i].baseEnergy = rd.uniform(*Pb)
            self.snode[i].maxEnergy = rd.uniform(*Pm)
        en = len(self.sedege)
        for i in range(en):
            self.sedege[i].baseEnergy = Pn

    def changedistribution(self, cpu, bandwidth,dtype=np.float32):
        # [dowm,up]
        n = len(self.snode)
        for i in range(n):
            self.snode[i].cpu = float("%.3f"%rd.uniform(*cpu))
            self.snode[i].lastcpu = self.snode[i].cpu
        en = len(self.sedege)
        for i in range(en):
            self.sedege[i].bandwidth = float("%.3f"%rd.uniform(*bandwidth))
            self.sedege[i].lastbandwidth = self.sedege[i].bandwidth

    def resetResource(self):
        self.p = 0
        self.t = 0
        n = len(self.snode)
        for i in range(n):
            self.snode[i].lastcpu = self.snode[i].cpu
            self.snode[i].vnodeindexs = []
            self.snode[i].open = False
        en = len(self.sedege)
        for i in range(en):
            self.sedege[i].lastbandwidth = self.sedege[i].bandwidth
            self.sedege[i].vedegeindexs = []
            self.sedege[i].open = False

    def getSNResource(self, alpha=1):
        sum = 0
        for i in range(len(self.snode)):
            sum = sum + self.snode[i].lastcpu
        for i in range(len(self.sedege)):
            sum = sum + alpha * self.sedege[i].lastbandwidth
        return sum

    def reven_cost(self, vnr, vnode_mapindex, alpha=1):
        if len(vnr.vnode) != len(vnode_mapindex):
            print("naping no match")
            return []
        else:
            vsum = 0
            for i in range(len(vnr.vnode)):
                vsum = vsum + vnr.vnode[i].cpu
            for i in range(len(vnr.vedege)):
                vsum = vsum + alpha * vnr.vedege[i].bandwidth
            sum = self.getSNResource()
            for i in range(len(vnode_mapindex)):
                if vnr.vnode[i].cpu > self.snode[vnode_mapindex[i]].lastcpu:
                    print("naping no match")
                    return []
            self.nodemapping(vnr, vnode_mapindex)
            asnode = cp.deepcopy(self.snode)
            asedege = cp.deepcopy(self.sedege)
            success, ve2seindex, asnode, asedege = self.testedegemapping(asnode, asedege, vnr, vnode_mapindex)
            if success:
                self.edegemapping(vnr, ve2seindex)
                sum2 = self.getSNResource()
                self.removenodemapping(vnr)
                self.removeedegemapping(vnr)
                return vsum / abs(sum2 - sum)
            return []


    def yenksp(self, graph, source, sink, k):
        # graph=nx.Graph
        global distance
        a = nx.dijkstra_path(graph, source, sink, weight="none")
        # a = graph.get_shortest_paths(source, sink, weights=distance, mode=ALL, output="vpath")[0]
        b = []  # Initialize the heap to store the potential kth shortest path
        # for xk in range(1,k):
        for xk in range(1, k + 1):
            # for i in range(0,len(a)-1):
            for i in range(0, len(a)):
                neibornode = graph.neighbors(i)
                edeges = [(i, u, graph.get_edge_data(i, u)) for u in neibornode]
                if i != len(a[:-1]) - 1:
                    spurnode = a[i]
                    rootpath = a[0:i]
                    for p in a:
                        if rootpath == p:
                            graph.remove_node(i)
                spurpath = nx.dijkstra_path(graph, spurnode, sink, weight="none")
                totalpath = rootpath + spurpath
                b.append(totalpath)
                graph.add_weighted_edges_from(edeges)
            for ti in range(len(b)):
                for tj in range(len(b)):
                    if len(b[ti]) < len(b[tj]):
                        tmp = b[ti]
                        b[ti] = b[tj]
                        b[tj] = tmp
            a[k] = b[0]
        return a

    def drawSN(self,edege_label=False,classflag=False):
        plt.figure()
        g = self.Sn2_networkxG()
        pos = {snode.index: snode.position for snode in self.snode}
        if classflag:
            color = {}
            colomap = []
            for i in range(len(self.snode)):
                if self.snode[i].classflag not in color.keys():
                    color[self.snode[i].classflag] = self.randRGB()
                colomap.append(color[self.snode[i].classflag])
            nx.draw(g, node_color=colomap, font_size=8, node_size=300, pos=pos, with_labels=True,
                    nodelist=g.nodes())
            if  edege_label:nx.draw_networkx_edge_labels(g, pos, edge_labels={edege: g[edege[0]][edege[1]]["lastbandwidth"] for edege in
                                                              g.edges()})
        else:
            nx.draw(g, node_color=[0.5, 0.8, 0.8], font_size=8, node_size=300, pos=pos, with_labels=True,
                    nodelist=g.nodes())
            if  edege_label:nx.draw_networkx_edge_labels(g, pos, edge_labels={edege: g[edege[0]][edege[1]]["lastbandwidth"] for edege in
                                                              g.edges()})
        plt.show()

    def randRGB(self):
        return (np.random.randint(0, 255) / 255.0,
                np.random.randint(0, 255) / 255.0,
                np.random.randint(0, 255) / 255.0)

    def resourcedistribution(self, printflag=True):
        cpu = {}
        for snode in self.snode:
            if snode.classflag not in cpu.keys():
                cpu[snode.classflag] = []
            cpu[snode.classflag] = cpu[snode.classflag] + [snode.lastcpu]
        if printflag:
            for key in cpu.keys():
                print("class:", key, "num:", len(cpu[key]), "total:", sum(cpu[key]))
        return cpu

    def msg(self):
        n = len(self.snode)
        for i in range(n):
            print('--------------------')
            self.snode[i].msg()
        n = len(self.sedege)
        for i in range(n):
            print('--------------------')
            self.sedege[i].msg()

