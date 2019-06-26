
from colortext import error

def dictreplace(srcdict, trgdict):
    if not isinstance(srcdict, dict):
        return error('type \'dict\' expected, got', type(trgdict))
    newdict = {}
    for (k, v) in srcdict.items():
        if k in trgdict.keys() and isinstance(trgdict[k], dict):
            __dict = dictreplace(srcdict[k], trgdict[k])
            if 'delkey' not in trgdict[k].keys():
                newdict[k] = __dict
                continue
            for (ik, iv) in __dict.items():
                newdict[ik] = iv
        else:
            newdict[k] = v
    return newdict
