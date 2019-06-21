class PassthroughJsonError(Exception):
    def __init__(self, message, json):
        Exception.__init__(self)
        self.message = message
        self.json = json
     