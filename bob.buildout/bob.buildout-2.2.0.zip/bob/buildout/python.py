#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds a custom python script interpreter
"""

import os
import sys
import time

from . import tools
from .script import Recipe as Script

class Recipe(Script):
  """Just creates a python interpreter with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    # Preprocess some variables
    self.interpreter = options.setdefault('interpreter', 'python')

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

    # Python interpreter script template
    self.template = """#!%(interpreter)s
# Automatically generated on %(date)s

'''Booting interpreter - starts a new one with a proper environment'''

import os

# builds a new path taking into considerating the user settings
path = os.environ.get("PYTHONPATH", "") + os.pathsep + "%(paths)s"
os.environ['PYTHONPATH'] = path.lstrip(os.pathsep) #in case PYTHONPATH is empty

# re-writes a startup file for Python respecting user settings
user_profile = os.environ.get("PYTHONSTARTUP", None)
if user_profile and os.path.exists(user_profile):
  with open(user_profile, 'r') as f: user_profile_contents = f.read()
else:
  user_profile_contents = ''

def encode(s):
  import sys
  if sys.version_info[0] >= 3:
    return s.encode('UTF-8')
  else:
    return s

import tempfile
profile = tempfile.NamedTemporaryFile()
if user_profile_contents:
  profile.write(encode('\\n\\n'))
  profile.write(encode(user_profile_contents))
  profile.write(encode('\\n'))
profile.write(encode('import pkg_resources #fixes namespace import\\n\\nimport os\\nos.unlink("%%s")\\n' %% profile.name))
if user_profile:
  profile.write(encode('os.environ["PYTHONSTARTUP"] = "%%s"\\n' %% user_profile))
profile.flush() #makes sure contents are written to the temp file

# overwrites PYTHONSTARTUP for the following process bootstrap
os.environ['PYTHONSTARTUP'] = profile.name
#print("Set temporary profile name to `%%s'" %% (profile.name,))

# this will start a new Python process, that will erase the temp profile
import sys
os.execvp("%(interpreter)s", ["%(interpreter)s"] + sys.argv[1:])
"""

  def set_template(self, template):
    self.template = template

  def install_on_wrapped_env(self):
    eggs, ws = self.working_set()
    retval = os.path.join(self.buildout['buildout']['bin-directory'],
        self.interpreter)
    self._write_executable_file(retval, self.template % {
      'date': time.asctime(),
      'paths': os.pathsep.join(tools.get_pythonpath(ws, self.buildout['buildout'], self.prefixes)),
      'interpreter': sys.executable,
      })
    self.logger.info("Generated script '%s'." % retval)
    return (retval,)

  def _write_executable_file(self, name, content):
    f = open(name, 'w')
    current_umask = os.umask(0o022) # give a dummy umask
    os.umask(current_umask)
    perms = 0o777 - current_umask
    try:
      f.write(content)
    finally:
      f.close()
      os.chmod(name, perms)
