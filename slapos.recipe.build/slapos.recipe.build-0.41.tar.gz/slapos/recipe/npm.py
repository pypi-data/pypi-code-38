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
import logging
import os
import subprocess
import zc.buildout

def createExecutable(name, content, mode=0o755):
  """Create an executable with content

  The parent directory should exists, else it would raise IOError"""
  with open(name, 'w') as fileobject:
    fileobject.write(content)
    os.chmod(fileobject.name, mode)
  return os.path.abspath(name)

def createWrapper(node, package):
  """Creates a node package wrapper"""

class Npm(object):
  """Download and install locally node packages from node.js' NPM"""

  def __init__(self, buildout, name, options):
    self.cleanup_dir_list = []
    self.buildout = buildout
    self.name = name
    self.logger = logging.getLogger(self.name)
    self.options = {}

    # Check for mandatory fields
    if not options.get('packages'):
       raise zc.buildout.UserError('No package specified in \'packages\' '
           'parameter')

    # Get variables
    for k in ['location', 'packages', 'environment-section', 'node',
        'environment']:
      self.options[k] = options.get(k, '').strip()

    # Expose ${:location}
    if self.options['location'] == '':
      self.options['location'] = options['location'] = os.path.join(
          buildout['buildout']['parts-directory'], self.name)

    # Get npm and node binaries. Mimic zc.recipe.egg behavior.
    node = self.options.get('node')
    if node:
      _node_executable = buildout[node].get('node_executable',
          os.path.join(buildout[node]['location'], 'bin', 'node'))
      _npm_executable = buildout[node].get('npm_executable',
          os.path.join(buildout[node]['location'], 'bin', 'npm'))
      self.popen_arguments = [_node_executable, _npm_executable, 'install']
    else:
      self.logger.warn('Using system node.')
      self.popen_arguments = ['npm', 'install']

    # Get list of packages to install
    self.package_list = [
        "%s" % s.strip()
        for r in self.options['packages'].splitlines()
        for s in r.split(' ')
        if r.strip()]
    self.popen_arguments.extend(self.package_list)

  def install(self):
    # Create part directory
    location = self.options.get('location')
    if not os.path.isdir(location):
      os.makedirs(location)
    os.chdir(location)

    environ = {}
    # Set minimal working environment
    environ['PATH'] = os.environ['PATH']
    # Set NPM envvar to not share cache
    environ['NPM_CONFIG_CACHE'] = os.path.join(location, 'cache')
    # Arbitrary put packages installation to node_module directory
    environ['NODE_PATH'] = os.path.join(location, 'node_modules')
    # Override HOME so that npm won't create ~/.npm directory
    environ['HOME'] = location

    # Apply variables from defined environment (code from h.r.cmmi)
    environment_section = self.options['environment-section']
    if environment_section and environment_section in self.buildout:
      # Use environment variables from the designated config section.
      environ.update(self.buildout[environment_section])
    for variable in self.options.get('environment', '').splitlines():
      if variable.strip():
        try:
          key, value = variable.split('=', 1)
          environ[key.strip()] = value
        except ValueError:
          raise zc.buildout.UserError('Invalid environment variable '
              'definition: %s', variable)
    # Extrapolate the environment variables using values from the current
    # environment.
    for key in environ:
      environ[key] = environ[key] % os.environ

    # Install packages
    npm_process = subprocess.Popen(self.popen_arguments, env=environ)
    npm_process.communicate()

    if npm_process.returncode is not 0:
      raise zc.buildout.UserError('Failed to install npm module(s).')

    # Create wrappers
    #for package in self.package_list:
    #  createExecutable()
    #  NODE_PATH=${:destination}/node_modules ${nodejs:node_location} ${:cloud9_js_location}
    
    return [self.options['location']]

  def update(self):
    return None
