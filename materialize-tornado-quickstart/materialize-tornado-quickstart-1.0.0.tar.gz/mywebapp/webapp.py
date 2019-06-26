"placeholder for your webapp api"


class API:

    def __init__(self):
        self.message = "Hello, World"
        self.server = None

    def register_server(self, server):
        self.server = server
