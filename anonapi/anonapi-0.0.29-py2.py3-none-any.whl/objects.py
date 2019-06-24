"""classes and methods shared by anonapi modules """


class RemoteAnonServer:
    """An anonymization server that can be talked to via the API

    """

    def __init__(self, name, url):
        """Create a Remote anon server entry

        Parameters
        ----------
        name: str
            short keyword to identify this server
        url: str
            full url to a valid Anonymization server web API
        """
        self.name = name
        self.url = url

    def to_dict(self):
        """Dictionary representation of this server

        Returns
        -------
        Dict

        """
        return {'name': self.name,
                'url': self.url}

    @classmethod
    def from_dict(cls, dict_in):
        """Load instance from output of to_dict

        Returns
        -------
        RemoteAnonServer

        """
        return cls(name=dict_in['name'], url=dict_in['url'])

    def __str__(self):
        return f"{self.name}: {self.url}"
