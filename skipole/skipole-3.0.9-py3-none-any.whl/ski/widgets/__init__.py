


"""This package contains modules of Widget classes which can be added to pages.

These Widgets inherit from the classes defined here, which themselves inherit
from tag.Part and tag.ClosedPart"""

import html, copy, collections, re, json, datetime
from string import Template

from .. import tag, skiboot
from ..excepts import ServerError, ValidateError

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')

#########################################################
# Field Arguments consist of a set of classes which
# act as the input for Widgets
#########################################################


# Each of these field arguments carries a value, which can be one
# of the following types:

# text
# url           - either a url string, label string or ident
# textblock_ref
# ident         - the ident of a page or folder
# element_ident - the string ident of a page element
# boolean
# integer
# widgfield
# cssclass
# cssstyle
# date          - python datetime.date object
# datetime      - python datetime.datetime object


class ParentFieldArg(object):
    "The parent class of FieldArg classes"

    def __init__(self, field_type, valdt=False, jsonset=False, senddict = False):
        """Acts as a parent to the field argument classes"""
        self.field_type = field_type
        # the name is usually set to the argument name when a widget is initialised,
        # but can be altered
        self.name = None
        self._value = None
        # val_list is a list of validators
        self.val_list = []
        # this is true if the expected value submitted by the browser is a dictionary
        self.senddict = senddict
        # True if validators can be added
        self.valdt = valdt
        # True if this field can be set by json
        self.jsonset = jsonset
        # True if field has a default css class or style, only valid for FieldArg
        self.cssclass = False
        self.cssstyle = False

    def _typematch(self, val, valtype):
        "Returns val, matched to valtype"
        try:
            if valtype == 'boolean':
                if isinstance(val, str):
                    if val.lower() == 'false':
                        return False
                return bool(val)
            elif valtype == 'ident':
                if val is 0:
                    return skiboot.make_ident(val)
                if not val:
                    return None
                return skiboot.make_ident(val)
            elif valtype == 'url':
                if val is 0:
                    sval = '0'
                else:
                    if not val:
                        return ''
                    sval = str(val)
                if '/' in sval:
                    # a url
                    return sval
                # could be an ident or label
                if ',' in sval:
                    labelparts = sval.split(',')
                    if labelparts[0].isalnum() and labelparts[1].isnumeric():
                        # probably an ident
                        ident = skiboot.make_ident(sval)
                        if ident is None:
                            return ''
                        return ident
                if '_' in sval:
                    # _ exists, but could still be a label
                    labelparts = sval.split('_')
                    if labelparts[0].isalnum() and labelparts[1].isnumeric():
                        # probably an ident
                        ident = skiboot.make_ident(sval)
                        if ident is not None:
                            return ident
                # a label
                return sval
            elif valtype == 'textblock_ref':
                if not val:
                    val = tag.TextBlock('')
                elif not isinstance(val, tag.TextBlock):
                    val = tag.TextBlock(str(val))
                # so val is a tag.TextBlock, set its parameters the same as self._value
                if isinstance(self._value, tag.TextBlock):
                    if (not val.failmessage_set()) and self._value.failmessage_set():
                        val.failmessage = self._value.failmessage
                    val.linebreaks = self._value.linebreaks
                    val.project = self._value.project
            elif valtype == 'integer':
                if not val:
                    return 0
                try:
                    int_val = int(val)
                except Exception:
                    raise ValidateError("Given value invalid, should be integer")
                return int_val
            elif valtype =='widgfield':
                if not val:
                    return ''
                return skiboot.make_widgfield(val)
            elif (valtype == 'text') or (valtype == 'cssclass') or (valtype == 'cssstyle'):
                if val is 0:
                    return '0'
                if not val:
                    return ''
                return str(val)
            elif valtype =='date':
                if isinstance(val, datetime.date):
                    return val
                elif not val:
                    return ''
                elif isinstance(val, str):
                    # only accept yyyy-mm-dd
                    try:
                        yearstring,monthstring,daystring = val.split('-')
                        year = int(yearstring)
                        month = int(monthstring)
                        day = int(daystring)
                        thisday = datetime.date(year,month,day)
                    except:
                        raise ValidateError("Given value invalid, should be yyyy-mm-dd or a datetime.date object")
                    return thisday
                else:
                    raise ValidateError("Given value invalid, should be a datetime.date object")
            elif valtype =='datetime':
                if not val:
                    return datetime.datetime.utcnow()
                elif isinstance(val, datetime.datetime):
                    return val
                else:
                    raise ValidateError("Given value invalid, should be a datetime.datetime object")
            else:
                raise ValidateError("Field type %s not recognised" % (valtype,))
        except Exception as e:
            if hasattr(e, 'message'):
                if e.message:
                    raise ValidateError(e.message)
            raise ValidateError("Given value invalid")
        return val

    @property
    def string_value(self):
        "The string version of the field value"
        return ''

    def __len__(self):
        return 1

    def __bool__(self):
        return bool(self._value)

    def add_validator(self, val):
        if self.valdt:
            self.val_list.append(val)

    def validate(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        """validates against the val_list returns item, empty list on success
           or empty item, errorlist on failure - however
           If item is a dictionary, successful items will have value, failed items will be empty
           If item is a list, any item failing will produce an empty item"""
        if not self.valdt:
            raise ValidateError('Invalid field to apply validator')
        if not self.val_list:
            if widgfield:
                message = "No validator has been set on field %s" % (widgfield,)
            elif self.name:
                message = "No validator has been set on field %s" % (self.name,)
            else:
                message = "No validator has been set on field"
            raise ValidateError(message)
        if isinstance(item, dict):
            error_list = []
            newdict = item.copy()
            # need to test each item in newdict against val list - but some items may pass
            # others may fail, so have to keep testing the passed ones against further tests
            for val in self.val_list:
                if not newdict:
                    break
                newdict, errors = val(widgfield, newdict, environ, lang, form_data, call_data, caller_page_ident)

                if errors:
                    error_list.extend(errors)
            # newdict is a dictionary of ok values, all other values in item are set to empty string
            for key, val in item.items():
                if key in newdict:
                    item[key] = newdict[key]
                else:
                    item[key] = ''
        else:
            for val in self.val_list:
                item, error_list = val(widgfield, item, environ, lang, form_data, call_data, caller_page_ident)
                if error_list:
                    break
        return item, error_list


class FieldArg(ParentFieldArg):
    "A basic single value field"

    def __init__(self, field_type, default='', valdt=False, jsonset=False, senddict = False):
        """
        default is the initial value of this field
        """
        ParentFieldArg.__init__(self, field_type, valdt=valdt, jsonset=jsonset, senddict=senddict)
        self.value = default
        # cssclass is True if this field represents a css class,
        # and can be set with defaults from defaults.json
        if field_type == 'cssclass':
            self.cssclass = True
        else:
            self.cssclass = False
        if field_type == 'cssstyle':
            self.cssstyle = True
        else:
            self.cssstyle = False

    def get_value(self):
        return self._value

    def set_value(self, val):
        self._value = self._typematch(val, self.field_type)

    value = property(get_value, set_value)

    @property
    def string_value(self):
        "Converts idents and WidgFields to strings, Textblocks to textref's"
        if self.field_type == 'textblock_ref':
            return self._value.textref
        if self.field_type == 'boolean':
            if self._value:
                return "True"
            else:
                return "False"
        if self._value is None:
            return ''
        return str(self._value)



class FieldArgList(ParentFieldArg):
    "A field which takes a list of items"

    def __init__(self, field_type, valdt=False, jsonset=False, senddict = False):
        """A list
        """
        ParentFieldArg.__init__(self, field_type, valdt=valdt, jsonset=jsonset, senddict=senddict)
        self._value = []

    def get_value(self):
        return self._value

    def set_value(self, val):
        # val should be a list
        self._value = []
        if not val:
            return
        elif (not isinstance(val, list)) and (not isinstance(val, tuple)):
            val = [val]
        for item in val:
            self._value.append(self._typematch(item, self.field_type))

    value = property(get_value, set_value)

    @property
    def string_value(self):
        "Converts list of idents and WidgFields to list of strings, Textblocks to textref's"
        value_list = []
        for val in self._value:
            if self.field_type == 'textblock_ref':
                value_list.append(val.textref)
            elif self.field_type == 'boolean':
                value_list.append(val)
            elif val is None:
                value_list.append('')
            else:
                value_list.append(str(val))
        return value_list

    def __len__(self):
        return len(self._value)

    def __bool__(self):
        "Returns boolean value of the list"
        return bool(self._value)


class FieldArgTable(ParentFieldArg):
    """A field which takes a table of items - a list of rows, each row being a list
       for example: [[r1c1, r1c2, r1c3], [r2c1, r2c2, r2c3], [r3c1, r3c2, r3c3]]
    """

    def __init__(self, field_type, valdt=False, jsonset=False, senddict = False):
        """
           field_type is a list or tuple of column types
        """
        ParentFieldArg.__init__(self, field_type, valdt=valdt, jsonset=jsonset, senddict=senddict)
        self.value = None


    @property
    def cols(self):
        return len(self.field_type)

    def get_value(self):
        return self._value

    def set_value(self, val):
        "Sets the value"
        # val should be a list of row lists
        # ie [[r1c1, r1c2, r1c3], [r2c1, r2c2, r2c3], [r3c1, r3c2, r3c3]]
        self._value = []
        if val is 0:
             val = [[0]]
        elif not val:
            return
        elif (not isinstance(val, list)) and (not isinstance(val, tuple)):
            val = [[val]] 
        cols = len(self.field_type)
        for row in val:
            if (not isinstance(row, list)) and (not isinstance(row, tuple)):
                row = [row]
            reqrow = []         # required row
            for idx, col in enumerate(row):
                if idx >= cols:
                    continue
                reqrow.append(self._typematch(col, self.field_type[idx]))
            # If the reqrow does not have enough column entries, pad it out
            if len(reqrow)<cols:
                for c in range(len(reqrow),cols):
                    reqrow.append(self._typematch(None, self.field_type[c]))
            # add the row to value
            self._value.append(reqrow)

    value = property(get_value, set_value)

    @property
    def string_value(self):
        "Converts list of idents and WidgFields to list of strings, Textblocks to textref's"
        table = []
        row_list = []
        for row in self._value:
            row_list = []
            for idx, item in enumerate(row):
                if self.field_type[idx] == 'textblock_ref':
                    row_list.append(item.textref)
                elif self.field_type[idx] == 'boolean':
                    if item:
                        row_list.append("True")
                    else:
                        row_list.append("False")
                elif item is None:
                    row_list.append('')
                else:
                    row_list.append(str(item))
            table.append(row_list)
        return table


    def __len__(self):
        "Returns the number of rows"
        return len(self._value)

    def __bool__(self):
        "Returns True if any item in the table is boolean true, otherwise returns False"
        for row in self._value:
            for col in row:
                if col:
                    return True
        return False


class FieldArgDict(ParentFieldArg):
    "A field which takes a dictionary of items"

    def __init__(self, field_type, valdt=False, jsonset=False, senddict = False):
        """A dictionary
        """
        ParentFieldArg.__init__(self, field_type, valdt=valdt, jsonset=jsonset, senddict=senddict)
        self._value = collections.OrderedDict()

    def __getitem__(self, index):
        return self._value[index]

    def __setitem__(self, index, val):
        self._value[index] = val

    def __delitem__(self, index):
        del self._value[index]

    def get_value(self):
        return self._value

    def set_value(self, val):
        # val should be a either a dictionary or an ordered dictionary
        self._value = collections.OrderedDict()
        if not val:
            return
        if not isinstance(val, dict):
            raise ValidateError("Invalid value")
        if isinstance(val, collections.OrderedDict):
            value_list = list(val.items())
        else:
            value_list = sorted(val.items(), key=lambda t: t[0])
        # value_list is a list of tuples [(key, value), ... ]
        typed_list = [ (key, self._typematch(value, self.field_type)) for key,value in value_list ]
        self._value = collections.OrderedDict(typed_list)

    value = property(get_value, set_value)

    @property
    def string_value(self):
        "Converts ordered dict of idents and WidgFields to ordered dict of strings, Textblocks to textref's"
        value = collections.OrderedDict()
        for key, val in self._value.items():
            if self.field_type == 'textblock_ref':
                value[key] = val.textref
            elif self.field_type == 'boolean':
                if val:
                    value[key] = "True"
                else:
                    value[key] = "False"
            elif val is None:
                value[key] = ''
            else:
                value[key] = str(val)
        return value

    def __len__(self):
        return len(self._value)

    def __bool__(self):
        "Returns True if any item in the dictionarey is boolean true, otherwise returns False"
        for val in self._value.values():
            if val:
                return True
        return False


def _create_validator_list(val_list, proj_ident):
    v_list = []
    for validator in val_list:
        val_dict = collections.OrderedDict()
        v_mod = validator.__module__.split(".")[-1]
        val_dict['class'] = "%s.%s" % (v_mod, validator.__class__.__name__)
        # now write the validator fields
        if validator.message:
            val_dict["message"] = validator.message
        if validator.message_ref:
            val_dict["message_ref"] = validator.message_ref
        if validator.displaywidget:
            val_dict["displaywidget"] = validator.displaywidget.to_tuple()
        allowed_values = validator.allowed_values
        if allowed_values:
            val_dict["allowed_values"] = tag.make_list(allowed_values, proj_ident)
        val_args = {}
        if validator.val_args:
            val_args = collections.OrderedDict(sorted(validator.val_args.items(), key=lambda t: t[0]))
            val_dict["val_args"] = tag.make_dictionary(val_args, proj_ident)
        v_list.append(val_dict)
    return v_list



############################################################
#
# The Widget class - subclassed to produce widgets
#
############################################################


class Widget(tag.Part):
    """
    Inherits from tag.Part, and should be subclassed to produce widgets.
    """

    # If this widget can contain further widgets or parts, these container locations will be held within
    # tuple _container, which is a tuple of location tuples, giving the location of the container within the widget
    # that is, the location tuple is relative to the widget, not the page.

    # This container is the widget itself
    # _container=((), )

    _container = None
    # _container is set to None if no container is available in the widget

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=False

    # display_errors is a class attribute, True if this widget accepts and displays error messages, False otherwise
    display_errors = True

    # error_location is either None, or an integer or tuple, pointing to an error location,
    # if it is not None, then show_error will show the error at that location
    error_location = None

    arg_descriptions = {'widget_class':FieldArg("cssclass", "", jsonset=True)}

    # All widgets automatically have a show, show_error, widget_class and widget_style field arguments

    def __init__(self, name=None, tag_name="div", brief='', **field_args):

        if not brief:
            brief = self.__class__.__name__

        tag.Part.__init__(self, tag_name=tag_name, text='', show=True, brief=brief, hide_if_empty=False)
        self.name = name
        # create self.fields which is a dictionary of {field_arg:FieldArg,...}
        # for example - in this case field_arg is the string 'widget_class', and value is
        # a deep copy of the FieldArg object created by FieldArg("cssclass", "", jsonset=True)
        self.fields = copy.deepcopy(self.arg_descriptions)
        # ALL Widgets have a show and widget_class arguments
        if 'show' not in self.fields:
            self.fields['show'] = FieldArg("boolean", True)
        if 'widget_class' not in self.fields:
            self.fields['widget_class'] = FieldArg("cssclass", '', jsonset=True)
        if 'widget_style' not in self.fields:
            self.fields['widget_style'] = FieldArg("cssstyle", '', jsonset=True)
        # if widget has display_errors set True, then they also have a show_error and clear_error argument
        if self.display_errors:
            if 'show_error' not in self.fields:
                self.fields['show_error'] = FieldArg("text", '', jsonset=True)
            if 'clear_error' not in self.fields:
                self.fields['clear_error'] = FieldArg("boolean", False, jsonset=True )
        # Each FieldArg object has a name and value.
        # **field_args is a dictionary of {field_arg:value, ...}  - in this example it could be
        # {"widget_class": "css_class_name',...}
        # For each FieldArg object in self.fields, if its field_arg does not appear in the **field_args, then its value will be that
        # given in the class attribute 'default'. If it does appear, then its
        # value is set to that given in **field_args
        for field_arg, field in self.fields.items():
            # initially set field names to be the same as field argument
            if self.name:
                field.name = field_arg
            else:
                # If this widget has no name - it is set inside another. To avoid name clashes when inserting one widget in another,
                # all names in this widget are initially set to start with an underscore"
                field.name = '_' + field_arg
            # set field values to be the values given in **field_args (note: field_args is plural to differentiate)
            if field_arg in field_args:
                field.value = field_args[field_arg]
        # set initial self.error_message to the value given in show_error argument
        if self.display_errors and self.fields['show_error'].value:
            self.error_message = self.fields['show_error'].value
        else:
            self.error_message = ''

        # the widget show is set by the show argument
        self.show = self.fields["show"].value

        # Creates a dictionary of names against field arguments in self._names
        self._create_name_dict()

        # If the widget is in error status, this becomes True
        self.error_status = False

    @classmethod
    def module_name(cls):
        return cls.__module__.split('.')[-1]

    def _create_name_dict(self):
        "Creates a dictionary of names against field arguments"
        self._names = { field.name:field_arg for field_arg, field in self.fields.items() }


    def get_container_parts(self, index):
        """"index is the index in the self._container list
           If index out of range, return None"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        return container_part.parts


    def append_to_container(self, index, value):
        """appends value into the container, in this case index is not the part location,
           it is the index in the self._container list"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        if (len(container_part.parts) == 1) and (container_part.parts[0] == ''):
            # replace the empty string
            container_part.parts[0] = value
        else:
            # append the value to the container
            container_part.append(value)


    def is_container_empty(self, index):
        """"index is the index in the self._container list
           If index out of range, return None, otherwise True if empty, False if not"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        if container_part.parts:
            # has contents
            if (len(container_part.parts) == 1) and (container_part.parts[0] == ""):
                return True
        else:
            return True
        return False


    @classmethod
    def can_contain(cls):
        if cls._container is None:
            return False
        return True


    def container_part(self, index):
        "Returns element, genearlly a div which is the container holding element, used internally"
        if self._container is None:
            return
        if (index < 0) or (index >= len(self._container)):
            return
        location = self._container[index]
        if location == ():
            # the container is the widget itself
            return self
        return self.get_location_value(location)


    def set_in_container(self, index, location, value):
        """Sets a value within a container, index is the container index
           and location is an integer or tuple within the container.
           for example index=0, location=(0,1) referes to location (0,1) inside container 0"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        container_part.set_location_value(location, value)


    def insert_into_container(self, index, position, value):
        """Inserts a value within a container at position, index is the container index
           and position is an integer within the container.
           for example index=0, position=0 referes to the first position inside container 0"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        if not isinstance(position, int):
            return
        container_part.insert(position, value)        


    def get_from_container(self, index, location):
        """gets the value from within a container, index is the container index
           and location is an integer or tuple within the container.
           for example index=0, location=(0,1) referes to location (0,1) inside container 0"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        # empty container contains an empty string
        if self.is_container_empty(index) and ((not location) or (location == (0,)) or (location == [0])):
            return ''
        return container_part.get_location_value(location)


    def del_from_container(self, index, location):
        """Deletes the value from within a container, index is the container index
           and location is an integer or tuple within the container.
           for example index=0, location=(0,1) referes to location (0,1) inside container 0"""
        container_part = self.container_part(index)
        if container_part is None:
            return
        container_part.del_location_value(location)


    @classmethod
    def len_containers(cls):
        "Returns number of containers"
        if cls._container is None:
            return 0
        return len(cls._container)


    @classmethod
    def get_container_loc(cls, index):
        """Returns the location tuple of the container, in this case index is not
           the part location, it is the index in the self._container list"""
        if cls._container is None:
            return
        if (index < 0) or (index >= len(cls._container)):
            return
        return cls._container[index]


    @classmethod
    def get_container_string_loc(cls, index):
        """Returns the string location of the container, in this case index is not
           the part location, it is the index in the self._container list"""
        if cls._container is None:
            return
        if (index < 0) or (index >= len(cls._container)):
            return
        location = cls._container[index]
        if not location:
            return ''
        return '-'.join(str(i) for i in location)


    def get_parent_widget(self, page_or_section):
        """Returns the parent widget and container index of this widget"""
        section_name, parent_widget_name, parent_container = self.embedded
        if not parent_widget_name:
            return None, None
        # Find parent widget of this widget
        widgets_dict = page_or_section.widgets
        if parent_widget_name in widgets_dict:
            return widgets_dict[parent_widget_name], parent_container
        else:
            return None, None


    @classmethod
    def field_arguments_single(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset, cssclass, cssstyle]
        sorted by field argument"""
        args = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArg):
                args.append( [arg, item.field_type, item.valdt, item.jsonset, item.cssclass, item.cssstyle] )
        if 'show' not in cls.arg_descriptions:
            args.append( ['show', 'boolean', False, False, False, False] )
        if 'widget_class' not in cls.arg_descriptions:
            args.append( ['widget_class', 'cssclass', False, True, True, False] )
        if 'widget_style' not in cls.arg_descriptions:
            args.append( ['widget_style', 'cssstyle', False, True, False, True] )
        if cls.display_errors and ('show_error' not in cls.arg_descriptions):
            args.append( ['show_error', 'text', False, True, False, False] )
        if cls.display_errors and ('clear_error' not in cls.arg_descriptions):
            args.append( ['clear_error', 'boolean', False, True, False, False] )
        args.sort(key=lambda row: row[0])
        return args


    @classmethod
    def field_arguments_list(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument"""
        arg_list = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgList):
                arg_list.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_list:
            arg_list.sort(key=lambda row: row[0])
        return arg_list


    @classmethod
    def field_arguments_table(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument.
        field type is a list of column types"""
        arg_table = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgTable):
                arg_table.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_table:
            arg_table.sort(key=lambda row: row[0])
        return arg_table


    @classmethod
    def field_arguments_dictionary(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument"""
        arg_dict = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgDict):
                arg_dict.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_dict:
            arg_dict.sort(key=lambda row: row[0])
        return arg_dict


    @classmethod
    def field_arguments(cls):
        """Returns a list of field args"""
        args = []
        for arg in cls.arg_descriptions:
            args.append(arg)
        if 'show' not in cls.arg_descriptions:
            args.append('show')
        if 'widget_class' not in cls.arg_descriptions:
            args.append('widget_class')
        if 'widget_style' not in cls.arg_descriptions:
            args.append('widget_style')
        if cls.display_errors and ('show_error' not in cls.arg_descriptions):
            args.append('show_error')
        if cls.display_errors and ('clear_error' not in cls.arg_descriptions):
            args.append('clear_error')
        args.sort()
        return args


    def field_arg_info(self, dataarg):
        """Returns (field name, fieldvalue, str_fieldvalue, fieldarg class string, field type, field.valdt, field.jsonset, field.cssclass, field.cssstyle)
           where fieldarg class string is one of the strings 'args', 'arg_list', 'arg_table', 'arg_dict'
           returns an empty tuple if not found"""
        if not dataarg in self.fields:
            return ()
        field = self.fields[dataarg]
        if isinstance(field, FieldArg):
            fieldarg = 'args'
        elif isinstance(field, FieldArgList):
            fieldarg = 'arg_list'
        elif isinstance(field, FieldArgTable):
            fieldarg = 'arg_table'
        elif isinstance(field, FieldArgDict):
            fieldarg = 'arg_dict'
        else:
            return ()
        return (field.name, field.value, field.string_value, fieldarg, field.field_type, field.valdt, field.jsonset, field.cssclass, field.cssstyle)


    def field_arg_val_list(self, dataarg):
        "Returns the list of validators attached to this field"
        if not dataarg in self.fields:
            return []
        field = self.fields[dataarg]
        return field.val_list

    def changed_names(self):
        "Returns a dictionary of those arguments whose name is different to the argument"
        return {a:n for n,a in self._names.items() if n != a}


    def _build(self, page, ident_list, environ, call_data, lang):
        "Called by update - the dynamic parts of the widget should be created here"
        return


    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded):
        """Runs self._build, then update all sub widgets"""
        if not self.show:
            return
        if placename:
            self.placename = placename
        if not self.ident_string:
            # item is a dynamic part, newly created within a widget
            self.embedded = embedded
            self.ident_string = ident_string
        if self.name:
            # parts beneath this named widget will be embedded
            embedded_parts = (self.embedded[0], self.name, None)
        else:
            embedded_parts = self.embedded
        if self._error:
            if isinstance(self._error, TextBlock):
                self._error.update(page, ident_list, environ, call_data, lang, self.ident_string, self.placename, embedded_parts)
            return
        # build the widget
        # the class attribute is set by 'widget_class'
        if self.fields['widget_class'].value:
            self.update_attribs({'class':self.fields['widget_class'].value})
        if self.fields['widget_style'].value:
            self.update_attribs({'style':self.fields['widget_style'].value})
        # Insert this widgets id
        self.insert_id()
        # insert further parts according to each widget build
        self._build(page, ident_list, environ, call_data, lang)
        # update all parts, including those created by self._build
        try:
            for index, part in enumerate(self.parts):
                part_ident_string = self.ident_string + "-" + str(index)
                if hasattr(part, "update"):
                    part.update(page, ident_list, environ, call_data, lang, part_ident_string, self.placename, embedded_parts)
        except ValidateError as e:
            if not e.ident_list:
                e.ident_list = ident_list
            raise


    def _make_fieldvalues(self, *fieldargs, **otherparams):
        "Creates a javascript string of fieldvalues, which can be used by _build_js"
        fieldvalues = {}
        for farg in fieldargs:
            fieldvalues[farg] = self.get_field_value(farg)
        fieldvalues.update(otherparams)
        if not fieldvalues:
            return ''
        return """  SKIPOLE.widgets["{ident}"].fieldvalues={fieldvalues};
""".format(ident=self.get_id(), fieldvalues=json.dumps(fieldvalues))

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Called by make_js, and should be overwritten by widgets to set widget specific javascript
           into the page.  This javascript is added last, after all other widget updates are done, and
           this function is only called if the widget has a name."""
        return ''

    def make_js(self, page, ident_list, environ, call_data, lang):
        """Called by page.update - after parts update is called.
           Makes javascript for this widget, calls make_js for sub parts/widgets, then if widget
           has a name, calls self._build_js to build further javascript for this widget"""
        if self._error:
            return
        if not self.show:
            return
        # First, call make_js of sub widgets
        tag.Part.make_js(self, page, ident_list, environ, call_data, lang)

        if not self.name:
            return

        # js_validators is a class attribute, True is javascript validation is enabled
        if self.js_validators and not skiboot.get_debug():
            # Add the javascript validators for this widget,
            # adds a line for each widgfield that has validators
            # SKIPOLE.validators[widgfield] = [[...], [...], ... ]
            # where each of the lists correspond to a validator for this widgfield
            # [val_mod, val_class, message, [allowed values], {args}]
            for field_arg, field in self.fields.items():
                all_validators_list = []
                val_list = field.val_list
                if not val_list:
                    # no validators to add on this field
                    continue
                widgfield = self.name + ':' + field.name
                if self.placename:
                    widgfield = self.placename + '-' + widgfield
                for val in val_list:
                    one_validator_list = []
                    one_validator_list.append(val.__class__.__module__.split(".")[-1])
                    one_validator_list.append(val.__class__.__name__)
                    message = val.get_message(lang, page.proj_ident)
                    if not message:
                        message = ""
                    one_validator_list.append(message)
                    one_validator_list.append(val.allowed_values)
                    one_validator_list.append(val.val_args)
                    one_validator_list.append(str(val.displaywidget))
                    one_validator_list
                    all_validators_list.append(one_validator_list)
                if all_validators_list:
                    v = "  SKIPOLE.validators[\"%s\"] = " % (widgfield,)
                    v += json.dumps(all_validators_list)
                    page.add_javascript(v+';\n')

        # information about the widget, its id, module, class and arguments
        j = Template("""  SKIPOLE.widgets["$widgident"] = new SKIPOLE["$widg_mod"]["$widg_class"]("$widgident", $error_message, $widg_fields);
""")
        page.add_javascript(j.substitute(widgident = self.get_id(),
                                         widg_mod=self.__class__.__module__.split(".")[-1],
                                         widg_class=self.__class__.__name__,
                                         error_message = json.dumps(self.error_message),
                                         widg_fields=str(self.changed_names())))

        # and add widget specific json
        contents = self._build_js(page, ident_list, environ, call_data, lang)
        if contents:
            page.add_javascript(contents)


    def set_placename(self, section_name, placename):
        "Widgets in sections with displayname validators need displaynames to change"
        self.placename = placename
        for field in self.fields.values():
            if field.val_list:
                # the field has a list of validators
                val_list = field.val_list
                for val in val_list:
                    # If the displaywidget for a validator is equal to the section_name
                    # replace it with the placename
                    if val.displaywidget.s == section_name:
                        val.displaywidget = val.displaywidget._replace(s=placename)

    def mark_field_in_error(self, errorfieldname):
        "Marks a given field as an errored field, for example, by setting it red, child classes may optionally implement this"
        pass

    def _error_build(self, message):
        """Overwritten by child widgets if required, note this is run before the _build method
           and should set any appropriate flags that _build will then use to build the widget"""
        if self.error_location is None:
            # no error location set, so replace entire widget by the message
            if message:
                self._error = message


    def show_error(self, message=''):
        """Shows error message"""

        if not self.show:
            return
        if not self.display_errors:
            return
        self.error_status = True
        # if this is a named widget update attribute with data-status="error"
        if self.name:
            self.update_attribs({'data-status':'error'})
        if not message:
            message = self.error_message
        if self.error_location is not None:
            error_part = self.get_location_value(self.error_location)
            if hasattr(error_part, 'show_error'):
                error_part.show_error(message)
            elif message:
                self.set_location_value(self.error_location, message)
        # and call _error_build
        self._error_build(message)
    
    def field_list(self):
        "Returns a list of fields, ordered alphabetically by field argument"
        return [ self.fields[key] for key in sorted(self.fields.keys())]


    def get_field(self, name):
        "Given a name, get the associated field"
        if not name:
            return
        if name in self._names:
            field_arg = self._names[name]
            if field_arg in self.fields:
                field = self.fields[field_arg]
                if field.name == name:
                    return field
        # failed to find field, refresh self._names and try again
        self._create_name_dict()
        if name in self._names:
            field_arg = self._names[name]
            if field_arg in self.fields:
                field = self.fields[field_arg]
                if field.name == name:
                    return field

    def get_field_arg(self, name):
        "Given a name, get the associated field_arg, returns None if name not found"
        if name in self._names:
            return self._names[name]


    def get_field_valdt(self, name):
        "Given a name, get field.valdt status, True if validators can be added, False if not"
        field = self.get_field(name)
        if field is None:
            return False
        return field.valdt


    def is_fieldname_in_widget(self, name):
        field = self.get_field(name)
        if field is None:
            return False
        return True


    def is_senddict(self, name):
        field = self.get_field(name)
        if field is None:
            raise ValidateError(message = "Widget %s field name %s not recognised" % (self.name, name))
        return field.senddict
        

    def add_validator(self, field_name, val):
        "adds a validator to the field with the given name"
        f = self.get_field(field_name)
        if f is not None:
            f.add_validator(val)

    def validate(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        "Calls the field validate method, returns item, error_list"
        f = self.get_field(widgfield.f)
        if f is None:
            raise ValidateError(message = "Field name not recognised")
        return f.validate(widgfield, item, environ, lang, form_data, call_data, caller_page_ident)

    def get_value(self, name):
        """If this widget contains fields, then this should return a field
        content, given its name.  If name not found, return None
        """
        field = self.get_field(name)
        if field is not None:
            return field.value

    def set_value(self, name, value):
        """If this widget contains fields, then this should set a field
           content, given its name."""
        if not name:
            return
        if '-' in name:
            self.set_single_multivalue(name, value)
            return
        if (name == 'show_error') or (('show_error' in self.fields) and (name == self.fields['show_error'].name)):
            # the show_error field is special as it accepts both a given field name
            # and the name 'show_error'
            if value:
                self.show_error(message=value)
            else:
                self.show_error()
            return
        field = self.get_field(name)
        if field is None:
            return
        field.value = value
        if name == self.fields["show"].name:
            self.show = bool(value)
        if name == self.fields['widget_class'].name:
            if value:
                self.update_attribs({'class':value})
            else:
                self.del_one_attrib('class')
        if name == self.fields['widget_style'].name:
            if value:
                self.update_attribs({'style':value})
            else:
                self.del_one_attrib('style')

        

    def set_single_multivalue(self, name, value):
        """If a field name is given with a -, then after the dash must be an index
           This sets the single value with the appropriate index"""
        if '-' not in name: return
        fname, findex = name.split('-')
        field = self.get_field(fname)
        if field is None:
            return
        if not isinstance(field, FieldArgDict):
            return
        field[findex] = value

    def _set_data(self, *loc):
        """Clears attributes of the part at location loc, then sets n data- atts"""
        # get the number of fields with arguments data1, data2,..
        n = 0   # increments for each data field
        m = 0   # records max number
        for field_arg in self.fields:
            if len(field_arg) < 5: continue
            if field_arg.startswith('data'):
                endnumber = field_arg[4:]
                try:
                    num = int(endnumber)
                except Exception:
                    continue
                if not num: continue
                if num > m:
                    m = num
                n += 1
        if not n:
            # no field_arg's with name data1,...
            return
        if n != m:
            raise ServerError("field data values are mismatched")
        if loc:
            part = self.get_location_value(loc)
        else:
            part = self
        part.del_attribs()
        for idx in range(n):
            # field_arg is data1, data2 etc..
            field_arg = 'data' + str(idx+1)
            if field_arg not in self.fields:
                raise ServerError("Field argument %s does not exist in this widget." % (field_arg,))
            if self.get_field_value(field_arg):
                key = 'data-' + self.get_formname(field_arg)
                part.update_attribs({key:str(self.get_field_value(field_arg))})

    def set_field_value(self, field_arg, value):
        """If this widget contains fields, then this should set a field
           content, given its field_arg"""
        if not field_arg:
            return
        if field_arg not in self.fields:
            return
        field = self.fields[field_arg]
        if field is None:
            return
        field.value = value
        if field_arg == "show":
            self.show = field.value
        if field_arg == 'widget_class':
            if value:
                self.update_attribs({'class':value})
            else:
                self.del_one_attrib('class')
        if field_arg == 'widget_style':
            if value:
                self.update_attribs({'style':value})
            else:
                self.del_one_attrib('style')

        if field_arg == 'show_error':
            self.error_message = field.value

    def get_field_value(self, field_arg):
        """If this widget contains fields, then this should get a field
           content, given its field_arg"""
        if not field_arg:
             raise ValidateError(message="A valid field argument is required")
        if field_arg not in self.fields:
            raise ValidateError(message="Field argument %s not recognised in %s" % (field_arg, self.__class__.__name__))
        return self.fields[field_arg].value

    def set_name(self, field_arg, name):
        """Sets a field name, raises ValidateError if the name already exists in the widget"""
        # check name does not already exist
        if not name:
            return
        if name.lower() == "ident":
            raise ValidateError(message="Field name ident is used internally and is not allowed")
        if name == 'tag_name':
            raise ValidateError(message="Field name tag_name is used internally and is not allowed")
        if name == 'error_message':
            raise ValidateError(message="Field name error_message is used internally and is not allowed")
        if _AN.search(name):
            raise ValidateError(message="Invalid name - letters, numbers, underscore only.")
        if field_arg not in self.fields:
            return
        if self.fields[field_arg].name == name:
            # no change
            return
        # check name does not already exist in the widget
        if self.is_fieldname_in_widget(name):
            # a field has been found
            raise ValidateError(message="This field name already exists in the widget")
        # set the name
        self.fields[field_arg].name = name
        # refresh self._names
        self._create_name_dict()

    def get_name(self, field_arg):
        """Gets a field name"""
        if not field_arg:
             raise ValidateError(message="A valid field argument is required")
        if field_arg not in self.fields:
            raise ValidateError(message="Field argument not recognised")
        return self.fields[field_arg].name

    def get_formname(self, field_arg):
        """Returns the string 'sectionname-widgetname:fieldname', used to set submission field names"""
        fieldname = self.get_name(field_arg)
        if not fieldname:
            raise ValidateError(message="Invalid field name")
        if self.name:
            fieldname = self.name + ':' + fieldname
        elif self.embedded[1]:
            fieldname = self.embedded[1] + ':' + fieldname
        else:
            raise ValidateError(message="Widget \"%s\", has no name." % (self.__class__.__name__,))
        if self.placename:
            fieldname = self.placename + '-' + fieldname
        return fieldname


    def add_hiddens(self, form, page=None):
        "Used to add ident and four hidden fields to a form, requires this widget to have these hidden fields"
        # all submissions always have an 'ident' hidden field to provide the ident of the calling page
        if page is not None:
            form.append(tag.ClosedPart(tag_name="input",
                                   attribs ={"name":'ident',
                                             "value":page.ident_data_string,
                                             "type":"hidden"}))
        # hidden field on the form
        if self.get_field_value('hidden_field1'):
            form.append(tag.ClosedPart(tag_name="input",
                                       attribs ={"name":self.get_formname('hidden_field1'),
                                                 "value":self.get_field_value('hidden_field1'),
                                                 "type":"hidden"}))

        # Second hidden field on the form
        if self.get_field_value('hidden_field2'):
            form.append(tag.ClosedPart(tag_name="input",
                                       attribs ={"name":self.get_formname('hidden_field2'),
                                                 "value":self.get_field_value('hidden_field2'),
                                                 "type":"hidden"}))

        # third hidden field on the form
        if self.get_field_value('hidden_field3'):
            form.append(tag.ClosedPart(tag_name="input",
                                       attribs ={"name":self.get_formname('hidden_field3'),
                                                 "value":self.get_field_value('hidden_field3'),
                                                 "type":"hidden"}))
        # fourth hidden field on the form
        if self.get_field_value('hidden_field4'):
            form.append(tag.ClosedPart(tag_name="input",
                                       attribs ={"name":self.get_formname('hidden_field4'),
                                                 "value":self.get_field_value('hidden_field4'),
                                                 "type":"hidden"}))


    def widget_hide(self, hide):
        "Hides widget if not error"
        if (not self.error_status) and hide:
            self.set_hide()
        else:
            self.set_block()


    def __repr__(self):
        if self.name:
            return self.__class__.__name__ + '(' + self.name + ')'
        else:
            return self.__class__.__name__


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """<div>  <!-- with widget id and class widget_class -->
</div>"""


    def __str__(self):
        """Returns a text string to illustrate the widget"""
        return self.description()


    def outline(self, proj_ident):
        part_dict = collections.OrderedDict()
        w_mod = self.__module__.split(".")[-1]
        part_dict['class'] = "%s.%s" % (w_mod, self.__class__.__name__)
        if self.name:
            part_dict["name"] = self.name
        if self.brief:
            part_dict["brief"] = self.brief
        fields_dict = {f_arg: f.value for f_arg, f in self.fields.items()}
        if fields_dict:
            ordered_fields_dict = collections.OrderedDict(sorted(fields_dict.items(), key=lambda t: t[0]))
            part_dict["fields"] = tag.make_dictionary(ordered_fields_dict, proj_ident)
        # set widget containers
        if self.can_contain():
            for cont in range(self.len_containers()):
                container_name = "container_%s" % (cont,)
                # get list of parts in the container
                parts = self.get_container_parts(cont)
                item_list = []
                for item in parts:
                    if hasattr(item, 'outline'):
                        item_list.append(item.outline(proj_ident))
                    else:
                        # must be a text string
                        item_list.append(['Text', str(item)])
                part_dict[container_name] = item_list
        # set widget field names
        if fields_dict:
            # check if any field name is not equal to f_arg
            fields_names = {f_arg:f.name for f_arg, f in self.fields.items() if f_arg != f.name}
            if fields_names:
                ordered_fields_names = collections.OrderedDict(sorted(fields_names.items(), key=lambda t: t[0]))
                part_dict["set_names"] = tag.make_dictionary(ordered_fields_names, proj_ident)
            # set widget validators
            field_validators = {f.name:f.val_list for f in self.fields.values() if f.val_list}
            if field_validators:
                val_dict = {}
                for name, val_list in field_validators.items():
                    val_dict[name] = _create_validator_list(val_list, proj_ident)
                part_dict["validators"] = collections.OrderedDict(sorted(val_dict.items(), key=lambda t: t[0]))
        return ['Widget', part_dict]





class ClosedWidget(tag.ClosedPart):
    """
    Inherits from tag.ClosedPart, and should be subclassed to produce widgets.
    """

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=False

    # display_errors is a class attribute, True if this widget accepts and displays error messages, False otherwise
    display_errors = True

    # always empty list and unused
    _container=[]

    # always None and unused
    error_location = None

    arg_descriptions = {'widget_class':FieldArg("cssclass", "", jsonset=True)}


    def __init__(self, name=None, tag_name="link", brief='', **field_args):
        if not brief:
            brief = self.__class__.__name__
        tag.ClosedPart.__init__(self, tag_name=tag_name, show=True, brief=brief)
        self.name = name
        # Get fields from arg_descriptions
        self.fields = copy.deepcopy(self.arg_descriptions)
        # ALL Widgets have a show, widget_class and widget_style arguments
        if 'show' not in self.fields:
            self.fields['show'] = FieldArg("boolean", True)
        if 'widget_class' not in self.fields:
            self.fields['widget_class'] = FieldArg("cssclass", "", jsonset=True)
        if 'widget_style' not in self.fields:
            self.fields['widget_style'] = FieldArg("cssstyle", '', jsonset=True)
        # if widget has display_errors set True, then they also have a show_error and clear_error argument
        if self.display_errors:
            if 'show_error' not in self.fields:
                self.fields['show_error'] = FieldArg("text", '', jsonset=True)
            if 'clear_error' not in self.fields:
                self.fields['clear_error'] = FieldArg("boolean", False, jsonset=True )
        for field_arg, field in self.fields.items():
            # initially set field names to be the same as field argument
            if self.name:
                field.name = field_arg
            else:
                # If this widget has no name - it is set inside another. To avoid name clashes when inserting one widget in another,
                # all names in this widget are initially set to start with an underscore"
                field.name = '_' + field_arg
            # set field values to be the values given in **field_args
            if field_arg in field_args:
                field.value = field_args[field_arg]

        # Creates a dictionary of names against field arguments in self._names
        self._create_name_dict()

        # Unlike a Widget, does not use error_location or _container
        # the widget show is set by the show argument
        self.show = self.fields["show"].value

        # set initial self.error_message to the value given in show_error argument
        if self.display_errors and self.fields['show_error'].value:
            self.error_message = self.fields['show_error'].value
        else:
            self.error_message = ''

        # If the widget is in error status, this becomes True
        self.error_status = False

    @classmethod
    def module_name(cls):
        return cls.__module__.split('.')[-1]

    @classmethod
    def can_contain(cls):
        # Always False, only provided for consistancy with Widget
        return False

    @classmethod
    def len_containers(cls):
        return 0

    def get_parent_widget(self, page_or_section):
        """Returns the parent widget and container  index of this widget"""
        section_name, parent_widget_name, parent_container = self.embedded
        if not parent_widget_name:
            return None, None
        # Find parent widget of this widget
        widgets_dict = page_or_section.widgets
        if parent_widget_name in widgets_dict:
            return widgets_dict[parent_widget_name], parent_container
        else:
            return None, None

    def _create_name_dict(self):
        "Creates a dictionary of names against field arguments"
        self._names = { field.name:field_arg for field_arg, field in self.fields.items() }


    @classmethod
    def field_arguments_single(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset, cssclass, cssstyle]
        sorted by field argument"""
        args = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArg):
                args.append( [arg, item.field_type, item.valdt, item.jsonset, item.cssclass, item.cssstyle] )
        if 'show' not in cls.arg_descriptions:
            args.append( ['show', 'boolean', False, False, False, False] )
        if 'widget_class' not in cls.arg_descriptions:
            args.append( ['widget_class', 'cssclass', False, True, True, False] )
        if 'widget_style' not in cls.arg_descriptions:
            args.append( ['widget_style', 'cssstyle', False, True, False, True] )
        if cls.display_errors and ('show_error' not in cls.arg_descriptions):
            args.append( ['show_error', 'text', False, True, False, False] )
        if cls.display_errors and ('clear_error' not in cls.arg_descriptions):
            args.append( ['clear_error', 'boolean', False, True, False, False] )
        args.sort(key=lambda row: row[0])
        return args


    @classmethod
    def field_arguments_list(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument"""
        arg_list = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgList):
                arg_list.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_list:
            arg_list.sort(key=lambda row: row[0])
        return arg_list


    @classmethod
    def field_arguments_table(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument.
        field type is a list of column types"""
        arg_table = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgTable):
                arg_table.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_table:
            arg_table.sort(key=lambda row: row[0])
        return arg_table


    @classmethod
    def field_arguments_dictionary(cls):
        """Returns a list of lists.
        The inner list consists of: [ field arg, field type, valdt, jsonset].
        sorted by field argument"""
        arg_dict = []
        for arg, item in cls.arg_descriptions.items():
            if isinstance(item, FieldArgDict):
                arg_dict.append( [arg, item.field_type, item.valdt, item.jsonset] )
        if arg_dict:
            arg_dict.sort(key=lambda row: row[0])
        return arg_dict


    @classmethod
    def field_arguments(cls):
        """Returns a list of field args"""
        args = []
        for arg in cls.arg_descriptions:
            args.append(arg)
        if 'show' not in cls.arg_descriptions:
            args.append('show')
        if 'widget_class' not in cls.arg_descriptions:
            args.append('widget_class')
        if 'widget_style' not in cls.arg_descriptions:
            args.append('widget_style')
        if cls.display_errors and ('show_error' not in cls.arg_descriptions):
            args.append('show_error')
        if cls.display_errors and ('clear_error' not in cls.arg_descriptions):
            args.append('clear_error')
        args.sort()
        return args


    def field_arg_info(self, dataarg):
        """Returns (field name, fieldvalue, str_fieldvalue, fieldarg class string, field type, field.valdt, field.jsonset, field.cssclass, field.csstyle)
           where fieldarg class string is one of the strings 'args', 'arg_list', 'arg_table', 'arg_dict'
           returns an empty tuple if not found"""
        if not dataarg in self.fields:
            return ()
        field = self.fields[dataarg]
        if isinstance(field, FieldArg):
            fieldarg = 'args'
        elif isinstance(field, FieldArgList):
            fieldarg = 'arg_list'
        elif isinstance(field, FieldArgTable):
            fieldarg = 'arg_table'
        elif isinstance(field, FieldArgDict):
            fieldarg = 'arg_dict'
        else:
            return ()
        return (field.name, field.value, field.string_value, fieldarg, field.field_type, field.valdt, field.jsonset, field.cssclass, field.cssstyle)

    def field_arg_val_list(self, dataarg):
        "Returns the list of validators attached to this field"
        if not dataarg in self.fields:
            return []
        field = self.fields[dataarg]
        return field.val_list

    def changed_names(self):
        "Returns a dictionary of arg:name for those arguments whose name is different to the argument"
        return {a:n for n,a in self._names.items() if n != a}

    def _build(self, page, ident_list, environ, call_data, lang):
        "Called by update - the dynamic parts of the widget should be created here"
        return

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded):
        """builds the widget"""
        if not self.show:
            return
        if placename:
            self.placename = placename
        if not self.ident_string:
            # item is a dynamic part, newly created within a widget
            self.embedded = embedded
            self.ident_string = ident_string
        if self.name:
            # parts beneath this named widget will be embedded
            embedded_parts = (self.embedded[0], self.name, None)
        else:
            embedded_parts = self.embedded
        if self._error:
            if isinstance(self._error, TextBlock):
                self._error.update(page, ident_list, environ, call_data, lang, self.ident_string, self.placename, embedded_parts)
            return
        # build the widget
        # the class attribute is set by 'widget_class'
        if self.fields['widget_class'].value:
            self.update_attribs({'class':self.fields['widget_class'].value})
        if self.fields['widget_style'].value:
            self.update_attribs({'style':self.fields['widget_style'].value})
        # Insert this widgets id
        self.insert_id()
        self._build(page, ident_list, environ, call_data, lang)

    def _make_fieldvalues(self, *fieldargs, **otherparams):
        "Creates a javascript string of fieldvalues, which can be used by _build_js"
        fieldvalues = {}
        for farg in fieldargs:
            fieldvalues[farg] = self.get_field_value(farg)
        fieldvalues.update(otherparams)
        if not fieldvalues:
            return ''
        return """  SKIPOLE.widgets["{ident}"].fieldvalues={fieldvalues};""".format(ident=self.get_id(), fieldvalues=json.dumps(fieldvalues))

    def _build_js(self, page, ident_list, environ, call_data, lang):
        return ''

    def make_js(self, page, ident_list, environ, call_data, lang):
        """Called by page.update - after parts update is called.
           Makes javascript for this widget, calls self._build_js to build further javascript for this widget"""
        if self._error:
            return
        if not self.show:
            return
        if not self.name:
            return

        # js_validators is a class attribute, True is javascript validation is enabled
        if self.js_validators:
            # Add the javascript validators for this widget,
            # adds a line for each widgfield that has validators
            # SKIPOLE.validators[widgfield] = [[...], [...], ... ]
            # where each of the lists correspond to a validator for this widgfield
            # [val_mod, val_class, message, [allowed values], {args}]
            for field_arg, field in self.fields.items():
                all_validators_list = []
                val_list = field.val_list
                if not val_list:
                    # no validators to add on this field
                    continue
                widgfield = self.name + ':' + field.name
                if self.placename:
                    widgfield = self.placename + '-' + widgfield
                for val in val_list:
                    one_validator_list = []
                    one_validator_list.append(val.__class__.__module__.split(".")[-1])
                    one_validator_list.append(val.__class__.__name__)
                    message = val.message
                    if (not message) and val.message_ref:
                        project = skiboot.getproject(page.proj_ident)
                        if project is not None:
                            message = project.textblocks.get_text(val.message_ref, lang)
                    if not message:
                        message = ""
                    one_validator_list.append(message)
                    one_validator_list.append(val.allowed_values)
                    one_validator_list.append(val.val_args)
                    one_validator_list.append(str(val.displaywidget))
                    all_validators_list.append(one_validator_list)
                if all_validators_list:
                    v = "  SKIPOLE.validators[\"%s\"] = " % (widgfield,)
                    v += json.dumps(all_validators_list)
                    page.add_javascript(v+';\n')

        # information about the widget, its id, module, class and arguments
        j = Template("""  SKIPOLE.widgets["$widgident"] = new SKIPOLE["$widg_mod"]["$widg_class"]("$widgident", $error_message, $widg_fields);
""")
        page.add_javascript(j.substitute(widgident = self.get_id(),
                                         widg_mod=self.__class__.__module__.split(".")[-1],
                                         widg_class=self.__class__.__name__,
                                         error_message = json.dumps(self.error_message),
                                         widg_fields=str(self.changed_names())))

        # and add widget specific json
        contents = self._build_js(page, ident_list, environ, call_data, lang)
        if contents:
            page.add_javascript(contents)


    def set_placename(self, section_name, placename):
        "Widgets in sections with displayname validators need displaynames to change"
        self.placename = placename
        for field in self.fields.values():
            if field.val_list:
                # the field has a list of validators
                val_list = field.val_list
                for val in val_list:
                    # If the displaywidget for a validator is equal to the section_name
                    # replace it with the placename
                    if val.displaywidget.s == section_name:
                        val.displaywidget = val.displaywidget._replace(s=placename)


    def mark_field_in_error(self, errorfieldname):
        "Marks a given field as an errored field, for example, by setting it red, child classes may optionally implement this"
        pass

    def _error_build(self, message):
        "Overwritten by child widgets if required"
        if message:
            self._error = message
 
    def show_error(self, message=''):
        """Shows error message"""
        if not self.show:
            return
        if not self.display_errors:
            return
        self.error_status = True
        # if this is a named widget update attribute with data-status="error"
        if self.name:
            self.update_attribs({'data-status':'error'})
        if not message:
            message = self.error_message
        self._error_build(message)

    def field_list(self):
        "Returns a list of fields, ordered alphabetically by field argument"
        return [ self.fields[key] for key in sorted(self.fields.keys())]

    def get_field(self, name):
        "Given a name, get the associated field"
        if not name:
            return
        if name in self._names:
            field_arg = self._names[name]
            if field_arg in self.fields:
                field = self.fields[field_arg]
                if field.name == name:
                    return field
        # failed to find field, refresh self._names and try again
        self._create_name_dict()
        if name in self._names:
            field_arg = self._names[name]
            if field_arg in self.fields:
                field = self.fields[field_arg]
                if field.name == name:
                    return field

    def get_field_arg(self, name):
        "Given a name, get the associated field_arg, returns None if name not found"
        if name in self._names:
            return self._names[name]

    def get_field_valdt(self, name):
        "Given a name, get field.valdt status, True if validators can be added, False if not"
        field = self.get_field(name)
        if field is None:
            return False
        return field.valdt

    def is_fieldname_in_widget(self, name):
        field = self.get_field(name)
        if field is None:
            return False
        return True

    def is_senddict(self, name):
        field = self.get_field(name)
        if field is None:
            raise ValidateError(message = "Widget %s field name %s not recognised" % (self.name, name))
        return field.senddict

    def add_validator(self, field_name, val):
        "adds a validator to the field with the given name"
        f = self.get_field(field_name)
        if f is not None:
            f.add_validator(val)

    def validate(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        "Calls the field validate method, returns item, error_list"
        f = self.get_field(widgfield.f)
        if f is None:
            raise ValidateError(message = "Field name not recognised")
        return f.validate(widgfield, item, environ, lang, form_data, call_data, caller_page_ident)

    def get_value(self, name):
        """If this widget contains fields, then this should return a field
        content, given its name.  If name not found, return None
        """
        field = self.get_field(name)
        if field is not None:
            return field.value

    def set_value(self, name, value):
        """If this widget contains fields, then this should set a field
           content, given its name"""
        if not name:
            return
        if '-' in name:
            self.set_single_multivalue(name, value)
            return
        if (name == 'show_error') or (('show_error' in self.fields) and (name == self.fields['show_error'].name)):
            # the show_error field is special as it accepts both a given field name
            # and the name 'show_error'
            if value:
                self.show_error(message=value)
            else:
                self.show_error()
            return
        field = self.get_field(name)
        if field is None:
            return
        field.value = value
        if name == self.fields["show"].name:
            self.show = bool(value)
        if name == self.fields['widget_class'].name:
            if value:
                self.update_attribs({'class':value})
            else:
                self.del_one_attrib('class')
        if name == self.fields['widget_style'].name:
            if value:
                self.update_attribs({'style':value})
            else:
                self.del_one_attrib('style')


    def set_single_multivalue(self, name, value):
        """If a field name is given with a -, then after the dash must be an index
           This sets the single value with the appropriate index"""
        if '-' not in name: return
        fname, findex = name.split('-')
        field = self.get_field(fname)
        if field is None:
            return
        if not isinstance(field, FieldArgDict):
            return
        field[findex] = value

    def _set_data(self):
        """Clears attributes, then sets n data- atts"""
        # get the number of fields with arguments data1, data2,..
        n = 0   # increments for each data field
        m = 0   # records max number
        for field_arg in self.fields:
            if len(field_arg) < 5: continue
            if field_arg.startswith('data'):
                endnumber = field_arg[4:]
                try:
                    num = int(endnumber)
                except Exception:
                    continue
                if not num: continue
                if num > m:
                    m = num
                n += 1
        if not n:
            # no field_arg's with name data1,...
            return
        if n != m:
            raise ServerError("field data values are mismatched")
        self.del_attribs()
        for idx in range(n):
            # field_arg is data1, data2 etc..
            field_arg = 'data' + str(idx+1)
            if field_arg not in self.fields:
                raise ServerError("Field argument %s does not exist in this widget." % (field_arg,))
            if self.get_field_value(field_arg):
                key = 'data-' + self.get_formname(field_arg)
                self.update_attribs({key:str(self.get_field_value(field_arg))})

    def set_field_value(self, field_arg, value):
        """If this widget contains fields, then this should set a field
           content, given its field_arg"""
        if not field_arg:
            return
        if field_arg not in self.fields:
            return
        field = self.fields[field_arg]
        if field is None:
            return
        field.value = value
        if field_arg == "show":
            self.show = field.value
        if field_arg == 'widget_class':
            if value:
                self.update_attribs({'class':value})
            else:
                self.del_one_attrib('class')
        if field_arg == 'widget_style':
            if value:
                self.update_attribs({'style':value})
            else:
                self.del_one_attrib('style')
        if field_arg == 'show_error':
            self.error_message = field.value

    def get_field_value(self, field_arg):
        """If this widget contains fields, then this should get a field
           content, given its field_arg"""
        if not field_arg:
             raise ValidateError(message="A valid field argument is required")
        if field_arg not in self.fields:
            raise ValidateError(message="Field argument not recognised")
        return self.fields[field_arg].value

    def set_name(self, field_arg, name):
        """Sets a field name, raises ValidateError if the name already exists in the widget"""
        # check name does not already exist
        if not name:
            return
        if name.lower() == "ident":
            raise ValidateError(message="Field name ident is used internally and is not allowed")
        if name == 'tag_name':
            raise ValidateError(message="Field name tag_name is used internally and is not allowed")
        if name == 'error_message':
            raise ValidateError(message="Field name error_message is used internally and is not allowed")
        if _AN.search(name):
            raise ValidateError(message="Invalid name - letters, numbers, underscore only.")
        if field_arg not in self.fields:
            return
        if self.fields[field_arg].name == name:
            # no change
            return
        # check name does not already exist in the widget
        if self.is_fieldname_in_widget(name):
            # a field has been found
            raise ValidateError(message="This field name already exists in the widget")
        # set the name
        self.fields[field_arg].name = name
        # refresh self._names
        self._create_name_dict()

    def get_name(self, field_arg):
        """Gets a field name"""
        if not field_arg:
             raise ValidateError(message="A valid field argument is required")
        if field_arg not in self.fields:
            raise ValidateError(message="Field argument not recognised")
        return self.fields[field_arg].name

    def get_formname(self, field_arg):
        """Returns the string 'sectionname-widgetname:fieldname', used to set submission field names"""
        fieldname = self.get_name(field_arg)
        if not fieldname:
            raise ValidateError(message="Invalid field name")
        if self.name:
            fieldname = self.name + ':' + fieldname
        elif self.embedded[1]:
            fieldname = self.embedded[1] + ':' + fieldname
        else:
            raise ValidateError(message="Widget \"%s\", has no name." % (self.__class__.__name__,))
        if self.placename:
            fieldname = self.placename + '-' + fieldname
        return fieldname

    def widget_hide(self, hide):
        "Hides widget if not error"
        if (not self.error_status) and hide:
            self.set_hide()
        else:
            self.set_block()

    def __repr__(self):
        if self.name:
            return self.__class__.__name__ + '(' + self.name + ')'
        else:
            return self.__class__.__name__

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """<path />  <!-- with widget id and class widget_class -->
"""

    def __str__(self):
        """Returns a text string to illustrate the widget"""
        return self.description()


    def outline(self, proj_ident):
        part_dict = collections.OrderedDict()
        w_mod = self.__module__.split(".")[-1]
        part_dict['class'] = "%s.%s" % (w_mod, self.__class__.__name__)
        if self.name:
            part_dict["name"] = self.name
        if self.brief:
            part_dict["brief"] = self.brief
        fields_dict = {f_arg: f.value for f_arg, f in self.fields.items()}
        if fields_dict:
            ordered_fields_dict = collections.OrderedDict(sorted(fields_dict.items(), key=lambda t: t[0]))
            part_dict["fields"] = tag.make_dictionary(ordered_fields_dict, proj_ident)
            # set widget field names, check if any field name is not equal to f_arg
            fields_names = {f_arg:f.name for f_arg, f in self.fields.items() if f_arg != f.name}
            if fields_names:
                ordered_fields_names = collections.OrderedDict(sorted(fields_names.items(), key=lambda t: t[0]))
                part_dict["set_names"] = tag.make_dictionary(ordered_fields_names, proj_ident)
            # set widget validators
            field_validators = {f.name:f.val_list for f in self.fields.values() if f.val_list}
            if field_validators:
                val_dict = {}
                for name, val_list in field_validators.items():
                    val_dict[name] = _create_validator_list(val_list, proj_ident)
                part_dict["validators"] = collections.OrderedDict(sorted(val_dict.items(), key=lambda t: t[0]))
        return ['ClosedWidget', part_dict]

