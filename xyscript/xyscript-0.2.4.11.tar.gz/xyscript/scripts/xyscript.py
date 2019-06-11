"""
Implementation of the command-line I{xyscript} tool.
"""
from __future__ import absolute_import

# For backward compatibility
__all__ = ['pull', 'pullsubmodule', 'initproject', 'package', "pps", 'syn', 'merge','main']
from xyscript.api import pull, pullsubmodule, initproject, pps, package, syn, merge, main