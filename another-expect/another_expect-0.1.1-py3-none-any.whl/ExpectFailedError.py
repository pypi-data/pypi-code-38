class ExpectFailedError(Exception):
    def __init__(self, msg, expectInstance):
        super().__init__(msg)
        self.message = msg
        self.expect = expectInstance
