

"""Functions for editing a validator"""

import pkgutil, importlib, inspect


from ..ski import skiboot, widgets, validators
from ..ski.excepts import ServerError

from . import get_proj_page, get_proj_section

from .info_tuple import ValidatorInfo


def _get_section_val_list(project, section_name, schange, widget_name, field_arg):
    "Returns proj, section, val_list"
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if field_arg not in widget.fields:
        raise ServerError("Field not found")
    field = widget.fields[field_arg]
    if not field.valdt:
        raise ServerError("Field does not take validators")
    return proj, section, field.val_list


def _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg):
    "Returns proj, page, val_list"
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if field_arg not in widget.fields:
        raise ServerError("Field not found")
    field = widget.fields[field_arg]
    if not field.valdt:
        raise ServerError("Field does not take validators")
    return proj, page, field.val_list


def validator_modules():
    "Returns a tuple of validator modules"
    return tuple(name for (module_loader, name, ispkg) in pkgutil.iter_modules(validators.__path__))


def validators_in_module(module_name):
    "Returns a tuple of validator names in a module"
    module = importlib.import_module("skipole.ski.validators." + module_name)
    return tuple(name for name,obj in inspect.getmembers(module, lambda member: inspect.isclass(member) and (member.__module__ == module.__name__)))


def get_section_field_validator_list(project, section_name, schange, widget_name, field_arg):
    "Returns list of validators attached to this widget field, each item in the list being a tuple of validator class name, module name)"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    return tuple( (v.__class__.__name__, v.module_name()) for v in val_list )


def get_page_field_validator_list(project, pagenumber, pchange, widget_name, field_arg):
    "Returns list of validators attached to this widget field, each item in the list being a tuple of validator class name, module name)"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    return tuple( (v.__class__.__name__, v.module_name()) for v in val_list )


def page_field_validator_info(project, pagenumber, pchange, widget_name, field_arg, validx):
    "Returns a named tuple of info about a validator, validx is the index number of the validator within the validator list attached to the field"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    # get validator
    if val_list and (validx >= 0) and (validx < len(val_list)):
        validator = val_list[validx]
    else:
        raise ServerError("Unknown validator")
    return ValidatorInfo(validator.__class__.__name__,
                         validator.module_name(),
                         validator.message,
                         validator.message_ref,
                         validator.displaywidget.to_str_tuple(),
                         validator.allowed_values,
                         validator.val_args
                        )


def section_field_validator_info(project, section_name, schange, widget_name, field_arg, validx):
    "Returns a named tuple of info about a validator, validx is the index number of the validator within the validator list attached to the field"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    # get validator
    if val_list and (validx >= 0) and (validx < len(val_list)):
        validator = val_list[validx]
    else:
        raise ServerError("Unknown validator")
    return ValidatorInfo(validator.__class__.__name__,
                         validator.module_name(),
                         validator.message,
                         validator.message_ref,
                         validator.displaywidget.to_str_tuple(),
                         validator.allowed_values,
                         validator.val_args
                        )
   

def create_section_field_validator(project, section_name, schange, widget_name, field_arg, validator_module, validator_name):
    "Add a validator to the field, return the new section change"
    proj, section = get_proj_section(project, section_name, schange)
    widget = section.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if field_arg not in widget.fields:
        raise ServerError("Field not found")
    field = widget.fields[field_arg]
    if not field.valdt:
        raise ServerError("Field does not take validators")

    val_modules = validator_modules()
    if validator_module not in val_modules:
        raise ServerError("Validator module not found")
    module = importlib.import_module("skipole.ski.validators." + validator_module)

    validator_dict = {name:cls for (name,cls) in inspect.getmembers(module, lambda member: inspect.isclass(member) and (member.__module__ == module.__name__))}

    if validator_name not in validator_dict:
        raise ServerError("Validator not identified")

    validator_cls = validator_dict[validator_name]
    validator_instance = validator_cls()
    field.add_validator(validator_instance)

    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def create_page_field_validator(project, pagenumber, pchange, widget_name, field_arg, validator_module, validator_name):
    "Add a validator to the field, return the new page change"
    proj, page = get_proj_page(project, pagenumber, pchange)
    widget = page.widgets.get(widget_name)
    if (not isinstance(widget, widgets.Widget)) and (not isinstance(widget, widgets.ClosedWidget)):
        raise ServerError("Widget not found")
    if field_arg not in widget.fields:
        raise ServerError("Field not found")
    field = widget.fields[field_arg]
    if not field.valdt:
        raise ServerError("Field does not take validators")

    val_modules = validator_modules()
    if validator_module not in val_modules:
        raise ServerError("Validator module not found")
    module = importlib.import_module("skipole.ski.validators." + validator_module)

    validator_dict = {name:cls for (name,cls) in inspect.getmembers(module, lambda member: inspect.isclass(member) and (member.__module__ == module.__name__))}

    if validator_name not in validator_dict:
        raise ServerError("Validator not identified")

    validator_cls = validator_dict[validator_name]
    validator_instance = validator_cls()
    field.add_validator(validator_instance)

    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def remove_page_field_validator(project, pagenumber, pchange, widget_name, field_arg, validx):
    "Removes a validator, validx is the index number of the validator within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    # get validator
    if val_list and (validx >= 0) and (validx < len(val_list)):
        del val_list[validx]
    else:
        raise ServerError("Unknown validator")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def remove_section_field_validator(project, section_name, schange, widget_name, field_arg, validx):
    "Removes a validator, validx is the index number of the validator within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    # get validator
    if val_list and (validx >= 0) and (validx < len(val_list)):
        del val_list[validx]
    else:
        raise ServerError("Unknown validator")
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def swap_page_field_validators(project, pagenumber, pchange, widget_name, field_arg, validx1, validx2):
    "swaps validators at index positions validx1, validx2, which are positions within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    # swap validators
    try:
        val_list[validx1], val_list[validx2] = val_list[validx2], val_list[validx1]
    except Exception:
        raise ServerError("Invalid operation")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def swap_section_field_validators(project, section_name, schange, widget_name, field_arg, validx1, validx2):
    "swaps validators at index positions validx1, validx2, which are positions within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    # swap validators
    try:
        val_list[validx1], val_list[validx2] = val_list[validx2], val_list[validx1]
    except Exception:
        raise ServerError("Invalid operation")
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_section_field_validator_error_message(project, section_name, schange, widget_name, field_arg, validx, e_message):
    "Set the error message on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    val_list[validx].message = e_message
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_page_field_validator_error_message(project, pagenumber, pchange, widget_name, field_arg, validx, e_message):
    "Set the error message on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    val_list[validx].message = e_message
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_section_field_validator_error_message_reference(project, section_name, schange, widget_name, field_arg, validx, e_message_ref):
    "Set the error message reference on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    val_list[validx].message_ref = e_message_ref
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_page_field_validator_error_message_reference(project, pagenumber, pchange, widget_name, field_arg, validx, e_message_ref):
    "Set the error message reference on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    val_list[validx].message_ref = e_message_ref
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_section_field_validator_displaywidget(project, section_name, schange, widget_name, field_arg, validx, displaywidget):
    "Set the error message reference on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    val_list[validx].displaywidget = displaywidget
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_page_field_validator_displaywidget(project, pagenumber, pchange, widget_name, field_arg, validx, displaywidget):
    "Set the displaywidget on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    val_list[validx].displaywidget = displaywidget
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def add_section_field_validator_allowed_value(project, section_name, schange, widget_name, field_arg, validx, allowed_value):
    "Add allowed value on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    validator = val_list[validx]
    if not allowed_value:
        raise ServerError("A none empty string is required")
    if allowed_value in validator.allowed_values:
        raise ServerError("Allowed value already exists")
    lowval = allowed_value.lower()
    if lowval == "</script>":
        raise ServerError("Invalid allowed value : strings of this form may confuse javascript")
    if "\"" in lowval:
        raise ServerError("Invalid allowed value : strings of this form may confuse javascript")
    validator.allowed_values.append(allowed_value)
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def add_page_field_validator_allowed_value(project, pagenumber, pchange, widget_name, field_arg, validx, allowed_value):
    "Add allowed value on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    validator = val_list[validx]
    if not allowed_value:
        raise ServerError("A none empty string is required")
    if allowed_value in validator.allowed_values:
        raise ServerError("Allowed value already exists")
    lowval = allowed_value.lower()
    if lowval == "</script>":
        raise ServerError("Invalid allowed value : strings of this form may confuse javascript")
    if "\"" in lowval:
        raise ServerError("Invalid allowed value : strings of this form may confuse javascript")
    validator.allowed_values.append(allowed_value)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def remove_section_field_validator_allowed_value(project, section_name, schange, widget_name, field_arg, validx, allowed_value_index):
    "Remove allowed value (given its index) on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    value_list = val_list[validx].allowed_values
    if not value_list:
        raise ServerError("Allowed value list is empty")
    if (allowed_value_index >= 0) and (allowed_value_index < len(value_list)):
        del value_list[allowed_value_index]
    else:
        raise ServerError("Invalid value to remove")
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def remove_page_field_validator_allowed_value(project, pagenumber, pchange, widget_name, field_arg, validx, allowed_value_index):
    "Remove allowed value (given its index) on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    value_list = val_list[validx].allowed_values
    if not value_list:
        raise ServerError("Allowed value list is empty")
    if (allowed_value_index >= 0) and (allowed_value_index < len(value_list)):
        del value_list[allowed_value_index]
    else:
        raise ServerError("Invalid value to remove")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_section_field_validator_argument(project, section_name, schange, widget_name, field_arg, validx, arg_name, arg_value):
    "Set an argument value on the validator at index validx within the validator list attached to the field, return the new section change"
    proj, section, val_list = _get_section_val_list(project, section_name, schange, widget_name, field_arg)
    validator = val_list[validx]
    try:
        validator[arg_name] = arg_value
    except Exception:
        raise ServerError("Invalid argument")
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def set_page_field_validator_argument(project, pagenumber, pchange, widget_name, field_arg, validx, arg_name, arg_value):
    "Set an argument value (given its index) on the validator at index validx within the validator list attached to the field, return the new page change"
    proj, page, val_list = _get_page_val_list(project, pagenumber, pchange, widget_name, field_arg)
    validator = val_list[validx]
    try:
        validator[arg_name] = arg_value
    except Exception:
        raise ServerError("Invalid argument")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)





