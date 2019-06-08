class ParserError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return (repr(self.value))


def handle_invalid_scenario(msg):
    raise ParserError(msg)
