################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import sys


class PythonVersion(object):
    @staticmethod
    def significant():
        return "{}.{}".format(sys.version_info[0], sys.version_info[1])
