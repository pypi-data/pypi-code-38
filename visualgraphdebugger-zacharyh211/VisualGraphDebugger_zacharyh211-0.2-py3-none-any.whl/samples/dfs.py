

from graphdebugger.Graph import Color, Graph

time = 0
def dfs(g):
	global time
	time = 0
	for u in g.nodes:
		u.color = Color.WHITE
		u.parent = None
	for u in g.nodes:
		if u.color == Color.WHITE:
			dfs_visit(g,u)

def dfs_visit(g,u):
	global time
	time = time + 1
	u.d = time
	u.color = Color.GRAY

	for v in u.adj:
		if v.color == Color.WHITE:
			v.parent = u
			dfs_visit(g,v)
	u.color = Color.BLACK
	time = time + 1
	u.f = time
	u.label = str(u.d) + ',' + str(u.f)

graph = Graph.get_graph()
dfs(graph)