class PerformanceReporterBase(object):
    def __init__(self, config):
        self.config = config

    def set_metrics(self, name, metrics):
        raise NotImplementedError
