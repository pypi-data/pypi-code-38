"""
This script containts a custom error created to avoid code repetion for mode check in eppy_funcs and config.
"""
class ModeError(ValueError):
    def __init__(self, mode=None, message=None):
        if message is None:
            message = f'Invalid mode {mode}. Expected "idf" or "json"'
        super().__init__(message)
