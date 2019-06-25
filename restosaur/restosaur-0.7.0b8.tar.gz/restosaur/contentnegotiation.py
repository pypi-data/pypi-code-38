from . import _mimeparsepatched


def best_match(acceptables, header):
    """
    Match "Accept" `header` together with `acceptables` defined on
    the server side
    """

    return _mimeparsepatched.best_match(acceptables, header)


def parse_media_type(media_type):
    return _mimeparsepatched.parse_mime_type(media_type)
