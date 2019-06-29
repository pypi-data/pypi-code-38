import json
import namespace as ns
import data

class Hub:
    namespace = None

    def __init__(self):
        if not data.DAO().exists():
            self.namespace = []
            self.namespace.append(ns.Namespace())
            data.DAO(self).save()

        else:
            data.DAO().load(self)

    def serialize(self):
        return data.DAO(self).serialize()   
    
    def listNamespaces(self):
        namespaces = ""
        for index, i in enumerate(self.namespace):
            arg = self.namespace[index]
            namespaces = namespaces + arg['name'] + "\n"

        return namespaces

    def findService(self, name):
        services = ""
        for index, i in enumerate(self.namespace):
            arg = self.namespace[index]
            for jndex, j in enumerate(arg['service']):
                if j['name'] == name.replace("'", "").replace("\"", ""):
                    services = services + arg['name'] + ":" + j['name'] + ":" + j['href'] + "\n"

        return services
