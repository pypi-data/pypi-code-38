# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *


class Feature:
    """
    Used during setting fairness monitoring, describes features passed to fairness monitoring.

    :param name: name of feature
    :type name: str
    :param majority: range of feature values for majorities
    :type majority: list of list of ints
    :param minority: range of feature values for minorities
    :type minority: list of list of ints
    :param threshold: threshold
    :type threshold: float
    """
    def __init__(self, name, majority, minority, threshold):
        validate_type(name, 'name', str, True)
        validate_type(majority, 'majority', list, True)
        validate_type(minority, 'minority', list, True)
        validate_type(threshold, 'threshold', float, True)

        self.name = name
        self.majority = majority
        self.minority = minority
        self.threshold = threshold

    def _to_json(self):
        return {
            'feature': self.name,
            'majority': self.majority,
            'minority': self.minority,
            'threshold': self.threshold
        }
