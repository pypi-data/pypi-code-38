from qsa.lib.datastructures import DTO
from .base import Resource
from .clusterwide import ClusterWide
from .persistable import Persistable
from .prefixable import ClusterPrefixable


class PodSecurityPolicy(Persistable, ClusterWide, ClusterPrefixable):
    kind = 'PodSecurityPolicy'
    api_version = 'policy/v1beta1'
    group = 'security'
    stage = 'cluster'

    @property
    def allowed_capabilities(self):
        return self.spec.setdefault('allowedCapabilities', [])

    @property
    def forbidden_capcabilities(self):
        return self.spec.setdefault('requiredDropCapabilities', [])

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO(
            
        ))

    def on_bound(self):
        """Executed when the resource is marked as bound."""
        self.name  = f'{self.prefix}{self.base_name}'
        self.label('name', self.name,
            'app.kubernetes.io')

    def allowcap(self, cap):
        self.allowed_capabilities.append(cap)

    def allowescalation(self, enable):
        self.spec.allowPrivilegeEscalation = enable

    def forbidcap(self, cap):
        self.forbidden_capcabilities.append(cap)

    def setdefaults(self):
        self.spec.update(DTO(
            seLinux=DTO(rule='RunAsAny'),
            supplementalGroups=DTO(rule='RunAsAny'),
            runAsUser=DTO(rule='RunAsAny'),
            fsGroup=DTO(rule='RunAsAny'),
            volumes=[
                'configMap',
                'downwardAPI',
                'emptyDir',
                'persistentVolumeClaim',
                'secret',
                'projected'
            ]
        ))
