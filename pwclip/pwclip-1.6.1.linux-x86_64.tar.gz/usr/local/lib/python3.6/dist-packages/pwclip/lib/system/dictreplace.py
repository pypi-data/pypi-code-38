
from colortext import error

def dictreplace(srcdict, trgdict):
	if not isinstance(srcdict, dict):
		return error('type \'dict\' expected, got', type(trgdict))
	newdict = {}
	for (k, v) in srcdict.items():
		if k in trgdict.keys() and isinstance(trgdict[k], dict):
			__dict = dictreplace(srcdict[k], trgdict[k])
			if 'delkey' in trgdict[k].keys():
				for (ik, iv) in __dict.items():
					newdict[ik] = iv
			else:
				newdict[k] = __dict
			continue
		elif k in trgdict.keys():
			newdict[trgdict[k]] = v
		else:
			newdict[k] = v
	return newdict
