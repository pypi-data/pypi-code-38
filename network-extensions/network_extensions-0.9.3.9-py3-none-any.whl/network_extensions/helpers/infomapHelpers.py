name = "urn:uuid:75b728c5-3916-41f9-a7fe-28ef54e18992"
# gr_2 = graph_tool.Graph()
# level = gr_2.new_vertex_property()
elist_extended = []
import pickle
with open("/tmp/%s.mpt" % name, "r") as inf:
    vertexes = set()
    start = False
    cnt = 0
    for l in inf:
        if "*Multiplex" in l:
            start = True

        if cnt == 5000:
            print("next")
            cnt = 0
        cnt += 1
        if start:
            splitted = l.split(" ")  # split into layer1,node1,layer2,node2,weight
            if len(splitted) == 5:
                vertexes.add("%s_%s"%(splitted[0],splitted[1]))
                vertexes.add("%s_%s"%(splitted[2],splitted[3]))


pickle.dump(vertexes,open("/tmp/vertices.pickle","wb")) 