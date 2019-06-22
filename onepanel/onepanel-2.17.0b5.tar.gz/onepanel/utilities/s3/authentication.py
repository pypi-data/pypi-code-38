class Credentials:
    def __init__(self, access_key_id, secret_access_key, session_token):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token

    def dict(self):
        return {
            'AWS_ACCESS_KEY_ID': self.access_key_id,
            'AWS_SECRET_ACCESS_KEY': self.secret_access_key,
            'AWS_SESSION_TOKEN': self.session_token
        }


class Provider:
    def __init__(self):
        # Do nothing
        pass

    def loads_credentials(self):
        """Returns true if the provider needs to load the credentials
           and provides them. E.g. if you need to make a network request
           for them. Returns false if you want to use the default logic
           to check for credentials via AWS config files, etc."""

        return False

    def credentials(self, refresh=False):
        return None


class APIProvider(Provider):
    """Loads credentials with a network request"""
    def __init__(self, conn, endpoint):
        Provider.__init__(self)
        self.conn = conn
        self.endpoint = endpoint

    def loads_credentials(self):
        return True

    def credentials(self, refresh=False):
        response = self.conn.get(self.endpoint)

        if response.status_code != 200:
            raise ValueError(response.status_code)

        data = response.json()

        aws_access_key_id = data['AccessKeyID']
        aws_secret_access_key = data['SecretAccessKey']
        aws_session_token = data['SessionToken']

        return Credentials(aws_access_key_id, aws_secret_access_key, aws_session_token)


class StaticProvider(Provider):
    """Provides credentials that are set on object creation"""
    def __init__(self, access_key, secret_access_key, session_token):
        Provider.__init__(self)
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.session_token = session_token

    def loads_credentials(self):
        return True

    def credentials(self, refresh=False):
        return Credentials(self.access_key, self.secret_access_key, self.session_token)


class MemoryCachedCredentialsProvider(Provider):
    """
    Caches credentials in memory.
    Wrap around another provider to cache the credentials.
    """
    def __init__(self, provider):
        Provider.__init__(self)
        """
        :param provider:
        :type provider Provider
        """
        self.provider = provider
        self.cache = None

    def loads_credentials(self):
        return True

    def credentials(self, refresh=False):
        if refresh or self.cache is None:
            self.cache = self.provider.credentials(refresh=True)

        return self.cache
