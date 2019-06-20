


"""
This module defines base exceptions. It can be imported
by any other module as it has no dependencies
"""

class ErrorMessage(object):
    """Acts as a store for attributes message, section, widget

       The message can be either a string, or an empty string

       The following are all optional

       section is the section name (if it is in a section) of the widget where the message is to be displayed
       widget is the widget name where the message is to be displayed
"""
    def __init__(self, message='', section='', widget=''):
        self.message = message
        self.section = section
        self.widget = widget

    def __str__(self):
        return """message: %s
section: %s
widget: %s
code: %s
""" % (self.message,
       self.section,
       self.widget)


class SkiError(Exception):
    """Exception used as a parent to other exception classes that carry message information.
    """

    def __init__(self, message = '', section='', widget=''):
        if message:
            Exception.__init__(self, message)
        self.errormessage = ErrorMessage(message, section, widget)
        # These attributes are filled in by the framework when an error is raised
        self.ident_list = []
        self.form_data = ''

    def get_message(self):
        return self.errormessage.message

    def set_message(self, message):
        self.errormessage.message = message

    message = property(get_message, set_message)

    def get_section(self):
        return self.errormessage.section

    def set_section(self, section):
        self.errormessage.section = section

    section = property(get_section, set_section)

    def get_widget(self):
        return self.errormessage.widget

    def set_widget(self, widget):
        self.errormessage.widget = widget

    widget = property(get_widget, set_widget)


class FailPage(SkiError):
    """Call a responder fail ident page
    """


class ServerError(SkiError):
    """Flag a server problem"""
    def __init__(self, message = '', section='', widget='', status='500 Internal Server Error', code=0):
        SkiError.__init__(self, message, section, widget)
        self.status = status
        # code 0 is default
        # codes 9000 to 9999 are reserved for system use
        self.code = code


class ValidateError(SkiError):
    """Flag a validation error."""
    def __init__(self, message = '', section='', widget='', status='400 Bad Request'):
        SkiError.__init__(self, message, section, widget)
        self.status = status


class PageError(Exception):
    """Exception used to flag a page error - used internally by responders."""

    def __init__(self, page, e_list=[]):
        "Sets an exception with a page"
        self.page = page
        self.e_list = e_list


class GoTo(Exception):
    """Exception used to force a jump to another page

       target being the ident, label or external
                      url of the page to jump to. If a url is given it should start
                      with 'http://' or 'https://' or '//'

       clear_submitted - if True, any submitted data widgets/fields will be cleared,
       clear_page_data - if True, page_data dictionary will be cleared,
       clear_errors - if a FailPage raises an error and the failpage calls
                      a submit function with a GoTo, then setting clear_errors True
                      will remove the error condition from the call, which will therefore
                      not be displayed on the final template page returned

       Note, 'call_data' will not be changed.
"""

    def __init__(self, target, clear_submitted=False, clear_page_data=False, clear_errors=False):
        Exception.__init__(self, "GoTo jump to page " + str(target))
        self.clear_submitted = clear_submitted
        self.clear_page_data = clear_page_data
        self.clear_errors = clear_errors
        self.target = target
        # this is set by the calling responder
        self.proj_ident=None
        # this is set if a FailPage call leads to a responder which raises a GoTo
        self.e_list = []

