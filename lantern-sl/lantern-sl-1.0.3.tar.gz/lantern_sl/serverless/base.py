from lantern_sl.utils.request import http_response, http_error


class ServerlessBase(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context

    def response(self):
        raise NotImplementedError("response function should be implemented")