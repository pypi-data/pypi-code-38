


"""This package contains classes to validate user input

The __init__ module defines the parent Validator class,
used by the modules within the package"""

from ..excepts import ErrorMessage
from ..skiboot import make_widgfield, getproject


class Validator(object):
    "The parent class of Validator objects"

    # arg_descriptions is a dictionary where every key can be accepted as an argument in the class __init__ **val_args
    # and the value is the default if the argument is not given
    arg_descriptions = {}

    @classmethod
    def args_exist(cls):
        return bool(cls.arg_descriptions)

    @classmethod
    def module_name(cls):
        return cls.__module__.split('.')[-1]


    def __init__(self, message='', message_ref='', displaywidget='', allowed_values=[], **val_args):
        """message is the message to be displayed in displaywidget if this validation fails
           if no message, but message_ref is given, then the textblock with message_ref will be shown.
           Note: if the displaywidget is in a section, then it will be of the form (section, widget_name)
           when imported into a page, if section is equal to the section_name - then it will be changed
           to the page_section_name.
        """
        self.message = message
        self.message_ref = message_ref
        self._displaywidget = make_widgfield(displaywidget, widgetonly=True)
        self.allowed_values = allowed_values
        # set self._val_args to be a dictionary of {arg:value}
        self._val_args = {}
        for arg in self.arg_descriptions:
            if arg in val_args:
                self[arg] = val_args[arg]
            else:
                self[arg] = self.arg_descriptions[arg]


    def get_message(self, lang, proj):
        if self.message:
            return self.message
        project = getproject(proj)
        if project is None:
            return ''
        text = project.textblocks.get_text(self.message_ref, lang)
        if text:
            return text
        return ''

    def get_displaywidget(self):
        return self._displaywidget

    def set_displaywidget(self, displaywidget):
        self._displaywidget = make_widgfield(displaywidget, widgetonly=True)

    displaywidget = property(get_displaywidget, set_displaywidget)

    @property
    def val_args(self):
        return self._val_args.copy()

    def __getitem__(self, arg_name):
        "Returns the value for the given argument name"
        if arg_name in self._val_args:
            return self._val_args[arg_name]

    def __setitem__(self, arg_name, value):
        "Sets an argument value, this is normally overriden to set the value correctly"
        if arg_name not in self.arg_descriptions:
            raise ValidateError(message = 'unrecognised value')
        # Overriden method should store the value in self._val_args
        # self._val_args[arg_name] = value

    def __contains__(self, arg_name):
        return arg_name in self._val_args


    def error_dict(self, widgfield, lang, proj):
        "Returns ErrorMessage"
        message = self.get_message(lang, proj)
        return ErrorMessage(message = message,
                            section  = self.displaywidget.s,
                            widget = self.displaywidget.w)

    def _add_to_call_data(self, widgfield, call_data, key=None):
        """On error adds 'failed_validation': { widgfieldtuple:[mod.validator, ...],..}.
              Note  widgfieldtuple has four elements, section, widget, name and dictionary key.
              section and dictionary key may be empty strings if not used"""
        if 'failed_validation' in call_data:
            failed_validation = call_data['failed_validation']
        else:
            failed_validation = {}
        if key:
            widgfieldtuple = widgfield.set_index(key).to_tuple()
        else:
            widgfieldtuple = widgfield.to_tuple()
        if widgfieldtuple in  failed_validation:
            val_list = failed_validation[widgfieldtuple]
        else:
            val_list = []
        # add this validator name
        validatorname = self.__str__()
        if validatorname not in val_list:
            val_list.append(validatorname)
        failed_validation[widgfieldtuple] = val_list
        call_data['failed_validation'] = failed_validation


    def __call__(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        """Tests allowed values, deals with dictionaries and calls _check, returns (item, error list)
           where error_list is a list of ErrorMessage instances"""
        if isinstance(item, dict):
            result_dict = {}
            error_list = []
            for key, val in item.items():
                if val in self.allowed_values:
                    result_dict[key] = val
                else:
                    newval, status = self._check(widgfield, val, environ, lang, form_data, call_data, caller_page_ident)
                    if status:
                        # item added to result_dict if no error
                        result_dict[key] = newval
                    else:
                        self._add_to_call_data(widgfield, call_data, key)
                        error_list.append(self.error_dict(widgfield, lang, caller_page_ident.proj))
            return result_dict, error_list
        if isinstance(item, list):
            result_list = []
            for val in item:
                if val in self.allowed_values:
                    result_list.append(val)
                else:
                    newval, status = self._check(widgfield, val, environ, lang, form_data, call_data, caller_page_ident)
                    if not status:
                        # On error return empty list
                        self._add_to_call_data(widgfield, call_data)
                        return [], [self.error_dict(widgfield, lang, caller_page_ident.proj)]
                    result_list.append(newval)
            return result_list, []
        if item in self.allowed_values:
            return item, []
        newval, status = self._check(widgfield, item, environ, lang, form_data, call_data, caller_page_ident)
        if not status:
            self._add_to_call_data(widgfield, call_data)
            return newval, [self.error_dict(widgfield, lang, caller_page_ident.proj)]
        return newval, []


    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        """Override this - return (newitemvalue, status) - for example (item, True) if validated, or ('', False) if not"""
        if not item:
            return '', False
        return item, True

    def __str__(self):
        module_name = self.__class__.__module__.split('.')[-1]
        return module_name + "." + self.__class__.__name__

