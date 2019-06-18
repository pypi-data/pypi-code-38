for n, d in G.nodes(data=True):
	if n in sensor_ids:
	max_depth = 0
	for up_node in G.predecessors(n):
		for fid, edge in G[up_node][n].items():
			max_depth = max(max_depth, float(edge['Geom1']))
		for dn_node in G.successors(n):
			for fid, edge in G[n][dn_node].items():
				max_depth = max(max_depth, float(edge['Geom1']))