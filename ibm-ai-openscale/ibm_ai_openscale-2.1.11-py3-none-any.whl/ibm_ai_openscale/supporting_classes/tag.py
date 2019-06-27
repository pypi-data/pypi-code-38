# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *


class Tag:
    """
    Used during custom monitor registration, describes tags passed with metrics to custom monitor.

    :param name: name of the tag
    :type name: str
    :param description: description of the tag (optional)
    :type description: str
    :param required: is this tag obligatory? (default value True)
    :type required: bool
    """

    def __init__(self, name, description=None, required=True):
        validate_type(name, 'name', str, True)
        validate_type(description, 'description', str, False)
        validate_type(required, 'required', bool, False)

        self.name = name
        self.description = description
        self.required = required

    def _to_json(self):

        json_object = {
            'name': self.name,
            'required': self.required
        }

        if self.description is not None:
            json_object['description'] = self.description

        return json_object
