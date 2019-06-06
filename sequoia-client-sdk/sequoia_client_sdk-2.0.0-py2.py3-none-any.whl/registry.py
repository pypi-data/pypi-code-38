import logging


class Registry(dict):
    def __init__(self, registry_url, http):
        self.http = http
        self.registry_url = registry_url
        self.refresh()

    def refresh(self):
        response = self.http.get(self.registry_url)
        self._parse_json_response(response.data)

    def _parse_json_response(self, data):
        for service in data['services']:
            logging.debug("Service registry entry loaded: %s - %s", service['name'], service['location'])
            registered_service = RegisteredService(service)
            self[registered_service.name] = registered_service


class RegisteredService(object):
    def __init__(self, service_data):
        self.name = service_data['name']
        self.owner = service_data['owner']
        self.location = service_data['location']
        self.title = service_data['title']
