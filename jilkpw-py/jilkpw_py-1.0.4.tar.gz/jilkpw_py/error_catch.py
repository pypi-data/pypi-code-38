"""
error_catch.py contains the basic error/exeption class to hook onto incase things
go a bit.. wrong
"""


class ResponseErrors:
    info_endpoint = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/"

    def __init__(self, status_code):
        if status_code == 404:
            raise self.NotFound(
                f"Jilk.pw could not find the guild_id you passed in! ({self.info_endpoint}404)")
        elif status_code == 405:
            raise self.BadRequest(
                f"A request to Jilk.pw was not handled properly & was aborted! ({self.info_endpoint}405)")
        elif status_code == 401:
            raise self.NotAuthed(
                f"For whatever reason, you are not authorized to use Jilk.pw's public api! ({self.info_endpoint}401)")
        elif status_code == 301:
            raise self.WebMoved(
                f"Jilk.pw has moved, aborting as a failsafe! ({self.info_endpoint}301)")
        elif status_code == 408:
            raise self.WebTimeout(
                f"Request to Jilk.pw timed out, please try again later! ({self.info_endpoint}408)")
        elif status_code == 414:
            raise self.UriTooLong(
                f"The URI is too long for the server to process ({self.info_endpoint}414)!")
        elif status_code == 9091:
            raise self.CannotMain(
                "You are trying to run the wrapper as a module directly!")
        elif status_code != 200:
            raise self.MiscError(f"HTTP response code is \'{status_code}\'!")

    class NotFound(BaseException):
        pass

    class NotAuthed(BaseException):
        pass

    class WebMoved(BaseException):
        pass

    class BadRequest(BaseException):
        pass

    class WebTimeout(BaseException):
        pass

    class UriTooLong(BaseException):
        pass

    class MiscError(BaseException):
        pass

    class CannotMain(BaseException):
        pass
