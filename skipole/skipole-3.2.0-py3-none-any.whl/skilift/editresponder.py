
"""Functions for editing a responder"""

import inspect

from ..ski import skiboot, responders
from ..ski.page_class_definition import RespondPage
from ..ski.excepts import ServerError

from . import get_proj_page

from .info_tuple import ResponderInfo



def _label_or_ident(ident):
    "Returns ident tuple or label"
    if isinstance(ident, skiboot.Ident):
        return ident.to_tuple()
    if ident is None:
        return ''
    return str(ident)


def list_responders():
    """Returns a list of lists, each inner list consisting of
       0) the responder class name
       1) the responder module name"""
    responderlist = []
    for name,responder in inspect.getmembers(responders, inspect.isclass):
        if issubclass(responder, responders.Respond):
            if name == 'Respond': continue
            responderlist.append([name, responder.module_name()])
    return responderlist


def responder_info(project, pagenumber, pchange):
    """Return a ResponderInfo named tuple"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder

    if responder.widgfield_required and responder.widgfield:
        widgfield = responder.widgfield.to_str_tuple()
    else:
        widgfield = None

    if responder.alternate_ident_required and responder.alternate_ident:
        alternate_ident = responder.alternate_ident
    else:
        alternate_ident = None

    if responder.target_ident_required and responder.target_ident:
        target_ident = responder.target_ident
    else:
        target_ident = None

    if responder.allowed_callers_required and responder.allowed_callers:
        allowed_callers = [_label_or_ident(ident) for ident in responder.allowed_callers]
    else:
        allowed_callers = []

    if responder.validate_option_available:
        validate_option = responder.validate_option
    else:
        validate_option = False

    if responder.validate_option_available and responder.validate_fail_ident:
        validate_fail_ident = responder.validate_fail_ident
    else:
        validate_fail_ident = None

    # submit option

    if responder.submit_option_available:
        submit_option = responder.submit_option
    else:
        submit_option = False

    if responder.submit_required or submit_option:
        if responder.submit_list:
            submit_list = responder.submit_list[:]
        else:
            submit_list = []
        if responder.fail_ident:
            fail_ident = responder.fail_ident
        else:
            fail_ident = None
    else:
        submit_list = []
        fail_ident = None

    # fields

    field_options = responder.field_options.copy()
    field_values_list = []
    field_list = []
    single_field_value = []
    single_field = None

    if field_options['fields']:

        # field_values_list
        if field_options['field_values'] and ( not field_options['single_field'] ):
            field_vals = responder.fields
            for field, value in field_vals.items():
                if isinstance(field, skiboot.WidgField):
                    f = field.to_tuple()
                elif isinstance(field, skiboot.Ident):
                    f = str(field)
                else:
                    f = field
                if isinstance(value, skiboot.WidgField):
                    v = value.to_tuple()
                elif isinstance(value, skiboot.Ident):
                    v = str(value)
                else:
                    v = value
                field_values_list.append([f,v])

        # field_list
        if (not field_options['field_values']) and (not field_options['single_field']):
            field_vals = responder.fields
            for field in field_vals:
                if isinstance(field, skiboot.WidgField):
                    f = field.to_tuple()
                elif isinstance(field, skiboot.Ident):
                    f = str(field)
                else:
                    f = field
                field_list.append(f)

        if field_options['single_field']:

            # single_field_value - still to do
            # as there is currently no responder which takes a single field and value
            #????????????????????????????????????????????????????????

            # single_field
            if not field_options['field_values']:
                if not responder.responder_fields.keys():
                    single_field = ''
                else:
                    single_field = list(responder.responder_fields.keys())[0]

    return ResponderInfo(responder.__class__.__name__,
                         responder.module_name(),
                         responder.widgfield_required,
                         widgfield,
                         responder.alternate_ident_required,
                         _label_or_ident(alternate_ident),
                         responder.target_ident_required,
                         _label_or_ident(target_ident),
                         responder.allowed_callers_required,
                         allowed_callers,
                         responder.validate_option_available,
                         validate_option,
                         _label_or_ident(validate_fail_ident),
                         responder.submit_option_available,
                         submit_option,
                         responder.submit_required,
                         submit_list,
                         _label_or_ident(fail_ident),
                         field_options,
                         field_values_list,
                         field_list,
                         single_field_value,
                         single_field
                       )


def get_submit_list(project, pagenumber, pchange):
    "Returns a copy of the submit list"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if responder.submit_required or responder.submit_option:
        if responder.submit_list:
            return responder.submit_list[:]
        else:
            return []
    raise ServerError(message = "Invalid responder - no submit list available")


def set_submit_list(project, pagenumber, pchange, submit_list):
    "Sets the submit list"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if (not responder.submit_required) and (not responder.submit_option):
        raise ServerError(message = "Invalid responder - no submit list available")
    responder.submit_list = submit_list[:]
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_widgfield(project, pagenumber, pchange, widgfield):
    "sets responder widgfield, returns new pchange"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.widgfield_required:
        raise ServerError(message="Invalid submission, this responder does not have a widgfield")
    responder.widgfield = skiboot.make_widgfield(widgfield)._replace(i='')
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_alternate_ident(project, pagenumber, pchange, ident):
    "Sets the alternate page"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.alternate_ident_required:
        raise ServerError(message="Invalid submission, this responder does not have an alternate page")
    a_i = skiboot.make_ident_or_label_or_url(ident, proj_ident=project)
    if a_i is None:
        raise ServerError(message="Invalid alternate ident")
    responder.alternate_ident = a_i
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_target_ident(project, pagenumber, pchange, ident):
    "Sets the target page"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.target_ident_required:
        raise ServerError(message="Invalid submission, this responder does not have a target ident")
    t_i = skiboot.make_ident_or_label_or_url(ident, proj_ident=project)
    if t_i is None:
        raise ServerError(message="Invalid target ident")
    responder.target_ident = t_i
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_validate_fail_ident(project, pagenumber, pchange, ident):
    "Sets the fail page for validate error"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.validate_option_available:
        raise ServerError(message="Invalid submission, this responder does not have a validate option")
    v_f_i = skiboot.make_ident_or_label_or_url(ident, proj_ident=project)
    if v_f_i is None:
        raise ServerError(message="Invalid validate fail ident")
    responder.validate_fail_ident = v_f_i
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_fail_ident(project, pagenumber, pchange, ident):
    "Sets the fail page"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not (responder.submit_required or responder.submit_option_available):
        raise ServerError(message="Invalid submission, this responder does not have a fail ident")
    f_i = skiboot.make_ident_or_label_or_url(ident, proj_ident=project)
    if f_i is None:
        raise ServerError(message="Invalid fail ident")
    responder.fail_ident = f_i
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def add_allowed_caller(project, pagenumber, pchange, ident):
    "Add an allowed caller"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.allowed_callers_required:
        raise ServerError(message="Invalid submission, this responder does not have allowed callers")
    a_c = skiboot.make_ident_or_label(ident, proj_ident=project)
    if a_c is None:
        raise ServerError(message="Invalid allowed caller")
    # check not already in list
    allowed_callers = [str(idt) for idt in responder.allowed_callers ]
    s_a_c = str(a_c)
    if s_a_c in allowed_callers:
        raise ServerError(message='This allowed caller already exists')
    responder.allowed_callers.append(a_c)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def delete_allowed_caller(project, pagenumber, pchange, ident):
    "Deletes an allowed caller"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.allowed_callers_required:
        raise ServerError(message="Invalid submission, this responder does not have allowed callers")
    d_a_c = skiboot.make_ident_or_label(ident, proj_ident=project)
    if d_a_c is None:
        raise ServerError(message="Invalid caller to delete")
    allowed_callers = [str(idt) for idt in responder.allowed_callers ]
    s_d_a_c = str(d_a_c)
    try:
        idx = allowed_callers.index(s_d_a_c)
    except ValueError:
        raise ServerError('This allowed caller does not exist')
    del responder.allowed_callers[idx]
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def remove_field(project, pagenumber, pchange, field):
    "Deletes a field"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    # field options
    f_options = responder.field_options
    if not f_options['fields']:
        raise ServerError(message="Invalid submission, this responder does not have fields")
    if f_options['widgfields']:
        # ensure the field to remove is a widgfield
        field = skiboot.make_widgfield(field)
    if field in responder.fields:
        del responder.fields[field]
    else:
        raise ServerError(message="Field not found")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def add_field_value(project, pagenumber, pchange, field, value):
    "Adds a field and value"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    # field options
    f_options = responder.field_options
    if not f_options['fields']:
        raise ServerError(message="Invalid submission, this responder does not have fields")
    if not f_options['field_values']:
        raise ServerError(message="Invalid submission, this responder does not have values")
    if (not value) and (not f_options['empty_values_allowed']):
        raise ServerError(message="Invalid submission, empty field values are not allowed")
    responder.set_field(field, value)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def add_field(project, pagenumber, pchange, field):
    "Adds a field, without a value, options['field_values'] must be False"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    # field options
    f_options = responder.field_options
    if not f_options['fields']:
        raise ServerError(message="Invalid submission, this responder does not have fields")
    if f_options['field_values']:
        raise ServerError(message="Invalid submission, this responder requires fields with values")
    responder.set_field(field, '')
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def set_single_field(project, pagenumber, pchange, field):
    "Sets a single field, without a value, options['field_values'] must be False and options['single_field'] must be True"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    # field options
    f_options = responder.field_options
    if not f_options['fields']:
        raise ServerError(message="Invalid submission, this responder does not have fields")
    if f_options['field_values']:
        raise ServerError(message="Invalid submission, this responder requires fields with values")
    if not f_options['single_field']:
        raise ServerError(message="Invalid submission, this function can only be used with single_field responders")
    responder.set_fields({ field:'' })
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def toggle_validate_option(project, pagenumber, pchange):
    "Toggles the validate option, returns (pchange, validate_option)"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.validate_option_available:
        raise ServerError(message="Invalid submission, this responder does not accept the validate option")
        
    if responder.validate_option:
        responder.validate_option = False
    else:
        responder.validate_option = True
    # save the altered page, and return the page.change uuid and validate option
    return proj.save_page(page), responder.validate_option


def toggle_submit_option(project, pagenumber, pchange):
    "Toggles the submit option, returns (pchange, submit_option)"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "RespondPage":
        raise ServerError(message = "Invalid page type")
    responder = page.responder
    if not responder.submit_option_available:
        raise ServerError(message="Invalid submission, this responder does not accept the submit option")
        
    if responder.submit_option:
        responder.submit_option = False
        responder.submit_list = []
    else:
        responder.submit_option = True
    # save the altered page, and return the page.change uuid and submit option
    return proj.save_page(page), responder.submit_option





