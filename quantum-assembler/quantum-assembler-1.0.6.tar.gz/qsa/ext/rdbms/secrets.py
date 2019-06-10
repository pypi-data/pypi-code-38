import requests

from qsa.ext.secrets.secret import SecretAdapter
from qsa.lib.serializers import Base64DER


class ClientCertificateAdapter(SecretAdapter):
    secret_type = 'DatabaseClientCertificate'
    base_url = 'https://raw.githubusercontent.com/wizardsofindustry/'
    urls = {
        'ca.crt': 'k8s-devenv/develop/pki/quantum.crt',
        'client.crt': 'k8s-devenv/develop/pki/rdbms-client.crt',
        'client.rsa': 'k8s-devenv/develop/pki/rdbms-client.rsa'
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
