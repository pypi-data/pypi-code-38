from qsa.lib.datastructures import DTO
from qsa.lib.serializers import DoubleQuotedString
from .base import Resource
from .persistable import Persistable


class Certificate(Resource, Persistable):
    api_version = 'certmanager.k8s.io/v1alpha1'
    kind = 'Certificate'
    group = 'pki'
    stage = 'security'

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO(
            duration="2160h",
            renewBefore="360h"
        ))

    @property
    def secret(self):
        return self.spec.secretName

    @secret.setter
    def secret(self, value):
        self.spec.secretName = value

    @property
    def issuer(self):
        return self.spec.setdefault('issuerRef', DTO())

    @issuer.setter
    def issuer(self, value):
        self.spec.issuerRef = value

    @property
    def altnames(self):
        return self.spec.setdefault('dnsNames', [])

    @property
    def cn(self):
        return self.spec.commonName

    @cn.setter
    def cn(self, value):
        self.spec.commonName = value

    def setacme(self, enable):
        """Enable or disable ACME certificate issueing."""
        if enable:
            self.spec.pop('duration', None)
            self.spec.pop('renewBefore', None)
        else:
            self.spec.update(DTO(
                duration="2160h",
                renewBefore="360h"
            ))

    def setcn(self, common_name, istls=False):
        """Sets the common name for the certificate. If `istls` is ``True``, also
        add the common name as Subject Alternative Name (SAN).
        """
        self.cn = DoubleQuotedString(common_name)
        if istls:
            self.altnames.append(self.cn)

    def setsecret(self, name):
        """Sets the target secret created by the issuer holding the certificate."""
        self.secret = name

    def setissuer(self, name, namespace=None):
        """Set the issuer for this certificate. If `namespace` is ``None``,
        a ``ClusterIssuer`` is assumed.
        """
        self.issuer = DTO(
            kind='Issuer' if namespace else 'ClusterIssuer',
            name=DoubleQuotedString(name)
        )
        if namespace is not None:
            self.issuer.namespace = DoubleQuotedString(namespace)
        return self


