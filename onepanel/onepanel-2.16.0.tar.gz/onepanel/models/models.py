import json

from onepanel.models.api_json import APIJSON

class APIJSONEncoder(json.JSONEncoder):
    """JSONEncoder for uploading items via API"""
    def default(self, obj):
        if isinstance(obj, APIJSON):
            return obj.api_json()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)