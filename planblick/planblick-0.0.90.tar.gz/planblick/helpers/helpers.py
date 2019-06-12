from flask import request

class Helpers:

    def get_gateway_info(self):
        data = {}
        data["account_id"] = request.headers.get("X-Consumer-Id", None)
        data["username"] = request.headers.get("X-Credential-Username", None)
        data["consumername"] = request.headers.get("X-Consumer-Username", None)
        data["consumer_groups"] = request.headers.get("X-Consumer-Groups", None)
        data["consumer_id"] = request.headers.get("X-Consumer-ID", None)
        data["consumer_custom_id"] = request.headers.get("X-Consumer-Custom-ID", None)
        data["correlation_id"] = request.headers.get("X-Correlation-ID", None)



        return data



