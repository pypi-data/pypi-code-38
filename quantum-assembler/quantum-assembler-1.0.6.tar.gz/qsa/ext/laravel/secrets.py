from qsa.ext.secrets.secret import SecretAdapter


class DatabaseConnectionAdapter(SecretAdapter):
    secret_type = 'laravel.quantumframework.org/secrets/rdbms'

    def create(self, source):
        """Clone the secret and replace the certificates with the standard
        Quantum Development Environment (QDE) certificates.
        """
        target = self.clone(source)
        target.data.update({
            'DB_HOST': 'rdbms.local.quantumframework.org',
            'DB_USERNAME': 'quantum',
            'DB_PASSWORD': 'quantum'
        })
        return target

