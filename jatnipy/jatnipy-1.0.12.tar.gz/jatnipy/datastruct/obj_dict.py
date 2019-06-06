def obj_dict(d):
	top = type('new', (object,), d)
	seqs = tuple, list, set, frozenset
	for i, j in d.items():
		if isinstance(j, dict):
			setattr(top, i, obj_dict(j))
		elif isinstance(j, seqs):
			setattr(top, i, 
				type(j)(obj_dict(sj) if isinstance(sj, dict) else sj for sj in j))
		else:
			setattr(top, i, j)
	return top
