from strongr.clouddomain.handler.abstract.cloud import AbstractDestroyVmsHandler

class DestroyVmsHandler(AbstractDestroyVmsHandler):
    def __call__(self, command):
        pass # we cant deploy vms in the mockcloud
