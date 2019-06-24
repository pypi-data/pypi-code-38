import datetime
import requests
from interscity_client.exceptions import *


SHOULD_REGISTER_REMOTELLY = True
SHOULD_NOT_REGISTER_REMOTELLY = False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class connection():
    def __init__(self, protocol="http", kong_host="localhost:8000"):
        self.protocol = protocol
        self.kong_host = kong_host
        self.interscity_health_check()


    def interscity_health_check(self):
        print("Microservices status:")
        microservices = [
            "adaptor", "catalog", "discovery", "collector", "actuator"
        ]
        host = self.protocol + "://" + self.kong_host
        for m in microservices:
            try:
                response = requests.get(host + "/" + m + "/health_check", timeout=2)
                if (response.status_code != 200):
                    raise MicroserviceNotWorking(m, response.text)
                else:
                    print(bcolors.OKGREEN + "{0} is properly working.".format(m))
            except:
                raise MicroserviceNotWorking(m, "Not responding.")


    def capability_available(self, title):
        ENDPOINT = '/catalog/capabilities'
        response = requests.get(self.protocol + "://" + self.kong_host + ENDPOINT)
        capabilities = response.json()["capabilities"]
        if any(capability["name"] == title for capability in capabilities):
            print("{0}Capability {1} exists.".format(bcolors.OKGREEN, title))
            return True
        else:
            print("{0}Capability {1} does not exist.".format(bcolors.FAIL, title))
            return False


    def create_capability(self, title, description, capability_type = "sensor"):
        if (not self.capability_available(title)):
            ENDPOINT = '/catalog/capabilities'
            capability_json = {
                "name": title,
                "description": description,
                "capability_type": capability_type
            }
            response = requests.post(self.protocol + "://" + self.kong_host + ENDPOINT,
                                     json=capability_json)
            if (response.status_code > 300):
                raise Exception("Couldn't create capability {0}".format(title))
            else:
                print("{0}Capability {1} successfully created.".format(bcolors.OKGREEN, title))
                return True
        else:
            print("{0}Capability {1} already exist.".format(bcolors.WARNING, title))
            return False


    def _register_resource(self, resource):
        ENDPOINT = "/catalog/resources"
        response = requests.post(self.protocol + "://" + self.kong_host + ENDPOINT,
                json={"data": resource})
        if (response.status_code > 300):
            print("Couldn't register resource {0}.".format(resource["uniq_key"]))
            print("Reason: {0}".format(response.text))
            return False
        else:
            return response.json()["data"]["uuid"]


    def _send_data(self, uuid, resource):
        ENDPOINT = "/adaptor/components/{0}/data".format(uuid)

        response = requests.post(self.protocol + "://" + self.kong_host + ENDPOINT,
                json={"data": resource})
        if (response.status_code > 300):
            print("Couldn't send resource {0} data.".format(uuid))
            print("Reason: {0}".format(response.text))
        return response


    def _get_data(self, uuid):
        ENDPOINT = "/collector/resources/{0}/data".format(uuid)
        response = requests.post(self.protocol + "://" + self.kong_host + ENDPOINT)
        if (response.status_code > 300):
            return False
        else:
            return response.json()


    def all_resources_uuid(self, capability=None):
        if (capability):
            ENDPOINT = "/discovery/resources?capability="+capability
        else:
            ENDPOINT = "/catalog/resources"
        response = requests.get(self.protocol + "://" + self.kong_host + ENDPOINT)
        resources = response.json()["resources"]
        return list(map(lambda x: x["uuid"], resources))


    def all_resources_description(self, capability=None):
        if (capability):
            ENDPOINT = "/discovery/resources?capability="+capability
        else:
            ENDPOINT = "/catalog/resources"
        response = requests.get(self.protocol + "://" + self.kong_host + ENDPOINT)
        resources = response.json()["resources"]
        return list(map(lambda x: x["description"], resources))


    def find_resource_uuid_using_uniq_id(self, uniq_id, capability=None):
        if (capability):
            ENDPOINT = "/discovery/resources?capability="+capability
        else:
            ENDPOINT = "/catalog/resources"
        response = requests.get(self.protocol + "://" + self.kong_host + ENDPOINT)
        resources = response.json()["resources"]
        for resource in resources:
            if (uniq_id in resource["description"]):
                return resource["uuid"]
        return False


    def find_resource_uuid_using_uniq_id_v2(self, uniq_id, capabilities, uniq_key):
        ENDPOINT = "/collector/resources/data/last"
        response = requests.post(self.protocol + "://" + self.kong_host + ENDPOINT,
                json={"capabilities": capabilities})
        resources = response.json()["resources"]

        possibilities = ["{0}={1}".format(uniq_key, uniq_id)]

        for resource in resources:
            for k, v in resource["capabilities"].items():
                for measure in v:
                    if ("uniq-id" in measure.keys()):
                        for item in v:
                            if (item["uniq-id"] in possibilities):
                                return resource["uuid"]
        return False


class resource_builder():
    def __init__(self, connection, capability, uniq_key):
        self.connection = connection
        self.capability = capability
        self.uniq_key = uniq_key
        self.resources = {}


    def register_locally(self, resource):
        if (resource["uniq_key"] in self.resources.keys()):
            print("Resource {0} already exist locally.".format(resource["uniq_key"]))
            if ("uuid" in self.resources[resource["uniq_key"]].keys()):
                return SHOULD_REGISTER_REMOTELLY
            else:
                print("Resource {0} already exist remotelly.".format(resource["uniq_key"]))
                return SHOULD_NOT_REGISTER_REMOTELLY
        else:
            self.resources[resource["uniq_key"]] = resource
            print("Resource {0} registered locally...".format(resource["uniq_key"]))
            return SHOULD_REGISTER_REMOTELLY


    def register_remotelly(self, resource):
        REQUIRED_ATTRS = ["description", "capabilities", "status", "lat", "lon"]

        for attr in REQUIRED_ATTRS:
            if (not(attr in resource.keys())):
                raise Exception("Missing {0} in resource.".format(attr))

        if type(resource["capabilities"]) != list:
            resource["capabilities"] = [resource["capabilities"]]

        r = self.connection._register_resource(resource)
        if (r != False):
            self.resources[resource["uniq_key"]]["uuid"] = r
            print("Resource {0} successfully registered.".format(resource["uniq_key"]))
        self.send_data(resource["uniq_key"], {})


    def register(self, uniq_key, description, capabilities, lat=-23, lon=-46):
        if (not(self.connection.capability_available(self.capability))):
            raise CapabilityDoesNotExist(self.capability)

        resource = {
            "uniq_key": uniq_key,
            "description": description,
            "capabilities": capabilities,
            "lat": lat,
            "lon": lon,
            "status": "active"
        }
        if (self.register_locally(resource) == SHOULD_REGISTER_REMOTELLY):
            if (not self.exist_remotelly(uniq_key, capabilities)):
                self.register_remotelly(resource)
            else:
                print("Resource {0} exist remotelly.".format(uniq_key))
                resource = self.connection.find_resource_uuid_using_uniq_id_v2(uniq_key, capabilities, self.uniq_key)
                if (resource != False):
                    print("Resource found! UUID: {0}".format(resource))


    def send_data(self, uniq_id, measure):
        if (not uniq_id in self.resources.keys()):
            print("Resource {0} not registered.".format(uniq_id))
            raise ResourceDoesNotExistLocally(uniq_id)
        else:
            if (not "uuid" in self.resources[uniq_id].keys()):
                uuid = self.connection.find_resource_uuid_using_uniq_id_v2(uniq_id, [self.capability], self.uniq_key)
                if (uuid == False):
                    print("Resource {0} not registered remotelly.".format(uniq_id))
                    raise ResourceDoesNotExistRemotelly(uniq_id)
                else:
                    self.resources[uniq_id]["uuid"] = uuid
            resource = {}

            if not "date" in measure.keys():
                measure["date"] = str(datetime.datetime.now())
            resource[self.capability] = [measure]
            resource[self.capability][0]["uniq-id"] = "{0}={1}".format(self.uniq_key, uniq_id)
            response = self.connection._send_data(self.resources[uniq_id]["uuid"], resource)
            if (response.status_code != 201):
                print("{0}Could not send data for resource {1}".format(bcolors.FAIL, uuid))
                return False
            else:
                print("{0}Data sent for resource.".format(bcolors.OKGREEN))
                return True


    def exist_remotelly(self, uniq_key, capabilities):
        return self.connection.find_resource_uuid_using_uniq_id_v2(uniq_key, capabilities, self.uniq_key) != False


    def get_data(self, uniq_key):
        if (uniq_key not in self.resources.keys()):
            raise ResourceDoesNotExistLocally(uniq_key)
        else:
            if ("uuid" not in self.resources[uniq_key].keys()):
                uuid = self.connection.find_resource_uuid_using_uniq_id(uniq_key)
                if (uuid == False):
                    raise ResourceDoesNotExistRemotelly(uniq_key)
                else:
                    self.resources[uniq_key]["uuid"] = uuid
        return self.connection._get_data(self.resources[uniq_key]["uuid"])
