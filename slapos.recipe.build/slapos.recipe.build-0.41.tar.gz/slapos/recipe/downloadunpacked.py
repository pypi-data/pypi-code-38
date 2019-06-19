##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
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
import os
import logging
import shutil
import subprocess
import tarfile
import zc.buildout
import tempfile
import setuptools.archive_util
import stat
from hashlib import md5

is_true = ('false', 'true').index

class Recipe:

  def __init__(self, buildout, name, options):
    self.buildout = buildout
    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)
    if 'filename' in self.options and 'destination' in self.options:
      raise zc.buildout.UserError('Parameters filename and destination are '
          'exclusive.')
    self.parts = None
    self.destination = self.options.get('destination', None)
    self.shared = shared = (is_true(options.get('shared', 'false').lower()) and
                            buildout['buildout'].get('shared-parts', None))
    if self.destination is None:
      if shared:
        shared_part = buildout['buildout'].get('shared-parts', None)
        top_location = options.get('top_location', '')
        shared = os.path.join(shared_part.strip().rstrip('/'), top_location, name)
        if not os.path.exists(shared):
          os.makedirs(shared)
        self._signature = Signature('.slapos.recipe.build.signature')
        profile_base_location = options.get('_profile_base_location_', '')
        for k, v in sorted(options.items()):
          if profile_base_location:
            v = v.replace(profile_base_location, '${:_profile_base_location_}')
          self._signature.update(k, v)
        shared = os.path.join(shared, self._signature.hexdigest())
        self.parts = shared
        self.logger.info('shared directory  %s set for %s', shared, name)
      else:
        self.parts = os.path.join(self.buildout['buildout']['parts-directory'],
            self.name)
      self.destination = self.parts
      # backward compatibility with other recipes -- expose location
      options['location'] = self.parts
    options['target'] = self.destination
    options.setdefault('extract-directory', '')

    self.environ = {}
    self.original_environment = os.environ.copy()
    environment_section = self.options.get('environment-section', '').strip()
    if environment_section and environment_section in buildout:
      # Use environment variables from the designated config section.
      self.environ.update(buildout[environment_section])
    for variable in self.options.get('environment', '').splitlines():
      if variable.strip():
        try:
          key, value = variable.split('=', 1)
          self.environ[key.strip()] = value
        except ValueError:
          raise zc.buildout.UserError('Invalid environment variable definition: %s', variable)
    # Extrapolate the environment variables using values from the current
    # environment.
    for key in self.environ:
      self.environ[key] = self.environ[key] % os.environ

  def install(self):
    if self.shared:
      self.logger.info('Checking whether package is installed at shared path : %s', self.destination)
      if self._signature.test(self.destination):
        self.logger.info('This shared package has been installed by other package')
        return []
    if self.parts is not None:
      if not os.path.isdir(self.parts):
        os.mkdir(self.parts)

    download = zc.buildout.download.Download(self.buildout['buildout'],
        hash_name=True, cache=self.buildout['buildout'].get('download-cache'))
    extract_dir = tempfile.mkdtemp(self.name)
    try:
      self.logger.debug('Created working directory %r', extract_dir)
      path, is_temp = download(self.options['url'],
          md5sum=self.options.get('md5sum'))
      try:
        patch_archive_util()
        # ad-hoc support for .xz and .lz archive
        hdr = open(path, 'rb').read(6)
        for magic, cmd in ((b'\xfd7zXZ\x00', ('xzcat',)),
                           (b'LZIP', ('lunzip', '-c'))):
          if hdr.startswith(magic):
            new_path = os.path.join(extract_dir, os.path.basename(path))
            with open(new_path, 'wb') as stdout:
              subprocess.check_call(cmd + (path,),
                stdout=stdout, env=self.environ)
            setuptools.archive_util.unpack_archive(new_path, extract_dir)
            os.unlink(new_path)
            break
        else:
          setuptools.archive_util.unpack_archive(path, extract_dir)
      finally:
        unpatch_archive_util()
        if is_temp:
          os.unlink(path)

      if os.path.exists(self.destination):
        shutil.rmtree(self.destination)
      os.makedirs(self.destination)

      strip = self.options.get('strip-top-level-dir')
      if strip:
        if is_true(strip.lower()):
          base_dir, = os.listdir(extract_dir)
          base_dir = os.path.join(extract_dir, base_dir)
        else:
          base_dir = extract_dir
      else:
        directories = os.listdir(extract_dir)
        if len(directories) == 1:
          base_dir = os.path.join(extract_dir, directories[0])
          if not os.path.isdir(base_dir):
            base_dir = extract_dir
      base_dir = os.path.join(base_dir, self.options['extract-directory'])
      for filename in os.listdir(base_dir):
        shutil.move(os.path.join(base_dir, filename), self.destination)
    finally:
      shutil.rmtree(extract_dir)
    self.logger.debug('Downloaded %r and saved to %r.',
      self.options['url'], self.destination)

    if self.shared:
      self._signature.save(self.parts)
      make_read_only_recursively(self.parts)
      return []
    if self.parts is not None:
      return [self.parts]
    else:
      return []
  
  def update(self):
    pass

# Monkey patch to keep symlinks in tarfile
def unpack_tarfile_patched(filename, extract_dir, progress_filter=setuptools.archive_util.default_filter):
    """Unpack tar/tar.gz/tar.bz2 `filename` to `extract_dir`

    Raises ``UnrecognizedFormat`` if `filename` is not a tarfile (as determined
    by ``tarfile.open()``).  See ``unpack_archive()`` for an explanation
    of the `progress_filter` argument.
    """
    try:
        tarobj = tarfile.open(filename)
    except tarfile.TarError:
        raise setuptools.archive_util.UnrecognizedFormat(
            "%s is not a compressed or uncompressed tar file" % (filename,)
        )
    with setuptools.archive_util.contextlib.closing(tarobj):
        # don't do any chowning!
        tarobj.chown = lambda *args: None
        for member in tarobj:
            name = member.name
            # don't extract absolute paths or ones with .. in them
            if not name.startswith('/') and '..' not in name.split('/'):
                prelim_dst = os.path.join(extract_dir, *name.split('/'))

                if member is not None and (member.isfile() or member.isdir() or member.islnk() or member.issym()):
                    # Prepare the link target for makelink().
                    if member.islnk():
                        member._link_target = os.path.join(extract_dir, member.linkname)
                    final_dst = progress_filter(name, prelim_dst)
                    if final_dst:
                        if final_dst.endswith(os.sep):
                            final_dst = final_dst[:-1]
                        try:
                            # XXX Ugh
                            tarobj._extract_member(member, final_dst)
                        except tarfile.ExtractError:
                            # chown/chmod/mkfifo/mknode/makedev failed
                            pass
        return True

def patch_archive_util():
  setuptools.archive_util.extraction_drivers = (
    setuptools.archive_util.unpack_directory,
    setuptools.archive_util.unpack_zipfile,
    unpack_tarfile_patched,
  )

def unpatch_archive_util():
  setuptools.archive_util.extraction_drivers = (
    setuptools.archive_util.unpack_directory,
    setuptools.archive_util.unpack_zipfile,
    setuptools.archive_util.unpack_tarfile,
  )

_read_only_mask = 0o777 ^ (stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
def make_read_only(path):
  os.chmod(path, os.stat(path).st_mode & _read_only_mask)

def make_read_only_recursively(path):
  make_read_only(path)
  for root, dir_list, file_list in os.walk(path):
    for dir in dir_list:
      make_read_only(os.path.join(root, dir))
    for file_ in file_list:
      make_read_only(os.path.join(root, file_))

class Signature:

  def __init__(self, filename):
    self.filename = filename
    self.item_list = []

  def update(self, key, value):
    self.item_list.append(('%r: %r' % (key, value)).encode())

  def hexdigest(self): # -> str
    m = md5()
    for item in self.item_list:
      m.update(item)
    return m.hexdigest()

  def dumps(self):
    return b'\n'.join(self.item_list)

  def test(self, folder_path):
    assert type(folder_path) is str, folder_path
    digest = self.hexdigest()
    if os.path.basename(folder_path) == digest:
      target_path = os.path.join(folder_path, self.filename)
      if os.path.exists(target_path) and open(target_path, 'rb').read() == self.dumps():
        return True
    return False

  def save(self, folder_path):
    with open(os.path.join(folder_path, self.filename), 'wb') as f:
      f.write(self.dumps())
