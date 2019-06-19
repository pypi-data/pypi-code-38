##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import errno
import hashlib
import os
import shutil
import sys
import time
import traceback

from zc.buildout import UserError
from subprocess import check_call, CalledProcessError
import subprocess

try:
  try:
    from slapos.networkcachehelper import \
       helper_upload_network_cached_from_directory, \
       helper_download_network_cached_to_directory
  except ImportError:
    LIBNETWORKCACHE_ENABLED = False
  else:
    LIBNETWORKCACHE_ENABLED = True
except:
  print('There was problem while trying to import slapos.libnetworkcache:\n%s'
        % traceback.format_exc())
  LIBNETWORKCACHE_ENABLED = False
  print('Networkcache forced to be disabled.')

GIT_DEFAULT_REMOTE_NAME = 'origin'
GIT_DEFAULT_BRANCH_NAME = 'master'
TRUE_VALUES = ('y', 'yes', '1', 'true')

GIT_CLONE_ERROR_MESSAGE = 'Impossible to clone repository.'
GIT_CLONE_CACHE_ERROR_MESSAGE = 'Impossible to clone repository and ' \
    'impossible to download from cache.'

def upload_network_cached(path, name, revision, networkcache_options):
  """
  Creates uploads repository to cache.
  """
  if not (LIBNETWORKCACHE_ENABLED and networkcache_options.get(
      'upload-dir-url')):
    return False
  try:
    print('Uploading git repository to cache...')
    metadata_dict = {
        'revision':revision,
        # XXX: we set date from client side. It can be potentially dangerous
        # as it can be badly configured.
        'timestamp':time.time(),
    }
    helper_upload_network_cached_from_directory(
        path=path,
        directory_key='git-buildout-%s' % hashlib.md5(name).hexdigest(),
        metadata_dict=metadata_dict,
        # Then we give a lot of not interesting things
        dir_url=networkcache_options.get('upload-dir-url'),
        cache_url=networkcache_options.get('upload-cache-url'),
        signature_private_key_file=networkcache_options.get(
            'signature-private-key-file'),
        shacache_ca_file=networkcache_options.get('shacache-ca-file'),
        shacache_cert_file=networkcache_options.get('shacache-cert-file'),
        shacache_key_file=networkcache_options.get('shacache-key-file'),
        shadir_ca_file=networkcache_options.get('shadir-ca-file'),
        shadir_cert_file=networkcache_options.get('shadir-cert-file'),
        shadir_key_file=networkcache_options.get('shadir-key-file'),
    )
    print('Uploaded git repository to cache.')
  except Exception:
    print('Unable to upload to cache:\n%s.' % traceback.format_exc())


def download_network_cached(path, name, revision, networkcache_options):
  """
  Download a tar of the repository from cache, and untar it.
  """
  if not (LIBNETWORKCACHE_ENABLED and networkcache_options.get(
      'download-dir-url')):
    return False
  def strategy(entry_list):
    """
    Get the latest entry.
    """
    timestamp = 0
    best_entry = None
    for entry in entry_list:
      if entry['timestamp'] > timestamp:
        best_entry = entry
    return best_entry

  return helper_download_network_cached_to_directory(
      path=path,
      directory_key='git-buildout-%s' % hashlib.md5(name).hexdigest(),
      wanted_metadata_dict={'revision':revision},
      required_key_list=['timestamp'],
      strategy=strategy,
      # Then we give a lot of not interesting things
      dir_url=networkcache_options.get('download-dir-url'),
      cache_url=networkcache_options.get('download-cache-url'),
      signature_certificate_list=\
          networkcache_options.get('signature-certificate-list'),
  )

class Recipe(object):
  """Clone a git repository."""

  def __init__(self, buildout, name, options):
    options.setdefault('location',
        os.path.join(buildout['buildout']['parts-directory'], name))
    self.name = name
    for option in ('branch', 'revision', 'location', 'repository'):
      value = options.get(option, '').strip()
      if value == '':
        setattr(self, option, None)
      else:
        setattr(self, option, value)
    self.git_command = options.get('git-executable', '')
    if self.git_command == '':
      self.git_command = 'git'
    self.sparse = options.get('sparse-checkout', '').strip()
    # Set boolean values
    for key in ('develop', 'shared', 'use-cache', 'ignore-ssl-certificate',
                'ignore-cloning-submodules'):
      setattr(self, key.replace('-', '_'), options.get(key, '').lower() in TRUE_VALUES)
    if self.shared:
      self.use_cache = False

    self.networkcache = buildout.get('networkcache', {})

    # Check if input is correct
    if not self.repository:
      raise UserError('repository parameter is mandatory.')
    if self.revision and self.branch:
      # revision option has priority over branch option
      self.branch_overrided = self.branch
      self.branch = None

    # Check existence of directory
    if not os.path.exists(self.location):
      self.update = self.install

  def gitReset(self, revision=None):
    """Operates git reset on the repository."""
    command = [self.git_command, 'reset', '--hard']
    if revision:
      command.append(revision)
    check_call(command, cwd=self.location)

  def install(self):
    """
    Do a git clone.
    If branch is specified, checkout to it.
    If revision is specified, reset to it.
    If something fails, try to download from cache.
    Else, if possible, try to upload to cache.
    """
    # If directory already exist: delete it.
    if os.path.exists(self.location):
      print('destination directory already exists.')
      if not self.develop:
        print('Deleting it.')
        shutil.rmtree(self.location)
      else:
        # If develop is set, assume that this is a valid working copy
        return [self.location]

    if getattr(self, 'branch_overrided', None):
      print('Warning: "branch" parameter with value "%s" is ignored. '
            'Checking out to revision %s.' % (
            self.branch_overrided, self.revision)
      )
      sys.stdout.flush()

    git_clone_command = [self.git_command, 'clone',
                self.repository,
                self.location]
    config = []
    if self.shared:
      git_clone_command.append('--shared')
    if self.sparse:
      git_clone_command.append('--no-checkout')
      config.append('core.sparseCheckout=true')
    if self.branch:
      git_clone_command += '--branch', self.branch
    if self.ignore_ssl_certificate:
      config.append('http.sslVerify=false')

    if config and self.use_cache:
      raise NotImplementedError

    if not self.ignore_cloning_submodules:
      # `--recurse-submodules` to the git clone command will automatically
      # initialize and update each submodule in the repository.
      config.append('submodule.recurse=true')
      git_clone_command.append('--recurse-submodules')

    for config in config:
      git_clone_command += '--config', config

    try:
      check_call(git_clone_command, stdout=sys.stdout, stderr=sys.stdout)
      if not os.path.exists(self.location):
        raise UserError("Unknown error while cloning repository.")
      if self.sparse:
        with open(os.path.join(self.location, '.git',
                               'info', 'sparse-checkout'), 'w') as f:
          f.write(self.sparse + '\n')
        self.gitReset(self.revision)
      elif self.revision:
        self.gitReset(self.revision)
      if self.use_cache:
        upload_network_cached(os.path.join(self.location, '.git'),
                              self.repository, self.revision, self.networkcache)
      if not self.ignore_cloning_submodules:
        # Update submodule repository to the commit which is being pointed to
        # in main repo
        check_call([self.git_command, 'submodule', 'update', '--init',
                    '--recursive'], cwd=self.location)
    except CalledProcessError:
      print("Unable to download from git repository."
            " Trying from network cache...")
      if os.path.exists(self.location):
        shutil.rmtree(self.location)
      if not self.use_cache:
        raise UserError(GIT_CLONE_ERROR_MESSAGE)
      os.mkdir(self.location)
      if not download_network_cached(os.path.join(self.location, '.git'),
          self.repository, self.revision, self.networkcache):
        raise UserError(GIT_CLONE_CACHE_ERROR_MESSAGE)
      self.gitReset()

    return [self.location]

  def deletePycFiles(self, path):
    """Delete *.pyc files so that deleted/moved files can not be imported"""
    for path, dir_list, file_list in os.walk(path):
      for file in file_list:
        if file[-4:] in ('.pyc', '.pyo'):
          # allow several processes clean the same folder at the same time
          try:
            os.remove(os.path.join(path, file))
          except OSError as e:
            if e.errno != errno.ENOENT:
              raise

  def update(self):
    """
    Do a git fetch.
    If user doesn't develop, reset to upstream of the branch.
    With support for submodules, we also update the submodule repository if
    there has been update to the pointer of the submodules in the parent repo.
    This however puts the updated submodules in a DETACHED state.
    """
    # If develop or revision parameter, no need to update
    if self.develop or self.revision:
      return
    try:
      # first cleanup pyc files
      self.deletePycFiles(self.location)

      # Fetch and reset to the upstream
      check_call([self.git_command, 'fetch', '--all'], cwd=self.location)
      self.gitReset('@{upstream}')

      if not self.ignore_cloning_submodules:
        # Update the submodule to the commit which parent repo points to if
        # there has been revision is present for the parent repo.
        # According to man-page of submodule, update also clones missing
        # submodules and updating the working tree of the submodules. This is
        # why we do update here only after we are ok with revision of parent
        # repo being checked out to the desired one.
        # It will also init a submodule if required
        # NOTE: This will put the submodule repo in a `Detached` state.
        check_call([self.git_command, 'submodule', 'update', '--init', '-f',
                    '--recursive'], cwd=self.location)

    except:
      # Buildout will remove the installed location and mark the part as not
      # installed if an error occurs during update. If we are developping this
      # repository we do not want this to happen.
      print('Unable to update:\n%s' % traceback.format_exc())

def uninstall(name, options):
  """Keep the working copy, unless develop is set to false.
  """
  if not os.path.exists(options['location']):
    return
  force_keep = False
  if options.get('develop', 'yes').lower() in TRUE_VALUES:
    git_path = options.get('git-executable', 'git')
    if not os.path.isabs(git_path) or os.path.exists(git_path):
      p = subprocess.Popen([git_path, 'status', '--short'],
                            cwd=options['location'],
                            stdout=subprocess.PIPE)
      if p.communicate()[0].strip():
        print("You have uncommited changes in %s."
              " This folder will be left as is." % options['location'])
        force_keep = True

      p = subprocess.Popen([git_path,
                              'log', '--branches', '--not', '--remotes'],
                            cwd=options['location'],
                            stdout=subprocess.PIPE)
      if p.communicate()[0].strip():
        print("You have commits not pushed upstream in %s."
              " This folder will be left as is." % options['location'])
        force_keep = True
    else:
      print("Cannot check if there are unpushed/uncommitted changes in %s."
            " This folder will be left as is." % options['location'])
      force_keep = True

  if force_keep:
    # Eventhough this behaviour is not documented, buildout won't uninstall
    # anything if we unset __buildout_installed__
    options['__buildout_installed__'] = ''
