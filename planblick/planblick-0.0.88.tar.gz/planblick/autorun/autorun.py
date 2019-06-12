import requests
import json
import os


class Autorun:

    def __init__(self):
        self.ENVIRONMENT = json.loads(os.getenv("CLUSTER_CONFIG")).get("environment")
        self.kong_api = json.loads(os.getenv("CLUSTER_CONFIG")).get("kong-admin-url")
        print("Detected environment:", self.ENVIRONMENT)
        print("Using " + str(self.kong_api) + "as api-gateway")

    def post_deployment(self):
        ENVIRONMENT = json.loads(os.getenv("CLUSTER_CONFIG")).get("environment")
        KONG_ADMIN = json.loads(os.getenv("CLUSTER_CONFIG")).get("kong-admin-url")
        print("Detected environment:", ENVIRONMENT)

        request = requests.get(self.kong_api)
        if request.status_code == 200:
            self.add_service("Deployment-Service", "http://openshift-deployment-pipeline.planblick.svc:8000")
            self.add_route(service_name="Deployment-Service", path="/deployment")
        else:
            print("Kong-API not available:", str(self.kong_api))

    def add_service(self, service_name, service_url):
        payload = {
            "name": service_name,
            "url": service_url
        }
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }
        url = self.kong_api + "/services"
        response = requests.request("GET", url, headers=headers)

        services = response.json()
        for service in services.get("data", []):
            if service_name == service.get("name"):
                print("Service already exists")
                return

        self.post(api_path="/services", payload=payload, headers=headers)

    def add_route(self, service_name, path, plugins=["key-auth"], strip_path=True):
        payload = {
            "paths": [path],
            "strip_path": strip_path,
        }
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }

        url = self.kong_api + "/services/" + service_name + "/routes/"

        response = requests.request("GET", url, headers=headers)

        routes = response.json()
        route_id = None
        path_exists = False
        for route in routes.get("data", []):
            if path in route.get("paths"):
                print("Path already exists")
                route_id = route.get("id")
                path_exists = True

        if path_exists is False:
            reply = self.post(api_path="/services/" + service_name + "/routes", payload=payload, headers=headers)
            route_id = reply.get("id")

        url = self.kong_api + "/plugins"
        for plugin in plugins:
            payload = {"route_id": route_id, "name": plugin}
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache",
            }

            try:
                response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
                print(response.text)
            except Exception:
                pass

    def post(self, api_path, payload, headers):
        if type(payload) == dict:
            payload = json.dumps(payload)

        url = self.kong_api + api_path
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        return response.json()
