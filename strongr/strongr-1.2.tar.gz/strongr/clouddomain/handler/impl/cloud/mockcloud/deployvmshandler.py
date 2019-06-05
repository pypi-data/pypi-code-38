from strongr.clouddomain.handler.abstract.cloud import AbstractDeployVmsHandler

class DeployVmsHandler(AbstractDeployVmsHandler):
    def __call__(self, command):
        pass # we can't deploy VM's in the mockcloud
