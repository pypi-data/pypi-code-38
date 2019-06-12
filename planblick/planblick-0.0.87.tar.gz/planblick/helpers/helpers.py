from flask import request

class Helpers:

    def get_gateway_info(self):
        data = {}
        data["account_id"] = request.headers.get("X-Consumer-Id", "DEV")
        data["username"] = request.headers.get("X-Credential-Username", "DEV")
        data["consumername"] = request.headers.get("X-Consumer-Username", "DEV")

        return data



