from qsa.lib.datastructures import DTO
from .base import Resource
from .clusterwide import ClusterWide
from .persistable import Persistable


class ClusterIssuer(ClusterWide, Persistable):
    api_version = 'certmanager.k8s.io/v1alpha1'
    kind = 'ClusterIssuer'
    group = 'pki'
    stage = 'cluster'

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO())

    @property
    def ca(self):
        return self.spec.setdefault('ca', DTO())

    @property
    def secret(self):
        return self.ca.secretName

    @secret.setter
    def secret(self, value):
        self.ca.secretName = value

    def setsecret(self, name):
        """Sets the secret used by the issuer to sign certificates."""
        self.secret = name


class AcmeClusterIssuer(ClusterIssuer):
    default_url = "https://acme-v02.api.letsencrypt.org/directory"

    @property
    def acme(self):
        return self.spec.setdefault('acme', DTO(
            http01={},
            server=self.default_url,
            privateKeySecretRef=DTO())
        )

    def setacmeemail(self, value):
        """Set the value for ACME email registration address."""
        self.acme.email = value

    def setsecret(self, name):
        """Sets the name for the private key used to sign certificates."""
        self.acme.privateKeySecretRef.name = name
