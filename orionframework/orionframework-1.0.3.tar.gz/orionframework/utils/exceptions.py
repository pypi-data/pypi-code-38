def to_string(cls, exception):
    """
    Translate the given exception to String, either by its defined message or
    """

    if isinstance(exception, Exception):

        if hasattr(exception, 'message') and exception.message:

            return exception.message

        else:

            return str(exception)

    if exception != None:
        return str(exception)

    return None
