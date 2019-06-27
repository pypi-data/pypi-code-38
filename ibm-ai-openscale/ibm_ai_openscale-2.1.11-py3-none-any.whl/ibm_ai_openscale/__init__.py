# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""Package skeleton

.. moduleauthor:: Wojciech Sobala <wojciech.sobala@pl.ibm.com>
"""

from .utils import version
from .client import APIClient
from .client_4_icp import APIClient4ICP
from .supporting_classes import *
from .engines import *

if sys.version_info[0] == 2:
    import logging
    logger = logging.getLogger('ibm_ai_openscale_initialization')
    logger.warning("Python 2 is not supported.")
