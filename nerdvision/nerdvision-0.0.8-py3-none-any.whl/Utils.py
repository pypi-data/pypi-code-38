import sys


class Utils(object):

    @staticmethod
    def is_python_3():
        return sys.version_info[0] == 3
