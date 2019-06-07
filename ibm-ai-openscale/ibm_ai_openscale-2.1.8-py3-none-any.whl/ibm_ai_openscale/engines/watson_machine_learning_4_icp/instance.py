# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.instances import AIInstance
from ibm_ai_openscale.engines.watson_machine_learning.consts import WMLConsts


class WatsonMachineLearningInstance4ICP(AIInstance):
    """
    Describes ICP Watson Machine Learning instance.
    """
    def __init__(self):
        AIInstance.__init__(self, '999', {}, WMLConsts.SERVICE_TYPE)