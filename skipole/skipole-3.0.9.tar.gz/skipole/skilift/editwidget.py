

"""Functions for editing a widget"""

import pkgutil, importlib, inspect, re

from ..ski import widgets, dump_project
from ..ski.excepts import ServerError

from . import widget_info, fromjson, insert_item_in_page, insert_item_in_section, get_proj_page, get_proj_section


from .info_tuple import WidgetDescription, FieldDescription, ContainerInfo


# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')


def widget_modules():
    "Return a tuple of widget module names"
    return tuple(name for (module_loader, name, ispkg) in pkgutil.iter_modules(widgets.__path__))


def widgets_in_module(module_name):
    "Returns a list of WidgetDescription's present in the module"
    module = importlib.import_module("skipole.ski.widgets." + module_name)
    widget_list = []
    for classname,obj in inspect.getmembers(module, lambda member: inspect.isclass(member) and (member.__module__ == module.__name__)):
        fields_single = [ FieldDescription(*fld) for fld in obj.field_arguments_single() ]
        fields_list = [ FieldDescription(*fld, False, False) for fld in obj.field_arguments_list() ]
        fields_table = [ FieldDescription(*fld, False, False) for fld in obj.field_arguments_table() ]
        fields_dictionary = [ FieldDescription(*fld, False, False) for fld in obj.field_arguments_dictionary() ]
        widget_list.append( WidgetDescription( module_name,
                                               classname,
                                               '',
                                               obj.field_arguments(),
                                               obj.len_containers(),
                                               obj.description(),
                                               fields_single,
                                               fields_list,
                                               fields_table,
                                               fields_dictionary,
                                               '',
                                               None
                                               ) )
    return widget_list


def _create_new_widget(project, module_name, widget_classname, name, brief):
    "Creates a new widget"
    if not name:
        raise ServerError("Invalid name")
    lower_name = name.lower()
    if (lower_name == 'body') or (lower_name == 'head') or (lower_name == 'svg')  or (lower_name == 'show_error'):
        raise ServerError(message="Unable to create the widget, the name given is reserved")
    if _AN.search(name):
        raise ServerError(message="Invalid name, alphanumeric and underscore only")
    if name[0] == '_':
        raise ServerError(message="Invalid name, must not start with an underscore")
    if name.isdigit():
        raise ServerError(message="Unable to create the widget, the name must include some letters")
    modules_tuple = widget_modules()
    if module_name not in modules_tuple:
        raise FailPage("Module not identified")
    module = importlib.import_module("skipole.ski.widgets." + module_name)
    widget_dict = {name:cls for (name,cls) in inspect.getmembers(module, lambda member: inspect.isclass(member) and (member.__module__ == module.__name__))}
    if widget_classname not in widget_dict:
        raise ServerError(message="Widget not identified")

    widget_cls = widget_dict[widget_classname]
    widget_instance = widget_cls(name=name, brief=brief)
    # set widget css class defaults, taken from defaults.json
    widget_fields = widget_instance.fields
    try:
        for fieldarg, field in widget_fields.items():
            if field.cssclass or field.cssstyle:
                # get default
                default_value = fromjson.get_widget_default_field_value(project, module_name, widget_classname, fieldarg)
                widget_instance.set_field_value(fieldarg, default_value)
    except e:
        raise ServerError("Unable to obtain defaults from defaults.json")
    return widget_instance


def create_new_widget_in_page(project, pagenumber, pchange, location, module_name, widget_classname, name, brief):
    "Creates a new widget in the given page, returns the new pchange and new location"
    widget_instance = _create_new_widget(project, module_name, widget_classname, name, brief)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange and new location
    return insert_item_in_page(project, pagenumber, pchange, location, widget_instance)


def create_new_widget_in_section(project, section_name, schange, location, module_name, widget_classname, name, brief):
    "Creates a new widget in the given section, returns the new schange and new location"
    widget_instance = _create_new_widget(project, module_name, widget_classname, name, brief)
    # call skilift.insert_item_in_section to insert the item, save the section and return schange and new location
    return insert_item_in_section(project, section_name, schange, location, widget_instance)


def page_widget(project, pagenumber, pchange, name):
    """Return a widget dictionary from the page"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    parttext, partdict = widget.outline(project)
    return partdict


def section_widget(project, section_name, schange, name):
    """Return a widget dictionary from the section"""
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    parttext, partdict = widget.outline(project)
    return partdict


def page_widget_description(project, pagenumber, pchange, name):
    """Return a WidgetDescription from the page"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    fields_single = [ FieldDescription(*fld) for fld in widget.field_arguments_single() ]
    fields_list = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_list() ]
    fields_table = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_table() ]
    fields_dictionary = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_dictionary() ]
    widgetsection_name, parent_widget_name, parent_container = widget.embedded
    return WidgetDescription( widget.module_name(),
                              widget.__class__.__name__,
                              widget.brief,
                              widget.field_arguments(),
                              widget.len_containers(),
                              widget.description(),
                              fields_single,
                              fields_list,
                              fields_table,
                              fields_dictionary,
                              parent_widget_name,
                              parent_container
                               )


def section_widget_description(project, section_name, schange, name):
    """Return a widget WidgetDescription from the section"""
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    fields_single = [ FieldDescription(*fld) for fld in widget.field_arguments_single() ]
    fields_list = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_list() ]
    fields_table = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_table() ]
    fields_dictionary = [ FieldDescription(*fld, False, False) for fld in widget.field_arguments_dictionary() ]
    widgetsection_name, parent_widget_name, parent_container = widget.embedded
    return WidgetDescription( widget.module_name(),
                              widget.__class__.__name__,
                              widget.brief,
                              widget.field_arguments(),
                              widget.len_containers(),
                              widget.description(),
                              fields_single,
                              fields_list,
                              fields_table,
                              fields_dictionary,
                              parent_widget_name,
                              parent_container
                               )


def rename_page_widget(project, pagenumber, pchange, name, new_name):
    """Given a widget at project, pagenumber, with name 
       sets a new name, returns page change uuid """
    if not new_name:
        raise ServerError("Invalid name")
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if name == new_name:
        raise ServerError("Name unchanged")
    new_lower_name = new_name.lower()
    if (new_lower_name == 'body') or (new_lower_name == 'head') or (new_lower_name == 'svg')  or (new_lower_name == 'show_error'):
        raise ServerError(message="Unable to create the widget, the name given is reserved")
    if _AN.search(new_name):
        raise ServerError(message="Invalid name, alphanumeric and underscore only")
    if new_name[0] == '_':
        raise ServerError(message="Invalid name, must not start with an underscore")
    if new_name.isdigit():
        raise ServerError(message="Unable to create the widget, the name must include some letters")
    if new_name in page.widgets:
        raise ServerError("Duplicate widget name in the page")
    if new_name in page.section_places:
        raise ServerError("This name clashes with a section alias within this page")
    widget.name = new_name
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def new_brief_in_page_widget(project, pagenumber, pchange, name, brief):
    """Given a widget at project, pagenumber, with name 
       sets a new brief, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    widget.brief = brief
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def rename_section_widget(project, section_name, schange, name, new_name):
    """Given a widget at project, pagenumber, with name 
       sets a new name, returns page change uuid """
    if not new_name:
        raise ServerError("Invalid name")
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if name == new_name:
        raise ServerError("Name unchanged")
    new_lower_name = new_name.lower()
    if (new_lower_name == 'body') or (new_lower_name == 'head') or (new_lower_name == 'svg')  or (new_lower_name == 'show_error'):
        raise ServerError(message="Unable to create the widget, the name given is reserved")
    if _AN.search(new_name):
        raise ServerError(message="Invalid name, alphanumeric and underscore only")
    if new_name[0] == '_':
        raise ServerError(message="Invalid name, must not start with an underscore")
    if new_name.isdigit():
        raise ServerError(message="Unable to create the widget, the name must include some letters")
    if new_name in section.widgets:
        raise ServerError("Duplicate widget name in the section")
    widget.name = new_name
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def new_brief_in_section_widget(project, section_name, schange, name, brief):
    """Given a widget at project, section_name, with name 
       sets a new brief, returns section change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    widget.brief = brief
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_widget_field_name_in_page(project, pagenumber, pchange, widget_name, field_arg, name):
    "Given a widget field, sets its name"
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if not name:
        raise ServerError("Invalid name")
    if name.startswith('_'):
        raise ServerError(message="Invalid name - cannot start with an underscore.")
    if (name == "show_error") and (field_arg != "show_error"):
        raise ServerError(message="Invalid name - show_error is a reserved name.")
    try:
        widget.set_name(field_arg, name)
    except ValidateError as e:
        raise ServerError(message=e.message)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_widget_field_name_in_section(project, section_name, schange, widget_name, field_arg, name):
    "Given a widget field, sets its name"
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if not name:
        raise ServerError("Invalid name")
    if name.startswith('_'):
        raise ServerError(message="Invalid name - cannot start with an underscore.")
    if (name == "show_error") and (field_arg != "show_error"):
        raise ServerError(message="Invalid name - show_error is a reserved name.")
    try:
        widget.set_name(field_arg, name)
    except ValidateError as e:
        raise ServerError(message=e.message)
    # save the altered page, and return the page.change uuid
    return proj.add_section(section_name, section)


def set_widget_field_value_in_page(project, pagenumber, pchange, widget_name, field_arg, value):
    "Given a widget field, sets its value"
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    # only single values can be set, not lists tables or dictionaries
    single_field_args = { arg[0]: arg for arg in widget.field_arguments_single() }
    if field_arg not in single_field_args:
        raise ServerError("Cannot set a value on this field")
    field_info = single_field_args[field_arg]
    str_value = str(value)
    if (field_info[2] == "ident" or field_info[2] == "url") and str_value.isdigit():
        # The user is inputting a digit as a page ident
        str_value = project + '_' + str_value
    try:
        widget.set_field_value(field_arg, str_value)
    except ValidateError as e:
        raise ServerError(message=e.message)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_widget_field_value_in_section(project, section_name, schange, widget_name, field_arg, value):
    "Given a widget field, sets its value"
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    # only single values can be set, not lists tables or dictionaries
    single_field_args = { arg[0]: arg for arg in widget.field_arguments_single() }
    if field_arg not in single_field_args:
        raise ServerError("Cannot set a value on this field")
    field_info = single_field_args[field_arg]
    str_value = str(value)
    if (field_info[2] == "ident" or field_info[2] == "url") and str_value.isdigit():
        # The user is inputting a digit as a page ident
        str_value = project + '_' + str_value
    try:
        widget.set_field_value(field_arg, str_value)
    except ValidateError as e:
        raise ServerError(message=e.message)
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def container_in_page(project, pagenumber, pchange, widget_name, container):
    "Returns a ContainerInfo named tuple"
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    return ContainerInfo(container, widget.is_container_empty(container))


def container_in_section(project, section_name, schange, widget_name, container):
    "Returns a ContainerInfo named tuple"
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    return ContainerInfo(container, widget.is_container_empty(container))



