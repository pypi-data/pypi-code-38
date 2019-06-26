#-*- python -*-
import logging

from ming.utils import LazyProperty
from ming.orm.ormsession import ThreadLocalORMSession
from tg import tmpl_context as c
from timermiddleware import Timer

# Pyforge-specific imports
import allura.tasks
from allura.lib import helpers as h
from allura import model as M
from allura.controllers.repository import RepoRootController, RefsController, CommitsController
from allura.controllers.repository import MergeRequestsController, RepoRestController
from allura.lib.repository import RepositoryApp
from allura.app import SitemapEntry

# Local imports
from . import model as HM
from . import version
from .controllers import BranchBrowser

log = logging.getLogger(__name__)

class ForgeHgApp(RepositoryApp):
    '''This is the Hg app for Allura'''
    __version__ = version.__version__
    tool_label='Mercurial'
    tool_description="""
        Mercurial ("hg") is a distributed version control system.
        It is fast, easy to learn, and scalable.
    """
    ordinal=3
    forkable=True

    def __init__(self, project, config):
        super(ForgeHgApp, self).__init__(project, config)
        self.root = RepoRootController()
        self.api_root = RepoRestController()
        self.root.ref = RefsController(BranchBrowser)
        self.root.ci = CommitsController()
        setattr(self.root, 'merge-requests', MergeRequestsController())

    @LazyProperty
    def repo(self):
        return HM.Repository.query.get(app_config_id=self.config._id)

    @property
    def default_branch_name(self):
        return self.repo.get_default_branch('default')

    def admin_menu(self):
        links = []
        links.append(SitemapEntry(
                'Set default branch',
                c.project.url()+'admin/'+self.config.options.mount_point+'/' + 'set_default_branch_name',
                className='admin_modal'))
        links += super(ForgeHgApp, self).admin_menu()
        return links

    def install(self, project):
        '''Create repo object for this tool'''
        super(ForgeHgApp, self).install(project)
        repo = HM.Repository(
            name=self.config.options.mount_point,
            tool='hg',
            status='initializing',
            fs_path=self.config.options.get('fs_path'))
        ThreadLocalORMSession.flush_all()
        cloned_from_project_id = self.config.options.get('cloned_from_project_id')
        cloned_from_repo_id = self.config.options.get('cloned_from_repo_id')
        init_from_url = self.config.options.get('init_from_url')
        init_from_path = self.config.options.get('init_from_path')
        if cloned_from_project_id is not None:
            cloned_from = HM.Repository.query.get(_id=cloned_from_repo_id)
            repo.default_branch_name = cloned_from.default_branch_name
            repo.additional_viewable_extensions = cloned_from.additional_viewable_extensions
            allura.tasks.repo_tasks.clone.post(
                cloned_from_path=cloned_from.full_fs_path,
                cloned_from_name=cloned_from.app.config.script_name(),
                cloned_from_url=cloned_from.full_fs_path)
        elif init_from_url or init_from_path:
            allura.tasks.repo_tasks.clone.post(
                cloned_from_path=init_from_path,
                cloned_from_name=None,
                cloned_from_url=init_from_url)
        else:
            allura.tasks.repo_tasks.init.post()


def hg_timers():
    import mercurial.hg
    return [
        Timer('hg_lib.{method_name}', mercurial.hg.localrepo.localrepository, 'heads',
              'branchmap', 'tags'),
        Timer('hg_lib.{method_name}', mercurial.cmdutil, 'walkchangerevs'),
    ]


def forgehg_timers():
    return Timer('hg_tool.{method_name}', HM.hg.HgImplementation, '*')

