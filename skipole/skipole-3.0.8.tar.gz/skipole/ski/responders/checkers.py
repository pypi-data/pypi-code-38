

"""A Respond object instance is placed in a Respond page,
   The instance is callable, and the respondpage calls it
   to provide the page action"""

import pprint

from .. import skiboot, tag
from ..excepts import ValidateError, ServerError, FailPage, ErrorMessage

from . import Respond


class AllowedFields(Respond):
    """
Takes a list of widgfields, any which do not appear in the
submitted form data will be set into form data with an empty value. If any form
data field appears which is NOT in this list, it will be considered unwanted data,
and will cause the project validate error page to be called, if no fields are given,
the caller must not provide any form data. It also takes a list
of allowed page idents which are the possible callers to this page.

If the calling page submits no ident, and the
alternate_ident has been set - send the call there.  If it has not, then it
calls the project validate error page.

If submit_data option is True, then received data is placed in the submit_dict dictionary
under key 'received_data' which contains a dictionary of widgfield tuples:values.
"""

    # This indicates a target page ident is required
    target_ident_required = True
    
    # This indicates if another alternate page is required
    alternate_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True
    
    # The form data can be validated
    validate_option_available = True

    # The form data can be submitted
    submit_option_available = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'fields_optional': True,        # if fields is True, then False here means fields must be supplied
                     'widgfield_values':False,        # If True the field values are widgfields
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Gets the target page, filling in the form data"
        if caller_page is None:
            if self.alternate_ident:
                return self.get_alternate_page(skicall, {}, None, ident_list, proj_ident, rawformdata)
            else:
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='No caller page, and no alternate ident set in AllowedFields responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message='No caller page, and no alternate ident set in AllowedFields responder')
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # previous caller is allowed, now check the form data

        if not self.fields:
            if form_data :
                # if no fields specified, there should be no form data
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='No form data expected by AllowedFields responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message="No form data expected by AllowedFields responder")
            else:
                # no form_data received, no fields to check, go to target page or submit_data
                if self.submit_option:
                    try:
                        self._submit_data(ident_list, skicall)
                    except FailPage as e:
                        # raises a PageError exception
                        self.raise_error_page([e.errormessage], skicall, {}, caller_page, ident_list, proj_ident, rawformdata)
                return self.get_target_page(skicall, {}, caller_page, ident_list, proj_ident, rawformdata)

        # generate new form data
        new_form_data = {}
        # populate new form data with received form data
        for field in form_data:
            if field not in self.fields:
                # any form data field not in those specified by self.fields, causes an error
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='Recieved data in a field not specified in the AllowedFields responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message="Recieved data in a field not specified in the AllowedFields responder")
            new_form_data[field] = form_data[field]

        for field in self.fields:
            # add field with empty value if the field has not been submitted
            if field not in new_form_data:
                new_form_data[field] = ''
                
        if self.validate_option:
            validated_form_data = self._validate_fields(skicall, new_form_data, caller_page, ident_list, proj_ident, rawformdata)
        else:
            validated_form_data = new_form_data


        # call user submit_data
        if self.submit_option:
            received_data = {}
            for field in self.fields:
                formvalue =  validated_form_data[field]
                if isinstance(formvalue, list) or isinstance(formvalue, dict):
                    received_data[field.to_tuple_no_i()] = formvalue.copy()
                else:
                    received_data[field.to_tuple_no_i()] = formvalue

            skicall.submit_dict['received_data'] = received_data

            try:
                self._submit_data(ident_list, skicall)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
                
        # return the target page
        return self.get_target_page(skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)


class StoreData(Respond):
    """For widgfields set here, takes the data from the submitted form, and stores them in the dictionary
       call_data with keys equal to widgfield tuples submitting the data. If widgfields specified do not appear in the form
       they will be assumed to be empty strings"""

    # This indicates a target page ident is required
    target_ident_required = True
    
    # The form data can be validated
    validate_option_available = True

    # The form data can be submitted
    submit_option_available = True

    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,           # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):

        if self.validate_option:
            if caller_page is None:
                # raises a PageError exception
                self.raise_error_page([], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
            validated_form_data = self._validate_fields(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        else:
            validated_form_data = form_data

        for field in self.fields:
            if field not in validated_form_data:
                skicall.call_data[field.to_tuple_no_i()] = ''
                continue
            formvalue =  validated_form_data[field]
            if isinstance(formvalue, list) or isinstance(formvalue, dict):
                skicall.call_data[field.to_tuple_no_i()] = formvalue.copy()
            else:
                skicall.call_data[field.to_tuple_no_i()] = formvalue

        if self.submit_option:
            if caller_page is None:
                caller_ident = None
            else:
                caller_ident = caller_page.ident

            try:
                self._submit_data(ident_list, skicall)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
 
        return self.get_target_page(skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)


class StoreDataKeyed(Respond):
    """For widgfields set here, takes the data from the submitted form, and stores them in the dictionary
       call_data.  The dictionary keys used to store these are the values given to the widgfields here."""

    # This indicates a target page ident is required
    target_ident_required = True

    # The form data can be validated
    validate_option_available = True

    # The form data can be submitted
    submit_option_available = True

    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':False,    # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
    
        if self.validate_option:
            if caller_page is None:
                # raises a PageError exception
                self.raise_error_page([], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
            validated_form_data = self._validate_fields(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        else:
            validated_form_data = form_data

        for field, key in self.fields.items():
            if field not in validated_form_data:
                skicall.call_data[key] = ''
                continue
            formvalue =  validated_form_data[field]
            if isinstance(formvalue, list) or isinstance(formvalue, dict):
                skicall.call_data[key] = formvalue.copy()
            else:
                skicall.call_data[key] = formvalue

        if self.submit_option:
            if caller_page is None:
                caller_ident = None
            else:
                caller_ident = caller_page.ident

            try:
                self._submit_data(ident_list, skicall)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)

        return self.get_target_page(skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)


class AllowStoreKeyed(Respond):
    """
Accepts only allowed widgfields, validate submitted data
and store in call_data.

If the calling page submits no data at all, not even an ident, then if the
alternate_ident has been set - send the call there.  If it has not, then it
calls the project validate error page.

The submitted values are placed in the call_data dictionary,
with keys equal to the field values set here.

"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates if another alternate page is required
    alternate_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True
    
    # The form data can be validated
    validate_option_available = True

    # The form data can be submitted
    submit_option_available = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'widgfield_values':False,        # If True the field values are widgfields
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':False,    # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Gets the target page, filling in the form data"

        if caller_page is None:
            if self.alternate_ident:
                return self.get_alternate_page(skicall, {}, None, ident_list, proj_ident, rawformdata)
            else:
                raise ValidateError(message='No caller page, and no alternate ident set in AllowStoreKeyed responder')
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # previous caller is allowed
        
        if not self.fields:
            if form_data :
                # if no fields specified, there should be no form data
                raise ValidateError(message="No form data expected by AllowedStoreKeyed responder")
            else:
                # no form_data received, no fields to check, go to target page or submit_data
                if self.submit_option:

                    try:
                        self._submit_data(ident_list, skicall)
                    except FailPage as e:
                        # raises a PageError exception
                        self.raise_error_page([e.errormessage], skicall, {}, caller_page, ident_list, proj_ident, rawformdata)
                return self.get_target_page(skicall, {}, caller_page, ident_list, proj_ident, rawformdata)
        
        # check fields received are specified in this responder
        for field in form_data:
            if field not in self.fields:
                # any form data field not in those specified by self.fields, causes an error
                raise ValidateError(message="Recieved data in a field not specified in the AllowStoreKeyed responder")

        if self.validate_option:
            validated_form_data = self._validate_fields(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        else:            
            # no validation
            validated_form_data = form_data


        for field, key in self.fields.items():
            if field not in validated_form_data:
                skicall.call_data[key] = ''
                continue
            formvalue =  validated_form_data[field]
            if isinstance(formvalue, list) or isinstance(formvalue, dict):
                skicall.call_data[key] = formvalue.copy()
            else:
                skicall.call_data[key] = formvalue

        # call user submit_data
        if self.submit_option:

            try:
                self._submit_data(ident_list, skicall)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
        return self.get_target_page(skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
        
        
class AllowStore(Respond):
    """For widgfields set here, takes the data from the submitted form, and stores them in the dictionary
       call_data with keys equal to widgfield tuples submitting the data"""

    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates if another alternate page is required
    alternate_ident_required = True
    
    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True
    
    # The form data can be validated
    validate_option_available = True
    
    # The form data can be submitted
    submit_option_available = True

    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,           # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):

   
        if caller_page is None:
            if self.alternate_ident:
                return self.get_alternate_page(skicall, {}, None, ident_list, proj_ident, rawformdata)
            else:
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='No caller page, and no alternate ident set in AllowStore responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message='No caller page, and no alternate ident set in AllowStore responder')
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # previous caller is allowed
        
        if not self.fields:
            if form_data :
                # if no fields specified, there should be no form data
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='No form data expected by AllowStore responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message="No form data expected by AllowStore responder")
            else:
                # no form_data received, no fields to check, go to target page or submit_data
                if self.submit_option:

                    try:
                        self._submit_data(ident_list, skicall)
                    except FailPage as e:
                        # raises a PageError exception
                        self.raise_error_page([e.errormessage], skicall, {}, caller_page, ident_list, proj_ident, rawformdata)
                return self.get_target_page(skicall, {}, caller_page, ident_list, proj_ident, rawformdata)
        
        # check fields received are specified in this responder
        for field in form_data:
            if field not in self.fields:
                # any form data field not in those specified by self.fields, causes an error
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='Recieved data in a field not specified in the AllowStore responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message="Recieved data in a field not specified in the AllowStore responder")

        if self.validate_option:
            validated_form_data = self._validate_fields(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        else:            
            # no validation
            validated_form_data = form_data

        for field in self.fields:
            if field not in validated_form_data:
                skicall.call_data[field.to_tuple_no_i()] = ''
                continue
            formvalue =  validated_form_data[field]
            if isinstance(formvalue, list) or isinstance(formvalue, dict):
                skicall.call_data[field.to_tuple_no_i()] = formvalue.copy()
            else:
                skicall.call_data[field.to_tuple_no_i()] = formvalue
                    
        # call user submit_data
        if self.submit_option:

            try:
                self._submit_data(ident_list, skicall)
            except FailPage as e:
                # raises a PageError exception
                self.raise_error_page([e.errormessage], skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)
 
        return self.get_target_page(skicall, validated_form_data, caller_page, ident_list, proj_ident, rawformdata)


class PrettyFormData(Respond):
    """Places a pretty print string of received widgfield:value's form data into submit_dict with key 'form_data'
       and pretty print of received raw data into submit_dict with key 'raw_data' and calls user submit_data function.
       Used for diagnostics. If no data available, the values are empty strings."""


    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': True,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):

        if form_data:
            new_dict = { key.to_tuple_no_i():val for key, val in form_data.items() }
            skicall.submit_dict['form_data'] = pprint.pformat(new_dict)
        else:
            skicall.submit_dict['form_data'] = ''


        # rawformdata is a FieldStorage object
        new_dict = {}
        for field in rawformdata.keys():
            value = rawformdata.getlist(field)
            if len(value) == 1:
                new_dict[field] = value[0]
            else:
                new_dict[field] = value

        if new_dict:
            skicall.submit_dict['raw_data'] = pprint.pformat(new_dict)
        else:
            skicall.submit_dict['raw_data'] = ''

        try:
            self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # so all ok, get the target page
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)



class Accept(Respond):
    """places received raw data into submit_dict under key 'received_data'.
       Required when received data is not in widgfield format and without ident information"""


    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': True,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):



        # rawformdata is a FieldStorage object

        received_data = {}
        for field in rawformdata.keys():
            value = rawformdata.getlist(field)
            if len(value) == 1:
                received_data[field] = value[0]
            else:
                received_data[field] = value

        skicall.submit_dict['received_data'] = received_data

        try:
            self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)




class AllowedAccept(Respond):
    """places received data into submit_dict under key 'received_data', unlike Accept, the caller page must provide its ident
       otherwise alternate page is called, received data keys are widgfield tuples"""


    # This indicates a target page ident is required
    target_ident_required = True

    # This indicates if another alternate page is required
    alternate_ident_required = True

    # This indicates a list of allowed caller idents is required
    allowed_callers_required = True

    # This indicates an optional submit_list and fail_ident is required
    submit_required = True

    # Options for the fields argument
    field_options = {'fields': False,                  # If False, no fields are expected
                     'widgfields':False,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': True,        # if fields is True, then False here means fields must be supplied
                     'field_values': False,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):

        if caller_page is None:
            if self.alternate_ident:
                return self.get_alternate_page(skicall, {}, None, ident_list, proj_ident, rawformdata)
            else:
                if skiboot.get_debug():
                    responder_ident = ident_list[-1]
                    message='No caller page, and no alternate ident set in AllowedFields responder %s,%s' % responder_ident
                    raise ValidateError(message)
                else:
                    raise ValidateError(message='No caller page, and no alternate ident set in AllowedAccept responder')
        self._check_allowed_callers(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        # previous caller is allowed, now store the received form data


        received_data = {}
        if form_data:
            for key, value in form_data.items():
                received_data[key.to_tuple_no_i()] = value

        skicall.submit_dict['received_data'] = received_data

        try:
            self._submit_data(ident_list, skicall)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)



class PageData(Respond):
    """Places widgfield values into page_data"""

    # This indicates a target page ident is required
    target_ident_required = True

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # Multiple fields accepted


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Places given widgfields and values into page_data"
        for field, value in self.fields.items():
            str_field = str(field)
            if ':' in str_field: 
                # a widgfield with widget:field component
                skicall.page_data[field.to_tuple_no_i()] = value
            else:
                # widgfield is actually a string, such as 'show_error'
                skicall.page_data[str_field] = value
        return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)

