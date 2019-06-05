# test-batching.py - tests for transparent command batching
#
# Copyright 2011 Peter Arrenbrecht <peter@arrenbrecht.ch>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import, print_function

import contextlib

from mercurial import (
    localrepo,
    pycompat,
    wireprotov1peer,
)

def bprint(*bs):
    print(*[pycompat.sysstr(b) for b in bs])

# equivalent of repo.repository
class thing(object):
    def hello(self):
        return b"Ready."

# equivalent of localrepo.localrepository
class localthing(thing):
    def foo(self, one, two=None):
        if one:
            return b"%s and %s" % (one, two,)
        return b"Nope"
    def bar(self, b, a):
        return b"%s und %s" % (b, a,)
    def greet(self, name=None):
        return b"Hello, %s" % name

    @contextlib.contextmanager
    def commandexecutor(self):
        e = localrepo.localcommandexecutor(self)
        try:
            yield e
        finally:
            e.close()

# usage of "thing" interface
def use(it):

    # Direct call to base method shared between client and server.
    bprint(it.hello())

    # Direct calls to proxied methods. They cause individual roundtrips.
    bprint(it.foo(b"Un", two=b"Deux"))
    bprint(it.bar(b"Eins", b"Zwei"))

    # Batched call to a couple of proxied methods.

    with it.commandexecutor() as e:
        ffoo = e.callcommand(b'foo', {b'one': b'One', b'two': b'Two'})
        fbar = e.callcommand(b'bar', {b'b': b'Eins', b'a': b'Zwei'})
        fbar2 = e.callcommand(b'bar', {b'b': b'Uno', b'a': b'Due'})

    bprint(ffoo.result())
    bprint(fbar.result())
    bprint(fbar2.result())

# local usage
mylocal = localthing()
print()
bprint(b"== Local")
use(mylocal)

# demo remoting; mimicks what wireproto and HTTP/SSH do

# shared

def escapearg(plain):
    return (plain
            .replace(b':', b'::')
            .replace(b',', b':,')
            .replace(b';', b':;')
            .replace(b'=', b':='))
def unescapearg(escaped):
    return (escaped
            .replace(b':=', b'=')
            .replace(b':;', b';')
            .replace(b':,', b',')
            .replace(b'::', b':'))

# server side

# equivalent of wireproto's global functions
class server(object):
    def __init__(self, local):
        self.local = local
    def _call(self, name, args):
        args = dict(arg.split(b'=', 1) for arg in args)
        return getattr(self, name)(**args)
    def perform(self, req):
        bprint(b"REQ:", req)
        name, args = req.split(b'?', 1)
        args = args.split(b'&')
        vals = dict(arg.split(b'=', 1) for arg in args)
        res = getattr(self, pycompat.sysstr(name))(**pycompat.strkwargs(vals))
        bprint(b"  ->", res)
        return res
    def batch(self, cmds):
        res = []
        for pair in cmds.split(b';'):
            name, args = pair.split(b':', 1)
            vals = {}
            for a in args.split(b','):
                if a:
                    n, v = a.split(b'=')
                    vals[n] = unescapearg(v)
            res.append(escapearg(getattr(self, pycompat.sysstr(name))(
                **pycompat.strkwargs(vals))))
        return b';'.join(res)
    def foo(self, one, two):
        return mangle(self.local.foo(unmangle(one), unmangle(two)))
    def bar(self, b, a):
        return mangle(self.local.bar(unmangle(b), unmangle(a)))
    def greet(self, name):
        return mangle(self.local.greet(unmangle(name)))
myserver = server(mylocal)

# local side

# equivalent of wireproto.encode/decodelist, that is, type-specific marshalling
# here we just transform the strings a bit to check we're properly en-/decoding
def mangle(s):
    return b''.join(pycompat.bytechr(ord(c) + 1) for c in pycompat.bytestr(s))
def unmangle(s):
    return b''.join(pycompat.bytechr(ord(c) - 1) for c in pycompat.bytestr(s))

# equivalent of wireproto.wirerepository and something like http's wire format
class remotething(thing):
    def __init__(self, server):
        self.server = server
    def _submitone(self, name, args):
        req = name + b'?' + b'&'.join([b'%s=%s' % (n, v) for n, v in args])
        return self.server.perform(req)
    def _submitbatch(self, cmds):
        req = []
        for name, args in cmds:
            args = b','.join(n + b'=' + escapearg(v) for n, v in args)
            req.append(name + b':' + args)
        req = b';'.join(req)
        res = self._submitone(b'batch', [(b'cmds', req,)])
        for r in res.split(b';'):
            yield r

    @contextlib.contextmanager
    def commandexecutor(self):
        e = wireprotov1peer.peerexecutor(self)
        try:
            yield e
        finally:
            e.close()

    @wireprotov1peer.batchable
    def foo(self, one, two=None):
        encargs = [(b'one', mangle(one),), (b'two', mangle(two),)]
        encresref = wireprotov1peer.future()
        yield encargs, encresref
        yield unmangle(encresref.value)

    @wireprotov1peer.batchable
    def bar(self, b, a):
        encresref = wireprotov1peer.future()
        yield [(b'b', mangle(b),), (b'a', mangle(a),)], encresref
        yield unmangle(encresref.value)

    # greet is coded directly. It therefore does not support batching. If it
    # does appear in a batch, the batch is split around greet, and the call to
    # greet is done in its own roundtrip.
    def greet(self, name=None):
        return unmangle(self._submitone(b'greet', [(b'name', mangle(name),)]))

# demo remote usage

myproxy = remotething(myserver)
print()
bprint(b"== Remote")
use(myproxy)
