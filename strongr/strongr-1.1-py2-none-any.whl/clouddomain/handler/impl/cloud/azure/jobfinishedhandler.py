from strongr.clouddomain.handler.abstract.cloud import AbstractJobFinishedHandler

class JobFinishedHandler(AbstractJobFinishedHandler):
    def __call__(self, command):
        pass
        # convert command to inter-domain event
