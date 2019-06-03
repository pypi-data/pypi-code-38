####### SKIPOLE WEB FRAMEWORK #######
#
# off_piste.py  - Specialist functions
#
# This file is part of the Skipole web framework
#
#
# Somewhat risky functions, hence 'off_piste'.
#

import copy, os, json, collections

from ..ski import skiboot, tag, widgets
from ..ski.excepts import ServerError

from . import project_loaded


def _get_proj(project):
    "Returns the Project with name project"
    project_loaded(project)
    return skiboot.getproject(project)


def _get_project_template_pages(project):
    "yields all template pages in the project"
    proj = _get_proj(project)
    identitems = proj.identitems
    for ident, item  in identitems.items():
        # item is taken direct from the project without copying or importing sections
        if item.page_type == 'TemplatePage':
            yield item


def set_widget_field_value(project, widget_name, widget_field_name, new_value, new_brief=None):
    """For each template page, with a given widget name and field name, set the field value, and widget brief.

       For every template page in the project, if it contains a widget with the given widget name and field name,
       then set the field value, and widget brief.
       The field can only be a single value field, not dictionary, table or list fields.
       If no brief is given, or an empty string is given, then the brief is not changed."""
    field_value = str(new_value)
    proj = _get_proj(project)
    for page in _get_project_template_pages(project):
        if widget_name in page.widgets:
            widget = page.widgets[widget_name]
            field_arg = widget.get_field_arg(widget_field_name)
            if field_arg is None:
                continue
            field_info = widget.field_arg_info(field_arg)
            # (field name, fieldvalue, str_fieldvalue, fieldarg class string, field type, field.valdt, field.jsonset, field.cssclass, field.csstyle)
            if field_info[3] != 'args':
                raise ServerError(message="Invalid field type in widget in page %s " % (page.ident,))
            if (field_info[4] == "ident" or field_info[4] == "url") and field_value.isdigit():
                # A digit is being input as a page ident
                field_value = project + '_' + field_value
            widget.set_field_value(field_arg, field_value)
            if new_brief:
                widget.brief = new_brief
            proj.save_page(page)


def insert_div_in_body(project, css_class, brief):
    """Inserts a div with the given css class as the containing div in each template page body

       For every template page in the project, inserts a div with the given css class attribute
       as the containing div in each page body (thus encapsulating all other body contents),
       unless a div with this class already exists at this point.
       Sets the containing div brief description with the brief given here."""
    proj = _get_proj(project)
    for page in _get_project_template_pages(project):
        body = page.body
        if (len(body) == 1) and hasattr(body[0], 'attribs') and body[0].get_attrib_value('class'):
            # body has one item with a class attribute
            if body[0].get_attrib_value('class') == css_class:
                # container div already exists
                if body[0].brief != brief:
                    body[0].brief = brief
                continue
        # so insert a div
        contents = copy.deepcopy(body.parts)
        newdiv = tag.Part(tag_name='div', attribs={'class':css_class}, brief=brief)
        newdiv.parts = contents
        body.parts = [newdiv]
        proj.save_page(page)


def set_backcol_in_pages(project, backcol):
    """Sets a background colour in the <html> tags of template pages.

       For every template page in the project, which has the option to set a background colour enabled,
       this function sets the background colour in the top <html> tag.
       The backcol argument should be a colour string, such as #FF0000."""
    proj = _get_proj(project)
    for page in _get_project_template_pages(project):
        page.backcol = backcol
        proj.save_page(page)


def set_bodyclass_in_pages(project, bodyclass):
    """For every template page in the project, sets the CSS class into the <body> tag."""
    proj = _get_proj(project)
    for page in _get_project_template_pages(project):
        page.body.set_class(bodyclass)
        proj.save_page(page)


def append_scriptlink_in_pages(project, label):
    """Appends a script link to the head of each page

       For every template page in the project, appends a script link
       to the head section pointing to the page with the given label.
       Generally used to set a link to a javascript file in all your pages."""
    proj = _get_proj(project)
    if "/" in label:
        scriptlink = tag.Part(tag_name = "script", attribs={"src":label}, brief='script link to %s' % (label,))
    else:
        scriptlink = tag.Part(tag_name = "script", attribs={"src":"{" + label + "}"}, brief='script link to %s' % (label,))
    for page in _get_project_template_pages(project):
        page.head.append(scriptlink)
        proj.save_page(page)


def set_widget_css_to_default(project):
    """For each template page, set all widget css class fields to their default values.

       For each template page in the project, set all widget CSS class fields to their
       default values, if a default has been set.
       Note: This does not change widgets in sections or svg pages."""
    proj = _get_proj(project)
    defaults = {}
    defaultsfile = skiboot.project_defaults(proj_ident=project)
    if os.path.isfile(defaultsfile):
        # load defaultsfile into defaults
        with open(defaultsfile, 'r') as fp:
            defaults = json.load(fp, object_pairs_hook=collections.OrderedDict)
    else:
        return
    if not defaults:
        return
    if 'widgets' not in defaults:
        return
    widget_defaults = defaults['widgets']
    # widget_defaults is a dictionary with keys of widget modules, and values which are themselves dictionaries
    # the value dictionaries have keys of the widget class, and values which are dictionaries of field:css class
    for page in _get_project_template_pages(project):
        change_flag = False
        for widget in page.widgets.values():
            widget_module = widget.__class__.__module__.split('.')[-1]
            widget_class = widget.__class__.__name__
            field_css = {}
            if (widget_module in widget_defaults) and (widget_class in widget_defaults[widget_module]):
                field_css = widget_defaults[widget_module][widget_class]
            else:
                continue
            if not field_css:
                continue                
            # for each css field in the widget, if it has a default in field_css, set it
            args = widget.field_arguments_single()
            for field in args:
                field_arg = field[0]
                field_type = field[2]
                if field_type != 'cssclass':
                    continue
                if (field_arg in field_css) and (field_css[field_arg]):
                    widget.set_field_value(field_arg, field_css[field_arg])
                    change_flag = True
        if change_flag:
            proj.save_page(page)



