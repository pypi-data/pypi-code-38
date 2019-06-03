


"""A Respond object instance is placed in a Respond page,
   The instance is callable, and the respondpage calls it
   to provide the page action"""

import copy, sys, traceback

from .. import skiboot, tag
from ..excepts import ValidateError, ServerError, FailPage, ErrorMessage, PageError, GoTo


class Respond(object):
    """This respond object merely passes form data to the target page, its
main purpose is to act as a parent class for all other respond objects.
"""

    # This indicates if a list of allowed caller idents is required
    allowed_callers_required = False

    # This indicates if a target page ident is required
    target_ident_required = False

    # This indicates if a widgfield is required
    widgfield_required = False

    # This indicates if an alternate page ident is required
    alternate_ident_required = False

    # If True, then a submit list and a fail ident are required
    submit_required = False
    
   # This indicates if the submit option is available
   # if the submit option is chosen, then a submit list and fail ident can also be chosen
    submit_option_available = False
    
    # This indicates if the validate option is available
    validate_option_available = False

    # Options for the fields argument
    field_options = {'fields': True,                  # If False, no fields are expected
                     'widgfields':True,               # If True, fields are widgfields, if False, can be other constants
                     'widgfield_values':False,        # If True the field values are widgfields
                     'fields_optional': False,        # if fields is True, then False here means fields must be supplied
                     'field_values': True,            # if True, field values are used
                     'empty_values_allowed':True,     # If True, '' is a valid value, if False, some data must be provided
                     'single_field': False}           # False if any number of fields, True if only a single field is required

    def __init__(self, widgfield='', alternate_ident='', target_ident='', fail_ident='', validate_fail_ident='', validate_option=False, submit_option=False, allowed_callers=[], submit_list=[]):
        if self.widgfield_required:
            self.widgfield = skiboot.make_widgfield(widgfield)._replace(i='')
        else:
            self.widgfield = ''
        if self.alternate_ident_required:
            self.alternate_ident = skiboot.make_ident_or_label_or_url(alternate_ident)
        else:
            self.alternate_ident = ''
        if self.target_ident_required:
            self.target_ident = skiboot.make_ident_or_label_or_url(target_ident)
        else:
            self.target_ident = None
        if self.allowed_callers_required:
            self.allowed_callers = [ skiboot.make_ident_or_label(aci) for aci in allowed_callers ]
            if (None in self.allowed_callers) or ('' in self.allowed_callers):
                raise ValidateError("invalid allowed caller ident")
        else:
            self.allowed_callers = []
        if self.submit_option_available:
            self.submit_option = submit_option
        else:
            self.submit_option = False
        if self.submit_required or self.submit_option:
            self.submit_list = submit_list
            self.fail_ident = skiboot.make_ident_or_label_or_url(fail_ident)
        else:
            self.submit_list = []
            self.fail_ident = None
        if self.validate_option_available:
            self.validate_option = validate_option
        else:
            self.validate_option = False
        if self.validate_option:
            self.validate_fail_ident = skiboot.make_ident_or_label_or_url(validate_fail_ident)
        else:
            self.validate_fail_ident = None
        # self.fields is a dictionary of field:value
        self.fields = {}
        # the actual values are inserted when the responder is created
        # by a call to self.set_fields()


    def ident_for_user(self, ident):
        "Returns a tuple if item is ident, or just ident otherwise"
        if isinstance(ident, skiboot.Ident):
            return ident.to_tuple()
        return ident

    @classmethod
    def module_name(cls):
        return cls.__module__.split('.')[-1]


    def set_fields(self, fields):
        """Argument fields is a dictionary of fields and values passed to this
           responder by the user and subject to the field_options.
            This function sets the attribute self.fields to these fields, converting
           the keys and values to skiboot.WidgField objects if the widgfields option is True"""

        if fields:
            # fields are present
            if not self.field_options['fields']:
                raise ServerError(message="No fields are expected")
            if self.field_options['single_field']:
                if len(fields) != 1:
                    raise ServerError(message="Only one field should be given")
        else:
            # no fields present
            if self.field_options['fields'] and (not self.field_options['fields_optional']):
                raise ServerError(message="fields are expected")
            self.fields = {}
            return
        oldfields = self.fields.copy()
        self.fields.clear()
        try:
            for field,value in fields.items():
                self._set_field_value(field, value)
        except ServerError as e:
            self.fields = oldfields
            raise

    def set_field(self, field, value):
        """Sets a single field and value into self.fields"""
        if not field:
            raise ServerError(message="Invalid empty field")
        if not self.field_options['fields']:
            raise ServerError(message="No fields are expected")
        if self.field_options['single_field']:
            oldfields = self.fields.copy()
            self.fields = {}
            try:
                _set_field_value(self, field, value)
            except ServerError as e:
                self.fields = oldfields
                raise
        self._set_field_value(field, value)


    def _set_field_value(self, field, value):
        "Used by above two methods to set the field and value"
        if (not self.field_options['field_values']) and value:
            raise ServerError(message="field values are not expected")
        if not self.field_options['field_values']:
            # ensure False, None 0 are saved as ''
            value = ''
        if self.field_options['field_values'] and (not self.field_options['empty_values_allowed']) and (value==''):
            raise ServerError(message="No field can have an empty value")
        if self.field_options['widgfields']:
            # ensure field is a skiboot.WidgField object
            fld = skiboot.make_widgfield(field)._replace(i='')
        else:
            fld = field
        if self.field_options['widgfield_values']:
            # ensure value is a skiboot.WidgField object
            val = skiboot.make_widgfield(value)._replace(i='')
        else:
            val = value
        self.fields[fld] = val


    @property
    def responder_fields(self):
        """Returns a dictionary of fields to values - if items are widgfields, converts them to comma separated strings"""
        if not self.fields:
            return {}
        string_dict = {}
        for field, value in self.fields.items():
            fld = field.to_str_tuple() if isinstance(field, skiboot.WidgField) else field
            val = value.to_str_tuple() if isinstance(value, skiboot.WidgField) else value
            string_dict[fld] = val
        return string_dict


    def original_fields(self):
        """Returns a dictionary of fields to values - with strings rather than widgfields"""
        if not self.fields:
            return {}
        string_dict = {}
        for field, value in self.fields.items():
            fld = str(field) if isinstance(field, skiboot.WidgField) else field
            val = str(value) if isinstance(value, skiboot.WidgField) else value
            string_dict[fld] = val
        return string_dict


    def original_args(self):
        """Returns a dictionary of arguments - with strings rather than
           widgfields, however idents remain skiboot Ident objects and boolean validate_option remains boolean"""
        string_dict = {}
        if self.widgfield_required:
            string_dict['widgfield'] = str(self.widgfield)
        if self.alternate_ident_required:
            string_dict['alternate_ident'] = self.alternate_ident
        if self.target_ident_required:
            string_dict['target_ident'] = self.target_ident
        if self.submit_required or self.submit_option_available:
            string_dict['fail_ident'] = self.fail_ident
        if self.allowed_callers_required:
            string_dict['allowed_callers'] = self.allowed_callers
        if self.submit_list:
            string_dict['submit_list'] = self.submit_list
        if self.submit_option_available:
            string_dict['submit_option'] = self.submit_option
        if self.validate_option_available:
            string_dict['validate_option'] = self.validate_option
            string_dict['validate_fail_ident'] = self.validate_fail_ident
        return string_dict


    def _submit_data(self, ident_list, skicall):
        "Calls the appropriate user submit_data function"
        # the call could have been passed to another project
        # so update skicall with this project
        proj_ident = ident_list[-1].proj
        this_project = skiboot.getproject(proj_ident)
        skicall.project = proj_ident
        skicall.proj_data = this_project.proj_data
        skicall.rootproject = this_project.rootproject

        # add project brief to submit_dict
        skicall.submit_dict['project_brief'] = this_project.brief
        tuple_ident_list = [ ident.to_tuple() for ident in ident_list ]
        try:
            skicall.ident_list = tuple_ident_list
            skicall.submit_list = self.submit_list.copy()
            result = this_project.submit_data(skicall)
        except (GoTo, FailPage, ServerError, ValidateError) as e:
            raise e
        except Exception:
            message = 'Error in submit_data called by responder ' + str(tuple_ident_list[-1]) + '\n'
            if skiboot.get_debug():
                exc_type, exc_value, exc_traceback = sys.exc_info()
                str_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for item in str_list:
                    message += item
            raise ServerError(message)
        return result



    def _check_allowed_callers(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Method to check allowed callers, raises a ValidateError if caller not in list of allowed callers
           Only useful for responders that have 'allowed_callers_required'"""
        if not self.allowed_callers_required:
            raise ValidateError(message="Call to _check_allowed_callers in responder, but no allowed_callers_required")
        if not self.allowed_callers: 
            return
        allowed_idents = []
        # convert idents or labels to idents
        for item in self.allowed_callers:
            ident = skiboot.find_ident(item, proj_ident=proj_ident)
            if ident:
                allowed_idents.append(ident)
            else:
                raise ValidateError(message="ident not recognised in responder allowed_callers list")
        if not allowed_idents:
            raise ValidateError(message="No recognised idents given in responder allowed_callers list")
        if len(ident_list) > 1:
            # get previous responder which called this one
            if ident_list[-2] not in allowed_idents:
                raise ValidateError(message="Previouse responder not in this responders allowed_callers list")
        else:
            # not a responder, so check caller_ident
            if caller_page is None:
                raise ValidateError(message="Caller page not known")
            if caller_page.ident not in allowed_idents:
                raise ValidateError(message="Caller page ident not in responder allowed_callers list")


    def _validate_fields(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Validates the fields specified in self.fields, returns validated form data, but does not change original form_data"
        # validation tests are stored in caller page
        if caller_page is None:
            raise ValidateError()
        if not self.field_options['widgfields']:
            raise ValidateError()
                 
       # create a copy of form_data which will hold validated data
        validated_form_data = form_data.copy()
        
        # for each field and value, validate the value, placing data into validated_form_data
        # If any value fails, then place any errors into e_list
        # e_list is a list of ErrorMessage exceptions with message to be displayed, and where to display them
        e_list = []
        # error_dict is a dictionary of errored widgfields: original value
        error_dict = {}

        for field in self.fields:
            # validate each field
            if field not in form_data:
                validated_form_data[field] = ''
            value = validated_form_data[field]
            validated_form_data[field], errors = caller_page.validate(field, value, skicall.environ, skicall.lang, validated_form_data, skicall.call_data, skicall.page_data)
            if errors:
                e_list.extend(errors)
                if field.s:
                    error_dict[field.s, field.w, field.f] = value
                else:
                    error_dict[field.w, field.f] = value

        # validated_form_data now holds new values
        # e_list holds errors occurred
        if e_list:
            # on validation errors, call the validate_fail_ident page, get final target template, and show the errors
            page = self.get_page_from_ident(self.validate_fail_ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata, error_dict)
            raise PageError(page, e_list)
        # so all ok, no error, but some values may be substituted, so return the validated form data
        return validated_form_data

    def get_page_from_ident(self, ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata, error_dict=None):
        """Calls the next responder or template page given by ident (which can be an ident, label or url)
           - and if a responder, calls its respond object to finally return a final target page."""
        if isinstance(ident, str) and ('/' in ident):
            # this is a URL
            return ident
        # ident is either a string ident or label
        thisident = skiboot.find_ident_or_url(ident, proj_ident)
        # thisident is either None, an Ident object or a url
        if thisident is None:
            raise ValidateError()
        if isinstance(thisident, str):
            # this is a URL
            return thisident
        # so thisident is an Ident object
        page = thisident.item()
        if not page:
            raise ValidateError()
        # could be a folder
        if page.page_type == 'Folder':
            page = page.default_page
            if not page:
                raise ValidateError()
        if hasattr(page, 'page_type') and page.page_type == 'RespondPage':
            # must call the pages respond object
            page = page.call_responder(skicall, form_data, caller_page, ident_list, rawformdata, error_dict)
        return page

 
    def get_target_page(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        return self.get_page_from_ident(self.target_ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


    def get_fail_page(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        return self.get_page_from_ident(self.fail_ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


    def get_alternate_page(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        "Gets the alternate page, if the alternate page has an ident, if it is an external url, get the redirector page with this url"
        return self.get_page_from_ident(self.alternate_ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)


    def raise_error_page(self, e_list, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Gets the page with fail_ident, sets error_messages and raises a PageError holding the page
           e_list is a list of ErrorMessage instances"""
        try:
            page = self.get_page_from_ident(self.fail_ident, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        except GoTo as e:
            e.e_list = e_list
            raise e  
        raise PageError(page, e_list)


    def __call__(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata, error_dict=None):
        "gets the project ident, and page messages and calls self._respond"

        if self.target_ident_required:
            skicall.submit_dict['target_ident'] = self.ident_for_user(self.target_ident)
        if self.submit_required or self.submit_option_available:
            skicall.submit_dict['fail_ident'] = self.ident_for_user(self.fail_ident)
        if self.alternate_ident_required:
            skicall.submit_dict['alternate_ident'] = self.ident_for_user(self.alternate_ident)
        # call self._respond
        try:
            page = self._respond(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        except GoTo as e:
            e.proj_ident=proj_ident
            raise e
        except ValidateError:
            raise
        except ServerError:
            raise
        except PageError:
            raise
        # Any other error, raise ServerError
        except Exception:
            message = "Uncaught exception in user code responder %s,%s" % ident_list[-1]
            if skiboot.get_debug():
                message += "\n"
                exc_type, exc_value, exc_traceback = sys.exc_info()
                str_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for item in str_list:
                    message += item
            raise ServerError(message)
        return page


    def _respond(self, skicall, form_data, caller_page, ident_list, proj_ident, rawformdata):
        """Should be overridden
        this method then returns the target page - or the ultimate page
        if the target is itself another Respond page
        form_data is a dictionary"""
        # return the target page
        try:
            return self.get_target_page(skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)
        except FailPage as e:
            # raises a PageError exception
            self.raise_error_page([e.errormessage], skicall, form_data, caller_page, ident_list, proj_ident, rawformdata)



# import all responders here

from .checkers import AllowedFields, PrettyFormData, StoreData, StoreDataKeyed, AllowStoreKeyed, AllowStore, Accept, AllowedAccept, PageData
from .submitters import SubmitData, SubmitCSS, GetDictionaryDefaults, FieldStoreSubmit, ColourSubstitute, SetCookies, SubmitJSON, SubmitPlainText, SubmitIterator, MediaQuery
from .navigators import CaseSwitch, EmptyGoto, EmptyCallDataGoto, DelCallDataItem, NoOperation


