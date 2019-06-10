import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from qsa.lib.serializers import Base64DER
from .secret import SecretAdapter


class PublicFacingServerCertificateAdapter(SecretAdapter):
    secret_type = 'PublicFacingServerCertificate'
    base_url = 'https://raw.githubusercontent.com/wizardsofindustry/'
    urls = {
        'tls.key': 'k8s-devenv/develop/pki/http.crt',
        'tls.crt': 'k8s-devenv/develop/pki/http.rsa'
    }

    def create(self, source):
        """Clone the secret and replace the certificates with the standard
        Quantum Development Environment (QDE) certificates.
        """
        target = self.clone(source)
        for key, url in self.urls.items():
            self.logger.debug("Fetching %s", url)
            response = requests.get(self.base_url + url)
            assert response.status_code == 200
            target.data[key] = Base64DER(response.text)
        return target


class ApplicationSecretKeyAdapter(SecretAdapter):
    secret_type = 'secrets.quantumframework.org/application-key'

    def create(self, source):
        """Generate a new secret key of the same length as in the
        source.
        """
        n = int(len(source.data.secret_key) / 2)
        target = self.clone(source)
        target.data.secret_key = bytes.hex(os.urandom(n))
        return target


class OAuthKeypairAdapter(SecretAdapter):
    secret_type = 'secrets.quantumframework.org/oauth-keypair'

    def create(self, source):
        """Generate a new keypair for use with OAuth."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        target = self.clone(source)
        target.data.update({
            'oauth-public.key': Base64DER(bytes.decode(
                public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)
            )),
            'oauth-private.key': Base64DER(bytes.decode(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            ))
        })

        return target
