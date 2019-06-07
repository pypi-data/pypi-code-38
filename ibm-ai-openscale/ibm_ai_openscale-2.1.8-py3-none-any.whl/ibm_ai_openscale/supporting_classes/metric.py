# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *


class Metric:
    """
    Used during custom monitor registration, describes metrics passed to custom monitor.

    :param name: name of the metric
    :type name: str
    :param description: description of the metric (optional)
    :type description: str
    :param lower_limit_default: lower control limit default value (optional)
    :type lower_limit_default: float
    :param upper_limit_default: upper control limit default value (optional)
    :type upper_limit_default: float
    :param required: is this metric obligatory? (default value True)
    :type required: bool
    """

    def __init__(self, name, description=None, lower_limit_default=None, upper_limit_default=None, required=True):
        validate_type(name, 'name', str, True)
        validate_type(description, 'description', str, False)
        validate_type(lower_limit_default, 'lower_limit', float, False)
        validate_type(upper_limit_default, 'upper_limit', float, False)
        validate_type(required, 'required', bool, False)

        self.name = name
        self.description = description
        self.lower_limit = lower_limit_default
        self.upper_limit = upper_limit_default
        self.required = required
        self.thresholds = []

        if self.lower_limit is not None:
            self.thresholds.append({"type": "lower_limit", "default": self.lower_limit})

        if self.upper_limit is not None:
            self.thresholds.append({"type": "upper_limit", "default": self.upper_limit})

    def _to_json(self):
        json_object = {
            'name': self.name,
            'required': self.required
        }

        if self.description is not None:
            json_object['description'] = self.description

        if len(self.thresholds) > 0:
            json_object['thresholds'] = self.thresholds

        return json_object
