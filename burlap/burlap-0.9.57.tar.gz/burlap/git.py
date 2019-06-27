"""
Git
===

This module provides low-level tools for managing `Git`_ repositories.  You
should normally not use them directly but rather use the high-level wrapper
:func:`fabtools.require.git.working_copy` instead.

.. _Git: http://git-scm.com/

"""
from __future__ import print_function

import os

from fabric.api import run, sudo, hide
from fabric.context_managers import cd

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task
from burlap.exceptions import AbortDeployment
from burlap.utils import run_as_root
from burlap.files import file # pylint: disable=redefined-builtin

CURRENT_COMMIT = 'current_commit'

class GitSatchel(Satchel):

    name = 'git'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['git'],
        }

    def set_defaults(self):
        self.env.hooks = {
            #path/to/git/repo': ['local/path/to/hook']
        }

    @task
    def install_hooks(self):
        r = self.local_renderer
        for repo_path, hook_paths in r.env.hooks.items():
            r.env.repo_path_dot_git = '%s/.git' % repo_path
            assert file.is_dir(r.env.repo_path_dot_git), 'Repo %s does not exist.' % r.env.repo_path_dot_git
            for hook_path in hook_paths:
                r.env.local_hook_path = fqfn = self.find_template(hook_path)
                r.env.remote_hook_path = '%s/.git/hooks/%s' % (repo_path, os.path.split(hook_path)[-1])
                #r.env.remote_hook_dir = '%s/.git/hooks/' % (repo_path,)
                r.put(local_path=r.env.local_hook_path, remote_path=r.env.remote_hook_path)
                r.run_or_local('chmod +x {remote_hook_path}')

    @task
    def uninstall_hooks(self, hooks):
        raise NotImplementedError

    def clone(self, remote_url, path=None, use_sudo=False, user=None):
        """
        Clone a remote Git repository into a new directory.

        :param remote_url: URL of the remote repository to clone.
        :type remote_url: str

        :param path: Path of the working copy directory.  Must not exist yet.
        :type path: str

        :param use_sudo: If ``True`` execute ``git`` with
                         :func:`fabric.operations.sudo`, else with
                         :func:`fabric.operations.run`.
        :type use_sudo: bool

        :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                     with the given user.  If ``use_sudo is False`` this parameter
                     has no effect.
        :type user: str
        """

        cmd = 'git clone --quiet %s' % remote_url
        if path is not None:
            cmd = cmd + ' %s' % path

        if use_sudo and user is None:
            run_as_root(cmd)
        elif use_sudo:
            sudo(cmd, user=user)
        else:
            run(cmd)


    def add_remote(self, path, name, remote_url, use_sudo=False, user=None, fetch=True):
        """
        Add a remote Git repository into a directory.

        :param path: Path of the working copy directory.  This directory must exist
                     and be a Git working copy with a default remote to fetch from.
        :type path: str

        :param use_sudo: If ``True`` execute ``git`` with
                         :func:`fabric.operations.sudo`, else with
                         :func:`fabric.operations.run`.
        :type use_sudo: bool

        :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                     with the given user.  If ``use_sudo is False`` this parameter
                     has no effect.
        :type user: str

        :param name: name for the remote repository
        :type name: str

        :param remote_url: URL of the remote repository
        :type remote_url: str

        :param fetch: If ``True`` execute ``git remote add -f``
        :type fetch: bool
        """
        if path is None:
            raise ValueError("Path to the working copy is needed to add a remote")

        if fetch:
            cmd = 'git remote add -f %s %s' % (name, remote_url)
        else:
            cmd = 'git remote add %s %s' % (name, remote_url)

        with cd(path):
            if use_sudo and user is None:
                run_as_root(cmd)
            elif use_sudo:
                sudo(cmd, user=user)
            else:
                run(cmd)


    def fetch(self, path, use_sudo=False, user=None, remote=None):
        """
        Fetch changes from the default remote repository.

        This will fetch new changesets, but will not update the contents of
        the working tree unless yo do a merge or rebase.

        :param path: Path of the working copy directory.  This directory must exist
                     and be a Git working copy with a default remote to fetch from.
        :type path: str

        :param use_sudo: If ``True`` execute ``git`` with
                         :func:`fabric.operations.sudo`, else with
                         :func:`fabric.operations.run`.
        :type use_sudo: bool

        :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                     with the given user.  If ``use_sudo is False`` this parameter
                     has no effect.
        :type user: str

        :type remote: Fetch this remote or default remote if is None
        :type remote: str
        """

        if path is None:
            raise ValueError("Path to the working copy is needed to fetch from a remote repository.")

        if remote is not None:
            cmd = 'git fetch %s' % remote
        else:
            cmd = 'git fetch'

        with cd(path):
            if use_sudo and user is None:
                run_as_root(cmd)
            elif use_sudo:
                sudo(cmd, user=user)
            else:
                run(cmd)


    def pull(self, path, use_sudo=False, user=None, force=False):
        """
        Fetch changes from the default remote repository and merge them.

        :param path: Path of the working copy directory.  This directory must exist
                     and be a Git working copy with a default remote to pull from.
        :type path: str

        :param use_sudo: If ``True`` execute ``git`` with
                         :func:`fabric.operations.sudo`, else with
                         :func:`fabric.operations.run`.
        :type use_sudo: bool

        :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                     with the given user.  If ``use_sudo is False`` this parameter
                     has no effect.
        :type user: str
        :param force: If ``True``, append the ``--force`` option to the command.
        :type force: bool
        """

        if path is None:
            raise ValueError("Path to the working copy is needed to pull from a remote repository.")

        options = []
        if force:
            options.append('--force')
        options = ' '.join(options)

        cmd = 'git pull %s' % options

        with cd(path):
            if use_sudo and user is None:
                run_as_root(cmd)
            elif use_sudo:
                sudo(cmd, user=user)
            else:
                run(cmd)


    def checkout(self, path, branch="master", use_sudo=False, user=None, force=False):
        """
        Checkout a branch to the working directory.

        :param path: Path of the working copy directory.  This directory must exist
                     and be a Git working copy.
        :type path: str

        :param branch: Name of the branch to checkout.
        :type branch: str

        :param use_sudo: If ``True`` execute ``git`` with
                         :func:`fabric.operations.sudo`, else with
                         :func:`fabric.operations.run`.
        :type use_sudo: bool

        :param user: If ``use_sudo is True``, run :func:`fabric.operations.sudo`
                     with the given user.  If ``use_sudo is False`` this parameter
                     has no effect.
        :type user: str
        :param force: If ``True``, append the ``--force`` option to the command.
        :type force: bool
        """

        if path is None:
            raise ValueError("Path to the working copy is needed to checkout a branch")

        options = []
        if force:
            options.append('--force')
        options = ' '.join(options)

        cmd = 'git checkout %s %s' % (branch, options)

        with cd(path):
            if use_sudo and user is None:
                run_as_root(cmd)
            elif use_sudo:
                sudo(cmd, user=user)
            else:
                run(cmd)

    def get_changed_hooks(self):
        lm = self.last_manifest
        cm = self.current_manifest
        current_hooks = cm['hooks']
        last_hooks = lm.hooks or {}

        hooks_added = {} # {repo: [hooks]}, in current but not last
        for repo_path in current_hooks:
            hooks_added.setdefault(repo_path, [])
            added = set(current_hooks.get(repo_path, [])).difference(last_hooks.get(repo_path, []))
            hooks_added[repo_path].extend(added)

        hooks_removed = {} # {repo: [hooks]}, in last but not current
        for repo_path in last_hooks:
            hooks_removed.setdefault(repo_path, [])
            removed = set(last_hooks.get(repo_path, [])).difference(current_hooks.get(repo_path, []))
            hooks_removed[repo_path].extend(removed)

        return hooks_added, hooks_removed

    @task
    def update_hooks(self):
        added_hooks, removed_hooks = self.get_changed_hooks()
        if removed_hooks:
            self.uninstall_hooks(removed_hooks)
        if added_hooks:
            self.install_hooks()

    @task(precursors=['packager'])
    def configure(self):
        self.update_hooks()


class GitCheckerSatchel(Satchel):
    """
    Ensures the appropriate Git branch is being deployed.
    """

    name = 'gitchecker'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['git'],
            (UBUNTU, '12.04'): ['git'],
            (UBUNTU, '14.04'): ['git'],
            (UBUNTU, '16.04'): ['git'],
        }

    def set_defaults(self):
        self.env.branch = 'master'

    @task
    def check(self):
        self.vprint('Checking GIT branch...')
        with hide('running', 'stdout', 'stderr', 'warnings'):
            branch_name = self._local('git rev-parse --abbrev-ref HEAD', capture=True).strip()
            if self.env.branch != branch_name:
                raise AbortDeployment(
                    'You\'re trying to deploy branch "%s" but the target role "%s" only accepts branch "%s".' \
                        % (branch_name, self.genv.ROLE, self.env.branch))

    def record_manifest(self):
        self.check()
        return super(GitCheckerSatchel, self).record_manifest()

    @task
    def configure(self):
        pass


class GitTrackerSatchel(Satchel):
    """
    Tracks changes between Git commits.
    """

    name = 'gittracker'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['git'],
            (UBUNTU, '12.04'): ['git'],
            (UBUNTU, '14.04'): ['git'],
            (UBUNTU, '16.04'): ['git'],
        }

    def set_defaults(self):
        self.env.callbacks = []

    def get_logs_between_commits(self, a, b):
        """
        Retrieves all commit messages for all commits between the given commit numbers
        on the current branch.
        """
        self.vprint('REAL')
        ret = self.local('git --no-pager log --pretty=oneline %s...%s' % (a, b), capture=True)
        if self.verbose:
            print(ret)
        return str(ret)

    @task
    def get_current_commit(self):
        """
        Retrieves the git commit number of the current head branch.
        """
        with hide('running', 'stdout', 'stderr', 'warnings'):
            s = str(self.local('git rev-parse HEAD', capture=True))
            self.vprint('current commit:', s)
            return s

    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        manifest = super(GitTrackerSatchel, self).record_manifest()
        manifest[CURRENT_COMMIT] = self.get_current_commit()
        return manifest

    @task(precursors=['packager', 'pip', 'tarball', 'dj'])
    def configure(self):
        for callback in self.env.callbacks:
            satchel_name, method_name = callback.split('.')
            satchel = self.get_satchel(satchel_name)
            method = getattr(satchel, method_name)
            method()

git = GitSatchel()
gitchecker = GitCheckerSatchel()
gittracker = GitTrackerSatchel()
