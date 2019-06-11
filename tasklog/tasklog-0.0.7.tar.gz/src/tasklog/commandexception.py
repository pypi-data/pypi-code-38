class CommandException(Exception):
    def __init__(self, message, exitCode):

        super(CommandException, self).__init__(message)
        self.message = message
        self.exitCode = exitCode
