# Since it's not easy to write a test that portably deals
# with files from different users/groups, we cheat a bit by
# monkey-patching some functions in the util module

from __future__ import absolute_import, print_function

import os
import sys

from mercurial import (
    error,
    pycompat,
    ui as uimod,
    util,
)
from mercurial.utils import stringutil

hgrc = os.environ['HGRCPATH']
f = open(hgrc, 'rb')
basehgrc = f.read()
f.close()

def _maybesysstr(v):
    if isinstance(v, bytes):
        return pycompat.sysstr(v)
    return pycompat.sysstr(stringutil.pprint(v))

def bprint(*args, **kwargs):
    print(*[_maybesysstr(a) for a in args],
          **{k: _maybesysstr(v) for k, v in kwargs.items()})
    # avoid awkward interleaving with ui object's output
    sys.stdout.flush()

def testui(user=b'foo', group=b'bar', tusers=(), tgroups=(),
           cuser=b'foo', cgroup=b'bar', debug=False, silent=False,
           report=True):
    # user, group => owners of the file
    # tusers, tgroups => trusted users/groups
    # cuser, cgroup => user/group of the current process

    # write a global hgrc with the list of trusted users/groups and
    # some setting so that we can be sure it was read
    f = open(hgrc, 'wb')
    f.write(basehgrc)
    f.write(b'\n[paths]\n')
    f.write(b'global = /some/path\n\n')

    if tusers or tgroups:
        f.write(b'[trusted]\n')
        if tusers:
            f.write(b'users = %s\n' % b', '.join(tusers))
        if tgroups:
            f.write(b'groups = %s\n' % b', '.join(tgroups))
    f.close()

    # override the functions that give names to uids and gids
    def username(uid=None):
        if uid is None:
            return cuser
        return user
    util.username = username

    def groupname(gid=None):
        if gid is None:
            return b'bar'
        return group
    util.groupname = groupname

    def isowner(st):
        return user == cuser
    util.isowner = isowner

    # try to read everything
    #print '# File belongs to user %s, group %s' % (user, group)
    #print '# trusted users = %s; trusted groups = %s' % (tusers, tgroups)
    kind = (b'different', b'same')
    who = (b'', b'user', b'group', b'user and the group')
    trusted = who[(user in tusers) + 2*(group in tgroups)]
    if trusted:
        trusted = b', but we trust the ' + trusted
    bprint(b'# %s user, %s group%s' % (kind[user == cuser],
                                       kind[group == cgroup],
                                       trusted))

    u = uimod.ui.load()
    # disable the configuration registration warning
    #
    # the purpose of this test is to check the old behavior, not to validate the
    # behavior from registered item. so we silent warning related to unregisted
    # config.
    u.setconfig(b'devel', b'warn-config-unknown', False, b'test')
    u.setconfig(b'devel', b'all-warnings', False, b'test')
    u.setconfig(b'ui', b'debug', pycompat.bytestr(bool(debug)))
    u.setconfig(b'ui', b'report_untrusted', pycompat.bytestr(bool(report)))
    u.readconfig(b'.hg/hgrc')
    if silent:
        return u
    bprint(b'trusted')
    for name, path in u.configitems(b'paths'):
        bprint(b'   ', name, b'=', util.pconvert(path))
    bprint(b'untrusted')
    for name, path in u.configitems(b'paths', untrusted=True):
        bprint(b'.', end=b' ')
        u.config(b'paths', name) # warning with debug=True
        bprint(b'.', end=b' ')
        u.config(b'paths', name, untrusted=True) # no warnings
        bprint(name, b'=', util.pconvert(path))
    print()

    return u

os.mkdir(b'repo')
os.chdir(b'repo')
os.mkdir(b'.hg')
f = open(b'.hg/hgrc', 'wb')
f.write(b'[paths]\n')
f.write(b'local = /another/path\n\n')
f.close()

#print '# Everything is run by user foo, group bar\n'

# same user, same group
testui()
# same user, different group
testui(group=b'def')
# different user, same group
testui(user=b'abc')
# ... but we trust the group
testui(user=b'abc', tgroups=[b'bar'])
# different user, different group
testui(user=b'abc', group=b'def')
# ... but we trust the user
testui(user=b'abc', group=b'def', tusers=[b'abc'])
# ... but we trust the group
testui(user=b'abc', group=b'def', tgroups=[b'def'])
# ... but we trust the user and the group
testui(user=b'abc', group=b'def', tusers=[b'abc'], tgroups=[b'def'])
# ... but we trust all users
bprint(b'# we trust all users')
testui(user=b'abc', group=b'def', tusers=[b'*'])
# ... but we trust all groups
bprint(b'# we trust all groups')
testui(user=b'abc', group=b'def', tgroups=[b'*'])
# ... but we trust the whole universe
bprint(b'# we trust all users and groups')
testui(user=b'abc', group=b'def', tusers=[b'*'], tgroups=[b'*'])
# ... check that users and groups are in different namespaces
bprint(b"# we don't get confused by users and groups with the same name")
testui(user=b'abc', group=b'def', tusers=[b'def'], tgroups=[b'abc'])
# ... lists of user names work
bprint(b"# list of user names")
testui(user=b'abc', group=b'def', tusers=[b'foo', b'xyz', b'abc', b'bleh'],
       tgroups=[b'bar', b'baz', b'qux'])
# ... lists of group names work
bprint(b"# list of group names")
testui(user=b'abc', group=b'def', tusers=[b'foo', b'xyz', b'bleh'],
       tgroups=[b'bar', b'def', b'baz', b'qux'])

bprint(b"# Can't figure out the name of the user running this process")
testui(user=b'abc', group=b'def', cuser=None)

bprint(b"# prints debug warnings")
u = testui(user=b'abc', group=b'def', cuser=b'foo', debug=True)

bprint(b"# report_untrusted enabled without debug hides warnings")
u = testui(user=b'abc', group=b'def', cuser=b'foo', report=False)

bprint(b"# report_untrusted enabled with debug shows warnings")
u = testui(user=b'abc', group=b'def', cuser=b'foo', debug=True, report=False)

bprint(b"# ui.readconfig sections")
filename = b'foobar'
f = open(filename, 'wb')
f.write(b'[foobar]\n')
f.write(b'baz = quux\n')
f.close()
u.readconfig(filename, sections=[b'foobar'])
bprint(u.config(b'foobar', b'baz'))

print()
bprint(b"# read trusted, untrusted, new ui, trusted")
u = uimod.ui.load()
# disable the configuration registration warning
#
# the purpose of this test is to check the old behavior, not to validate the
# behavior from registered item. so we silent warning related to unregisted
# config.
u.setconfig(b'devel', b'warn-config-unknown', False, b'test')
u.setconfig(b'devel', b'all-warnings', False, b'test')
u.setconfig(b'ui', b'debug', b'on')
u.readconfig(filename)
u2 = u.copy()
def username(uid=None):
    return b'foo'
util.username = username
u2.readconfig(b'.hg/hgrc')
bprint(b'trusted:')
bprint(u2.config(b'foobar', b'baz'))
bprint(b'untrusted:')
bprint(u2.config(b'foobar', b'baz', untrusted=True))

print()
bprint(b"# error handling")

def assertraises(f, exc=error.Abort):
    try:
        f()
    except exc as inst:
        bprint(b'raised', inst.__class__.__name__)
    else:
        bprint(b'no exception?!')

bprint(b"# file doesn't exist")
os.unlink(b'.hg/hgrc')
assert not os.path.exists(b'.hg/hgrc')
testui(debug=True, silent=True)
testui(user=b'abc', group=b'def', debug=True, silent=True)

print()
bprint(b"# parse error")
f = open(b'.hg/hgrc', 'wb')
f.write(b'foo')
f.close()

# This is a hack to remove b'' prefixes from ParseError.__bytes__ on
# Python 3.
def normalizeparseerror(e):
    if pycompat.ispy3:
        args = [a.decode('utf-8') for a in e.args]
    else:
        args = e.args

    return error.ParseError(*args)

try:
    testui(user=b'abc', group=b'def', silent=True)
except error.ParseError as inst:
    bprint(normalizeparseerror(inst))

try:
    testui(debug=True, silent=True)
except error.ParseError as inst:
    bprint(normalizeparseerror(inst))

print()
bprint(b'# access typed information')
with open(b'.hg/hgrc', 'wb') as f:
    f.write(b'''\
[foo]
sub=main
sub:one=one
sub:two=two
path=monty/python
bool=true
int=42
bytes=81mb
list=spam,ham,eggs
''')
u = testui(user=b'abc', group=b'def', cuser=b'foo', silent=True)
def configpath(section, name, default=None, untrusted=False):
    path = u.configpath(section, name, default, untrusted)
    if path is None:
        return None
    return util.pconvert(path)

bprint(b'# suboptions, trusted and untrusted')
trusted = u.configsuboptions(b'foo', b'sub')
untrusted = u.configsuboptions(b'foo', b'sub', untrusted=True)
bprint(
    (trusted[0], sorted(trusted[1].items())),
    (untrusted[0], sorted(untrusted[1].items())))
bprint(b'# path, trusted and untrusted')
bprint(configpath(b'foo', b'path'), configpath(b'foo', b'path', untrusted=True))
bprint(b'# bool, trusted and untrusted')
bprint(u.configbool(b'foo', b'bool'),
       u.configbool(b'foo', b'bool', untrusted=True))
bprint(b'# int, trusted and untrusted')
bprint(
    u.configint(b'foo', b'int', 0),
    u.configint(b'foo', b'int', 0, untrusted=True))
bprint(b'# bytes, trusted and untrusted')
bprint(
    u.configbytes(b'foo', b'bytes', 0),
    u.configbytes(b'foo', b'bytes', 0, untrusted=True))
bprint(b'# list, trusted and untrusted')
bprint(
    u.configlist(b'foo', b'list', []),
    u.configlist(b'foo', b'list', [], untrusted=True))
