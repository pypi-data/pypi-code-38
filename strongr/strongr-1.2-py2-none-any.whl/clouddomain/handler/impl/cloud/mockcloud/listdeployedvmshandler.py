from strongr.clouddomain.handler.abstract.cloud import AbstractListDeployedVmsHandler

class ListDeployedVmsHandler(AbstractListDeployedVmsHandler):
    def __call__(self, command):
        return {'up': ['localhost'], 'down': []}
