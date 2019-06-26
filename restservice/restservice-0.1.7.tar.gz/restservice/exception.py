class RESTError(Exception):
    def __init__(self, error, message=None, detail=None, *, status=400):
        self.error = error
        self.message = message
        self.detail = detail
        self.status = status
