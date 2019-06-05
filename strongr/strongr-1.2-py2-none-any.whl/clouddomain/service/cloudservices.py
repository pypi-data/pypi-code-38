from .cloud import OpenNebula, MockCloud, Azure

# cloud service factory
class CloudServices():
    _clouds = [ \
        OpenNebula,
        MockCloud,
        Azure
    ]

    _instances = {}

    def getCloudNames(self):
        return [cloud.__name__ for cloud in self._clouds]

    def getCloudServiceByName(self, name):
        if name not in self._instances:
            service = next((cloud for cloud in self._clouds if cloud.__name__ == name), None)
            if service == None:
                return None
            self._instances[name] = service()

        return self._instances[name]
