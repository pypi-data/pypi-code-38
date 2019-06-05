"""
command line tools to simplify yeargraphs and extended graphs

"""
import igraph
from graph_tool import load_graph
from os.path import splitext

import os

import logging
logging.getLogger().setLevel(logging.DEBUG)

import pandas
from tqdm import tqdm
from network_extensions.extendedGraph.ExtendedGraphToolGraph import ExtendedGraph as EG
from network_extensions.extendedGraph.ExtendedGraph import ExtendedGraph
from network_extensions.igraphx import getGraphsFromFile, writeGraphsToFile
import getopt
import sys
import locale
try:
    locale.setlocale(locale.LC_ALL,"en_US.utf8") #set correct otherwise it write "," instead of dots in graphml "."
except:
    pass
def simplifyYearGraph(fn,loops=None,degree=0):
    with open(fn,"rb") as inf:
     print("READING...")
     ygr = getGraphsFromFile(inf)
     print("done...")
    #new_gr = {}
    for y,gr in ygr.items():
        print("process %s"%y)
        degr = gr.vs.select(_degree=0)

        len_del = len(degr)
        degr.delete()

        print("deleted %s:%s"%(y,len_del))

    fn,ext = splitext(fn)
    with open("%s_simpl.ygz"%fn,"wb") as outf:
        writeGraphsToFile(ygr,outf)


def addEdgePropertiesToYearGraph(extGraphFolder,attrs):


    ynw2 = {}
    for name in os.listdir(extGraphFolder):

        y = int(name)
        ynw2[y] = ExtendedGraph.load_extGraph(os.path.join(extGraphFolder,name))
        ynw2[y].edgeAttrs

        ynw = {}
        fn2  = fn
        for i in range(1900,2000):
            try:
                print("%s"%i)
                ynw[i] = load_graph(os.path.join(fn,"%s.graphml"%i))
            except FileNotFoundError:
                print("not:%s"%os.path.join(fn,"%s.graphml"%i))

    else:DictToEdgeAttr(attrs)

    print("writing all to file")
    writeGraphsToFile(ynw2, open(os.path.join("/tmp/", "extr2_year_pers_pers.ygz"), "wb"))



def mergeGraphs(fn,intervall,attr):
    if os.path.isdir(fn):
        ynw = {}
        fn2  = fn
        for i in range(1900,2000):
            try:
                print("%s"%i)
                ynw[i] = load_graph(os.path.join(fn,"%s.graphml"%i))
            except FileNotFoundError:
                print("not:%s"%os.path.join(fn,"%s.graphml"%i))
            
    else:
        with open(fn,"rb") as inf:
            ynw = EG.getGraphsFromFile(inf)
            fn2,ext = os.path.splitext(fn)
    mg = EG.mergeAllGraphsIntervall(ynw,intervall,mergeattr=attr)

    EG.replaceInAllGraphs(mg,"name","inst","Institution_","")

    with open(fn2+"_merge_%s.ygr"%intervall,"wb") as outf:
        EG.writeGraphsToFile(mg,outf)

def mergeGraphsX(extGraphFolder,intervall):

    #with open(fn, "rb") as inf:
    #    print("READING...")
    #    ygr = getGraphsFromFile(inf)

    ygr = {}
    for name in tqdm(os.listdir(extGraphFolder)):
        y = int(name)
        ygr[y] = ExtendedGraph.load_extGraph(os.path.join(extGraphFolder, name))

    for y,g in ygr.items():
        ynw = {}
        fn2  = fn
        for i in range(1900,2000):
            try:
                print("%s"%i)
                ynw[i] = load_graph(os.path.join(fn,"%s.graphml"%i))
            except FileNotFoundError:
                print("not:%s"%os.path.join(fn,"%s.graphml"%i))


        print("add edgedict",y)
        g.set_edgeAttrsDict()
        
    newgraphs = ExtendedGraph.mergeAllGraphsIntervall(ygr, intervall, mergeattr="ident")

    #fn, ext = splitext(fn)

    for y, nw in tqdm(newgraphs.items()):
        nw.edgeListLongToEdgeList()
        nw.set_edgeAttrsDict()
        print("Y",y,len(nw.edgeList),len(nw.edgeAttrs))
        
        nw.save_extGraph(os.path.join(extGraphFolder+"_out_intervall_%s", "yrg/%s")% (intervall,y), exist_ok=True)




def deleteDuplicatesByAttr(fn,attr,undirected=True,addWeights=None,simplifyEdges = False,debug = False,outputTypes = None, pattern = None):

    if pattern is None:
        pattern = "%s.graphml"


    if os.path.isdir(fn):
        ygr = {}
        fn2  = fn
        if not fn.endswith("/"):
            fn = fn + "/" #needed below
        for i in range(1900,2000):
            try:
                print("%s"%i)
                ygr[i] = igraph.load(os.path.join(fn,pattern%i))
            except FileNotFoundError:
                print("not:%s"%os.path.join(fn,pattern%i))

    else:

        with open(fn, "rb") as inf:
            print("READING...")
            ygr = getGraphsFromFile(inf)
            print("done...")
            # new_gr = {}
    cnt = 0
    for y, gr in tqdm(ygr.items()):
        print("process %s" % y)
        if debug == True and cnt not in  [4,10,15]: #take only a few
               continue

        attrset=set()
        delete_edges = []

        for i in range(0,len(gr.es)):
            edge = gr.es[i]

            source = edge.source
            target = edge.target
            if undirected and source < target:
                source_tmp = source
                source = target
                target = source_tmp
            if ((source,target,edge[attr])) in attrset: #gibt es schon, dann loeschen
                delete_edges.append(i)
            else:
                attrset.add((source,target,edge[attr]))


        len_del = len(delete_edges)
        gr.delete_edges(delete_edges)

        print("deleted %s:%s" % (y, len_del))


        if addWeights is not None:
            if attr not in gr.edge_attributes():
                continue
            attrs = pandas.Series(gr.es[attr]) #get all the attrs
            vals = dict(attrs.value_counts())
            weights = []
            for a in attrs:
                w = addWeights(vals[a])
                weights.append(w)
            gr.es["weight"] = weights

        if simplifyEdges:
            gr.simplify(combine_edges={"weight":sum,attr:join})

    fn, ext = splitext(fn)
    with open("%s_del.ygz" % fn, "wb") as outf:
        writeGraphsToFile(ygr, outf,outputTypes=outputTypes)


def lin_weight(x):
    if x > 5:
        return 1./float((x-4))
    else:
        return 1.

def join(l):
    return ",".join(l)



if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:f:i:a:sdp:")
        print(opts)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print("""Allowed options are:
        -c can be "simplify","addAttributes","merge" or "deleteDuplicateEdges"
        -f the filename for input
        -i intervall only needed for "merge" 
        -a for "deleteDuplicateEdges" attibutename  which identifies duplicate edges (only one edge with the same value stays, between two nodes)
        -s for "deleteDuplicateEdges" simplifyEdges, only one edge is kept, the identifying attribute is joined with ","
        -t for "deleteDuplicateEdges" can be "graphml","gml","payjek" defines the output format in the yeargraphs, more then one format can be choosen.  
        )
        sys.exit(2)
        """)

    mode = None
    simplify = False
    debug = False
    modes_str = None
    outputtype_str = None
    pattern = None
    attr = "ident"
    for o, a in opts:

        if o =="-c":
            if a =="simplify":
                mode= "simplify"
            elif a == "addAttributes":
                mode = "addAttributes"
            elif a == "merge":
                mode = "merge"
            elif a == "deleteDuplicateEdges":
                mode = a
        elif o =="-f":
            fn = a
        elif o == "-i":
            intervall = int(a)
        elif o =="-a":
            attr = a
        elif o =="-s":
            simplify = True
        elif o == "-d":
            debug = True
        elif o == "-t":
            outputtype_str=a
        elif o == "-p":
            pattern = a
            
    if mode == "simplify":
        simplifyYearGraph(fn)
    elif mode == "addAttributes":
        addEdgePropertiesToYearGraph(fn,["year","bibcode"])
    elif mode == "merge":
        mergeGraphs(fn,intervall,attr)
    elif mode == "deleteDuplicateEdges":
        if outputtype_str is not None:
            outputtypes = ",".split
        else:
            outputtypes = ["graphml"]
        deleteDuplicatesByAttr(fn,attr,addWeights=lin_weight,simplifyEdges=simplify,debug = debug,outputTypes=outputtypes,pattern=pattern)
