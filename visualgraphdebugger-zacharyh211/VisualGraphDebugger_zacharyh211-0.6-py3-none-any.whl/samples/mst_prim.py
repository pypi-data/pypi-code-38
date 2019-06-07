
from graphdebugger.Graph import Color, Graph
import heapq, math

def prim(g):

	for e in g.edges:
		e.color = Color.GRAY

	for u in g.nodes:
		u.color = Color.WHITE
		u.key = math.inf
		u.pi = None
	r = g.nodes[0]
	r.key = 0

	for i,v in enumerate(g.nodes):
		v.index = i
	q = [(v.key, v.index, v) for v in g.nodes]
	heapq.heapify(q)

	while q:
		prior,i,u = heapq.heappop(q)
		u.color = Color.BLACK
		if u.pi is not None:
			u.pi[1].color = Color.BLACK
		for e,v in u.adj_edges:
			if v.color == Color.WHITE and e.weight < v.key:
				#lazy "decrease key" since heapq doesn't natively support it
				v.pi = (u,e)
				j = q.index((v.key, v.index, v))
				v.key = e.weight
				q[j] = (v.key, v.index, v)
				heapq.heapify(q)

graph = EditDebugger.app.get_graph()

prim(graph)
pass