#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed  7 Feb 12:02:22 2018 CET

"""Builds a custom python script interpreter that is executed inside gdb/lldb
"""

import platform
from .python import Recipe as Script

# Python interpreter script template
class Recipe(Script):
  """Just creates a gdb/lldb executable running a python interpreter with the
  "correct" paths
  """

  def __init__(self, buildout, name, options):

    if platform.system() != 'Darwin':
      self.interpreter = options.setdefault('interpreter', 'gdb-python')
    else:
      self.interpreter = options.setdefault('interpreter', 'lldb-python')

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

    if platform.system() != 'Darwin':
      self.set_template("""#!%(interpreter)s
# %(date)s

'''Dummy program - only starts a new one with a proper environment'''

import os

existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = "%(paths)s" + os.pathsep + existing
os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"].strip(os.pathsep)

import sys
if sys.argv[1] in ('-?', '-h', '--help'):
  os.execvp('gdb', sys.argv)
else:
  args = [sys.argv[0], 'gdb', '--args', "%(interpreter)s"] + sys.argv[1:]
  os.execvp('gdb', args)
""")
    else:
      self.set_template("""#!%(interpreter)s
# %(date)s

'''Dummy program - only starts a new one with a proper environment'''

import os

existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = "%(paths)s" + os.pathsep + existing
os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"].strip(os.pathsep)

import sys
if sys.argv[1] in ('-?', '-h', '--help'):
  os.execvp('lldb', sys.argv)
else:
  args = [sys.argv[0], 'lldb', '--', "%(interpreter)s"] + sys.argv[1:]
  os.execvp('lldb', args)
""")
