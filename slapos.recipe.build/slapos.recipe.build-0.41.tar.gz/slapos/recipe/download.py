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
import errno
import os
import shutil
import zc.buildout
import logging
from hashlib import md5
from .downloadunpacked import make_read_only_recursively, Signature

class Recipe(object):
  _parts = None

  def __init__(self, buildout, name, options):
    buildout_section = buildout['buildout']
    self._downloader = zc.buildout.download.Download(buildout_section,
      hash_name=True)
    self._url = options['url']
    self._md5sum = options.get('md5sum')
    self._name = name
    mode = options.get('mode')
    log = logging.getLogger(name)
    self._shared = shared = ((options.get('shared', '').lower() == 'true') and
                             buildout['buildout'].get('shared-parts', None))
    if mode is not None:
      mode = int(mode, 8)
    self._mode = mode
    if 'filename' in options and 'destination' in options:
      raise zc.buildout.UserError('Parameters filename and destination are '
        'exclusive.')

    destination = options.get('destination', None)
    if destination is None:
      if shared:
        shared_part = buildout['buildout'].get('shared-parts', None)
        shared = os.path.join(shared_part.strip().rstrip('/'), name)
        if not os.path.exists(shared):
          os.makedirs(shared)
        self._signature = Signature('.slapos.recipe.build.signature')
        profile_base_location = options.get('_profile_base_location_', '')
        for k, v in sorted(options.items()):
          if profile_base_location:
            v = v.replace(profile_base_location, '${:_profile_base_location_}')
          self._signature.update(k, v)
        shared = os.path.join(shared, self._signature.hexdigest())
        self._parts = parts = shared
        log.info('shared directory  %s set for %s', shared, name)
      else:
        self._parts = parts = os.path.join(buildout_section['parts-directory'],
          name)

      destination = os.path.join(parts, options.get('filename', name))
      # Compatibility with other recipes: expose location
      options['location'] = parts
    options['target'] = self._destination = destination

  def install(self):
    destination = self._destination
    result = [destination]
    parts = self._parts
    log = logging.getLogger(self._name)
    if self._shared:
      log.info('Checking whether package is installed at shared path: %s', destination)
      if self._signature.test(self._parts):
        log.info('This shared package has been installed by other package')
        return []

    if parts is not None and not os.path.isdir(parts):
      os.mkdir(parts)
      result.append(parts)
    path, is_temp = self._downloader(self._url, md5sum=self._md5sum)
    with open(path, 'rb') as fsrc:
      if is_temp:
        os.remove(path)
      try:
        os.remove(destination)
      except OSError as e:
        if e.errno != errno.ENOENT:
          raise
      with open(destination, 'wb') as fdst:
        if self._mode is not None:
          os.fchmod(fdst.fileno(), self._mode)
        shutil.copyfileobj(fsrc, fdst)

    if self._shared:
      self._signature.save(parts)
      make_read_only_recursively(self._parts)
    return result

  def update(self):
    if not self._md5sum:
      self.install()
