# this error was created to avoid having to repeat the same code in every invalid mode check
class ModeError(ValueError):
    def __init__(self, mode=None, message=None):
        if message is None:
            message = f'Invalid mode {mode}. Expected "idf" or "json"'
        super().__init__(message)
