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
#
# pylint: disable=C0103

"""
Module for managing configuration parameters of hgview using Hg's
configuration system
"""
from functools import partial
import os
import re
import shlex

def cached(meth):
    """
    decorator to cache config values once they are read
    """
    name = meth.func_name
    def wrapper(self, *args, **kw):
        if name in self._cache:
            return self._cache[name]
        res = meth(self, *args, **kw)
        self._cache[name] = res
        return res
    wrapper.__doc__ = meth.__doc__
    return wrapper

class HgConfig(object):
    """
    Class managing user configuration from hg standard configuration system (.hgrc)
    """
    def __init__(self, ui, section="hgview"):
        self.ui = ui
        self.section = section
        self._cache = {}

    def _fromconfig(self, name, default, configmethod='config'):
        '''allow per-interface configuration.
        look for ``interface.config`` then for ``config`` if the first were not
        found'''
        getconfig = getattr(self.ui, configmethod)
        out = getconfig(self.section,
                        '.'.join((self.ui.opts.interface, name)),
                        None)
        if out is not None:
            return out
        return getconfig(self.section, name, default)


    @cached
    def getFancyReplace(self):
        r"""
        fancyreplace: ``"patt" "repl"`` used to modify description by replacing
            ``patt`` by ``repl`` using regular expression (``re.sub`` for instance).
            Ex: "#(\d+)":"`#\\1 <http://www.logilab.org/ticket/\\1>`_"
        """
        data = self._fromconfig('fancyreplace', None)
        if data is None:
            return data
        data = shlex.split(data)
        assert len(data) == 2
        patt, repl = data
        return partial(re.compile(patt).sub, repl)


    @cached
    def getFont(self, default='Monospace'):
        """
        font: default font used to display diffs and files. Use Qt4 format.
        """
        return self._fromconfig('font', default)

    @cached
    def getFontSize(self, default=9):
        """
        fontsize: text size in file content viewer
        """
        return int(self._fromconfig('fontsize', default))

    @cached
    def getDescriptionStylePath(self, default=None):
        """
        descriptionstylepath:
            stylesheet file path used to format the revision description.
            You should found a copy of the default style sheet in the documentation
            files location of your system (ex. /usr/share/doc/hgview/examples).
        """
        return self._fromconfig('descriptionstylepath', default)

    @cached
    def getDotRadius(self, default=8):
        """
        dotradius: radius (in pixels) of the dot in the revision graph
        """
        return int(self._fromconfig('dotradius', default))

    @cached
    def getUsers(self):
        """
        users: path of the file holding users configurations
        """
        users = {}
        aliases = {}
        usersfile = self._fromconfig('users', os.path.join('~', ".hgusers"))
        cfgfile = None
        if usersfile:
            try:
                cfgfile = open(os.path.expanduser(usersfile))
            except IOError:
                cfgfile = None

        if cfgfile:
            currid = None
            for line in cfgfile:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                cmd, val = line.split('=', 1)
                if cmd == 'id':
                    currid = val
                    if currid in users:
                        print "W: user %s is defined several times" % currid
                    users[currid] = {'aliases': set()}
                elif cmd == "alias":
                    users[currid]['aliases'].add(val)
                    if val in aliases:
                        print ("W: alias %s is used in several "
                               "user definitions" % val)
                    aliases[val] = currid
                else:
                    users[currid][cmd] = val
        return users, aliases

    @cached
    def getFileDescriptionView(self, default='persistent'):
        """
        descriptionview:

          :asfile: compact view with changeset description in the file list
          :persistent: persistent view with changeset description always visible (default)
        """
        return self._fromconfig('descriptionview', default).lower()

    @cached
    def getFileDescriptionColor(self, default='magenta'):
        """
        filedescriptioncolor: display color of the "description" entry
        """
        return self._fromconfig('filedescriptioncolor', default)
    @cached
    def getFileModifiedColor(self, default='blue'):
        """
        filemodifiedcolor: display color of a modified file
        """
        return self._fromconfig('filemodifiedcolor', default)
    @cached
    def getFileRemovedColor(self, default='red'):
        """
        fileremovedcolor: display color of a removed file
        """
        return self._fromconfig('fileremovededcolor', default)
    @cached
    def getFileDeletedColor(self, default='darkred'):
        """
        filedeletedcolor: display color of a deleted file
        """
        return self._fromconfig('filedeletedcolor', default)
    @cached
    def getFileAddedColor(self, default='green'):
        """
        fileaddedcolor: display color of an added file
        """
        return self._fromconfig('fileaddedcolor', default)

    @cached
    def getRowHeight(self, default=20):
        """
        rowheight: height (in pixels) on a row of the revision table
        """
        return int(self._fromconfig('rowheight', default))

    @cached
    def getHideFindDelay(self, default=10000):
        """
        hidefinddelay: delay (in ms) after which the find bar will disappear
        """
        return int(self._fromconfig('hidefindddelay', default))

    @cached
    def getFillingStep(self, default=300):
        """
        fillingstep: number of nodes 'loaded' at a time when updating repo graph log
        """
        return int(self._fromconfig('fillingstep', default))

    @cached
    def getChangelogColumns(self, default=None):
        """
        changelogcolumns: ordered list of displayed columns in changelog views;
                    defaults to ID, Branch, Log, Author, Date
        """
        cols = self._fromconfig('changelogcolumns', default)
        if cols is None:
            return None
        return [col.strip() for col in cols.split(',') if col.strip()]

    @cached
    def getFilelogColumns(self, default=None):
        """
        filelogcolumns: ordered list of displayed columns in filelog views;
                  defaults to ID, Log, Author, Date
        """
        cols = self._fromconfig('filelogcolumns', default)
        if cols is None:
            return None
        return [col.strip() for col in cols.split(',') if col.strip()]

    @cached
    def getDisplayDiffStats(self, default="yes"):
        """
        displaydiffstats: flag controlling the appearance of the
                    'Diff' column in a revision's file list
        """
        val = str(self._fromconfig('displaydiffstats', default))
        return val.lower() in ['true', 'yes', '1', 'on']

    @cached
    def getMaxFileSize(self, default=100000):
        """
        maxfilesize: max size of a file for diff computations, display content, etc.
                     (-1 means no max size)
        """
        return int(self._fromconfig('maxfilesize', default))

    @cached
    def getDiffBGColor(self, default='black'):
        """
        diffbgcolor: background color of diffs
        """
        return self._fromconfig('diffbgcolor', default)

    @cached
    def getDiffFGColor(self, default='white'):
        """
        difffgcolor: text color of diffs
        """
        return self._fromconfig('difffgcolor', default)

    @cached
    def getDiffPlusColor(self, default='green'):
        """
        diffpluscolor: text color of added lines in diffs
        """
        return self._fromconfig('diffpluscolor', default)

    @cached
    def getDiffMinusColor(self, default='red'):
        """
        diffminuscolor: text color of removed lines in diffs
        """
        return self._fromconfig('diffminuscolor', default)

    @cached
    def getDiffSectionColor(self, default='magenta'):
        """
        diffsectioncolor: text color of new section in diffs
        """
        return self._fromconfig('diffsectioncolor', default)

    @cached
    def getMQFGColor(self, default='#ff8183'):
        """
        mqfgcolor: bg color to highlight mq patches
        """
        return self._fromconfig('mqfgcolor', default)

    @cached
    def getMQHideTags(self, default=False):
        """
        mqhidetags: hide mq tags
        """
        return self._fromconfig('mqhidetags', default)

    @cached
    def getContentAtStartUp(self, default=True):
        """
        contentatstartup: show the content of changeset at startup (bottom part)
        """
        return bool(self._fromconfig('contentatstartup', default,
                                     configmethod='configbool'))

    @cached
    def getShowHidden(self, default=False):
        """
        showhidden: show hidden changeset at startup
        """
        return bool(self._fromconfig('showhidden', default,
                                     configmethod='configbool'))

    @cached
    def getInterface(self, default=None):
        """
        interface: which GUI interface to use (among "qt", "raw" and "curses")
        """
        return self.ui.config(self.section, 'interface', default)

    @cached
    def getNonPublicOnTop(self, default=False):
        """
        nonpublicontop: display non public changesets on top of the graph log
                        (disabled with *show hidden*)
        """
        return bool(self._fromconfig('nonpublicontop', default,
                                     configmethod='configbool'))

    @cached
    def getShowObsolete(self, default=True):
        """
        showobsolete: display obsolete relations
        """
        return bool(self._fromconfig('showobsolete', default,
                                     configmethod='configbool'))

    @cached
    def getExportTemplate(self):
        """
        exporttemplate: template used to serialize changeset metadata
                        while exporting into the window manager clipboard.
                        (default to `ui.logtemplate`)
        """
        return self._fromconfig('exporttemplate', None) or \
               self.ui.config('ui', 'logtemplate')

_HgConfig = HgConfig
# HgConfig is instantiated only once (singleton)
#
# this 'factory' is used to manage this (not using heavy guns of
# metaclass or so)
_hgconfig = None
def HgConfig(ui):
    """Factory to instantiate HgConfig class as a singleton
    """
    # pylint: disable=E0102
    global _hgconfig
    if _hgconfig is None:
        _hgconfig = _HgConfig(ui)
    return _hgconfig


def get_option_descriptions(rest=False):
    """
    Extract options descriptions (docstrings of HgConfig methods)
    """
    options = []
    for attr in dir(_HgConfig):
        if attr.startswith('get'):
            meth = getattr(_HgConfig, attr)
            if callable(meth):
                doc = meth.__doc__
                if doc and doc.strip():
                    doc = doc.strip()
                    if rest:
                        doc = re.sub(r' *(?P<arg>.*) *: *(?P<desc>.*)', r'``\1`` \2', doc.strip())
                        doc = ' '.join(doc.split()) # remove \n and other multiple whitespaces
                    options.append(doc)
    return options

