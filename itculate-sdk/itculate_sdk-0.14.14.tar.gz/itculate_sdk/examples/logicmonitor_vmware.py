import random

import requests
import json
import hashlib
import base64
import time
import hmac

import itculate_sdk as itsdk

itsdk.init(api_key="b8NgSwETBuaFR30L3a8JP0F5NwJ55Ale",
           api_secret="zVZYK-w-UEP_aqFUSN7AWvsEFmYffnbaT_sHRcSamit73pZVJWy0eS2lrny6sC7c")


class LogicMonitorAPI(object):
    access_id = "DT9Qu3tKQ7jD9JFX9HV5"
    access_key = "d8}[x43K(a}{F^]-T%nz8PE6--c){-S}4}av2^48"
    company = "itculate"
    collector_id = "{}_vmware".format(company)

    def call_rest_api(self,
                      resource_path="/device/devices",
                      query_parameters="?v=2",
                      filter=""):
        """
        :rtype: list[dict]
        """
        http_verb = "GET"
        data = ""

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

    def build_topology(self, virtual_center_id=85, data_source_id=2746):
        """
        :rtype: dict[str, dict]
        """
        resource_path = "/device/devices/{}/devicedatasources/{}/instances".format(
            virtual_center_id,
            data_source_id)

        items = self.call_rest_api(resource_path=resource_path,
                                   query_parameters="?v=2&size=500",
                                   filter="")  # &fields=systemProperties,autoProperties")

        for item in items:
            system_properties = {p["name"]: p["value"] for p in item.get("systemProperties", [])}
            auto_properties = {p["name"]: p["value"] for p in item.get("autoProperties", [])}

            instance_id = system_properties["system.instanceId"]
            instance_name = auto_properties["auto.map.name"]
            instance_type = auto_properties["auto.map.type"]
            instance_key = auto_properties["auto.map.id"]
            datastore_ids = auto_properties.get("auto.map.datastore.ids")
            vm_ids = auto_properties.get("auto.map.vm.ids")
            instance_key = self.create_id_key(instance_key)

            data = {
                "estimated-cost": 988 if instance_type == "HostSystem" else random.randint(45, 100),
                "system-properties": system_properties,
                "auto-properties": auto_properties,
                "resource-url": "https://{}.logicmonitor.com/santaba/uiv3/device/index.jsp#tree/{}-i-{}".format(
                    self.company,
                    -1,
                    instance_id,
                )
            }

            if instance_type == "HostSystem":
                instance_type = "VMware_ESX"
                if vm_ids:
                    for vm_id in vm_ids.split(","):
                        itsdk.connect(source=instance_key,
                                      target=self.create_id_key(id=vm_id.strip()),
                                      collector_id=api.collector_id,
                                      topology="compute")

            elif instance_type == "Datastore":
                instance_type = "VMware_Datastore"

            elif instance_type == "VirtualMachine":
                instance_type = "VMware_VM"

            elif instance_type == "VirtualDisk":
                instance_type = "VMware_VMDK"
                if vm_ids:
                    for vm_id in vm_ids.split(","):
                        itsdk.connect(source=self.create_id_key(id=vm_id.strip()),
                                      target=instance_key,
                                      collector_id=api.collector_id,
                                      topology="storage")
                if datastore_ids:
                    for datastore_id in datastore_ids.split(","):
                        itsdk.connect(source=instance_key,
                                      target=self.create_id_key(id=datastore_id.strip()),
                                      collector_id=api.collector_id,
                                      topology="storage")

            vertex = itsdk.add_vertex(name=instance_name,
                                      vertex_type=instance_type,
                                      keys=instance_key,
                                      collector_id=api.collector_id,
                                      data=data)

    def create_id_key(self, id):
        return "{}.id.{}".format(api.company, id)


if __name__ == '__main__':
    api = LogicMonitorAPI()

    device_id_to_member = {}
    group_id_to_service = {}
    api.build_topology()

itsdk.flush_all()

#
# # Print stajson.loads(response.text)tus and body of response
# print("URL:{}".format(url))
# print("Response Status:{}".format(response.status_code))
# print("Response Body:{}".format(response.content))
#



