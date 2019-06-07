# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
import datetime
import uuid


class PayloadRecord:
    """
    Used during payload logging, describes payload record.

    :param request: scoring request
    :type request: dict

    :param response: scoring response
    :type response: dict

    :param scoring_id: scoring identifier (optional). If not provided random uid is assigned.
    :type scoring_id: str

    :param scoring_timestamp: scoring request timestamp (optional). If not provided current time is assigned.
    :type scoring_timestamp: str

    :param response_time: scoring response time in ms (optional)
    :type response: int
    """

    def __init__(self, request, response, scoring_id=None, scoring_timestamp=None, response_time=None):
        validate_type(request, "request", dict, True)
        validate_type(response, "response", dict, True)
        validate_type(scoring_id, "scoring_id", str, False)
        validate_type(scoring_timestamp, "scoring_timestamp", str, False)
        validate_type(response_time, "response_time", int, False)

        self.request = request
        self.response = response
        self.scoring_id = scoring_id
        self.scoring_timestamp = scoring_timestamp
        self.response_time = response_time

    def _to_json(self, binding_uid, subscription_uid, deployment_uid):
        record = {
            "binding_id": binding_uid,
            "subscription_id": subscription_uid,
            "deployment_id": deployment_uid,
            'request': self.request,
            'response': self.response
        }

        if self.scoring_timestamp is not None:
            record['scoring_timestamp'] = self.scoring_timestamp
        else:
            record['scoring_timestamp'] = str(datetime.datetime.utcnow().isoformat()) + 'Z'

        if self.scoring_id is not None:
            record['scoring_id'] = self.scoring_id
        else:
            record['scoring_id'] = str(uuid.uuid4())

        if self.response_time is not None:
            record['response_time'] = int(self.response_time)

        return record
