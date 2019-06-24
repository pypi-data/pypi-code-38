class ResourceDoesNotExistLocally(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return "Resource {0} does not exist locally.".format(self.value)


class ResourceDoesNotExistRemotelly(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return "Resource {0} does not exist remotelly.".format(self.value)


class CapabilityDoesNotExist(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return "Capability {0} does not exist.".format(self.value)


class MicrosserviceNotWorking(Exception):
    def __init__(self, microsservice, description):
        self.microsservice = microsservice
        self.description = description


    def __str__(self):
        return """
        InterSCity microsservice {0} not working properly.
        
        Error: {1}
        """.format(self.microsservice, self.description)

