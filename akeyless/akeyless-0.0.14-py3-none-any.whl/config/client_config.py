class AkeylessClientConfig:
    def __init__(self, uam_server_dns, policy_id, prv_key_seed, protocol="https"):
        # type: (str, str, str, str) -> None
        self._protocol = protocol
        self._uam_server_dns = uam_server_dns
        self._prv_key_seed = prv_key_seed
        self._policy_id = policy_id

    @property
    def uam_server_dns(self):
        # type: () -> str
        return self._uam_server_dns

    @uam_server_dns.setter
    def uam_server_dns(self, val):
        self._uam_server_dns = val

    @property
    def protocol(self):
        # type: () -> str
        return self._protocol

    @protocol.setter
    def protocol(self, val):
        self._protocol = val

    @property
    def policy_id(self):
        # type: () -> str
        return self._policy_id

    @policy_id.setter
    def policy_id(self, val):
        self._policy_id = val

    @property
    def prv_key_seed(self):
        # type: () -> str
        return self._prv_key_seed

    @prv_key_seed.setter
    def prv_key_seed(self, val):
        self._prv_key_seed = val

    def __repr__(self):
        return 'AkeylessClientConfig({},{},{})'.format(self.protocol,
                                                       self.uam_server_dns,
                                                       self.policy_id)

    def __str__(self):
        return "Protocol: {} \nServer DNS: {}\nPolicy Id: {}\n".format(self.protocol,
                                                                       self.uam_server_dns,
                                                                       self.policy_id)
