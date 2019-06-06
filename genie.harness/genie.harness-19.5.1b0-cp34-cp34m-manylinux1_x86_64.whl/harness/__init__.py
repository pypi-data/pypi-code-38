

'''
Module:
    genie

Description:
    This module defines the base classes required to write testscripts. It's
    name is a direct carry over from Tcl-ATS's AEtest package.

    In short, this module is designed to offer a similar look-and-feel of its
    Tcl counterpart, whilst leveraging and building based on the advanced
    object-oriented capabilities of the Python Language.

    aetest can be broken down as follows:

        - Common Sections
        - Testcases
        - Python ``unittest`` support

    For more detailed explanation and usages, refer to aetest documentation on
    pyATS home page: http://wwwin-pyats.cisco.com/
'''
# metadata
__version__ = '19.5.1b'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2018, Cisco Systems Inc.'

# declare module as infra
__genie_infra__ = True

# user's short-cut call to infra
from .main import main

# Easypy integration requirements (Main class and AEReporter class)
# Needed for easypy task, for test_harness
from .main import Genie as Main
from ats.aetest import AEReporter


# try to record usage statistics
#  - only internal cisco users will have stats.CesMonitor module
#  - below code does nothing for DevNet users -  we DO NOT track usage stats
#    for PyPI/public/customer users
try:
    # new internal cisco-only pkg since devnet release
    from ats.cisco.stats import CesMonitor
except Exception:
    try:
        # legacy pyats version, stats was inside utils module
        from ats.utils.stats import CesMonitor
    except Exception:
        CesMonitor = None

finally:
    if CesMonitor is not None:
        # CesMonitor exists -> this is an internal cisco user
        CesMonitor(action = __name__, application='Genie').post()
        CesMonitor(action = __name__, application='pyATS Packages').post()
