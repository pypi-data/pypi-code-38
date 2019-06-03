

"""Functions that read a json string to create sections, pages and folders"""

import os, json, collections

from ..ski import skiboot, read_json, dump_project
from ..ski.excepts import ServerError

from . import project_loaded, item_info, ident_exists, get_proj_section, get_proj_page


def project_json_file(project):
    "Given a project name, returns the file path of the project.json file"
    return skiboot.project_json(project)


def item_outline(project, pagenumber, section_name, location):
    """Returns a list defining the item and its contents. Such as ['Part', dictionary] for Part,
      ['ClosedPart', dictionary] for ClosedPart etc.,

       The project must be currently loaded as either the root project or a sub-project, and the part must exist in the page.
       pagenumber and section_name are mutually exclusive, one must be None"""
    # item is either in a page or a section
    if (pagenumber is None) and (section_name is None):
        raise ServerError("Page and section both missing")
    if section_name:
        if pagenumber is not None:
            raise ServerError("Item cannot be in both a page and a section")
        # item is in a section
        proj, section = get_proj_section(project, section_name)
        item = section.location_item(location)
    else:
        # item is in a page
        proj, page = get_proj_page(project, pagenumber)
        item = page.location_item(location)
    if item is None:
        raise ServerError("Item not recognised")
    if hasattr(item, 'outline'):
        return item.outline(project)
    else:
        # must be a text string
        return ['Text', str(item)]


def create_section(project, section_name, json_data):
    """Builds the section from the given json string or ordered dictionary, and adds it to project


       Given a project name, a section name and a json string (or ordered dictionary) describing the section,
       this function creates a new section (or overwrites a section with the same name).
       The project must be currently loaded as either the root project or a sub-project.
"""
    # raise error if invalid project
    project_loaded(project)
    try:
        read_json.create_section(project, section_name, json_data)
    except Exception:
        raise ServerError("Unable to create section")


def section_outline(project, section_name):
    """Given a project name, and a section name, returns an outline list defining the section.

       The project must be currently loaded as either the root project or a sub-project,
       and the section must exist in the project."""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    section = proj.section(section_name, makecopy=False)
    if section is None:
        raise ServerError(message="Section not found")
    return section.outline(project)


def container_outline(project, pagenumber, section_name, widget_name, container):
    """Builds an outline list from the widget container, ServerError if not found"""
    # widget is either in a page or a section
    if (pagenumber is None) and (section_name is None):
        raise ServerError("Page and section both missing")
    if section_name:
        if pagenumber is not None:
            raise ServerError("Widget cannot be in both a page and a section")
        # widget is in a section
        proj, section = get_proj_section(project, section_name)
        widget = section.widgets[widget_name]
    else:
        # widget is in a page
        proj, page = get_proj_page(project, pagenumber)
        widget = page.widgets[widget_name]
    if widget is None:
        raise ServerError("widget not recognised")
    parttext, partdict = widget.outline(project)
    container_name = "container_%s" % container
    # partdict[container_name] is a list of parts in the container, for compatability
    # with other outlines, set this into a dictionary with key 'parts'
    container_dict = collections.OrderedDict()
    container_dict["parts"] = partdict[container_name]
    return ["Container", container_dict]



def create_page(project, parentnumber, pagenumber, page_name, page_brief, json_data):
    """Builds a page from the given json string / ordered dictionary, and adds it to project

       Given a project name, a parent folder number, a new page number, a page name, a brief description
       and a json string (or ordered dictionary) describing the page, it creates a new page with the new page number.
       The number should not already exist in the project."""
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(pagenumber, int):
        raise ServerError(message="pagenumber is not an integer")
    if not isinstance(parentnumber, int):
        raise ServerError(message="parentnumber is not an integer")
    if ident_exists(project, pagenumber):
        raise ServerError(message = "An item with this ident number already exists")
    parentinfo = item_info(project, parentnumber)
    if not parentinfo:
        raise ServerError(message = "The parent folder with this ident number has not been found")
    if parentinfo.item_type != "Folder":
        raise ServerError(message = "The parent with this ident number is not a folder")
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    # create the page
    if "SVG" in page_dict:
        read_json.create_svgpage(project, parentnumber, pagenumber, page_name, page_brief, page_dict)
        return
    elif "TemplatePage" in page_dict:
        read_json.create_templatepage(project, parentnumber, pagenumber, page_name, page_brief, page_dict)
        return
    raise ServerError(message = "Invalid JSON file")


def page_to_OD(project, pagenumber):
    """Given a project name, and a page number, returns an Ordered Dictionary defining the page.

       The project must be currently loaded as either the root project or a sub-project,
       and the page must exist in the project."""
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(pagenumber, int):
        raise ServerError(message="pagenumber is not an integer")
    page = skiboot.from_ident(pagenumber, project)
    if page is None:
        raise ServerError(message="Page not found")
    if page.page_type == 'SVG':
        page_dict = dump_project.svg_to_OD(project, page)
    elif page.page_type == 'TemplatePage':
        page_dict = dump_project.templatepage_to_OD(project, page)
    else:
        raise ServerError(message="The given pagenumber is not that of an svg or template page")
    return page_dict


def page_to_json(project, pagenumber, indent=0):
    """Given a project name, and a page number, returns a json string defining the page.

       The project must be currently loaded as either the root project or a sub-project,
       and the page must exist in the project.
       The indent parameter should be the number of indentation spaces to use when formatting the string."""
    page_dict = page_to_OD(project, pagenumber)
    return json.dumps(page_dict, indent=indent, separators=(',', ':'))


def create_folder(project, parentnumber, addition_number, folder_name, restricted, json_data):
    """Builds a folder and contents from the given json string / ordered dictionary, and adds it to project
       returns top folder_number


       Given a project name, a parent folder number, an addition_number, a folder name, a True or False restricted value
       and a json string (or ordered dictionary) describing the folder and its contents, it creates a new folder and contents.
       The folder name should not already exist in the parent folder.
       The json string is typically derived from a previously saved JSON file, and each folder and page within it will already
       have an ident number. The 'addition_number' argument of this function is added to each ident number, and should take the
       new ident numbers outside the range of existing numbers within the project.
"""
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(addition_number, int):
        raise ServerError(message="addition number is not an integer")
    if not isinstance(parentnumber, int):
        raise ServerError(message="parentnumber is not an integer")
    parentinfo = item_info(project, parentnumber)
    if not parentinfo:
        raise ServerError(message = "The parent folder with this ident number has not been found")
    if parentinfo.item_type != "Folder":
        raise ServerError(message = "The parent with this ident number is not a folder")
    if parentinfo.restricted:
        restricted = True
    # create the folder
    ident = read_json.create_folder(project, parentnumber, addition_number, folder_name, restricted, json_data)
    return ident.num


def folder_to_OD(project, foldernumber):
    """Given a project name, and a folder number, returns an Ordered Dictionary defining the folder and its contents.

       The project must be currently loaded as either the root project or a sub-project,
       and the folder must exist in the project."""
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(foldernumber, int):
        raise ServerError(message="foldernumber is not an integer")
    folder = skiboot.from_ident(foldernumber, project)
    if folder is None:
        raise ServerError(message="Folder not found")
    if folder.page_type != 'Folder':
        raise ServerError(message="The given foldernumber is not that of a Folder")
    return dump_project.folder_to_OD(project, folder)


def folder_to_json(project, foldernumber, indent=0):
    """Given a project name, and a folder number, returns a json string defining the folder and its contents.

       The project must be currently loaded as either the root project or a sub-project,
       and the folder must exist in the project.
       The indent parameter should be the number of indentation spaces to use when formatting the string."""
    folder_dict = folder_to_OD(project, foldernumber)
    return json.dumps(folder_dict, indent=indent, separators=(',', ':'))


def project_to_OD(project):
    """For the given project, returns an Ordered Dictionary, which could be large.

       The dictionary describes the project pages and widgets."""
    # raise error if invalid project
    project_loaded(project)
    return dump_project.project_to_OD(project)


def project_to_json(project, save_to_file=True, indent=0):
    """For the given project, creates a json file, or returns a json string, which could be large.

       If save_to_file is True, this function creates the file project.json under the projectfiles/project/data directory, and returns None.
       If save_to_file is False, the function returns a json string. This string describes the project pages and widgets.
       The indent parameter should be the number of indentation spaces to use when formatting the string."""

    project_dict = project_to_OD(project)

    if save_to_file:
        # write out the project dictionary to a json file
        filepath = project_json_file(project)
        with open(filepath, 'w') as fp:
            json.dump(project_dict, fp, indent=indent)
        return

    return json.dumps(project_dict, indent=indent, separators=(',', ':'))


def get_defaults_from_file(projectfiles, project, key=None):
    """Obtains values from the defaults.json file of the given project.
       This can be called before a WSGIApplication object is created
       since it uses the projectfiles information

        If a key is given, it returns the value of that key,
        otherwise it returns the entire dictionary of the JSON file.
        If no value is found, returns None."""
    defaults = {}
    defaultsfile = os.path.join(projectfiles, project, 'data', 'defaults.json')
    if os.path.isfile(defaultsfile):
        # load defaultsfile into defaults
        with open(defaultsfile, 'r') as fp:
            defaults = json.load(fp, object_pairs_hook=collections.OrderedDict)
    else:
        return
    if not defaults:
        return
    if not key:
        return defaults
    if key in defaults:
        return defaults[key]



def get_defaults(project, key=None):
    """Obtains values from the defaults.json file of the given project.

        If a key is given, it returns the value of that key,
        otherwise it returns the entire dictionary of the JSON file.
        If no value is found, returns None."""
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
    if not key:
        return defaults
    if key in defaults:
        return defaults[key]


def get_widget_default_field_value(project, widg_module, widg_class, widg_field):
    """Returns the default value to set into a widget field argument, returns '' if not found

       When a widget is created or edited, certain fields can be set with defaults - currently CSS classes and CSS Styles.
       You have the option to save these defaults for the widget field.
       These defaults are held in the project 'defaults.json' file.
       This function reads the defaults.json file and returns the default string value for the given widget and field.
       To specify the widget and field, you need to supply the project name, and:

       widg_module is the module name of the widget.
       widg_class is the class name of the widget
       widg_field is the field name of the widget
       If the default value is not found, the function returns an empty string."""
    if not (widg_module and widg_class and widg_field):
        return ''
    widg_defaults_dict = get_defaults(project, key='widgets')
    if widg_defaults_dict is None:
        return ''
    # widg_defaults_dict is a dictionary of keys being module names, values being another dictionary
    if widg_module in widg_defaults_dict:
        widg_module_dict = widg_defaults_dict[widg_module]
    else:
        return ''
    # widg_module_dict is a dictionary of keys being widget class names in the module, values being another dictionary
    if widg_class in widg_module_dict:
        widg_class_dict = widg_module_dict[widg_class]
    else:
        return ''
    # widg_class_dict is a dictionary of keys being widget field arg names in the module, values being the default field values
    if widg_field in widg_class_dict:
        default_field_value = widg_class_dict[widg_field]
    else:
        return ''
    if default_field_value:
        return default_field_value
    return ''


def set_defaults(project, key, value):
    "Sets a key:value pair into the defaults.json file for the project."
    defaults = get_defaults(project)
    if not defaults:
        defaults = {}
    defaults[key] = value
    save_defaults(project, defaults)


def save_defaults(project, defaults):
    "Given a defaults dictionary, saves the entire dictionary as the defaults.json file for the project."
    # create defaults.json
    defaults_json_filename = skiboot.project_defaults(project)
    # write out the project defaults dictionary to a json file
    ordered_defaults = collections.OrderedDict(sorted(defaults.items(), key=lambda t: t[0]))
    # put the 'widgets' key dictionary in order
    modules = ordered_defaults['widgets']
    ordered_modules = collections.OrderedDict(sorted(modules.items(), key=lambda t: t[0]))
    ordered_defaults['widgets'] = ordered_modules
    # modules are in correct order, for each module, sort its classes
    for module, classdict in ordered_modules.items():
        ordered_modules[module] = collections.OrderedDict(sorted(classdict.items(), key=lambda t: t[0]))
    # modules and classes are in correct order, for each class, sort its fields
    for classdict in ordered_modules.values():
        for widgclass, widgfield in classdict.items():
            classdict[widgclass] = collections.OrderedDict(sorted(widgfield.items(), key=lambda t: t[0]))
    with open(defaults_json_filename, 'w') as fp:
        json.dump(ordered_defaults, fp, indent=0)


def save_widget_default_field_value(project, widg_module, widg_class, widg_field, value):
    """Saves a default value string for a given widget field (currently CSS classes and CSS styles) in the project 'defaults.json' file.

       To specify the widget and field, you need to supply the project name, and:

       widg_module is the module name of the widget.
       widg_class is the class name of the widget
       widg_field is the field name of the widget

       The function returns True if ok, False if not."""
    if not (widg_module and widg_class and widg_field):
        return False
    widg_defaults_dict = get_defaults(project, key='widgets')
    if widg_defaults_dict is None:
        widg_defaults_dict = {}
    # widg_defaults_dict is a dictionary of keys being module names, values being another dictionary
    if widg_module in widg_defaults_dict:
        widg_module_dict = widg_defaults_dict[widg_module]
    else:
        widg_module_dict = {}
        widg_defaults_dict[widg_module] = widg_module_dict
    # widg_module_dict is a dictionary of keys being widget class names in the module, values being another dictionary
    if widg_class in widg_module_dict:
        widg_class_dict = widg_module_dict[widg_class]
    else:
        widg_class_dict = {}
        widg_module_dict[widg_class] = widg_class_dict
    # widg_class_dict is a dictionary of keys being widget field arg names in the module, values being the default field value
    widg_class_dict[widg_field] = value
    try:
        set_defaults(project, key='widgets', value=widg_defaults_dict)
    except Exception:
        return False
    return True



