
class StatusMessageException(Exception):
    """
    An exception which has an attached status code and message.
    For returning JSON responses in to_dict along with any additional_information
    that should be provided for debugging.
    """
    status_code = 400

    def __init__(self, message, status_code=None, additional_information=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.additional_information = additional_information

    def to_dict(self):
        output = dict(self.additional_information or {})
        output['message'] = self.message
        return output
