from os import environ

def envconf(srcdict):
    newdict = {}
    for (k, v) in srcdict.items():
        if k in environ.keys():
            newdict[v] = environ[k]
    return newdict

