

"""A Respond object instance is placed in a Respond page,
   The instance is callable, and the respondpage calls it
   to provide the page action"""


import re

from .. import skiboot, tag
from ..excepts import ValidateError, ServerError

from . import Respond


class CaseSwitch(Respond):
    """
Checks a single submitted field content against a list, and if a match occurs, passes the call
to an associated page (or responder) given by the value, which can be an ident, label or url.
If there is no match, the page (or responder) specified by 'alternate_ident' will be called.
This is not considered an error, and no error message will be raised
"""

    # This indicates a widgfield is required
    widgfield_required = True

    # This indicates a fail page ident is required
    alternate_ident_required = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':False,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}            # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Matches the value given in field self.widgfield against the fields given"
        if (not self.widgfield.w) or (not self.widgfield.f):
            raise ServerError(message="Invalid widgfield set in CaseSwitch Responder")
        if self.widgfield in form_data:
            value = form_data[self.widgfield]
            if value in self.fields:
                return self.get_page_from_ident(self.fields[value], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        return self.get_alternate_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

 
class EmptyGoto(Respond):
    """
For the given widgfield, if the submitted form has that widgfield with an empty value or the
widgfield is not present, then passes the call to target_ident, otherwise passes the call
to alternate_ident.
If no caller page ident is given then it calls the project validate error page.
It also takes a list of allowed page idents which are the possible callers to this page, if
empty, any page can call it - on failure, calls the project validate error page.
"""

    # This indicates a widgfield is required
    widgfield_required = True

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an alternate page ident is required
    alternate_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':False,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}            # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Matches the field values against the data"
        if caller_page is None:
            raise ValidateError()
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        if (self.widgfield not in form_data) or (form_data[self.widgfield] == ''):
            return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        return self.get_alternate_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


class EmptyCallDataGoto(Respond):
    """
For a single given key in call data, if call_data has that key with an empty value or the
key is not present, then passes the call to target_ident, otherwise passes the call
to alternate_ident.
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an alternate page ident is required
    alternate_ident_required = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': True}            # Only a single field is accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Matches the field against the data"
        call_data = skicall.call_data
        for field in self.fields:
            if (field not in call_data) or (call_data[field] == ''):
                return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        return self.get_alternate_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)



class DelCallDataItem(Respond):
    """
For a single given key in call data, if present, that key:value will be deleted from call_data.
"""

    # This indicates a target page ident is required
    target_ident_required = True


    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': True}            # Only a single field is accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Deletes call_data item with the given field key"
        call_data = skicall.call_data
        for field in self.fields:
            if field in call_data:
                del call_data[field]
                # there should only be one field
                break
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


class NoOperation(Respond):
    """
Goes to Target page, can be used as a temporary place holder
"""

    # This indicates a target page ident is required
    target_ident_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Goes to target page"
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)



