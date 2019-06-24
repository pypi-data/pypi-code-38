class SSL:

    def __init__(self, key, cert, cacert=None):
        self.key = key
        self.cert = cert
        self.cacert = cacert
