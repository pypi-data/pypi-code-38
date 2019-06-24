class LogType:
    name_to_type = {}

    def __init__(self, name, log_type):
        self.log_type = log_type
        self.name = name
        LogType.name_to_type[name] = log_type

    @staticmethod
    def get_type(name):
        return LogType.name_to_type.get(name)


CURRENT_USER = LogType("currentUser", str)
ASSET_NAME = LogType("assetName", str)
ASSET_ID = LogType("assetId", str)
metric = LogType("metric", float)
ORG_ID = LogType("org_id", str)
REQUEST_URL = LogType("requestUrl", str)
REQUEST_ID = LogType("requestId", str)
AGENT_ID = LogType("agentId", str)
RULE = LogType("rule", dict)
WORKSPACE_ID = LogType("workspace", str)
REQUEST_REMOTE_IP = LogType("requestRemoteIp", str)
REQUEST_URI = LogType("requestUri", str)  # Used by tornado
STATUS_CODE = LogType("statusCode", str)
REQUEST_METHOD = LogType("requestMethod", str)
