import yaml

from qsa.lib.datastructures import DTO
from qsa.lib import serializers


class Container(serializers.Representable):

    @property
    def args(self):
        return self.spec.setdefault('args', [])

    @property
    def env(self):
        return self.spec.setdefault('env', [])

    @property
    def ports(self):
        return self.spec.setdefault('ports', [])

    @property
    def securitycontext(self):
        return self.spec.setdefault('securityContext', DTO())

    @classmethod
    def represent(cls, dumper, data):
        return serializers.represent_ordereddict(dumper, data)

    def __init__(self, spec):
        super().__init__()
        self.spec = spec

    def items(self):
        return self.spec.items()

    def setargs(self, value):
        """Set the arguments of the container."""
        self.spec.args = value
        return self

    def setenv(self, key, value):
        """Set an environment variable in the container."""
        self.env.append({'name': key, 'value': value})
        return self

    def setenvfieldref(self, key, value):
        """Set an environment variable in the container from a manifest field
        reference.
        """
        self.env.append({'name': key, 'valueFrom': {'fieldRef': {'fieldPath': value}}})
        return self

    def expose(self, name, port, protocol='TCP'):
        """Exposes a port on the container."""
        self.ports.append({'name': name, 'containerPort': port, 'protocol': protocol})

    def setprobe(self, kind, success, failure, delay, period, timeout, probe):
        """Sets a liveness or readyness probe for the container."""
        self.spec[kind] = {
            'failureThreshold': failure,
            'successThreshold': success,
            'initialDelaySeconds': delay,
            'periodSeconds': period,
            'timeoutSeconds': timeout
        }
        self.spec[kind].update(probe)

    def setlivenessprobe(self, *args, **kwargs):
        return self.setprobe('livenessProbe', *args, **kwargs)

    def setreadynessprobe(self, *args, **kwargs):
        return self.setprobe('readynessProbe', *args, **kwargs)

    def setsecuritycontext(self, privileged, drop, add, user):
        self.securitycontext.update(DTO(
            allowPrivilegeEscalation=privileged,
            capabilities={'drop': drop, 'add': add},
            runAsUser=user
        ))


serializers.add_representer(Container)
