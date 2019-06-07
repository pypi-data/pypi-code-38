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
help messages for hgview
"""

help_msg = """
hgview: a visual hg log viewer
==============================

hgview without any parameters will launch the hgview log navigator, allowing to
visually browse the hg graph log, search in logs, and display diff
between arbitrary revisions of a file, with simple support for mq and
bigfile extensions.

If a filename is given the filelog diff viewer is launched for this file,
and with the '-n' option the filelog navigator is launched for the file.

With the '-r' option the manifest viewer is launched for the given revision.

Revision graph browser
----------------------

The main revision graph displays the repository history as a graph,
sorted by revision number.

Hit Space key or click the button to show or hide the changeset
content.

The color of the node of each revision depends on the named branch the
revision belongs to.

The color of the links (between nodes) is randomly chosen.

The position of the working directory is marked on the graph with a red
border around the node marker. If the working directory has local
modifications, a virtual 'WORKING DIRECTORY' revision is added in the graph with a warning
icon (with no revision number). Modified, added and removed files are
listed and browsable as a normal changeset node.

Note that if the working directory is in merge state, there will be 2
revisions marked as modified in the graph (since the working directory
is then a child of both the merged nodes).

mq support
~~~~~~~~~~

There is a simple support for the mq extension. Applied patches are
seen in the revlog graph with a special arrow icon. Unapplied patches
are not changesets and are not shown in the revlog graph.

Instead, when the currently selected revision is an applied patch, the revision
metadata display (see below) area shows an additional
'Patch queue' line with colored background listing all available patches, applied
or not. The content of unapplied patches cannot be shown, but it will be indicated that
there are other unapplied patches if there is at least one
applied patch). The current patch is bold and unapplied
patches are italic.


Revision metadata display
-------------------------

Parents, ancestors and children of the current changeset are showed with two kinds of links:

- clicking the **changeset ID** (hash value) navigates to the given revision,

- clicking the **revision number** (integer value) of parents and ancestors
  changes which other revision is used to compute
  the diff of merges. This allows you to compare the merged node with each
  of its parents, or even with the common ancestor of these 2
  nodes. The currently selected ancestor is shown bold.


Revision description rendering
------------------------------

The revision's description text is interpreted as ReStructuredText.
Commit messages can thus contain formatted text, links, tables, references, etc.

RST links without scheme will link to the specified revision (changeset ID/revision number/tag name). For instance::

  `links in fancy view open browser <e449146a687d7ca71520>`_


Revisions modified file list
-----------------------------

The file list displays the list of files modified in the current revision. The diff
view shows the diff of the currently selected modified file 
and the currently selected ancestor.

On a merge node, by default, only files which are different from
both its parents are listed here. However, you can display the
list of all modified files by double-clicking the file list column
header.


Quickbars
---------

Quickbars are toolbars that appear at the bottom of the screen.
Only one quickbar can be displayed at a time.

When a quickbar is visible, hitting the Esc key makes it disappear.

The goto quickbar
~~~~~~~~~~~~~~~~~

This toolbar appears when hitting Ctrl+G. It allows you to jump to a
given revision. The destination revision can be entered by:

- it's revision number (negative values allowed, counting back from tip=-1)
- it's changeset ID (short or long)
- a tag name (partial or full)
- a branch name
- an empty string - means the current parent of the working directory

The search quickbar
~~~~~~~~~~~~~~~~~~~

This toolbar appears when hitting Ctrl+F or / (if not in goto toolbar).

It allows you to type a string to be searched for:

- in the currently displayed revision commit message (with highlight-as-you-type)
- in the currently displayed file or diff (with highlight-as-you-type)

Hitting the "Search next" button starts a background task for searching through the whole
revision log, starting from the currently selected revision
and file.


Keyboard shortcuts
------------------

**Up/Down**
  go to next/previous revision

**Middle Click**
  go to the common ancestor of the clicked revision and the currently selected one

**Left/Right**
  display previous/next files of the current changeset

**Ctrl+F** or **/**
  display the search 'quickbar'

**Ctrl+G**
  display the goto 'quickbar'

**Esc**
  exit hgview or hide the visible 'quickbar'

**Enter**
  run the diff viewer for the currently selected file (display diff
  between revisions)

**Alt+Enter**
  run the filelog navigator

**Shift+Enter**
  run the manifest viewer for the displayed revision

**Ctrl+R**
  reload repository; should happen automatically
  if it is modified outside hgview (due to a commit, a pull, etc.)

**Alt+Up/Down**
  display previous/next diff block

**Alt+Left/Right**
  go to previous/next visited revision (in navigation history)

**Backspace**
  set current revision the current start revision (hide any revision above it)

**Shift+Backspace**
  clear the start revision value


    """

def get_options_helpmsg(rest=False):
    """display hgview full list of configuration options
    """
    from config import get_option_descriptions
    options = get_option_descriptions(rest)
    msg = """
Configuration options
=====================

The following options can be set in the ``[hgview]`` section of a Mercurial configuration file.

:Note: *User interface specific configuration* is possible.
       You can add a ``qt.`` or ``raw.`` prefix to each option
       in order to target a particular user interface.

       Without any prefix, the value is used as default for both user interfaces.


"""
    msg += '\n'.join(["- " + v for v in options]) + '\n'
    msg += """
The value of 'users' should be the name of a file
describing well-known users, like::

    --8<-------------------------------------------
    # file ~/.hgusers
    id=david
    alias=david.douard@logilab.fr
    alias=david@logilab.fr
    alias=David Douard <david.douard@logilab.fr>
    color=#FF0000
    id=ludal
    alias=ludovic.aubry@logilab.fr
    alias=ludal@logilab.fr
    alias=Ludovic Aubry <ludovic.aubry@logilab.fr>
    color=#00FF00
    --8<-------------------------------------------

This allows authors to be shown with consistent coloring in the graphlog
browser, even if they use different usernames.
    """
    return msg

long_help_msg = help_msg + get_options_helpmsg()
