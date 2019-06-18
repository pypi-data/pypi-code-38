#-*- coding:utf-8 -*-
import random as rn
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
class vnode:
    def __init__(self, index,cpu,position):
        self.index=index
        self.cpu=cpu
        self.position=position
        self.classflag = 0
    def msg(self):
        print('vnode',self.index,'cpu',self.cpu,'position',self.position)
class vedege:
    def __init__(self,index,bandwidth,a_t_b,delay):
        self.index=index
        self.bandwidth = bandwidth
        self.nodeindex=[int(a_t_b[0]),int(a_t_b[1])]
        self.delay=delay
        self.classflag = 0
    def msg(self):
        print('vedege',self.index,'bandwidth',self.bandwidth,'nodeindex',self.nodeindex)
class vnr:
    def __init__(self,filepath,id):
        self.id=id;
        self.time=0;
        self.duration=0;
        self.vnode=[]
        self.vedege = []
        with open(filepath) as filevnr:
            vnrmsg=[]
            while True:
                lines=filevnr.readline()
                if not lines:
                    break
                p_tmp= [float(value) for value in lines.split()]
                vnrmsg.append(p_tmp)

            self.time = vnrmsg[0][3];
            self.duration = vnrmsg[0][4];

            vnodenumber=vnrmsg[0][0]
            vedegenumber=vnrmsg[0][1]

            for i in range(int(vnodenumber)):
                vno=vnode(i,vnrmsg[i+1][2],vnrmsg[i+1][0:2])
                self.vnode.append(vno)

            n=len(self.vnode)
            for i in range(int(vedegenumber)):
                vedge=vedege(i,vnrmsg[n+1+i][2],vnrmsg[n+1+i][0:2],vnrmsg[n+1+i][3])
                self.vedege.append(vedge)
    def getEdege(self,u,v):
        for i in range(len(self.vedege)):
            if (self.vedege[i].nodeindex[0]==u and self.vedege[i].nodeindex[1]==v) or (self.vedege[i].nodeindex[1]==u and self.vedege[i].nodeindex[0]==v):
                return self.vedege[i]
        return []
    def distrution(self,cpu,bandwidth):
        #cpu:[low,up]
        #bandwidth [low,up]
        for i in range(len(self.vnode)):
            self.vnode[i].cpu=rn.uniform(cpu[0],cpu[1])
        for i in range(len(self.vedege)):
            self.vedege[i].bandwidth=rn.uniform(bandwidth[0],bandwidth[1])
    def getG(self):
        g = nx.Graph()
        for vnode in self.vnode:
            g.add_node(vnode.index,cpu=vnode.cpu,position=vnode.position,classflag=vnode.classflag)
        en = len(self.vedege)
        for i in range(en):
            g.add_edge( self.vedege[i].nodeindex[0], self.vedege[i].nodeindex[1], bandwidth=self.vedege[i].bandwidth)
        return g
    def drawVNR(self):
        plt.figure()
        g = self.getG()
        pos = {vnode.index: vnode.position for vnode in self.vnode}
        nx.draw(g, node_color=[0.5, 0.8, 0.5], font_size=8, node_size=300,  with_labels=True, nodelist=g.nodes())
        nx.draw_networkx_edge_labels(g, pos, edge_labels={edege: g[edege[0]][edege[1]]["bandwidth"] for edege in g.edges()})
        plt.show()
    def msg(self):
        n = len(self.vnode)
        for i in range(n):
            self.vnode[i].msg()
        n=len(self.vedege)
        for i in range(n):
            self.vedege[i].msg()
class VNRS:
    def __init__(self,vnrfilepath,n):
        self.vnr=[]
        for i in range(n):
            vnodef=vnrfilepath + "\\req" + str(i) + ".txt"
            self.vnr.append(vnr(vnodef,i))
    def changeDelayDistribution(self,units=1000):
        duration=np.round(np.random.exponential(units,len(self.vnr))+1)
        for i in range(len(self.vnr)):
            self.vnr[i].duration=duration[i]
    def msg(self):
        n=len(self.vnr)
        print('vnr:',n)
        for i in range(n):
            print('----------------------')
            self.vnr[i].msg()






