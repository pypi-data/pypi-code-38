import random

import requests
import json
import hashlib
import base64
import time
import hmac

import itculate_sdk as itsdk

itsdk.init(api_key="UWnljbEXtApUhy0HHe5c8sE2ruZB9gqF",
           api_secret="03Ytyb-QljxoFzjOLghquDMeNTMQ9olS8t-34SAKNjTdPpuO4hItyRwF3EMNrz64")


class LogicMonitorAPI(object):
    access_id = "dtEts54gj35esaIYRtg6"
    access_key = "=!nS]n3e54N}EFY}SKzg8I9{AtV-8!5BL8A(2C6p"
    company = "feature"
    collector_id = "{}_lm_services".format(company)

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
        url = "http://" + self.company + ".logicmonitor.com/santaba/rest" + resource_path + query_parameters + filter

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

    def get_service_members(self, device_id):
        result = self.call_rest_api(resource_path="/device/devices/{}/memberdevices".format(device_id))
        return result

    def get_services(self):
        """
        :rtype: dict[str, dict]
        """
        filter = "&filter=deviceType:6"
        # filter = "&filter=systemProperties.name:system.collectorid,systemProperties.value:-4"
        items = self.call_rest_api(filter=filter)
        id_to_service = {}
        for item in items:
            device_id = item["id"]
            group_ids = item["hostGroupIds"]
            system_properties = {p["name"]: p["value"] for p in item.get("systemProperties", [])}
            custom_properties = {p["name"]: p["value"] for p in item.get("customProperties", [])}
            inherited_properties = {p["name"]: p["value"] for p in item.get("inheritedProperties", [])}

            groups = []
            if group_ids in ("1", 1):
                groups = [{"name": "root", "id": 1}]
            else:
                group_names = system_properties["system.groups"].split(",")
                group_ids_list = system_properties["system.deviceGroupId"].split(",")
                for i in range(len(group_ids_list)):
                    groups.append({"name": group_names[i], "id": int(group_ids_list[i])})

            item["resource-url"] = "https://{}.logicmonitor.com/santaba/uiv3/device/index.jsp#tree/-{}-d-{}".format(
                self.company,
                groups[0]["id"],
                device_id,
            )

            item["systemProperties"] = system_properties
            item["customProperties"] = custom_properties
            item["inheritedProperties"] = inherited_properties
            item["groups"] = groups

            members = json.loads(custom_properties.get("predef.bizservice.members", {}))
            custom_properties["predef.bizservice.members"] = members

            id_to_service[device_id] = item
        return id_to_service


if __name__ == '__main__':
    api = LogicMonitorAPI()

    device_id_to_member = {}
    group_id_to_service = {}
    device_id_to_service = api.get_services()
    for id, service in device_id_to_service.items():

        if service.get('hostStatus') == "dead":
            print("skipping dead service {}".format(service["name"]))
            continue

        service_vertex = itsdk.add_vertex(name=service["name"],
                                          vertex_type="LM_Service",
                                          keys="{}.service.id.{}".format(api.company, service["id"]),
                                          collector_id=api.collector_id,
                                          data=service)

        for group in service["groups"]:
            group_id = group["id"]
            if group_id == 1:
                continue

            group_vertex = group_id_to_service.get(group_id)
            if group_vertex is None:
                group_name = group["name"]
                group["resource-url"] = "https://{}.logicmonitor.com/santaba/uiv3/device/index.jsp#tree/-{}". \
                    format(api.company, group_id)
                group_vertex = itsdk.add_vertex(name=group_name,
                                                vertex_type="Group",
                                                keys="{}.group.id.{}".format(api.company, group_id),
                                                collector_id=api.collector_id,
                                                data=group)
                group_id_to_service[group_id] = group_vertex

            itsdk.connect(source=group_vertex,
                          target=service_vertex,
                          collector_id=api.collector_id,
                          topology="group-member")

        members = api.get_service_members(device_id=service["id"])

        total_cost = 0
        for member in members:

            member_id = member["id"]
            if member_id == service_vertex["id"]:
                print("Error Service cand child service are the same {} device-id:{}".format(service_vertex.name,
                                                                                             member_id))
                continue

            child_service = device_id_to_service.get(member_id)
            if child_service:
                itsdk.connect(source=service_vertex,
                              target="{}.service.id.{}".format(api.company, member_id),
                              collector_id=api.collector_id,
                              topology="service")
                continue

            member_vertex = device_id_to_member.get(member_id)
            if member_vertex is None:
                name = member["name"]
                dot_count = name.count(".")
                cost = 54 + 31 * random.randint(1, 4)

                if name.startswith("ip-") and name.endswith(".compute.internal"):
                    vertex_type = "EC2"
                    cost = 71
                elif name.endswith(".com") and dot_count > 1:
                    vertex_type = "WWW"
                    cost = 891
                elif dot_count == 3 and name.replace(".", "").isdigit():
                    vertex_type = "CIDR-IPv4"
                else:
                    vertex_type = "Device"
                member["resource-url"] = "https://{}.logicmonitor.com/santaba/uiv3/device/index.jsp#tree/-1-d-{}". \
                    format(api.company, member_id)

                member["estimated-cost"] = cost
                member_vertex = itsdk.add_vertex(name=name,
                                                 vertex_type=vertex_type,
                                                 keys="{}.id.{}".format(api.company, member_id),
                                                 collector_id=api.collector_id,
                                                 data=member)
                device_id_to_member[member_id] = member_vertex
                total_cost += cost

            itsdk.connect(source=service_vertex,
                          target=member_vertex,
                          collector_id=api.collector_id,
                          topology="{}".format(member_vertex.type.lower()))

        service_vertex["estimated-cost"] = total_cost

itsdk.flush_all()

#
# # Print stajson.loads(response.text)tus and body of response
# print("URL:{}".format(url))
# print("Response Status:{}".format(response.status_code))
# print("Response Body:{}".format(response.content))
#


