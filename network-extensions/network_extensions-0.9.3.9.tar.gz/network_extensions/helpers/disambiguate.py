import subprocess
import uuid
from collections import defaultdict
from unidecode import unidecode
import graph_tool
import os
from tqdm import tqdm

from network_extensions.extendedGraph.ExtendedGraphToolGraph import ExtendedGraph
import logging

logger = logging

logger.basicConfig(level=logging.DEBUG)

logger.debug("START")
yrg = ExtendedGraph.getGraphsFromFile(open("/home/dwinter/Downloads/graphs_merge_3.ygr","rb"))



def findInitials(txt):
    txt = txt.replace(".", " ")
    txt = txt.replace("-", " ")
    inits = txt.split(" ")
    ret = []
    for init in inits:
        s = init.strip()
        if s == "":
            continue
        else:
            ret.append(s[0])
    return " ".join(ret)



for y,mrg in tqdm(yrg.items()):
    candidates = defaultdict(list)

    # ### Persons with same name and place will be identified
    logging.debug("Start level 1: institutions")
    cnt = 0
    for k, institution in zip(mrg.vertex_properties["ident_3"],mrg.vertex_properties["place"]):
            k = unidecode(k)
            try:
                name = k.split(",")[0].strip()
                vn = k.split(",")[1].strip()[0]
            except IndexError:
                name = k.split(" ")[0].strip()[0]
                try:
                    vn = k.split(" ")[1].strip()
                except IndexError:
                    vn = ""
            candidates[(name,vn,institution)].append(cnt)
            cnt += 1

    map_nodes = {}
    map_nodes_reverse = {}
    cnt = 0
    for k,ns in candidates.items():
        update_cnt = False
        for n in ns:


            if k[2] != "-": # institute exists:
                map_nodes[n] = cnt
                map_nodes_reverse[cnt] = n
                update_cnt  = True
            else:
                map_nodes[n] = cnt
                map_nodes_reverse[cnt] = n
                cnt+=1
        if update_cnt:
            cnt+=1
            update_cnt = False


    new_elist = []
    eprops = defaultdict(dict)
    for e in mrg.edges():
        new_elist.append((map_nodes[e.source()],map_nodes[e.target()]))
        for a,prop in mrg.edge_properties.items():
            eprops[a][(map_nodes[e.source()],map_nodes[e.target()])]=prop[e]

    new_gr = graph_tool.Graph()

    new_gr.add_vertex(cnt)

    new_gr.add_edge_list(new_elist)


    names = new_gr.new_vertex_property("string")
    places = new_gr.new_vertex_property("string")
    idents = new_gr.new_vertex_property("string")



    for num,(name,place,ident) in enumerate(zip(mrg.vertex_properties["ident_3"],mrg.vertex_properties["place"],mrg.vertex_properties["ident"])):
        name = unidecode(name)
        try:
            names[map_nodes[num]] = name
            places[map_nodes[num]] = place

            if  idents[map_nodes[num]] == "":
                idents[map_nodes[num]] == ident
            else:
                idents[map_nodes[num]] += ";"+ident

        except:
            print("NOT IN MRG: %s"%name)


    new_gr.vertex_properties["name"] = names
    new_gr.vertex_properties["place"] = places
    new_gr.vertex_properties["ident"] = idents


    for k,dict_v in eprops.items():

        v = [dict_v[(s,t)]  for s,t,n in new_gr.get_edges()]
        new_gr.edge_properties[k] = new_gr.new_edge_property("string",v)

    new_gr.save("/tmp/inst_new_%s_gr.graphml" % y)

    deg = new_gr.degree_property_map("total")

    new_short = graph_tool.GraphView(new_gr, vfilt=lambda x: deg[x] > 0)

    graph_tool.Graph(new_short, prune=True).save("/tmp/inst_new_%s_short.graphml" % y)

    same_names = defaultdict(list)

    logging.debug("Start level 2: infomap")
    for n,name in enumerate(names):
        same_names[name].append(n)

    es = set(new_gr.edge_properties["bibcode"])
    paperToNum={v:k for k,v in enumerate(es)}


    name = "%s"%uuid.uuid4().urn

    with open("/tmp/%s.mpt"%name,"w") as out:
        out.write("# Network\n")
        out.write("*Vertices %s\n" % new_gr.num_vertices())
        for i,n in enumerate(new_gr.vertex_properties["name"]):
            out.write('%s "%s"\n'%(i+1,n))
        out.write("*Multiplex\n")
        for (s,e,n),bibcode in zip(new_gr.get_edges(),new_gr.edge_properties["bibcode"]):
            out.write("%s %s %s %s\n"%(1,int(s)+1,2,int(paperToNum[bibcode])+1))
            out.write("%s %s %s %s\n"%(2,int(paperToNum[bibcode])+1,1,int(e)+1))

    os.makedirs("/tmp/%s"%name,exist_ok=True)
    x = subprocess.run(["/home/dwinter/infomap/Infomap","-N","10","--tree","-i","multilayer","/tmp/%s.mpt"%name,"/tmp/%s"%name])


    # In[45]:


    ind2modul= defaultdict(list)
    with open("/tmp/%s/%s.tree"%(name,name),"r") as inf:
        for line in inf.readlines():
            try:
                splitted = line.replace("\n","").split(" ")
                num = splitted[-1]
                path = splitted[0]

            except:
                print(line.replace("\n","").split(" "))
                continue
            try:
                clu = path.split(":")[-1]
                ind2modul[int(num)-1] = clu
            except ValueError:
                print(num)

    ident_by_block = defaultdict(list)

   # for k,nodes in same_names.items():
    #    for n in nodes:
   #         ident_by_block[(k,ind2modul[n])].append(n)


    def findInitials(txt):
        txt = txt.replace("."," ")
        txt = txt.replace("-"," ")
        inits=txt.split(" ")
        ret = []
        for init in inits:
            s = init.strip()
            if s == "":
                continue
            else:
                ret.append(s[0])

        return " ".join(ret)


    # In[57]:


    ident2_by_block = defaultdict(list)
    for k,nodes in same_names.items():
        for n in nodes:
            try:
                name = k.split(",")[0].strip()
                vn = k.split(",")[1].strip()
            except IndexError:
                name = k.split(" ")[-1].strip()
                try:
                    vn = " ".join(k.split(" ")[0:-1]).strip()
                except IndexError:
                    vn = ""
            vn = findInitials(vn)
            ident2_by_block[(name,vn,ind2modul[n])].append((n,k,places[n]))



    map_nodes = {}
    map_nodes_reverse = {}
    cnt = 0
    for k,ns in ident2_by_block.items():
        for n,k,p in ns:
                map_nodes[n] = cnt
                map_nodes_reverse[cnt] = n
        cnt+=1
    new_elist = []
    eprops = defaultdict(dict)
    for e in new_gr.edges():
        new_elist.append((map_nodes[e.source()],map_nodes[e.target()]))
        for a,prop in new_gr.edge_properties.items():
            eprops[a][(map_nodes[e.source()],map_nodes[e.target()])]=prop[e]


    new2_gr = graph_tool.Graph()


    # In[61]:


    new2_gr.add_vertex(cnt)
    new2_gr.add_edge_list(new_elist)
    names = new2_gr.new_vertex_property("string")
    places = new2_gr.new_vertex_property("string")
    idents = new2_gr.new_vertex_property("string")

    for num,(name,place,ident) in enumerate(zip(new_gr.vertex_properties["name"],new_gr.vertex_properties["place"],new_gr.vertex_properties["ident"])):
        try:
            names[map_nodes[num]] = name
            places[map_nodes[num]] = place
        except:
            print("NOT IN MRG: %s"%name)

        if idents[map_nodes[num]] == "":
            idents[map_nodes[num]] == ident
        else:
            idents[map_nodes[num]] += ";" + ident

    new2_gr.vertex_properties["name"] = names
    new2_gr.vertex_properties["place"] = places
    new2_gr.vertex_properties["ident"] = idents

    # In[63]:


    for k,dict_v in eprops.items():

        v = [dict_v[(s,t)]  for s,t,n in new2_gr.get_edges()]
        new2_gr.edge_properties[k] = new2_gr.new_edge_property("string",v)


    new2_gr.save("/tmp/new_%s_gr.graphml"%y)

    deg = new2_gr.degree_property_map("total")

    new2_short = graph_tool.GraphView(new2_gr,vfilt=lambda x:deg[x] > 0)

    graph_tool.Graph(new2_short,prune=True).save("/tmp/new_%s_short.graphml"%y)

