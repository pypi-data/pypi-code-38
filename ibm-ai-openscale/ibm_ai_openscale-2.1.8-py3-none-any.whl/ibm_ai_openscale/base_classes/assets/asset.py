# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_ai_openscale.utils import logging_class

@logging_class
class Asset:
    def __init__(self, binding_uid=None, input_data_type='structured'):
        self.binding_uid = binding_uid
        self.input_data_type = input_data_type
