from requests import Response

def _format_error(e):
        """Formats an Argus error message

        {
         "type": "ACTION_ERROR",
         "field": None,
         "message": "Something went wrong",
         "parameter": ...
        }

        into a single string to show as an error message at run-time
        :param e:
        :return:
        """
        if e["type"] == "FIELD_ERROR":
            return "%s (%s): %s" % (e["type"], e["field"], e["message"])
        else:
            return "%s: %s" % (e["type"], e["message"])

class ArgusException(Exception):
    def __init__(self, json_or_response, errors=None):
        
        if isinstance(json_or_response, dict):
            json = json_or_response
        elif isinstance(json_or_response, Response):
            try:
                json = json_or_response.json()
            except:
                json = {}
        
        if "messages" in json:
            self.message = "\n".join([
                _format_error(msg) for msg in json["messages"]
            ])

        super(ArgusException, self).__init__(self.message if hasattr(self, "message") else str(json))
        self.json = json


class AuthenticationFailedException(ArgusException):
    """Used for HTTP 401"""
    pass


class AccessDeniedException(ArgusException):
    """Used for HTTP 403"""
    pass


class ObjectNotFoundException(ArgusException):
    """Used for HTTP 404"""
    pass


class ValidationErrorException(ArgusException):
    """Used for HTTP 412"""
    pass


class MultipleValidationErrorException(Exception):
    pass
