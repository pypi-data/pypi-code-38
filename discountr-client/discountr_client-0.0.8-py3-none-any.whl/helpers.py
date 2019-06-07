import logging
import types


def serialize(key=None):
    def decorator(function: types.FunctionType):
        def wrapper(*args, **kwargs):
            self = args[0]

            logging.critical(function.__name__)
            self.serialized_keys[function.__name__] = key if key is not None else function.__name__
            result = function(*args, **kwargs)

            return result

        return wrapper

    return decorator
