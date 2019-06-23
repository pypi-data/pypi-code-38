# -*- coding: utf-8 -*-
__import__('pkg_resources').declare_namespace(__name__)

try:
    from missinglink.sdk import *
except ImportError:
    pass
