

"""A Respond object instance is placed in a Respond page,
   The instance is callable, and the respondpage calls it
   to provide the page action"""

import json, collections

from http import cookies
from string import Template

from .. import skiboot, tag
from ..excepts import ValidateError, ServerError, FailPage, ErrorMessage

from . import Respond


class SubmitData(Respond):
    """
This responder is used in conjunction with previous responders that validates and stores form data in call_data.
Given optional submit_list strings, they will be passed to the user provided submit_data function
in the submit_list argument.
If submit_data raises a FailPage then the fail_ident page will be called.
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': True,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""

        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

        try:
            self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, get the target page
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


class ColourSubstitute(Respond):
    """
This responder only applies where the final page returned is a css page.
It will call your submit_data function which should return a dictionary of strings as keys
and colour strings as values.  The keys will be searched for in the target page
with format '${keystring}' and where found the colour value will be placed there.
If submit_data raises a FailPage then the fail page will be called unchanged.
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""

        try:
            colours = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # return fail page unchanged
            return self.get_fail_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, get the target page
        csspage = self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        if colours and isinstance(colours, dict):
            csspage.colour_substitution = colours
        return csspage



class SetCookies(Respond):
    """
Sets cookies, submit_data should return an instance of http.cookies.BaseCookie
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data to get a http.cookies.BaseCookie object"""

        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

        try:
            sendcookies = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
             self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        page = self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # sets the cookies in the page headers
        if sendcookies:
            if not isinstance(sendcookies, cookies.BaseCookie):
                raise ServerError(message = "Returned cookies from submit_data not valid") 
            # set cookies in target_page
            for morsel in sendcookies.values():
                page.headers.append(("Set-Cookie", morsel.OutputString()))
        return page


class GetDictionaryDefaults(Respond):
    """
Web browsers do not send empty fields, therefore a submitted dictionary may have items missing. This responder calls
your submit_data function which should return a dictionary with default values.  Any missing fields
in the form data are then filled in with these defaults. 
The call to submit data will have the 'widgfield':widgfield tuple in the submit dictionary
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True

    # The widgfield to test
    widgfield_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': True,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted



    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Gets the target page, filling in the form data"
        if caller_page is None:
            raise ValidateError()
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # previous caller is allowed

        skicall.submit_dict['widgfield']=self.widgfield.to_tuple_no_i()
        try:
            # and send the widgfield to submit_data
            defaultdict = self._submit_data( ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        if not isinstance(defaultdict, dict):
            raise ServerError(message = "Returned value from submit_data not valid")

        # if widgfield empty
        if (self.widgfield not in form_data) or (not form_data[self.widgfield]):
            form_data[self.widgfield] = defaultdict
            return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

        formdict = form_data[self.widgfield]
        if not isinstance(formdict, dict):
            raise ValidateError()

        # check if an unexpected item has been submitted
        for field, val in formdict.items():
            if field not in defaultdict:
                raise ValidateError()

        # fill in any missing key values
        for field, val in defaultdict.items():
            if field not in formdict:
                formdict[field] = val

        # so all ok, get the target page
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


class FieldStoreSubmit(Respond):
    """Takes submitted data from the received form with the given field (regardless of widget name - only uses field name to choose data),
       and stores the data in the dictionary submit_dict under key 'received'.  The dictionary keys in received used to store are the
       widgfield tuple of the submitting widgets.
       Then calls the submit_data function, if no fieldname matches are found submit_data is still called, but no widgfield tuple key
       is inserted into submit_dict"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,           # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': True}            # A single field is accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):

        # field_name
        field_name = ''
        for key in self.fields:
            field_name = key
        if not field_name:
            raise ValidateError()

        skicall.submit_dict['field'] = field_name

        received = {}

        for field, value in form_data.items():
            # field is a widgfield object
            if field_name == field.f:
               if isinstance(value, list) or isinstance(value, dict):
                   received[field.to_tuple_no_i()] = value.copy()
               else:
                   received[field.to_tuple_no_i()] = value
        skicall.submit_dict['received'] = received

        try:
            self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, get the target page
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


class _JSON(object):
    """An object used by SubmitJSON responder"""

    page_type = "SubmitJSON"

    def __init__(self, ident, jsondict):
        if not jsondict:
            self.jsondict = json.dumps({}).encode('UTF-8')
        else:
            self.jsondict =  json.dumps(jsondict).encode('UTF-8')
        self.status = '200 OK'
        self.headers = [('content-type', 'application/json'),
                        ('cache-control','no-cache, no-store, must-revalidate'),
                        ('Pragma', 'no-cache'),
                        ( 'Expires', '0'),
                        ('content-length', str(len(self.jsondict)))]
        self.ident = ident
        self.ident_data = None
        # Set by end_call
        self.session_cookie = ()
        self.language_cookie = ()

    def import_sections(self, page_data):
        "Only used by Template and SVG, everything else just returns"
        return

    def show_error(self, error_messages=[]):
        return

    def set_values(self, page_data):
        """Checks for header and status values"""
        if not page_data:
            return
        if ('status' in page_data) and page_data['status']:
            self.status = page_data['status']
        if ('headers' in page_data) and page_data['headers']:
            self.headers = page_data['headers']

    def get_status(self):
        "Returns (status, headers)"
        return self.status, self.headers

    def update(self, environ, call_data, lang, ident_list=[]):
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def data(self):
         return [self.jsondict]



class SubmitJSON(Respond):
    """
This responder is intended to provide JSON data as a service to an external application,
submit_data should return a dictionary which will be set into a _JSON object
This dictionary is not widgfields, but is any data you like which can be transformed to JSON.
If a dictionary is successfully returned, the given JSON dictionary will be returned to the client.
Only page_data['status'] and page_data['headers'] will be used if given.
"""

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted

    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""

        try:
            jsondict = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, return JSON file
        return _JSON(ident_list[-1], jsondict)


class _PlainText(object):
    """An object used by SubmitPlainText responder"""

    page_type = "SubmitPlainText"

    def __init__(self, ident, text):
        if not text:
            self.text = "".encode('UTF-8')
        else:
            self.text = text.encode('UTF-8')
        self.status = '200 OK'
        self.headers = [('content-type', 'text/plain'),
                        ('content-length', str(len(self.text)))]
        self.ident = ident
        self.ident_data = None
        # Set by end_call
        self.session_cookie = ()
        self.language_cookie = ()

    def import_sections(self, page_data):
        "Only used by Template and SVG, everything else just returns"
        return

    def show_error(self, error_messages=[]):
        return

    def set_values(self, page_data):
        """Checks for header and status values"""
        if not page_data:
            return
        if ('status' in page_data) and page_data['status']:
            self.status = page_data['status']
        if ('headers' in page_data) and page_data['headers']:
            self.headers = page_data['headers']

    def get_status(self):
        "Returns (status, headers)"
        return self.status, self.headers

    def update(self, environ, call_data, lang, ident_list=[]):
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def data(self):
         return [self.text]



class SubmitPlainText(Respond):
    """
This responder is intended to return plain text to the client.
submit_data should return a string which will be returned to the client.
Only page_data['status'] and page_data['headers'] will be used if given
"""

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""
        try:
            text = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, return a _PlainText instance
        return _PlainText(ident_list[-1], text)


class _CSS(object):
    """An object used by SubmitCSS responder"""

    page_type = "SubmitCSS"

    def __init__(self, ident, style=collections.OrderedDict()):

        # self.style is a dictionary with keys being css selectors
        # and values being a list of two element lists
        # acting as css declaration blocks.
        self.style = style
        self.colour_substitution = {}
        # if self.style_binary given a non empty value, overrides anything else
        self.style_binary = []
        # imports
        self.imports = []
        self.status = '200 OK'
        self.headers = [('content-type', 'text/css'),
                        ('cache-control','no-cache, no-store, must-revalidate'),
                        ('Pragma', 'no-cache'),
                        ('Expires', '0')]
        self.ident = ident
        self.ident_data = None
        # Set by end_call
        self.session_cookie = ()
        self.language_cookie = ()


    # property style is a dictionary of lists
    def get_style(self):
        return self._style

    def set_style(self, style):
        if isinstance(style, collections.OrderedDict):
            self._style = style
        elif isinstance(style, dict):
            self._style = collections.OrderedDict([(selector,value) for selector,value in style.items()])
        else:
            self._style = collections.OrderedDict()

    style = property(get_style, set_style)

    def selector_list(self):
        return list(self._style.keys())

    def selector_properties(self, selector):
        "Returns the property strings of the selector"
        style_text = ""
        if selector not in self._style:
            return ""
        value = self._style[selector]
        if value:
            # value is a list of two element lists
            # created value_list, which is value, sorted by the first element in each sub list
            value_list = sorted(value, key=lambda val : val[0])
            for a,b in value_list:
                style_text += "{a} : {b};\n".format(a=a, b=b)
        return style_text

    def import_sections(self, page_data):
        "Only used by Template and SVG, everything else just returns"
        return

    def show_error(self, error_messages=[]):
        return

    def set_values(self, page_data):
        """Checks for header and status values"""
        if not page_data:
            return
        if '@import' in page_data:
            if isinstance(page_data['@import'], list):
                self.imports = page_data['@import']
            elif isinstance(page_data['@import'], str):
                self.imports = [page_data['@import']]
            del page_data['@import']
        if ('status' in page_data) and page_data['status']:
            self.status = page_data['status']
        if ('headers' in page_data) and page_data['headers']:
            self.headers = page_data['headers']

    def get_status(self):
        "Returns (status, headers)"
        return self.status, self.headers

    def update(self, environ, call_data, lang, ident_list=[]):
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def data(self):
        "Returns the page as a list of binary strings"
        if self.style_binary:
            return self.style_binary
        if not self._style:
            return []
        style_binary = ["@charset \"UTF-8\";\n".encode('UTF-8')]
        if self.imports:
            for imp in self.imports:
                style_binary.append("@import : {imp};\n".format(imp=imp.strip(';')).encode('UTF-8'))
        for selector,value in self._style.items():
            if value:
                style_binary.append("\n{selector} {{".format(selector=selector).encode('UTF-8'))
                # value is a list of two element lists
                # created value_list, which is value, sorted by the first element in each sub list
                value_list = sorted(value, key=lambda val : val[0])
                for a,b in value_list:
                    if self.colour_substitution and ('$' in b):
                        c = Template(b)
                        b= c.safe_substitute(self.colour_substitution)
                    style_binary.append("\n{a} : {b};".format(a=a, b=b).encode('UTF-8'))
                style_binary.append("}\n".encode('UTF-8'))
        return style_binary


class SubmitCSS(Respond):
    """
This responder is intended to return a CSS file to the client.
submit_data should return a style which will be set into a dynamically created
CSS page.
The style is an ordered dictionary with keys being css selectors and values being a
list of two element lists acting as css declaration blocks.
"""

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""

        try:
            styledict = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, return a _CSS instance
        return _CSS(ident_list[-1], styledict)


class MediaQuery(Respond):
    """
Given media queries and CSS page targets, wraps the targets with the media queries
"""

    # The form data can be submitted
    submit_option_available = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':False,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Matches the value given in field self.widgfield against the fields given"

        media_target =  self.fields.copy()

        # update media target with result of submit_data
        if self.submit_option:
            try:
                skicall.submit_dict['media_target'] = media_target.copy()
                mediadict = self._submit_data(ident_list, skicall)
                if mediadict:
                    media_target.update(mediadict)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

        if not media_target:
            raise ServerError(message = "No media queries found")

        style_binary = ["@charset \"UTF-8\";\n".encode('UTF-8')]
        
        for media_query, target_ident in media_target.items():
            target = self.get_page_from_ident(target_ident, skicall, form_data, caller_page, ident_list.copy(), proj_ident, rawformdata)
            if hasattr(target, 'style'):
                target_style = target.style
            else:
                continue
            if not target_style:
                continue
            style_binary.append("\n{media_query} {{".format(media_query=media_query).encode('UTF-8'))
            for selector,value in target_style.items():
                if value:
                    style_binary.append("\n{selector} {{".format(selector=selector).encode('UTF-8'))
                    # value is a list of two element lists
                    # created value_list, which is value, sorted by the first element in each sub list
                    value_list = sorted(value, key=lambda val : val[0])
                    for a,b in value_list:
                        if target.colour_substitution and ('$' in b):
                            c = Template(b)
                            b = c.safe_substitute(target.colour_substitution)
                        style_binary.append("\n{a} : {b};".format(a=a, b=b).encode('UTF-8'))
                    style_binary.append("}\n".encode('UTF-8'))
            style_binary.append("}\n".encode('UTF-8'))

        css_object = _CSS(ident_list[-1], {})
        css_object.style_binary = style_binary
        return css_object


class _Iterator(object):
    """An object used by SubmitIterator responder"""

    page_type = "SubmitIterator"

    def __init__(self, ident, biniterator):
        self.biniterator = biniterator
        self.status = '200 OK'
        self.headers = [('cache-control','no-cache, no-store, must-revalidate'),
                        ('Pragma', 'no-cache'),
                        ( 'Expires', '0')]
        self.ident = ident
        self.ident_data = None
        # Set by end_call
        self.session_cookie = ()
        self.language_cookie = ()

    def import_sections(self, page_data):
        "Only used by Template and SVG, everything else just returns"
        return

    def show_error(self, error_messages=[]):
        return

    def set_values(self, page_data):
        """Checks for header, status and mimetype values.  Note; mimetype only used if headers not given"""
        if not page_data:
            return
        if ('status' in page_data) and page_data['status']:
            self.status = page_data['status']
        if ('headers' in page_data) and page_data['headers']:
            self.headers = page_data['headers']
            return
        if ('mimetype' in page_data) and page_data['mimetype']:
            self.headers.append(('content-type', page_data['mimetype']))
        if ('content-length' in page_data) and page_data['content-length']:
            self.headers.append(('content-length', page_data['content-length']))

    def get_status(self):
        "Returns (status, headers)"
        return self.status, self.headers

    def update(self, environ, call_data, lang, ident_list=[]):
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def data(self):
         return self.biniterator


class SubmitIterator(Respond):
    """
submit_data should return a binary file iterator
"""

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,              # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,         # if fields is True, then False here means fields must be supplied
                     'field_values':False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Calls submit_data"""
        try:
            biniterator = self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, return a _Iterator instance
        return _Iterator(ident_list[-1], biniterator)


