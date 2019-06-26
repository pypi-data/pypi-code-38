from tg import expose, redirect
from tg.decorators import with_trailing_slash
from tg import tmpl_context as c

from allura.controllers import repository

class BranchBrowser(repository.BranchBrowser):

    @expose('jinja:forgehg:templates/hg/index.html')
    @with_trailing_slash
    def index(self, limit=None, page=0, count=0, **kw):
        is_empty = c.app.repo.is_empty()
        latest = c.app.repo.latest(branch=self._branch)
        if is_empty or not latest:
            return dict(allow_fork=False, log=[], is_empty=is_empty)
        redirect(c.app.repo.url_for_commit(self._branch) + 'tree/')
