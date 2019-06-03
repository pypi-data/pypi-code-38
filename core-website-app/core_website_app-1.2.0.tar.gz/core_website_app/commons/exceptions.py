"""
    Core website exceptions
"""


class WebsiteViewsError(Exception):
    """
        Exception raised by the Website package from views
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class WebsiteAjaxError(Exception):
    """
        Exception raised by the Website package from ajax
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class WebsiteWebPageDoesNotExistError(Exception):
    """
        Exception raised by the Website package from model
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)