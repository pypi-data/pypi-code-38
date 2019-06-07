# Code dedicated to adding various "safeguard" around evolution
#
# Some of these will be pollished and upstream when mature. Some other will be
# replaced by better alternative later.
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from mercurial.i18n import _

from mercurial import (
    configitems,
    error,
)

from . import exthelper

eh = exthelper.exthelper()

# hg <= 4.8
if 'auto-publish' not in configitems.coreitems.get('experimental', {}):

    eh.configitem('experimental', 'auto-publish', 'publish')

    @eh.reposetup
    def setuppublishprevention(ui, repo):

        class noautopublishrepo(repo.__class__):

            def checkpush(self, pushop):
                super(noautopublishrepo, self).checkpush(pushop)
                behavior = self.ui.config('experimental', 'auto-publish')
                nocheck = behavior not in ('warn', 'abort')
                if nocheck or getattr(pushop, 'publish', False):
                    return
                remotephases = pushop.remote.listkeys('phases')
                publishing = remotephases.get('publishing', False)
                if publishing:
                    if pushop.revs is None:
                        published = self.filtered('served').revs("not public()")
                    else:
                        published = self.revs("::%ln - public()", pushop.revs)
                    if published:
                        if behavior == 'warn':
                            self.ui.warn(_('%i changesets about to be published\n')
                                         % len(published))
                        elif behavior == 'abort':
                            msg = _('push would publish 1 changesets')
                            hint = _("behavior controlled by "
                                     "'experimental.auto-publish' config")
                            raise error.Abort(msg, hint=hint)

        repo.__class__ = noautopublishrepo
