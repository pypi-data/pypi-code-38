"""
Minipush
Copyright (c) 2019 Rémi LANGDORPH
Software under MIT license
https://opensource.org/licenses/mit-license.php
"""
print_status=True
import os, json, time, sys, re, hashlib, binascii
from .cssmin import cssmin
from .jsmin import jsmin

def log(*args, **kwargs):
    if print_status:
        return print(*args, **kwargs)

def min(file, cfiles, cpath, n):
    type=file.split(".")[::-1][0]
    data=open(file).read()
    if file in cfiles:
        if gen_hash(file)==cfiles[file]["hash"]:
            try:
                res=open(cpath+file).read()
                log(f"{n} Using cache for '{file}' (size: {round(len(res.encode('utf-8'))/1000, 3)} ko)")
                return {
                "type": file.split(".")[::-1][0],
                "status": "success",
                "result": res,
                "size": len(res.encode('utf-8')),
                "origin": {
                    "file": file
                },
                "cached": True,
                "cached_time": cfiles[file]["time"],
                "cached_hash": cfiles[file]["hash"]
                }
            except: pass
    res=None
    log(f"{n} Minimizing file '{file}' ...", end="\r")
    if type=="js":
        res=jsmin(data)
    elif type=="css":
        res=cssmin(data)
    if res!=None:
        log(f"{n} Minimized file '{file}' (before: {round(len(data.encode('utf-8'))/1000, 3)} ko; after: {round(len(res.encode('utf-8'))/1000, 3)} ko)")
        return {
        "type": type,
        "status": "success",
        "cached": False,
        "origin": {
            "file": file,
            "size": len(data.encode('utf-8'))
        },
        "result": res,
        "size": len(res.encode('utf-8'))
        }
    else:
        log(f"{n} Can't minimize file '{file}'")
        return {
        "status": "error",
        "cached": False,
        "origin": {
            "file": file,
            "size": len(data.encode('utf-8'))
        },
        "result": ""
        }
def gen_hash(file):
    return str(binascii.hexlify(hashlib.pbkdf2_hmac('sha256', open(file, "rb").read(), b'minipush', 100000)).decode("utf-8"))
def get_origins(folders, type):
    l=[]
    for folder in folders:
        l+=[folder+_ for _ in os.listdir(folder) if (_.split(".")[::-1][0] in type and len(_.split("."))>1)]
    return l
def get_cached_files(folder):
    try:
        f=json.load(open(folder+"mincachedindex.json"))
    except:
        return []
    return f
def get_templates(folder, type):
    return [folder+_ for _ in os.listdir(folder) if _.split(".")[::-1][0] in type]
def edit_templates(folder, exts, scripts, config):
    embed=True if config["destination"]["type"]=="embed" else False
    l=get_templates(folder, exts)
    for _ in l:
        edit_template(_, scripts, embed, config)
    return l
def edit_template(template, scripts, embed, config):
    temp=open(template).read()
    filters=get_template_filters(temp, config["anchors"]["conf"]["start"], config["anchors"]["conf"]["end"])
    if embed:
        new=edit_str_btw_balises(temp, get_code_str(scripts["js"], filters, config["format"]["embed"]["js"]), config["anchors"]["js"]["start"], config["anchors"]["js"]["end"])
        new=edit_str_btw_balises(new, get_code_str(scripts["css"], filters, config["format"]["embed"]["css"]), config["anchors"]["css"]["start"], config["anchors"]["css"]["end"])
        log(f"Template {template} edited (embed) (before: {round(len(temp.encode('utf-8'))/1000, 3)} ko; after: {round(len(new.encode('utf-8'))/1000, 3)} ko)")
    else:
        bfl=config["destination"].get("basefolderlink")
        new=edit_str_btw_balises(temp, get_code_str(scripts["js"], filters, config["format"]["link"]["js"], False, bfl), config["anchors"]["js"]["start"], config["anchors"]["js"]["end"])
        new=edit_str_btw_balises(new, get_code_str(scripts["css"], filters, config["format"]["link"]["css"], False, bfl), config["anchors"]["css"]["start"], config["anchors"]["css"]["end"])
        log(f"Template {template} edited (link) (before: {round(len(temp.encode('utf-8'))/1000, 3)} ko; after: {round(len(new.encode('utf-8'))/1000, 3)} ko)")
    open(template, "w").write(new)
def get_template_filters(data, startbal, endbal):
    x=get_template_recette(data, startbal, endbal)
    if x==None:
        return None
    return [parse_filepath(_) for _ in x]
def get_template_recette(data, startbal, endbal):
    s=get_str_btw_balises(data, startbal, endbal)
    j=json.loads(s) if s!=None else None
    return j
def get_code_str(scripts, filters, format, embed=True, bfl=""):
    return "".join([format.format(filename=name, content=code, path=bfl+name) for name, code in get_code_list(scripts, filters)])
def get_code_list(scripts, filters):
    l=[]
    for _ in scripts:
        if is_allowed_script(_, filters): l.append((_, scripts[_]))
    return l
def is_allowed_script(name, filters):
    if filters==None: return False
    n=parse_filepath(name)
    for _ in filters:
        if is_filterok(n, _):
            return True
    return False
def is_filterok(name, filter):
    if filter["path"]=="*": return True
    if (is_parsedlistok(name["folderlist"], filter["folderlist"], skip=False) or filter["folder"]=="**"):
        if is_parsedlistok(name["filelistr"], filter["filelistr"]):
            return True
    return False
def is_parsedlistok(filelist, filterlist, skip=True):
    if not skip:
        if len(filelist)!=len(filterlist): return False
    for f, r in zip(filelist, filterlist):
        if not (r=="*" or r==f): return False
    return True
def edit_str_btw_balises(basetext, secondtext, startbal, endbal):
    if (startbal in basetext and endbal in basetext):
        _start=basetext.split(startbal)[0]
        _end=basetext.split(endbal)[1]
        return _start+startbal+secondtext+endbal+_end
    return basetext
def get_str_btw_balises(basetext, startbal, endbal):
    if (startbal in basetext and endbal in basetext):
        _p0=basetext.split(startbal)[1]
        return _p0.split(endbal)[0]
    return None
def export_cache(l, config):
    j={}
    log("Updating Cache...")
    folder=config["cache"]["folder"]
    os.makedirs(folder, exist_ok=True)
    for _ in l:
        save_file(folder+_["origin"]["file"], _["result"])
        j[_["origin"]["file"]]={
        "time": time.time(),
        "hash": gen_hash(_["origin"]["file"])
        }
    _j=json.dumps(j)
    open(folder+"mincachedindex.json", "w").write(_j)
def export(scripts, rules, format):
    log("Exporting files...")
    for _ in rules:
        data=get_code_str(scripts[_["destination"].split(".")[::-1][0]], [parse_filepath(__) for __ in _["filters"]], format["js"])
        save_file(_["destination"], data)
        log(f"Exported {_['destination']} ({round(len(data.encode('utf-8'))/1000, 3)} ko)")
def lenext(l):
    d={}
    for _ in l:
        ext=_.split(".")[::-1][0]
        if d.get(ext)==None:
            d[ext]=0
        d[ext]+=1
    d["total"]=len(l)
    return d
def cache_status(config):
    if config.get("cache")!=None:
        if config["cache"]["enabled"]:
            return True
    return False
def export_status(config):
    if config.get("export")!=None:
        if config["export"]["enabled"]:
            return True
    return False
def save_file(file, data):
    regexPattern = '|'.join(map(re.escape, ["/", "\\"]))
    path=re.split(regexPattern, file)
    f=path[::-1][0]
    path.remove(f)
    p="/".join(path)
    os.makedirs(p, exist_ok=True)
    open(file, "w").write(data)
def parse_filepath(name):
    #name="/path/to/file.ext"
    regexPattern = '|'.join(map(re.escape, ["/", "\\"]))
    path=re.split(regexPattern, name)
    f=path[::-1][0]
    path.remove(f)
    p="/".join(path)
    pathlist=re.split(regexPattern, name)
    filelist=f.split(".")
    # path: "/path/to/file.ext"
    # pathlist: ["path", "to", "file.ext"]
    # pathlistr: ["file.ext", "to", "path"]
    # file: "file.ext"
    # filelist: ["file", "ext"]
    # filelistr: ["ext", "file"]
    # folder: "/path/to/"
    # folderlist: ["path", "to"]
    # folderlistr: [ "to", "path"]
    return {
    "path": name,
    "pathlist": pathlist,
    "pathlistr":pathlist[::-1],
    "file": f,
    "filelist": filelist,
    "filelistr": filelist[::-1],
    "folder": p,
    "folderlist": path,
    "folderlistr": path[::-1]
    }
