

class AuthToken:

    GUEST_COOKIE_NAME = 'MS_GUEST_COOKIE'

    def __init__(self, client):
        self.client = client

    def getTokenData(self):
        pass
        token = None
        # userAgent
