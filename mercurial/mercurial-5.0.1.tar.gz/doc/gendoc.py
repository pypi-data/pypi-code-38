#!/usr/bin/env python
"""usage: %s DOC ...

where DOC is the name of a document
"""

from __future__ import absolute_import

import os
import sys
import textwrap

try:
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)
except ImportError:
    pass

# This script is executed during installs and may not have C extensions
# available. Relax C module requirements.
os.environ[r'HGMODULEPOLICY'] = r'allow'
# import from the live mercurial repo
sys.path.insert(0, r"..")
from mercurial import demandimport; demandimport.enable()
# Load util so that the locale path is set by i18n.setdatapath() before
# calling _().
from mercurial import util
util.datapath
from mercurial import (
    commands,
    encoding,
    extensions,
    help,
    minirst,
    pycompat,
    ui as uimod,
)
from mercurial.i18n import (
    gettext,
    _,
)

table = commands.table
globalopts = commands.globalopts
helptable = help.helptable
loaddoc = help.loaddoc

def get_desc(docstr):
    if not docstr:
        return b"", b""
    # sanitize
    docstr = docstr.strip(b"\n")
    docstr = docstr.rstrip()
    shortdesc = docstr.splitlines()[0].strip()

    i = docstr.find(b"\n")
    if i != -1:
        desc = docstr[i + 2:]
    else:
        desc = shortdesc

    desc = textwrap.dedent(desc.decode('latin1')).encode('latin1')

    return (shortdesc, desc)

def get_opts(opts):
    for opt in opts:
        if len(opt) == 5:
            shortopt, longopt, default, desc, optlabel = opt
        else:
            shortopt, longopt, default, desc = opt
            optlabel = _(b"VALUE")
        allopts = []
        if shortopt:
            allopts.append(b"-%s" % shortopt)
        if longopt:
            allopts.append(b"--%s" % longopt)
        if isinstance(default, list):
            allopts[-1] += b" <%s[+]>" % optlabel
        elif (default is not None) and not isinstance(default, bool):
            allopts[-1] += b" <%s>" % optlabel
        if b'\n' in desc:
            # only remove line breaks and indentation
            desc = b' '.join(l.lstrip() for l in desc.split(b'\n'))
        desc += default and _(b" (default: %s)") % bytes(default) or b""
        yield (b", ".join(allopts), desc)

def get_cmd(cmd, cmdtable):
    d = {}
    attr = cmdtable[cmd]
    cmds = cmd.lstrip(b"^").split(b"|")

    d[b'cmd'] = cmds[0]
    d[b'aliases'] = cmd.split(b"|")[1:]
    d[b'desc'] = get_desc(gettext(pycompat.getdoc(attr[0])))
    d[b'opts'] = list(get_opts(attr[1]))

    s = b'hg ' + cmds[0]
    if len(attr) > 2:
        if not attr[2].startswith(b'hg'):
            s += b' ' + attr[2]
        else:
            s = attr[2]
    d[b'synopsis'] = s.strip()

    return d

def showdoc(ui):
    # print options
    ui.write(minirst.section(_(b"Options")))
    multioccur = False
    for optstr, desc in get_opts(globalopts):
        ui.write(b"%s\n    %s\n\n" % (optstr, desc))
        if optstr.endswith(b"[+]>"):
            multioccur = True
    if multioccur:
        ui.write(_(b"\n[+] marked option can be specified multiple times\n"))
        ui.write(b"\n")

    # print cmds
    ui.write(minirst.section(_(b"Commands")))
    commandprinter(ui, table, minirst.subsection)

    # print help topics
    # The config help topic is included in the hgrc.5 man page.
    helpprinter(ui, helptable, minirst.section, exclude=[b'config'])

    ui.write(minirst.section(_(b"Extensions")))
    ui.write(_(b"This section contains help for extensions that are "
               b"distributed together with Mercurial. Help for other "
               b"extensions is available in the help system."))
    ui.write((b"\n\n"
              b".. contents::\n"
              b"   :class: htmlonly\n"
              b"   :local:\n"
              b"   :depth: 1\n\n"))

    for extensionname in sorted(allextensionnames()):
        mod = extensions.load(ui, extensionname, None)
        ui.write(minirst.subsection(extensionname))
        ui.write(b"%s\n\n" % gettext(pycompat.getdoc(mod)))
        cmdtable = getattr(mod, 'cmdtable', None)
        if cmdtable:
            ui.write(minirst.subsubsection(_(b'Commands')))
            commandprinter(ui, cmdtable, minirst.subsubsubsection)

def showtopic(ui, topic):
    extrahelptable = [
        ([b"common"], b'', loaddoc(b'common'), help.TOPIC_CATEGORY_MISC),
        ([b"hg.1"], b'', loaddoc(b'hg.1'), help.TOPIC_CATEGORY_CONFIG),
        ([b"hg-ssh.8"], b'', loaddoc(b'hg-ssh.8'), help.TOPIC_CATEGORY_CONFIG),
        ([b"hgignore.5"], b'', loaddoc(b'hgignore.5'),
         help.TOPIC_CATEGORY_CONFIG),
        ([b"hgrc.5"], b'', loaddoc(b'hgrc.5'), help.TOPIC_CATEGORY_CONFIG),
        ([b"hgignore.5.gendoc"], b'', loaddoc(b'hgignore'),
         help.TOPIC_CATEGORY_CONFIG),
        ([b"hgrc.5.gendoc"], b'', loaddoc(b'config'),
         help.TOPIC_CATEGORY_CONFIG),
    ]
    helpprinter(ui, helptable + extrahelptable, None, include=[topic])

def helpprinter(ui, helptable, sectionfunc, include=[], exclude=[]):
    for h in helptable:
        names, sec, doc = h[0:3]
        if exclude and names[0] in exclude:
            continue
        if include and names[0] not in include:
            continue
        for name in names:
            ui.write(b".. _%s:\n" % name)
        ui.write(b"\n")
        if sectionfunc:
            ui.write(sectionfunc(sec))
        if callable(doc):
            doc = doc(ui)
        ui.write(doc)
        ui.write(b"\n")

def commandprinter(ui, cmdtable, sectionfunc):
    h = {}
    for c, attr in cmdtable.items():
        f = c.split(b"|")[0]
        f = f.lstrip(b"^")
        h[f] = c
    cmds = h.keys()

    for f in sorted(cmds):
        if f.startswith(b"debug"):
            continue
        d = get_cmd(h[f], cmdtable)
        ui.write(sectionfunc(d[b'cmd']))
        # short description
        ui.write(d[b'desc'][0])
        # synopsis
        ui.write(b"::\n\n")
        synopsislines = d[b'synopsis'].splitlines()
        for line in synopsislines:
            # some commands (such as rebase) have a multi-line
            # synopsis
            ui.write(b"   %s\n" % line)
        ui.write(b'\n')
        # description
        ui.write(b"%s\n\n" % d[b'desc'][1])
        # options
        opt_output = list(d[b'opts'])
        if opt_output:
            opts_len = max([len(line[0]) for line in opt_output])
            ui.write(_(b"Options:\n\n"))
            multioccur = False
            for optstr, desc in opt_output:
                if desc:
                    s = b"%-*s  %s" % (opts_len, optstr, desc)
                else:
                    s = optstr
                ui.write(b"%s\n" % s)
                if optstr.endswith(b"[+]>"):
                    multioccur = True
            if multioccur:
                ui.write(_(b"\n[+] marked option can be specified"
                           b" multiple times\n"))
            ui.write(b"\n")
        # aliases
        if d[b'aliases']:
            ui.write(_(b"    aliases: %s\n\n") % b" ".join(d[b'aliases']))


def allextensionnames():
    return set(extensions.enabled().keys()) | set(extensions.disabled().keys())

if __name__ == "__main__":
    doc = b'hg.1.gendoc'
    if len(sys.argv) > 1:
        doc = encoding.strtolocal(sys.argv[1])

    ui = uimod.ui.load()
    if doc == b'hg.1.gendoc':
        showdoc(ui)
    else:
        showtopic(ui, encoding.strtolocal(sys.argv[1]))
