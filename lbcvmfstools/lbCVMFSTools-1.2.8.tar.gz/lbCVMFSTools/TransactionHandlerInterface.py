class TransactionHandlerInterface(object):

    def __init__(self, *args, **kwargs):
        if kwargs.get('dry_run', None):
            self.dry_run = kwargs['dry_run']
        else:
            self.dry_run = False

    def transactionPublish(self):
        raise NotImplementedError()

    def transactionStart(self):
        raise NotImplementedError()

    def transactionAbort(self):
        raise NotImplementedError()
