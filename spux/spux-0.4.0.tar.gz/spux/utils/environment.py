from ..io import formatter

entries = {}
headers = []

import datetime
timestamp = datetime.datetime.now ()
timestamp = timestamp.strftime ('%Y-%m-%d %H:%M:%S')
del datetime
entries ['Timestamp'] = timestamp
headers += ['Timestamp']

from .. import __version__
version = __version__
del __version__
entries ['Version'] = version
headers += ['Version']

import os
path = os.path.normpath (os.path.dirname (__file__))
# path = os.path.normpath (os.path.join (os.path.join (os.path.dirname (__file__), '..'), '..'))
del os

try:
    import pygit2
    repo = pygit2.Repository (path)
    head = repo.head
    branch = head.shorthand
    revision = head.target
    del head
    del repo
    del pygit2
    entries ['GIT branch (plain)'] = formatter.plain (branch)
    headers += ['GIT branch (plain)']
    entries ['GIT revision'] = revision
    headers += ['GIT revision']
except:
    pass