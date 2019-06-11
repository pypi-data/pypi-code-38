# -*- coding: utf-8 -*-
__import__('pkg_resources').declare_namespace(__name__)

try:
    from .sdk import *
except ImportError:
    pass
