import requests
import hashlib
import base64
import time
import hmac


class LogicMonitorAPI(object):

    def __init__(self, access_id, access_key, company):
        super(LogicMonitorAPI, self).__init__()
        self.access_id = access_id
        self.access_key = access_key
        self.company = company

    def get_devices(self, resource_path="/device/devices", query_parameters="?v=2", filter=""):
        """
        :rtype: list[dict]
        """
        http_verb = "GET"
        data = ""

        filter = "&" + filter if filter and filter[0] != "&" else filter

        # Construct URL
        url = "https://" + self.company + ".logicmonitor.com/santaba/rest" + resource_path + query_parameters + filter

        # Get current time in milliseconds
        epoch = str(int(time.time() * 1000))

        # Concatenate Request details
        requestVars = http_verb + epoch + data + resource_path

        # Construct signature
        signature = base64.b64encode(hmac.new(self.access_key, msg=requestVars, digestmod=hashlib.sha256).hexdigest())

        # Construct headers
        auth = "LMv1 " + self.access_id + ":" + signature + ":" + epoch
        headers = {"Content-Type": "application/json", "Authorization": auth}

        # Make request
        print(url)
        response = requests.get(url, data=data, headers=headers)
        if response.status_code > 300:
            print("Failed to call url, error code:{}, reason {}".format(response.status_code, response.reason))
            return []

        return response.json()["items"]


if __name__ == '__main__':
    api = LogicMonitorAPI(access_id="pQq3HjKQV2v4L2e9zXHA",
                          access_key="Ggc_n}WTb2=K(q!2%56HZZH5GAtPEBBaW762+_dQ",
                          company="itculate")

    # https://www.logicmonitor.com/support/rest-api-developers-guide/v1/data/get-data/

    items = api.get_devices(query_parameters="?v=2&size=500")
    for item in items:
        print(item["name"])

    items = api.get_devices(query_parameters="?v=2&size=500", filter="fields=name,systemProperties")
    for item in items:
        system_properties = {sp["name"]: sp["value"] for sp in item.get("systemProperties", [])}
        print("{} : {}".format(item["name"], system_properties.get("system.cloud.category")))
