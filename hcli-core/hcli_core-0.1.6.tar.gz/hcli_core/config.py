from __future__ import absolute_import, division, print_function

import sys
import os
import importlib
import inspect

root = os.path.dirname(inspect.getfile(lambda: None))
sample = root + "/sample"
hcli_core_manpage_path = root + "/data/hcli_core.1"
template = None
plugin_path = root + "/cli"
cli = None

""" We parse the HCLI json template to load the HCLI navigation in memory """
def parse_template(t):
    global template
    template = t

""" we setup dynamic loading of the cli module to allow for independent development and loading, independent of hcli_core development """
def set_plugin_path(p):
    global plugin_path
    global cli
    if p is not None:
        plugin_path = p
  
    sys.path.insert(0, plugin_path)
    cli = importlib.import_module("cli", plugin_path)
