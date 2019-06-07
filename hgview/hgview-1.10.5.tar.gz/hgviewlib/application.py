# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Application utilities.
"""

import os, sys, traceback
from optparse import OptionParser

from mercurial import hg, ui as uimod
from mercurial.error import RepoError

from hgviewlib import __pkginfo__
from hgviewlib.util import find_repository, rootpath, build_repo
from hgviewlib.config import HgConfig

class NullRepo(object):
    """Placeholder repository"""
    ui = uimod.ui()
    root = None

class Viewer(object):
    """Base viewer class interface."""
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'This feature has not yet been implemented. Coming soon ...')

class FileViewer(Viewer):
    """Single file revision graph viewer."""
    def __init__(self, repo, filename, **kwargs):
        super(FileViewer, self).__init__(**kwargs)

class FileDiffViewer(Viewer):
    """Viewer that displays diffs between different revisions of a file."""
    def __init__(self, repo, filename, **kwargs):
        super(FileDiffViewer, self).__init__(**kwargs)

class HgRepoViewer(Viewer):
    """hg repository viewer."""
    def __init__(self, repo, **kwargs):
        super(HgRepoViewer, self).__init__(**kwargs)

class ManifestViewer(Viewer):
    """Viewer that displays all files of a repo at a given revision"""
    def __init__(self, repo, rev, **kwargs):
        super(ManifestViewer, self).__init__(**kwargs)

class ApplicationError(ValueError):
    """Exception that may occur while launching the application"""

class HgViewApplication(object):
    # class that must be instantiated
    FileViewer = FileViewer
    FileDiffViewer = FileDiffViewer
    HgRepoViewer = HgRepoViewer
    ManifestViewer = ManifestViewer

    def __init__(self, repo, opts, args, **kawrgs):
        self.viewer = None

        if opts.navigate and len(args) != 1:
            ApplicationError(
                    "you must provide a filename to start in navigate mode")

        if len(args) > 1:
            ApplicationError("provide at most one file name")

        self.opts = opts
        self.args = args
        self.repo = repo
        self.choose_viewer()

    def choose_viewer(self):
        """Choose the right viewer"""
        if len(self.args) == 1:
            filename = rootpath(self.repo, self.opts.rev, self.args[0])
            if not filename:
                raise ApplicationError("%s is not a tracked file" % self.args[0])

            # should be a filename of a file managed in the repo
            if self.opts.navigate:
                viewer = self.FileViewer(self.repo, filename)
            else:
                viewer = self.FileDiffViewer(self.repo, filename)
        else:
            rev = self.opts.rev
            if rev:
                try:
                    self.repo[rev]
                except RepoError, e:
                    raise ApplicationError("Cannot find revision %s" % rev)
                else:
                    viewer = self.ManifestViewer(self.repo, rev)
            else:
                viewer = self.HgRepoViewer(self.repo)
        self.viewer = viewer

    def exec_(self):
        raise NotImplementedError()

def _qt_application():
    from hgviewlib.qt4.application import HgViewQtApplication as Application
    return Application

def _curses_application():
    from hgviewlib.curses.application import HgViewUrwidApplication as Application
    return Application

LOADERS = {'qt': _qt_application,
           'raw': _curses_application,
           'curses': _curses_application}


def start(repo, opts, args, fnerror):
    """
    start hgview
    """
    config = HgConfig(repo.ui)
    repo.ui.opts = opts

    # pick the interface to use
    inter = opts.interface
    if not inter:
        inter = config.getInterface()

    if inter is None:
        interfaces = ['qt']
        if os.name != 'nt':
            # if we are not on Windows try terms fallback
            interfaces.append('raw')
    elif inter == 'qt':
        interfaces = ['qt']
    elif inter in ('raw', 'curses'):
        interfaces = [inter]
    else:
        fnerror('Unknown interface: %s' % inter)
        return 1

    # initialize possible interface
    errors = []
    Application = None
    for inter in interfaces:
        try:
            Application = LOADERS[inter]()
        except ImportError:
            # we store full exception context to allow --traceback option
            # to print a proper traceback.
            errors.append((inter, sys.exc_info()))
        else:
            opts.interface = inter
            break
    else:
        for inter, err in errors:
            if '--traceback' in sys.argv:
                traceback.print_exception(*err)
            fnerror('Interface %s is not available: %s' % (inter, err[1]))
        return 2

    # actually launch the application
    try:
        app = Application(repo, opts, args)
    except (ApplicationError, NotImplementedError), err:
        fnerror(str(err))

    return app.exec_()

def main():
    """
    Main application entry point.
    """

    usage = '''%prog [options] [filename]

    Starts a visual hg repository navigator.

    - With no options, starts the main repository navigator.

    - If a filename is given, starts in filelog diff mode (or in
      filelog navigation mode if -n option is set).

    - With -r option, starts in manifest viewer mode for given
      revision.
    '''

    parser = OptionParser(usage, version=__pkginfo__.version)
    parser.add_option('-I', '--interface', dest='interface',
                      help=('which GUI interface to use (among "qt", "raw"'
                             ' and "curses")'),
                      )
    parser.add_option('-R', '--repository', dest='repo',
                      help='location of the repository to explore')
    parser.add_option('-r', '--rev', dest='rev', default=None,
                      help='start in manifest navigation mode at rev R')
    parser.add_option('-n', '--navigate', dest='navigate', default=False,
                      action="store_true",
                      help='(with filename) start in navigation mode')

    opts, args = parser.parse_args()

    if opts.repo:
        dir_ = opts.repo
    else:
        dir_ = os.getcwd()
    repopath = find_repository(dir_)

    try:
        if repopath:
            u = uimod.ui()
            repo = build_repo(u, repopath)
        else:
            repo = NullRepo()
        try:
            sys.exit(start(repo, opts, args, parser.error))
        except KeyboardInterrupt:
            print 'interrupted!'
    except RepoError, e:
        parser.error(e)

