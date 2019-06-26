import re, os

def search_ext(dirname, ext) :
    results = []
    p = re.compile(".+[.]" + ext + "$")
    for (path, dir, files) in os.walk(dirname):
        for filename in files :
            m = p.search(filename)
            if m : results.append("%s/%s" % (path, m.group(0)))
    return results

def search_file(dirname, keyword) :
    results = []
    p = re.compile(".*" + keyword + ".*", re.I)
    for (path, dir, files) in os.walk(dirname):
        for filename in files :
            m = p.search(filename)
            if m : results.append("%s/%s" % (path, m.group(0)))
    return results