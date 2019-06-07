# hgview: visual mercurial graphlog browser in PyQt4
#
# Copyright 2008-2010 Logilab
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

'''browse the repository in a(n other) graphical way

The hgview extension allows browsing the history of a repository in a
graphical way. It requires PyQt4 with QScintilla.
'''

testedwith = '2.9 3.0 3.0.1'

buglink = 'https://www.logilab.org/project/hgview'

import os
import os.path as osp
import stat
import imp
from optparse import Values
from mercurial import error, demandimport

try:
    from mercurial.registrar import command as cmdregistry
except ImportError:
    from mercurial.cmdutil import command as cmdregistry

execpath = osp.abspath(__file__)
#   resolve symbolic links
statinfo = os.lstat(execpath)
if stat.S_ISLNK(statinfo.st_mode):
    execpath = join(osp.dirname(execpath), os.readlink(execpath))
    execpath = osp.abspath(execpath)
# if standalone, import manually
setuppath = osp.join(osp.dirname(osp.dirname(execpath)), 'setup.py')
if osp.exists(setuppath): # standalone if setup.py found in src dir
    hgviewlibpath = osp.join(osp.dirname(osp.dirname(execpath)), 'hgviewlib')
    hgviewlibpath = osp.abspath(hgviewlibpath)
    imp.load_package('hgviewlib', hgviewlibpath)



cmdtable = {}
command = cmdregistry(cmdtable)

@command('hgview|qv [OPTIONS] [FILENAME]',
                       [('n', 'navigate', False, '(with filename) start in navigation mode'),
                        ('r', 'rev', '', 'start in manifest navigation mode at rev R'),
                        ('s', 'start', '', 'show only graph from rev S'),
                        ('I', 'interface', '', 'GUI interface to use (among "qt", "raw" and "curses"')
                        ])
# every command must take a ui and and repo as arguments.
# opts is a dict where you can find other command line flags
#
# Other parameters are taken in order from items on the command line that
# don't start with a dash.  If no default value is given in the parameter list,
# they are required.

def hgview(ui, repo, *pats, **opts):
    # WARNING, this docstring is superseeded programmatically
    """
start hgview log viewer
=======================

    This command will launch the hgview log navigator, allowing to
    visually browse in the hg graph log, search in logs, and display
    diff between arbitrary revisions of a file.

    If a filename is given, launch the filelog diff viewer for this file,
    and with the '-n' option, launch the filelog navigator for the file.

    With the '-r' option, launch the manifest viewer for the given revision.

    """
    ### 2.5 compat
    # We ensure here that we work on unfiltered repo in all case. Unfiltered
    # repo are repo has we know them now.
    repo = getattr(repo, 'unfiltered', lambda: repo)()

    # If this user has a username validation hook enabled,
    # it could conflict with hgview because both will try to
    # allocate a QApplication, and PyQt doesn't deal well
    # with two app instances running under the same context.
    # To prevent this, we run the hook early before hgview
    # allocates the app
    try:
        from hgconf.uname import hook
        hook(ui, repo)
    except ImportError:
        pass

    from hgviewlib.application import start
    def fnerror(text):
        """process errors"""
        raise(error.Abort(text))
    options = Values(opts)
    start(repo, options, pats, fnerror)

import hgviewlib
# note: ``import hgviewlib.hgviewhelp`` is incompatible with standalone
#       because of the lazy import
from hgviewlib.hgviewhelp import long_help_msg
hgview.__doc__ = long_help_msg
