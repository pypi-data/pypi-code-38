from .base import Registry, Registration
from .model import ModelRegistration


REGISTRY = Registry()


def register(registration: Registration):
    REGISTRY.register(registration)


def register_model(model):
    register(ModelRegistration(model))


def register_metric(metric, cls=None):
    from .trackstats import MetricRegistration
    register(MetricRegistration(metric, cls))
