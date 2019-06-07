
import Graph, EditDebugger
from Graph import Color
import heapq, math

def fordfulkerson(g):
	for e in g.edges:
		e.flow = 0

	s = g.get_node('source')
	t = g.get_node('target')

	path = []
	while get_path(g,s,t,path,set()):
		residual_cap = min(e.weight - e.flow if forward else e.flow for forward,e in path)

		for forward,e in path:
			if forward:
				e.flow += residual_cap
			else:
				e.flow -= residual_cap
		path = []


def get_path(g,s,t,path,path_set):
	if s == t:
		return path

	for e in s.out:
		if e.weight > e.flow and e not in path_set:
			path.append((True,e))
			path_set.add(e)
			p = get_path(g,e.targ, t, path, path_set)
			if p:
				return p
			path_set.remove(e)
			path.pop()

	for e in s.inc:
		if e.flow > 0 and e not in path_set:
			path.append((False,e))
			path_set.add(e)
			p = get_path(g,e.src, t, path, path_set)
			if p:
				return p
			path_set.remove(e)
			path.pop()
	return None
graph = EditDebugger.app.get_graph()
fordfulkerson(graph)
pass