class OverwriteException(Exception):
    def __init__(self, msg, overwrites):
        self.msg = msg
        self.overwrites = overwrites

    def __str__(self):
        overwrites = '\n'.join(self.overwrites)
        return f'{self.msg}\n{overwrites}'


