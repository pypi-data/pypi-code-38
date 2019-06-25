__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"


class RpNotRunningError(Exception):
    """ Raise when RP/LC are not in running state after doing a show controller dpc rm dpa """ 
    pass
