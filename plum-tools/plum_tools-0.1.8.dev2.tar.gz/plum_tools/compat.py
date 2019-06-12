# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: compat
#         Desc: 兼容Python2/Python3
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 20:16
#=============================================================================
"""

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    exec("""def implements_to_unicode(cls):
        if isinstance(cls, unicode):
            return cls

        if isinstance(cls, str):
            cls = cls.decode('utf-8')
        else:
            cls = implements_to_unicode("%s" % cls)
        return cls""")

else:
    def implements_to_unicode(cls):
        """转换编码为unicode
        """
        return "%s" % cls
