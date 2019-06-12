from flask import request

class Helpers:

    def get_gateway_info(self):
        data = {}
        data["account_id"] = request.headers.get("X-Consumer-Id", None)
        data["username"] = request.headers.get("X-Credential-Username", None)
        data["consumername"] = request.headers.get("X-Consumer-Username", None)
        data["consumergroups"] = request.headers.get("X-Consumer-Groups", None)


        return data



