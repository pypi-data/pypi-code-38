class IsValidUserHandler():
    def __call__(self, command):
        # use a hardcoded test-user for now
        return (True if command.username == 'test' and command.password == 'test' else False)
