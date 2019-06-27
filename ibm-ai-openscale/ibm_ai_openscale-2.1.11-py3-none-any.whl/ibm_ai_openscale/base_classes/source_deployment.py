# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class SourceDeployment:
    def __init__(self, guid, url, name, deployment_type, created, scoring_endpoint=None, rn=None):
        self.guid = guid
        self.url = url
        self.name = name
        self.deployment_type = deployment_type
        self.created = created
        self.scoring_endpoint = scoring_endpoint
        self.rn = rn

    def _to_json(self):
        return {
            "deployment_id": self.guid,
            "url": self.url,
            "name": self.name,
            "deployment_type": self.deployment_type,
            "created_at": self.created,
            'scoring_endpoint': self.scoring_endpoint if self.scoring_endpoint is not None else {},
            "deployment_rn": self.rn if self.rn is not None else ''
        }
