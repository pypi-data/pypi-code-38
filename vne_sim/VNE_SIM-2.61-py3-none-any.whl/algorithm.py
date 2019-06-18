import networkx as nx
import numpy as np
import copy as cp
import matplotlib.pyplot as plt
def nodemapping(snode,sedege,vnr):
    success=True
    vn=len(vnr.vnode)
    sn=len(snode)
    v2sindex=[]
    for vi in range(vn):
        for si in range(sn):
            if vnr.vnode[vi].cpu<snode[si].lastcpu and vnr.id not in [x[0] for x in snode[si].vnodeindexs]:
                snode[si].lastcpu=snode[si].lastcpu-vnr.vnode[vi].cpu
                snode[si].vnodeindexs.append([vnr.id,vnr.vnode[vi].index])
                v2sindex.append(si)
                break
            else:
                if (si==sn-1) :
                    success=False
                    return success,[],[],[]
    return success,v2sindex,snode,sedege
def  edegemapping(asnode,asedege,vnr,v2sindex):
    success=True
    ve2seindex=[]
    ven=len(vnr.vedege)
    for i in range(ven):
        fromnode=vnr.vedege[i].nodeindex[0]
        tonode = vnr.vedege[i].nodeindex[1]
        fromnode=v2sindex[fromnode]
        tonode=v2sindex[tonode]
        bandlimit=vnr.vedege[i].bandwidth
        g=Sn2_networkxG(asnode,asedege,bandlimit)
        pathindex,cost=shortpath(g,asedege,fromnode,tonode)
        if not pathindex:
            return False,[],[],[]
        for j in pathindex:
            asedege[j].lastbandwidth=asedege[j].lastbandwidth-vnr.vedege[i].bandwidth
            asedege[j].vedegeindexs.append([vnr.id,i])
        ve2seindex.append(pathindex)
    return success,ve2seindex,asnode,asedege
#EH_ALG
def  edegemapping2(asnode,asedege,vnr,v2sindex):
    v2sindex=np.array(v2sindex)
    success=True
    ve2seindex=[]
    ven=len(vnr.vedege)
    for i in range(ven):
        fromnode=vnr.vedege[i].nodeindex[0]
        tonode = vnr.vedege[i].nodeindex[1]
        
        fromnode=v2sindex[v2sindex[:,0]==fromnode][0][1]
        tonode=v2sindex[v2sindex[:,0]==tonode][0][1]
        bandlimit=vnr.vedege[i].bandwidth
        g=Sn2_networkxG(asnode,asedege,bandlimit)
        pathindex,cost=shortpath(g,asedege,fromnode,tonode)
        if (not pathindex) and (cost is not 0):
            return False,[],[],[]
        for j in pathindex:
            asedege[j].lastbandwidth=asedege[j].lastbandwidth-vnr.vedege[i].bandwidth
            asedege[j].vedegeindexs.append([vnr.id,i])
        ve2seindex.append(pathindex)
    return success,ve2seindex,asnode,asedege

def  edegemapping3(asnode,asedege,myvnr,v2sindex):
    v2sindex = np.array(v2sindex)
    success = True
    ve2seindex = []
    for vedege in myvnr.vedege:
        fromnode = vedege.nodeindex[0]
        tonode = vedege.nodeindex[1]
        fromnode = v2sindex[v2sindex[:, 0] == fromnode][0][1]
        tonode = v2sindex[v2sindex[:, 0] == tonode][0][1]
        bandlimit = vedege.bandwidth
        g = Sn2_networkxG(asnode, asedege, bandlimit)
        pathindex, cost = shortpath(g, asedege, fromnode, tonode)
        if (not pathindex) and (cost is not 0):
            return False, [], [], []
        for j in pathindex:
            asedege[j].lastbandwidth = asedege[j].lastbandwidth - vedege.bandwidth
            asedege[j].vedegeindexs.append([myvnr.id, vedege.index])
        ve2seindex.append(pathindex)
    return success, ve2seindex, asnode, asedege
def Sn2_networkxG(snode,sedege,bandlimit=0):
    g=nx.Graph()
    for s in snode:
        g.add_node(s.index)
    en=len(sedege)
    for i in range(en):
        if  sedege[i].lastbandwidth>bandlimit:
            g.add_weighted_edges_from([(sedege[i].nodeindex[0], sedege[i].nodeindex[1], sedege[i].lastbandwidth)])
    return g

def shortpath(G,sedege,fromnode,tonode):
    try:
        sedegeindex=[]
        path=nx.dijkstra_path(G,fromnode,tonode,weight="none")
        for i in range(len(path)-1):
            sedegeindex.append(getedege(sedege,path[i],path[i+1]))
        cost=nx.dijkstra_path_length(G,fromnode,tonode,weight="none")
    except nx.NetworkXNoPath:
        return [],[]
    return sedegeindex,cost,
def kshortpath(G,sedege,source,slink,kpath=1,weight="None"):
    A = []
    B = []
    A.append(tuple(nx.dijkstra_path(G, source, slink,weight=weight)))
    for k in range(1, kpath):
        for i in range(0, len(A[k - 1]) - 1):
            g = cp.deepcopy(G)
            spurnode = A[k - 1][i]
            rootpath = A[k - 1][0:i]
            for p in A:
                if rootpath == p[0:i]:
                    if g.has_edge(p[i], p[i + 1]):
                        g.remove_edge(p[i], p[i + 1])
            for rootpathnode in rootpath:
                if g.has_node(rootpathnode):
                    g.remove_node(rootpathnode)
            try:
                spurpath = nx.dijkstra_path(g, spurnode, slink)
                totalpath = list(rootpath) + spurpath
                B.append(tuple(totalpath))
            except nx.NetworkXNoPath:
                continue
        if not B:
            break
        g = cp.deepcopy(G)
        for i in range(len(B) - 1):
            for j in range(len(B) - 1):
                costi = 0
                for nodei in range(len(B[i]) - 1):
                    costi = costi + g.get_edge_data(B[i][nodei], B[i][nodei + 1])["weight"]
                costj = 0
                for nodei in range(len(B[j]) - 1):
                    costj = costj + g.get_edge_data(B[j][nodei], B[j][nodei + 1])["weight"]
                if costi < costj:
                    t = B[i]
                    B[i] = B[j]
                    B[j] = t
        A.append(B[0])
        B.remove(B[0])
    paths=[]
    costs=[]
    for path in A:
        sedegeindex = []
        cost=0
        for i in range(len(path)-1):
            index=getedege(sedege, path[i], path[i + 1])
            cost=cost+sedege[index].lastbandwidth
            sedegeindex.append(index)
        paths.append(sedegeindex)
        costs.append(cost)
    return paths,costs
def getedege(sedege,sourcenode,targetnode):
    for i in range(len(sedege)):
        for j in range(len(sedege[i].nodeindex)):
            if (sourcenode==sedege[i].nodeindex[0] and targetnode==sedege[i].nodeindex[1] ) or (sourcenode==sedege[i].nodeindex[1] and targetnode==sedege[i].nodeindex[0] ) :
                return sedege[i].index
    return []



