import subprocess

from onepanel.utilities.s3.authentication import Provider


class AWSCLIWrapper:
    """Wraps AWS CLI commands so we get new credentials if they expired"""
    def __init__(self, credentials_provider=None, retry=3):
        """
        :param credentials_provider: Provides credentials for requests.
        :type credentials_provider: onepanel.lib.s3.authentication.Provider
        """
        if credentials_provider is None:
            credentials_provider = Provider()

        self.credentials_provider = credentials_provider
        self.retry = retry
        self.retries = 0

    def run(self, *args, **kwargs):
        while self.retries < self.retry:
            p = subprocess.Popen(*args, **kwargs)

            output = ""
            err = ""

            for line in iter(p.stdout.readline, '' or b''):  # replace '' with b'' for Python 3
                output += line.decode()
            for line in iter(p.stderr.readline, '' or b''):  # replace '' with b'' for Python 3
                err += line.decode()

            if ('(ExpiredToken)' in err or '(InvalidToken)' in err) and self.retries < self.retry:
                # If the credential provider doesn't load new credentials, then it has bad credentials
                # so don't bother trying again.
                if self.credentials_provider.loads_credentials():
                    credentials = self.credentials_provider.credentials()
                    for key, value in credentials.dict().items():
                        kwargs['env'][key] = value

                    self.retries += 1
                    continue

            return 0, output, err
