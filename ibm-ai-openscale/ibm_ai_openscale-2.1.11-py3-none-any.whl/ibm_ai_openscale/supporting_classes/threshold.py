# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *


class Threshold:
    """
    Used during custom monitor registration and configuration, describes threshold passed to custom monitor.

    :param metric_uid: metric uid
    :type metric_uid: str
    :param lower_limit: lower control limit default value (optional)
    :type lower_limit: float
    :param upper_limit: upper control limit default value (optional)
    :type upper_limit: float
    """

    def __init__(self, metric_uid, lower_limit=None, upper_limit=None):
        validate_type(metric_uid, 'metric_uid', str, True)
        validate_type(lower_limit, 'lower_limit', float, False)
        validate_type(upper_limit, 'upper_limit', float, False)

        self.metric_uid = metric_uid
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def _to_json(self):
        thresholds = []

        if self.lower_limit is not None:
            thresholds.append({"metric_id": self.metric_uid, "type": "lower_limit", "value": self.lower_limit})

        if self.upper_limit is not None:
            thresholds.append({"metric_id": self.metric_uid, "type": "upper_limit", "value": self.upper_limit})

        return thresholds
