
from graphdebugger.Graph import Color, Graph
import heapq, math


def dijkstra(g):

	for u in g.nodes:
		u.color = Color.WHITE
		u.key = math.inf
		u.pi = None

	src = g.get_node("source") #requires a node in graph to be given the "source" tag
	src.key = 0

	for i,v in enumerate(g.nodes):
		v.index = i
	q = [(v.key, v.index, v) for v in g.nodes]
	heapq.heapify(q)

	while q:
		k,i,u = heapq.heappop(q)
		u.color = Color.BLACK
		u.label = str(u.key) if not u.label else '{:s}:{:s}'.format(u.label,str(u.key))
		for e in u.out:
			relax(e,q)

def relax(e,q):
	u,v = e.src, e.targ
	if v.color == Color.WHITE:
		v.color = Color.GRAY
	if v.key > u.key + e.weight:

		v.pi = (u,e)
		j = q.index((v.key, v.index, v))
		v.key = e.weight+u.key
		q[j] = (v.key, v.index, v)
		heapq.heapify(q)


graph = EditDebugger.app.get_graph()
dijkstra(graph)
