import doctest
from zope.testing import renormalizing

import os
import re
import shutil
import tempfile
import unittest
import zc.buildout.testing
from zc.buildout.testing import buildoutTearDown
from contextlib import contextmanager
from functools import wraps
from subprocess import check_call, check_output, CalledProcessError
from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
    GIT_CLONE_CACHE_ERROR_MESSAGE

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

GIT_REPOSITORY = 'https://lab.nexedi.com/nexedi/slapos.recipe.build.git'
BAD_GIT_REPOSITORY = 'http://git.erp5.org/repos/nowhere'
REVISION = '2566127'

def setUp(test):
  # XXX side effect. Disable libnetworkcache because buildout testing
  # infrastructure doesn't support offline install of external egg "forced"
  # into itself.
  zc.buildout.buildout.LIBNETWORKCACHE_ENABLED = False

  zc.buildout.testing.buildoutSetUp(test)
  zc.buildout.testing.install_develop('slapos.recipe.build', test)

@contextmanager
def chdir(path):
  old = os.getcwd()
  try:
    os.chdir(path)
    yield old
  finally:
    os.chdir(old)

def with_buildout(wrapped):
  def wrapper(self):
    self.globs = {}
    setUp(self)
    try:
      wrapped(self, **self.globs)
    finally:
      buildoutTearDown(self)
  return wraps(wrapped)(wrapper)

class GitCloneNonInformativeTests(unittest.TestCase):

  def setUp(self):
    self.dir = os.path.realpath(tempfile.mkdtemp())
    self.parts_directory_path = os.path.join(self.dir, 'test_parts')

  def setUpParentRepository(self):
    """
    This function sets ups repositories for parent repo and adds file and commit
    to it.
    """
    # Create parent and submodule directory
    self.project_dir = os.path.join(self.dir, 'main_repo')
    os.mkdir(self.project_dir)

    # Add files and folder in parent repo and initialize git in it
    check_call(['git', 'init'], cwd=self.project_dir)
    self.setUpGitConfig(self.project_dir)
    os.mkdir(os.path.join(self.project_dir, 'dir1'))
    self.touch(self.project_dir, 'file1.py')
    self.gitAdd(self.project_dir)
    self.gitCommit(self.project_dir, msg='Add file and folder in main repo')

  def setUpSubmoduleRepository(self):
    """
    This function sets up repositories and config for parent repo and a
    submodule repo and create small commits as well as links the 2 repos.
    """
    # Create parent and submodule directory
    self.submodule_dir = os.path.join(self.dir ,'submodule_repo')
    os.mkdir(self.submodule_dir)

    # Add files in submodule repo and initialize git in it
    check_call(['git', 'init'], cwd=self.submodule_dir)
    self.setUpGitConfig(self.submodule_dir)
    self.touch(self.submodule_dir, 'file1.py')
    self.gitAdd(self.submodule_dir)
    self.gitCommit(self.submodule_dir, msg='Add file1 in submodule repo')

  def attachSubmoduleToParent(self):
    """
    Adds the submodule repo to parent repo and creates a commit in parent if
    parent and submodule repo are present.
    """
    assert hasattr(self, 'project_dir') and hasattr(self, 'submodule_dir'), (
      "Make sure parent repo and submodule repo are present")
    submodule_dir_main_repo = os.path.join(self.project_dir, 'dir1')
    # Add submodule to main repo and commit
    check_call(['git', 'submodule', 'add', self.submodule_dir],
                cwd=submodule_dir_main_repo)
    self.gitCommit(self.project_dir, msg='Add submodule repo')

  def createRepositoriesAndConnect(self):
    """
    Creates parent and submodule repository and then adds the submodule repo to
    parent repo and creates a commit in parent.
    """
    self.setUpParentRepository()
    self.setUpSubmoduleRepository()
    self.attachSubmoduleToParent()

  def tearDown(self):
    shutil.rmtree(self.dir)
    for var in list(os.environ):
      if var.startswith('SRB_'):
        del os.environ[var]

  def setUpGitConfig(self, proj_dir):
    """
    Setup user and email for given git repository
    """
    check_call(['git', 'config', 'user.email', 'test@example.com'], cwd=proj_dir)
    check_call(['git', 'config', 'user.name', 'Test'], cwd=proj_dir)

  def gitOutput(self, *args, **kw):
    return check_output(('git',) + args, universal_newlines=True, **kw)

  def gitAdd(self, proj_dir):
    """runs a 'git add .' in the provided git repo
    :param proj_dir:    path to a git repo
    """
    check_call(['git', 'add', '.'], cwd=proj_dir)

  def gitCommit(self, proj_dir, msg):
    """runs a 'git commit -m msg' in the provided git repo
    :param proj_dir:  path to a git repo
    """
    check_call(['git', 'commit', '-m', msg], cwd=proj_dir)

  def getRepositoryHeadCommit(self, proj_dir):
    """
    Returns the sha of HEAD of a git repo
    """
    return self.gitOutput('rev-parse', 'HEAD', cwd=proj_dir).rstrip()

  def touch(self, *parts):
    os.close(os.open(os.path.join(*parts), os.O_CREAT, 0o666))

  def readFile(self, *parts):
    with open(os.path.join(*parts), 'r') as f:
      return f.read()

  def checkLocalChanges(self, parent_local_change_path,
                        submodule_local_change_path):
    # Check if the file are created at the expected position and check contents
    self.assertTrue(os.path.exists(parent_local_change_path))
    self.assertTrue(os.path.exists(submodule_local_change_path))
    self.assertEqual(self.readFile(parent_local_change_path), 'foo')
    self.assertEqual(self.readFile(submodule_local_change_path), 'bar')

  def makeGitCloneRecipe(self, options):
    from slapos.recipe.gitclone import Recipe
    bo = {
        'buildout': {
            'parts-directory': self.parts_directory_path,
            'directory': self.dir,
         }
    }
    default_options = {
      'repository': GIT_REPOSITORY
      }
    default_options.update(**options)
    return Recipe(bo, 'test', default_options)

  def test_using_download_cache_if_git_fails(self):
    recipe = self.makeGitCloneRecipe({"use-cache": "true",
                                      "repository": BAD_GIT_REPOSITORY})
    with chdir(self.dir), \
         self.assertRaises(zc.buildout.UserError) as cm:
      recipe.install()
    self.assertEqual(str(cm.exception), GIT_CLONE_CACHE_ERROR_MESSAGE)

  def test_not_using_download_cache_if_forbidden(self):
    recipe = self.makeGitCloneRecipe({"repository": BAD_GIT_REPOSITORY})
    with chdir(self.dir), \
         self.assertRaises(zc.buildout.UserError) as cm:
      recipe.install()
    self.assertEqual(str(cm.exception), GIT_CLONE_ERROR_MESSAGE)

  def test_cleanup_of_pyc_files(self):
    recipe = self.makeGitCloneRecipe({})
    recipe.install()
    git_repository_path = os.path.join(self.parts_directory_path, "test")
    self.assertTrue(os.path.exists(git_repository_path))
    bad_file_path = os.path.join(git_repository_path, "foo.pyc")
    bade_file = open(bad_file_path, 'w')
    bade_file.close()
    self.assertTrue(os.path.exists(bad_file_path))
    # install again and make sure pyc file is removed
    recipe = self.makeGitCloneRecipe({})
    recipe.update()
    self.assertTrue(os.path.exists(git_repository_path))
    self.assertFalse(os.path.exists(bad_file_path), "pyc file not removed")

  @with_buildout
  def test_clone_and_update_submodule(self, buildout, write,
                                      sample_buildout, **kw):
    """
    Remote:
      Repositories status:  Parent repo(M1) and Submodule repo (S1)
      Parent repo (M1) ---references---> Submodule(S1)
    Local:
      Buildout should install(using branch) at M1+S1

    Remote:
      Repositories status:  Parent repo(M2) and Submodule repo (S2)
      Parent repo (M2) ---references---> Submodule(S1)
    Local:
      Buildout should update to at M2+S1

    Remote:
      Repositories status:  Parent repo(M3) and Submodule repo (S2)
      Parent repo (M3) ---references---> Submodule(S2)
    Local:
      Buildout should update to M3+S2
    """
    self.createRepositoriesAndConnect()

    # Clone repositories in status M1 and S1 (M1---->S1)
    write(sample_buildout, 'buildout.cfg',
"""
[buildout]
parts = git-clone

[git-clone]
recipe = slapos.recipe.build:gitclone
repository = %s
""" % self.project_dir)
    check_call([buildout])

    main_repo_path = os.path.join(sample_buildout, 'parts', 'git-clone')
    self.assertTrue(os.path.exists(main_repo_path))
    submodule_repo_path = os.path.join(main_repo_path, 'dir1',
                                       'submodule_repo')
    # Check if the submodule is not empty
    self.assertTrue(os.listdir(submodule_repo_path))

    # Get the head commit of the submodule repo
    head_commit_submodule_after_clone = self.getRepositoryHeadCommit(
                                              submodule_repo_path)

    # Add untracked files as markers to check that the part
    # was updated rather than removed+reinstalled.
    write(main_repo_path, 'local_change_main', 'foo')
    write(submodule_repo_path, 'local_change_submodule', 'bar')
    parent_local_change_path = os.path.join(main_repo_path,
                                            'local_change_main')
    submodule_local_change_path = os.path.join(submodule_repo_path,
                                               'local_change_submodule')
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)

    # Trigger `update` method call for gitclone recipe
    check_call([buildout])

    # The local changes should be still there after update
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)

    # On REMOTE, update submodule repository and parent repo with new commit,
    # but do not update the pointer to submodule on parent repo
    self.touch(self.project_dir, 'file2.py')
    self.gitAdd(self.project_dir)
    self.gitCommit(self.project_dir, msg='Add file2 in main repo')
    self.touch(self.submodule_dir, 'file2.py')
    self.gitAdd(self.submodule_dir)
    self.gitCommit(self.submodule_dir, msg='Add file2 in submodule repo')

    # Trigger update on the same branch. Remember the state at remote is
    # M2 and S2 (M2---->S1)
    check_call([buildout])
    head_commit_submodule_after_first_update = self.getRepositoryHeadCommit(
                                                      submodule_repo_path)
    # The local changes should be still there after update
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)

    # On REMOTE, add new commit to submodule and then update the submodule
    # pointer on parent repo and commit it
    submodule_dir_main_repo = os.path.join(self.project_dir, 'dir1',
                                           'submodule_repo')
    check_call(['git', 'checkout', 'master'], cwd=submodule_dir_main_repo)
    check_call(['git', 'pull', '--ff'], cwd=submodule_dir_main_repo)
    self.gitAdd(self.project_dir)
    self.gitCommit(self.project_dir, msg='Update submodule version')

    # Trigger update again on the same branch. Remember the state at remote is
    # M3 and S2(M3---->S2)
    check_call([buildout])
    head_commit_submodule_after_second_update = self.getRepositoryHeadCommit(
                                                      submodule_repo_path)
    # The local changes should be still there after update
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)


    # Check the HEAD of the submodule
    submodule_head_commit = self.getRepositoryHeadCommit(self.submodule_dir)
    self.assertEqual(head_commit_submodule_after_clone,
                     head_commit_submodule_after_first_update)

    self.assertNotEqual(head_commit_submodule_after_first_update,
                        head_commit_submodule_after_second_update)

    self.assertEqual(head_commit_submodule_after_second_update,
                     submodule_head_commit)

    # Update the recipe with new revision for parent and trigger uninstall/
    # install
    write(sample_buildout, 'buildout.cfg',
"""
[buildout]
parts = git-clone

[git-clone]
recipe = slapos.recipe.build:gitclone
repository = %s
revision = %s
""" % (self.project_dir, str(self.getRepositoryHeadCommit(self.project_dir))))
    check_call([buildout])

    self.assertTrue(os.path.exists(main_repo_path))
    # Check if the submodule is not empty
    self.assertTrue(os.listdir(submodule_repo_path))

    # Since calling buildout should've reinstalled, we expect the local changes
    # to be gone
    self.assertFalse(os.path.exists(parent_local_change_path))
    self.assertFalse(os.path.exists(submodule_local_change_path))

    # Get the head commit of the submodule repo
    head_commit_submodule_with_revision = self.getRepositoryHeadCommit(
                                                      submodule_repo_path)

    self.assertEqual(head_commit_submodule_with_revision,
                     submodule_head_commit)

  @with_buildout
  def test_clone_install_and_udpate_develop_mode(self, buildout, write,
                                                 sample_buildout, **kw):
    """
    Test to verify the result of development mode, i.e., develop = True.
    In this case, we expect local changes to be untouched
    """
    self.createRepositoriesAndConnect()

    # Clone repositories in status M1 and S1 (M1---->S1)
    write(sample_buildout, 'buildout.cfg',
"""
[buildout]
parts = git-clone

[git-clone]
recipe = slapos.recipe.build:gitclone
repository = %s
develop=True
""" % self.project_dir)
    check_call([buildout])

    main_repo_path = os.path.join(sample_buildout, 'parts', 'git-clone')
    self.assertTrue(os.path.exists(main_repo_path))
    submodule_repo_path = os.path.join(main_repo_path, 'dir1',
                                       'submodule_repo')
    # Check if the submodule is not empty
    self.assertTrue(os.listdir(submodule_repo_path))

    # Add untracked files as markers to check that the part
    # was updated rather than removed+reinstalled.
    write(main_repo_path, 'local_change_main', 'foo')
    write(submodule_repo_path, 'local_change_submodule', 'bar')
    parent_local_change_path = os.path.join(main_repo_path,
                                            'local_change_main')
    submodule_local_change_path = os.path.join(submodule_repo_path,
                                               'local_change_submodule')
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)

    # Trigger `update` method call for gitclone recipe
    check_call([buildout])

    # The local changes should be still there after update as it is develop mode
    self.checkLocalChanges(parent_local_change_path, submodule_local_change_path)

  @with_buildout
  def test_git_add_for_submodule_changes(self, buildout, write,
                                         sample_buildout, **kw):
    """
    Test to verify the result of `git status` being executed from parent as well
    as submodule repository after making some local changes in submodule repo
    """
    # Create a parent repo
    self.setUpParentRepository()
    # Create submodule repository
    self.setUpSubmoduleRepository()
    # Attach the submodule repository to the parent repo on remote
    self.attachSubmoduleToParent()

    write(sample_buildout, 'buildout.cfg',
"""
[buildout]
parts = git-clone

[git-clone]
recipe = slapos.recipe.build:gitclone
repository = %s
""" % self.project_dir)
    check_call([buildout])

    local_parent_dir = os.path.join(sample_buildout, 'parts', 'git-clone')
    local_submodule_dir = os.path.join(local_parent_dir, 'dir1',
                                       'submodule_repo')

    # Now so some change manually in submodule repo, but don't commit
    self.touch(local_submodule_dir, 'file2.py')
    self.gitAdd(local_submodule_dir)

    # Do `git status` to check if the changes are shown for the repo in parent
    # This should the changes been done in the main as well as submodule repo
    files_changed = self.gitOutput('status', '--porcelain',
                                    cwd=local_parent_dir)
    file_changed, = files_changed.splitlines()
    # Check if submodule directory is part of modified list
    self.assertEqual(file_changed, ' M dir1/submodule_repo')

    # Now that `git status` in parent repo shows changes in the submodule repo,
    # do `git status` in the submodule repo to re-confirm the exact file change
    files_changed = self.gitOutput('status', '--porcelain',
                                    cwd=local_submodule_dir)
    file_changed, = files_changed.splitlines()
    # Check if submodule directory is part of modified list
    self.assertEqual(file_changed, 'A  file2.py')

  def test_ignore_ssl_certificate(self, ignore_ssl_certificate=True):
    import slapos.recipe.gitclone

    # Monkey patch check_call
    original_check_call = slapos.recipe.gitclone.check_call
    check_call_parameter_list = []
    def patch_check_call(*args, **kw):
      check_call_parameter_list.extend((args, kw))
      original_check_call(args[0])
    slapos.recipe.gitclone.check_call = patch_check_call

    bo = {
        'buildout': {
            'parts-directory': self.parts_directory_path,
            'directory': self.dir,
         }
    }
    options = {
      'repository': GIT_REPOSITORY,
      "ignore-ssl-certificate": str(ignore_ssl_certificate).lower(),
    }
    recipe = slapos.recipe.gitclone.Recipe(bo, 'test', options)

    recipe.install()

    # Check git clone parameters
    _ = self.assertIn if ignore_ssl_certificate else self.assertNotIn
    _("http.sslVerify=false", check_call_parameter_list[0][0])

    # Restore original check_call method
    slapos.recipe.gitclone.check_call = original_check_call

  def test_ignore_ssl_certificate_false(self):
    self.test_ignore_ssl_certificate(ignore_ssl_certificate=False)

  def test_clone_submodules_by_default(self, ignore_cloning_submodules=False):
    self.createRepositoriesAndConnect()
    recipe = self.makeGitCloneRecipe(
      {'repository': self.project_dir,
        'ignore-cloning-submodules': str(ignore_cloning_submodules).lower()}
    )
    recipe.install()
    main_repo_path = os.path.join(self.parts_directory_path, "test")
    self.assertTrue(os.path.exists(main_repo_path))
    submodule_repo_path = os.path.join(main_repo_path, 'dir1',
                                       'submodule_repo')
    # Check if the folder exists
    self.assertTrue(os.path.exists(main_repo_path))
    # Check is there is anything in submodule repository path
    self.assertNotEqual(bool(ignore_cloning_submodules),
                        bool(os.listdir(submodule_repo_path)))

  def test_ignore_cloning_submodules(self):
    self.test_clone_submodules_by_default(ignore_cloning_submodules=True)

def test_suite():
  suite = unittest.TestSuite((
      doctest.DocFileSuite(
          os.path.join(os.path.dirname(__file__), '..', '..', '..', 'README.rst'),
          module_relative=False,
          setUp=setUp,
          tearDown=zc.buildout.testing.buildoutTearDown,
          optionflags=optionflags,
          checker=renormalizing.RENormalizing([
              zc.buildout.testing.normalize_path,
              (re.compile(r'http://localhost:\d+'), 'http://test.server'),
              # Clean up the variable hashed filenames to avoid spurious
              # test failures
              (re.compile(r'[a-f0-9]{32}'), ''),
              ]),
          ),
      unittest.makeSuite(GitCloneNonInformativeTests),
      ))
  return suite

if __name__ == '__main__':
  unittest.main(defaultTest='test_suite')
