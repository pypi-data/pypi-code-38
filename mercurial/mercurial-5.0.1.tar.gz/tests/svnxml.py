# Read the output of a "svn log --xml" command on stdin, parse it and
# print a subset of attributes common to all svn versions tested by
# hg.
from __future__ import absolute_import
import sys
import xml.dom.minidom

def xmltext(e):
    return ''.join(c.data for c
                   in e.childNodes
                   if c.nodeType == c.TEXT_NODE)

def parseentry(entry):
    e = {}
    e['revision'] = entry.getAttribute('revision')
    e['author'] = xmltext(entry.getElementsByTagName('author')[0])
    e['msg'] = xmltext(entry.getElementsByTagName('msg')[0])
    e['paths'] = []
    paths = entry.getElementsByTagName('paths')
    if paths:
        paths = paths[0]
        for p in paths.getElementsByTagName('path'):
            action = p.getAttribute('action').encode('utf-8')
            path = xmltext(p).encode('utf-8')
            frompath = p.getAttribute('copyfrom-path').encode('utf-8')
            fromrev = p.getAttribute('copyfrom-rev').encode('utf-8')
            e['paths'].append((path, action, frompath, fromrev))
    return e

def parselog(data):
    entries = []
    doc = xml.dom.minidom.parseString(data)
    for e in doc.getElementsByTagName('logentry'):
        entries.append(parseentry(e))
    return entries

def printentries(entries):
    try:
        fp = sys.stdout.buffer
    except AttributeError:
        fp = sys.stdout
    for e in entries:
        for k in ('revision', 'author', 'msg'):
            fp.write(('%s: %s\n' % (k, e[k])).encode('utf-8'))
        for path, action, fpath, frev in sorted(e['paths']):
            frominfo = b''
            if frev:
                frominfo = b' (from %s@%s)' % (fpath, frev)
            p = b' %s %s%s\n' % (action, path, frominfo)
            fp.write(p)

if __name__ == '__main__':
    data = sys.stdin.read()
    entries = parselog(data)
    printentries(entries)

