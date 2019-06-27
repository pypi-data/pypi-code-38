#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for import external blogs
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from twisted.python.procutils import which
from sat.tools.common import async_process
from sat.tools import utils
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Mercurial Merge Request handler",
    C.PI_IMPORT_NAME: "MERGE_REQUEST_MERCURIAL",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_DEPENDENCIES: ["MERGE_REQUESTS"],
    C.PI_MAIN: "MercurialHandler",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Merge request handler for Mercurial""")
}

SHORT_DESC = D_(u"handle Mercurial repository")
CLEAN_RE = re.compile(ur'[^\w -._]', flags=re.UNICODE)


class MercurialProtocol(async_process.CommandProtocol):
    """handle hg commands"""
    name = u"Mercurial"
    command = None

    @classmethod
    def run(cls, path, command, *args, **kwargs):
        """Create a new MercurialRegisterProtocol and execute the given mercurial command.

        @param path(unicode): path to the repository
        @param command(unicode): hg command to run
        """
        assert u"path" not in kwargs
        kwargs["path"] = path
        # FIXME: we have to use this workaround because Twisted's protocol.ProcessProtocol
        #        is not using new style classes. This can be removed once moved to
        #        Python 3 (super can be used normally then).
        d = async_process.CommandProtocol.run.__func__(cls, command, *args, **kwargs)
        d.addErrback(utils.logError)
        return d


class MercurialHandler(object):
    data_types = (u'mercurial_changeset',)

    def __init__(self, host):
        log.info(_(u"Mercurial merge request handler initialization"))
        try:
            MercurialProtocol.command = which('hg')[0]
        except IndexError:
            raise exceptions.NotFound(_(u"Mercurial executable (hg) not found, "
                                        u"can't use Mercurial handler"))
        self.host = host
        self._m = host.plugins['MERGE_REQUESTS']
        self._m.register('mercurial', self, self.data_types, SHORT_DESC)


    def check(self, repository):
        d = MercurialProtocol.run(repository, 'identify')
        d.addCallback(lambda __: True)
        d.addErrback(lambda __: False)
        return d

    def export(self, repository):
        return MercurialProtocol.run(repository, 'export', '-g', '-r', 'outgoing()',
                                     '--encoding=utf-8')

    def import_(self, repository, data, data_type, item_id, service, node, extra):
        parsed_data = self.parse(data)
        try:
            parsed_name = parsed_data[0][u'commit_msg'].split(u'\n')[0]
            parsed_name = CLEAN_RE.sub(u'', parsed_name)[:40]
        except Exception:
            parsed_name = u''
        name = u'mr_{item_id}_{parsed_name}'.format(item_id=CLEAN_RE.sub(u'', item_id),
                                                    parsed_name=parsed_name)
        return MercurialProtocol.run(repository, 'qimport', '-g', '--name', name,
                                     '--encoding=utf-8', '-', stdin=data)

    def parse(self, data, data_type=None):
        lines = data.splitlines()
        total_lines = len(lines)
        patches = []
        while lines:
            patch = {}
            commit_msg = []
            diff = []
            state = 'init'
            if lines[0] != '# HG changeset patch':
                raise exceptions.DataError(_(u'invalid changeset signature'))
            # line index of this patch in the whole data
            patch_idx = total_lines - len(lines)
            del lines[0]

            for idx, line in enumerate(lines):
                if state == 'init':
                    if line.startswith(u'# '):
                        if line.startswith(u'# User '):
                            elems = line[7:].split()
                            if not elems:
                                continue
                            last = elems[-1]
                            if (last.startswith(u'<') and last.endswith(u'>')
                                and u'@' in last):
                                patch[self._m.META_EMAIL] = elems.pop()[1:-1]
                            patch[self._m.META_AUTHOR] = u' '.join(elems)
                        elif line.startswith(u'# Date '):
                            time_data = line[7:].split()
                            if len(time_data) != 2:
                                log.warning(_(u'unexpected time data: {data}')
                                            .format(data=line[7:]))
                                continue
                            patch[self._m.META_TIMESTAMP] = (int(time_data[0])
                                                             + int(time_data[1]))
                        elif line.startswith(u'# Node ID '):
                            patch[self._m.META_HASH] = line[10:]
                        elif line.startswith(u'# Parent  '):
                            patch[self._m.META_PARENT_HASH] = line[10:]
                    else:
                        state = 'commit_msg'
                if state == 'commit_msg':
                    if line.startswith(u'diff --git a/'):
                        state = 'diff'
                        patch[self._m.META_DIFF_IDX] = patch_idx + idx + 1
                    else:
                        commit_msg.append(line)
                if state == 'diff':
                    if line.startswith(u'# ') or idx == len(lines)-1:
                        # a new patch is starting or we have reached end of patches
                        if idx == len(lines)-1:
                            # end of patches, we need to keep the line
                            diff.append(line)
                        patch[self._m.META_COMMIT_MSG] = u'\n'.join(commit_msg)
                        patch[self._m.META_DIFF] = u'\n'.join(diff)
                        patches.append(patch)
                        if idx == len(lines)-1:
                            del lines[:]
                        else:
                            del lines[:idx]
                        break
                    else:
                        diff.append(line)
        return patches
