from __future__ import absolute_import, print_function

from mercurial import demandimport
demandimport.enable()

import os
import subprocess
import sys
import types

# Don't import pycompat because it has too many side-effects.
ispy3 = sys.version_info[0] >= 3

# Only run if demandimport is allowed
if subprocess.call(['python', '%s/hghave' % os.environ['TESTDIR'],
                    'demandimport']):
    sys.exit(80)

# We rely on assert, which gets optimized out.
if sys.flags.optimize:
    sys.exit(80)

if ispy3:
    from importlib.util import _LazyModule

    try:
        from importlib.util import _Module as moduletype
    except ImportError:
        moduletype = types.ModuleType
else:
    moduletype = types.ModuleType

if os.name != 'nt':
    try:
        import distutils.msvc9compiler
        print('distutils.msvc9compiler needs to be an immediate '
              'importerror on non-windows platforms')
        distutils.msvc9compiler
    except ImportError:
        pass

import re

rsub = re.sub
def f(obj):
    l = repr(obj)
    l = rsub("0x[0-9a-fA-F]+", "0x?", l)
    l = rsub("from '.*'", "from '?'", l)
    l = rsub("'<[a-z]*>'", "'<whatever>'", l)
    return l

demandimport.disable()
os.environ['HGDEMANDIMPORT'] = 'disable'
# this enable call should not actually enable demandimport!
demandimport.enable()
from mercurial import node

# We use assert instead of a unittest test case because having imports inside
# functions changes behavior of the demand importer.
if ispy3:
    assert not isinstance(node, _LazyModule)
else:
    assert f(node) == "<module 'mercurial.node' from '?'>", f(node)

# now enable it for real
del os.environ['HGDEMANDIMPORT']
demandimport.enable()

# Test access to special attributes through demandmod proxy
assert 'mercurial.error' not in sys.modules
from mercurial import error as errorproxy

if ispy3:
    # unsure why this isn't lazy.
    assert not isinstance(f, _LazyModule)
    assert f(errorproxy) == "<module 'mercurial.error' from '?'>", f(errorproxy)
else:
    assert f(errorproxy) == "<unloaded module 'error'>", f(errorproxy)

doc = ' '.join(errorproxy.__doc__.split()[:3])
assert doc == 'Mercurial exceptions. This', doc
assert errorproxy.__name__ == 'mercurial.error', errorproxy.__name__

# __name__ must be accessible via __dict__ so the relative imports can be
# resolved
name = errorproxy.__dict__['__name__']
assert name == 'mercurial.error', name

if ispy3:
    assert not isinstance(errorproxy, _LazyModule)
    assert f(errorproxy) == "<module 'mercurial.error' from '?'>", f(errorproxy)
else:
    assert f(errorproxy) == "<proxied module 'error'>", f(errorproxy)

import os

if ispy3:
    assert not isinstance(os, _LazyModule)
    assert f(os) == "<module 'os' from '?'>", f(os)
else:
    assert f(os) == "<unloaded module 'os'>", f(os)

assert f(os.system) == '<built-in function system>', f(os.system)
assert f(os) == "<module 'os' from '?'>", f(os)

assert 'mercurial.utils.procutil' not in sys.modules
from mercurial.utils import procutil

if ispy3:
    assert isinstance(procutil, _LazyModule)
    assert f(procutil) == "<module 'mercurial.utils.procutil' from '?'>", f(
        procutil
    )
else:
    assert f(procutil) == "<unloaded module 'procutil'>", f(procutil)

assert f(procutil.system) == '<function system at 0x?>', f(procutil.system)
assert procutil.__class__ == moduletype, procutil.__class__
assert f(procutil) == "<module 'mercurial.utils.procutil' from '?'>", f(
    procutil
)
assert f(procutil.system) == '<function system at 0x?>', f(procutil.system)

assert 'mercurial.hgweb' not in sys.modules
from mercurial import hgweb

if ispy3:
    assert not isinstance(hgweb, _LazyModule)
    assert f(hgweb) == "<module 'mercurial.hgweb' from '?'>", f(hgweb)
    assert isinstance(hgweb.hgweb_mod, _LazyModule)
    assert (
        f(hgweb.hgweb_mod) == "<module 'mercurial.hgweb.hgweb_mod' from '?'>"
    ), f(hgweb.hgweb_mod)
else:
    assert f(hgweb) == "<unloaded module 'hgweb'>", f(hgweb)
    assert f(hgweb.hgweb_mod) == "<unloaded module 'hgweb_mod'>", f(
        hgweb.hgweb_mod
    )

assert f(hgweb) == "<module 'mercurial.hgweb' from '?'>", f(hgweb)

import re as fred

if ispy3:
    assert not isinstance(fred, _LazyModule)
    assert f(fred) == "<module 're' from '?'>"
else:
    assert f(fred) == "<unloaded module 're'>", f(fred)

import re as remod

if ispy3:
    assert not isinstance(remod, _LazyModule)
    assert f(remod) == "<module 're' from '?'>"
else:
    assert f(remod) == "<unloaded module 're'>", f(remod)

import sys as re

if ispy3:
    assert not isinstance(re, _LazyModule)
    assert f(re) == "<module 'sys' (built-in)>"
else:
    assert f(re) == "<unloaded module 'sys'>", f(re)

if ispy3:
    assert not isinstance(fred, _LazyModule)
    assert f(fred) == "<module 're' from '?'>", f(fred)
else:
    assert f(fred) == "<unloaded module 're'>", f(fred)

assert f(fred.sub) == '<function sub at 0x?>', f(fred.sub)

if ispy3:
    assert not isinstance(fred, _LazyModule)
    assert f(fred) == "<module 're' from '?'>", f(fred)
else:
    assert f(fred) == "<proxied module 're'>", f(fred)

remod.escape  # use remod
assert f(remod) == "<module 're' from '?'>", f(remod)

if ispy3:
    assert not isinstance(re, _LazyModule)
    assert f(re) == "<module 'sys' (built-in)>"
    assert f(type(re.stderr)) == "<class '_io.TextIOWrapper'>", f(
        type(re.stderr)
    )
    assert f(re) == "<module 'sys' (built-in)>"
else:
    assert f(re) == "<unloaded module 'sys'>", f(re)
    assert f(re.stderr) == "<open file '<whatever>', mode 'w' at 0x?>", f(
        re.stderr
    )
    assert f(re) == "<proxied module 'sys'>", f(re)

assert 'telnetlib' not in sys.modules
import telnetlib

if ispy3:
    assert not isinstance(telnetlib, _LazyModule)
    assert f(telnetlib) == "<module 'telnetlib' from '?'>"
else:
    assert f(telnetlib) == "<unloaded module 'telnetlib'>", f(telnetlib)

try:
    from telnetlib import unknownattr

    assert False, (
        'no demandmod should be created for attribute of non-package '
        'module:\ntelnetlib.unknownattr = %s' % f(unknownattr)
    )
except ImportError as inst:
    assert rsub(r"'", '', str(inst)).startswith(
        'cannot import name unknownattr'
    )

from mercurial import util

# Unlike the import statement, __import__() function should not raise
# ImportError even if fromlist has an unknown item
# (see Python/import.c:import_module_level() and ensure_fromlist())
assert 'zipfile' not in sys.modules
zipfileimp = __import__('zipfile', globals(), locals(), ['unknownattr'])
assert f(zipfileimp) == "<module 'zipfile' from '?'>", f(zipfileimp)
assert not util.safehasattr(zipfileimp, 'unknownattr')
