

"""Functions that access the ski framework"""

import os

from ..ski.excepts import FailPage, GoTo, ValidateError, ServerError

from ..ski import skiboot, tag

from .info_tuple import ProjectInfo, ItemInfo, PartInfo, PageInfo, FolderInfo, WidgetInfo, VersionInfo


def project_loaded(project, error_if_not=True):
    """Returns True if the project is the root or a sub project.

     If the given project is not one of these, either raises a ServerError exception (if error_if_not is True) or returns False.
"""
    if isinstance(project, str) and skiboot.is_project(project):
        return True
    if error_if_not:
        raise ServerError(message="The project has not been loaded")
    return False


def get_proj(project):
    """Returns the project instance, being the object used internally by the skipole framework"""
    project_loaded(project)
    return skiboot.getproject(project)


def get_proj_page(project, pagenumber, pchange=None):
    """Returns (project_object, page_object), being objects used internally by the skipole framework
       The page object returned is a deepcopy of the page in the project""" 

    project_loaded(project)
    proj = skiboot.getproject(project)

    # get a copy of the page
    if not isinstance(pagenumber, int):
        raise ServerError(message="Given pagenumber is not an integer")
    ident = skiboot.Ident.to_ident((project, pagenumber))
    if ident is None:
        raise ServerError(message="Invalid project, pagenumber")
    page = skiboot.from_ident(ident, project)
    if page is None:
        raise ServerError(message="Invalid Page - pagenumber not found in project")
    if page.page_type == 'Folder':
        raise ServerError(message = "Invalid page - requested item is a Folder")
    # if pchange is given, test it is equal to page.change
    if (pchange is not None) and (page.change != pchange):
        raise ServerError(message="The page has been changed prior to this submission, someone else may be editing this project")
    return proj, page


def get_proj_section(project, section_name, schange=None):
    """Returns (project_object, section_object), being objects used internally by the skipole framework
       The section object returned is a deepcopy of the section in the project""" 

    project_loaded(project)
    proj = skiboot.getproject(project)

    # get a copy of the section
    if not isinstance(section_name, str):
        raise ServerError(message="Given section_name is invalid")
    section = proj.section(section_name, makecopy=True)
    if section is None:
        raise ServerError(message="Given section_name is invalid")
    # if schange is given, test it is equal to section.change
    if (schange is not None) and (section.change != schange):
        raise ServerError(message="The section has been changed prior to this submission, someone else may be editing this project")
    return proj, section


def versions(project):
    """Returns a namedtuple with contents
       skipole, project - these being the skipole version, and the project version
    """
    project_loaded(project)
    proj = skiboot.getproject(project)
    return VersionInfo(skiboot.version(), proj.version)


def project_info(project):
    """Returns a namedtuple with contents
       project, version, brief, path, default_language, subprojects, json_path, tar_path, main_path, static_path, data_path
       where subprojects is an ordered dictionary of projectname:path
    """
    project_loaded(project)
    proj = skiboot.getproject(project)
    return ProjectInfo(
                   project,
                   proj.version,
                   proj.brief,
                   proj.url,
                   proj.default_language,
                   proj.subproject_paths,
                   skiboot.project_json(project),
                   skiboot.project_main(project),
                   skiboot.projectstatic(project),
                   skiboot.projectdata(project)
                   )


def projectURLpaths():
    """Returns a dictionary of project name : project path

       This function takes no arguments and returns a dictionary of project names as keys with the URL paths as values.
       The projects being the root project and any sub-projects attached to it.
       Please note, if this project is being administered using 'skiadmin' - then the project 'skiadmin' will be visible in this dictionary,
       however when the project is running without skiadmin, this project will no longer be present.

      You should expect to see the root project itself in the dictionary, and at least the 'skis' project which is normally attached as a sub-project.
"""
    all_projects = skiboot.project_register()
    return {proj_ident:proj.url for proj_ident, proj in all_projects.items()}


def get_root():
    "Takes no arguments and returns the project name of the current root project."
    return skiboot.root_project().proj_ident


def lib_list():
    "Returns list of library labels"
    return skiboot.lib_list()[:]


def sys_list():
    "Returns list of system page labels"
    return skiboot.sys_list()[:]


def get_debug():
    "Returns the debug mode"
    return skiboot.get_debug()

def set_debug(mode):
    "Sets debug mode"
    skiboot.set_debug(mode)


def get_proj_data(project, key):
    "Returns the value from the proj_data dictionary, or None if not found"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    return proj.proj_data.get(key)

def set_proj_data(project, key, value):
    "Sets the key, value in the proj_data dictionary"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    proj.proj_data[key] = value


def set_proj_default_language(project, default_language):
    "Sets the default language of the project"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    proj.default_language = default_language


def set_proj_brief(project, brief):
    "Sets the brief description of the project"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    proj.brief = brief


def set_proj_version(project, version):
    "Sets the version of the project"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    proj.version = version


def get_projectfiles_dir(project=None):
    """Returns the projectfiles directory for the given project

    Static files, and control files (such as the json files defining your project) are saved outside
    the python package structure under a 'projectfiles' directory.
    If project not given, returns the projectfiles directory path for the root project"""
    return skiboot.projectfiles(project)


def get_projectdir(project=None):
    """Returns the projectfiles/project directory for the given project

    Static files, and control files (such as the json files defining your project) are saved outside
    the python package structure under a 'projectfiles/project' directory.
    If project not given, returns the projectfiles/project path for the root project"""
    return skiboot.projectdir(project)


def get_projectcode_dir(project=None):
    """Returns the directory where your project code is saved
    If project not given, returns the projectcode directory path for the root project"""
    return skiboot.projectcode(project)

def get_projectstatic_dir(project=None):
    """Returns the directory where your project static files are saved
    If project not given, returns the projectstatic directory path for the root project"""
    return skiboot.projectstatic(project)


def next_ident_number(project):
    "Returns next ident number in the project by incrementing highest existing number"
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="Project not loaded")
    return proj.next_ident().num


def get_textblock_text(textref, lang, project=None):
    """This function returns the textblock text, given a textblock reference string,

       lang is the language tuple of (preferred language, default language).
       If text for a given language is not found, the function makes an effort to get text by trying the default language.

       If project is not given assumes the root project, if given, project must exist as either the root,
       or a sub project of the root.
       If no textblock is found, returns None."""
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    return proj.textblocks.get_text(textref, lang)


def get_accesstextblocks(project=None):
    """This function returns the instance of the AccessTextBlocks class used by the project to get TextBlock text.

       If project is None, assumes the root project, if project is given; returns the AccessTextBlocks instance
       of the project. If given, project must exist as either the root, or a sub project of the root."""
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return
    return proj.textblocks


def get_itemnumber(project, item):
    """Returns itemnumber if item is found in the project, where item is either
    a project,number tuple
    a number
    a label
    a path
    If not found returns None"""
    # return None if invalid project
    if not project_loaded(project, error_if_not=False):
        return
    proj = skiboot.getproject(project)
    if proj is None:
        return
    # check if item is a path
    if isinstance(item, str) and '/' in item:
        path = item.strip()
        path = path.strip("/")
        if path:
            path = "/" + path + "/"
        else:
            path = "/"
        ident = proj.root.ident_from_path(path)
    else:
        ident = skiboot.find_ident(item, project)
    if ident is None:
        return
    if ident.proj != project:
        return
    return ident.num



def item_info(project, itemnumber):
    """Returns None if page or folder not found, otherwise returns a namedtuple of item information.

       The project must exist as either the root, or a sub project of the root, itemnumber is the ident number of a page or folder.

       The function returns None, if no page or folder is found, otherwise returns a namedtuple with contents:
       project, project_version, itemnumber, item_type, name, brief, path, label_list, change, parentfolder_number, restricted.

       The values are:
       'project' - the project name from the argument.
       'project_version' is the project version string.
       'itemnumber' is the itemnumber from the argument.
       item_type' - one of 'TemplatePage', 'Folder', 'JSON', 'CSS', 'RespondPage', 'FilePage', 'SVG'.
       'name' holds the page or folder name.
       'brief' holds the brief description of the item.
       'path' is the url path.
       'label_list' is a list of labels (as there could be more than one) pointing to this item.
       'change' is a uuid of the item, changed whenever the item is altered by this admin site.
       'parentfolder_number' is the integer number of the parentfolder or None if this is the root folder.
       'restricted' is True if access is restricted (cannot be called by URL), False otherwise.
    """
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(itemnumber, int):
         raise ServerError(message="Given itemnumber is not an integer")
    ident = skiboot.Ident.to_ident((project, itemnumber))
    if ident is None:
        return
    info = skiboot.item_info(ident)
    if not info:
        return
    if info.parentfolder_ident:
        parentfolder_number = info.parentfolder_ident.num
    else:
        parentfolder_number = None

    return ItemInfo(
                   project,
                   info.project_version,
                   itemnumber,
                   info.item_type,
                   info.name,
                   info.brief,
                   info.path,
                   info.label_list,
                   info.change,
                   parentfolder_number,
                   info.restricted
                   )


def part_info(project, pagenumber, section_name, location):
    """Returns a PartInfo named tuple, giving the information about a part at a location in a page or section.

       The project must exist as either the root, or a sub project of the root,
       pagenumber and section_name are mutually exclusive, one must be None.

       location is a tuple or list consisting of three items:
       a string (such as 'head' or section name or widget name)
       a container integer, such as 0 for widget container 0, or None if not in container
       a tuple or list of location integers

       Returns None if part not found, otherwise returns a namedtuple with items
       project, pagenumber, page_part, section_name, name, location, part_type, brief.

       page_part is one of 'head', 'body', 'svg' or None if the part is in a section,
       name is the widgets name if it is a widget.
    """

    # part is either in a page or a section
    if (pagenumber is None) and (section_name is None):
        raise ServerError("Page and section both missing")

    page_part = None

    if section_name:
        if pagenumber is not None:
            raise ServerError("Part cannot be in both a page and a section")
        # item is in a section
        proj, section = get_proj_section(project, section_name)
        part = section.location_item(location)
    else:
        # item is in a page
        proj, page = get_proj_page(project, pagenumber)
        part = page.location_item(location)
        page_part = location[0]
        if location[1] is not None:
            # item is in a container in a widget, so location[0] will be the parent widget name
            widget = page.widgets[location[0]]
            if widget is not None:
               ident_top = widget.ident_string.split("-", 1)
               # ident_top[0] will be of the form proj_pagenum_head
               page_part = ident_top[0].split("_")[2]

    if part is None:
        raise ServerError("Part not found")

    if hasattr(part, '__class__'):
        part_type = part.__class__.__name__
    else:
        part_type = None

    if hasattr(part, 'name'):
        name = part.name
    else:
        name = None

    if hasattr(part, 'brief'):
        brief = part.brief
    else:
        brief = None

    return PartInfo(project, pagenumber, page_part, section_name, name, location, part_type, brief)


def part_contents(project, pagenumber, section_name, location):
    "If the given part is a Part or Section, returns a list of PartInfo tuples, one for each content"
    # part is either in a page or a section
    if (pagenumber is None) and (section_name is None):
        raise ServerError("Page and section both missing")

    page_part = None

    if section_name:
        if pagenumber is not None:
            raise ServerError("Part cannot be in both a page and a section")
        # item is in a section
        proj, section = get_proj_section(project, section_name)
        part = section.location_item(location)
    else:
        # item is in a page
        proj, page = get_proj_page(project, pagenumber)
        part = page.location_item(location)
        if location[1] is not None:
            # item is in a container in a widget, so location[0] will be the parent widget name
            widget = page.widgets[location[0]]
            if widget is not None:
               ident_top = widget.ident_string.split("-", 1)
               # ident_top[0] will be of the form proj_pagenum_head
               page_part = ident_top[0].split("_")[2]

    if part is None:
        return
    if hasattr(part, '__class__'):
        part_type = part.__class__.__name__
    if (part_type != "Part") and (part_type != "Section"):
        return

    subpart_list = []

    index = 0
    for subpart in part:
        if hasattr(subpart, '__class__'):
            subpart_type = subpart.__class__.__name__
        else:
            subpart_type = None

        if hasattr(subpart, 'name'):
            name = subpart.name
        else:
            name = None

        if hasattr(subpart, 'brief'):
            brief = subpart.brief
        else:
            brief = None

        location_list = list(location[2])

        sublocation = (location[0], location[1], location_list+[index])

        sub_tuple = PartInfo(project, pagenumber, page_part, section_name, name, sublocation, subpart_type, brief)
        subpart_list.append(sub_tuple)
        index += 1
    return subpart_list


def widget_info(project, pagenumber, section_name, widget_name):
    """returns None if widget not found, otherwise returns a namedtuple with items
       project, pagenumber, section_name, name, location, containers, display_errors, brief
       where containers is the number of containers this widget has, zero if it has none,
       and display_errors is True if this widget can display an error"""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    location = None
    # get the widget
    if section_name:
        section = proj.section(section_name, makecopy=False)
        if section is None:
            return
        if widget_name not in section.widgets:
            return
        widget = section.widgets[widget_name]
        if widget is None:
            return
        parent, container = widget.get_parent_widget(section)
        ident_items = widget.ident_string.split('-', 1)
        ident_integers = ident_items[1].split('-')
        if parent is None:
            location = (section_name, None, tuple(int(i) for i in ident_integers))
    elif pagenumber:
        page = proj.get_item(pagenumber)
        if widget_name not in page.widgets:
            return
        widget = page.widgets[widget_name]
        if widget is None:
            return
        parent, container = widget.get_parent_widget(page)
        ident_items = widget.ident_string.split('-', 1)
        ident_integers = ident_items[1].split('-')
        ident_locs = ident_items[0].split('_')
        # ident_locs are project, pagenumber, (head,body or svg)
        if parent is None:
            location = (ident_locs[2], None, tuple(int(i) for i in ident_integers))
    else:
        return
    if location is None:
        parent_ident_items = parent.ident_string.split('-', 1)
        parent_ident_integers = parent_ident_items[1].split('-')
        length_of_container_location = len(parent_ident_integers) + len(parent.get_container_loc(container))
         # widget location integers, are the integers beyond the parent + container integers
        location_integers = ident_integers[length_of_container_location:]
        location = (parent.name, container, tuple(location_integers))
    return WidgetInfo(project, pagenumber, section_name, widget_name, location, widget.len_containers(), widget.display_errors, widget.brief)



def ident_exists(project, itemnumber):
    "Return True if a page or folder with this itemnumber exists, False otherwise."
    return skiboot.ident_exists((project, itemnumber))


def ident_numbers(project=None):
    "Returns a list of the project ident numbers"
    num_list = [0]
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return []
    return proj.ident_numbers


def labels(project=None):
    """Returns a dictionary of labels to page, folder tuple idents or urls

       If project is not given assumes the root project, if given, project must exist as either the root, or a sub project of the root.
"""
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return {}
    return proj.labels()


def set_label(project, label, target):
    """Sets a label and target, where target is a page ident or url"""
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError("Project not recognised")
    proj.set_special_page(label, target)


def delete_label(project, label):
    """Deletes a label"""
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError("Project not recognised")
    proj.delete_special_page(label)


def pages(project, foldernumber):
    """Returns generator of PageInfo named tuples, one for each page in the folder

       The project must exist as either the root, or a sub project of the root, foldernumber is the ident number of a folder.

       The generator raises a ServerError if no folder is found, otherwise the generator yields a namedtuple describing each page within the folder over each iterated pass.

       The named tuple has contents:
       'name', 'number', 'restricted', 'brief', 'item_type', 'responder', 'enable_cache', 'change', 'parentfolder_number'

       The values are:
       'name' holds the page name.
       'number' is the ident page number.
       'restricted' is True if access is restricted (cannot be called by URL), False otherwise.
       'brief' holds the brief description of the page.
       'item_type' - one of 'TemplatePage', 'JSON', 'CSS', 'RespondPage', 'FilePage', 'SVG'.
       'responder' - responder Class name, such as 'SubmitData' etc., or empty string if the page is not a responder.
       'enable_cache' - True if client caching is enabled on the page, False otherwise.
       'change' - A UUID string changed whenever the page is edited
       'parentfolder_number' - The uident number of the folder containing this page
"""

    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    folder_ident = skiboot.Ident(project, foldernumber)
    folder = proj.get_item(folder_ident)
    if folder is None:
        raise ServerError("Folder not recognised")
    for page_ident in folder.page_idents():
        page = proj.get_item(page_ident)
        if page.page_type == 'RespondPage':
            responder = page.responder.__class__.__name__
        else:
            responder = ''
        if hasattr(page, 'enable_cache'):
            enable_cache = page.enable_cache
        else:
            enable_cache = False
        if page.parentfolder_ident:
            parentfolder_number = page.parentfolder_ident.num
        else:
            parentfolder_number = None
        yield PageInfo(page.name, page.ident.num, page.restricted, page.brief, page.page_type, responder, enable_cache, page.change, parentfolder_number)


def page_info(project, pagenumber):
    """Returns PageInfo named tuple for page

       The project must exist as either the root, or a sub project of the root, pagenumber is the ident number of a page.

       The function raises a ServerError, if no page is found, otherwise returns a namedtuple with contents:
       'name', 'number', 'restricted', 'brief', 'item_type', 'responder', 'enable_cache', 'change', 'parentfolder_number'

       The values are:
       'name' holds the page name.
       'number' is the page number from the argument.
       'restricted' is True if access is restricted (cannot be called by URL), False otherwise.
       'brief' holds the brief description of the page.
       'item_type' - one of 'TemplatePage', 'JSON', 'CSS', 'RespondPage', 'FilePage', 'SVG'.
       'responder' - responder Class name, such as 'SubmitData' etc., or empty string if the page is not a responder.
       'enable_cache' - True if client caching is enabled on the page, False otherwise.
       'change' - A UUID string changed whenever the page is edited
       'parentfolder_number' - The uident number of the folder containing this page
"""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    page_ident = skiboot.Ident(project, pagenumber)
    page = proj.get_item(page_ident)
    if page is None:
        raise ServerError("Page not recognised")
    if page.page_type == 'Folder':
        raise ServerError("Item is a Folder, not a page")
    if page.page_type == 'RespondPage':
        responder = page.responder.__class__.__name__
    else:
        responder = ''
    if hasattr(page, 'enable_cache'):
        enable_cache = page.enable_cache
    else:
        enable_cache = False
    if page.parentfolder_ident:
        parentfolder_number = page.parentfolder_ident.num
    else:
        parentfolder_number = None
    return PageInfo(page.name, page.ident.num, page.restricted, page.brief, page.page_type, responder, enable_cache, page.change, parentfolder_number)


def folders(project, foldernumber):
    """Returns generator of FolderInfo named tuples, one for each sub folder in the folder

    The project must exist as either the root, or a sub project of the root, foldernumber is the ident number of a folder.

    The generator raises a ServerError if no folder is found, otherwise the generator yields a namedtuple describing each sub folder within the folder over each iterated pass.

    The named tuple has contents:
    'name', 'number', 'restricted', 'brief', 'contains_pages', 'contains_folders', 'change'.

    The values are:
    'name' holds the sub folder name.
    'number' is the sub folder number.
    'restricted' is True if access is restricted (cannot be called by URL), False otherwise.
    'brief' holds the brief description of the sub folder.
    'contains_pages' - True if the sub folder contains pages, False otherwise.
    'contains_folders' - True if the sub folder contains pages, False otherwise.
    'change' - A UUID string, changed whenever the folder is changed.
"""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    folder_ident = skiboot.Ident(project, foldernumber)
    folder = proj.get_item(folder_ident)
    if folder is None:
        raise ServerError("Folder not recognised")
    for subfolder_ident in folder.folder_idents():
        subfolder = proj.get_item(subfolder_ident)
        yield FolderInfo(subfolder.name, subfolder.ident.num, subfolder.restricted, subfolder.brief, bool(subfolder.pages), bool(subfolder.folders), subfolder.change)


def folder_info(project, foldernumber):
    """Returns FolderInfo named tuple for folder

    The project must exist as either the root, or a sub project of the root, foldernumber is the ident number of a folder.

    The function raises a ServerError, if no folder is found, otherwise returns a namedtuple with contents:
    'name', 'number', 'restricted', 'brief', 'contains_pages', 'contains_folders', 'change'.

    The values are:
    'name' holds the folder name.
    'number' is the folder number from the argument.
    'restricted' is True if access is restricted (cannot be called by URL), False otherwise.
    'brief' holds the brief description of the folder.
    'contains_pages' - True if the folder contains pages, False otherwise.
    'contains_folders' - True if the folder contains pages, False otherwise.
    'change' - A UUID string, changed whenever the folder is changed
"""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    folder_ident = skiboot.Ident(project, foldernumber)
    folder = proj.get_item(folder_ident)
    if folder is None:
        raise ServerError("Folder not recognised")
    if folder.page_type != 'Folder':
        raise ServerError("Item is not a Folder")
    return FolderInfo(folder.name, folder.ident.num, folder.restricted, folder.brief, bool(folder.pages), bool(folder.folders), folder.change)


def folder_page_names(project, foldernumber):
    """Returns tuple of (default_page_name, [page names,....]) where default_page_name is None if no default page has been set
       and the page names list is empty if no pages are present. The page names list is sorted."""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    folder_ident = skiboot.Ident(project, foldernumber)
    folder = proj.get_item(folder_ident)
    if folder is None:
        raise ServerError("Folder not recognised")
    # folder.pages is a dictionary of page.name:page.ident
    if not folder.pages:
        return None, []
    page_names = list(folder.pages.keys())
    page_names.sort()
    if folder.default_page_name:
        return folder.default_page_name, page_names
    return None, page_names


def parent_list(project, itemnumber):
    """Returns list of [(name,number),...] of parents, starting with ('root',0) ending with name and number of item"""
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    item_ident = skiboot.Ident(project, itemnumber)
    item = proj.get_item(item_ident)
    if item is None:
        raise ServerError("Item not recognised")
    return item.parent_list()


def page_path(project, item):
    "Returns a url path given a page or folder number or label, if not found, return None"
    # raise error if invalid project
    project_loaded(project)
    return skiboot.get_url(item, project)


def insert_item_in_page(project, pagenumber, pchange, location, item):
    "Insert the item in the page at location, return the new pchange value and new location"
    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != 'TemplatePage') and (page.page_type != 'SVG'):
        raise ServerError(message="The page must be a Template or SVG page")
    if hasattr(item, 'name') and item.name:
        name = item.name
        if name in page.widgets:
            raise ServerError(message="The name clashes with a widget name already in the page")
        if name in page.section_places:
            raise ServerError(message="This name clashes with a section alias within this page")
    if hasattr(item, 'placename'):
        name = item.placename
        if name in page.widgets:
            raise ServerError(message="The alias clashes with a widget name already in the page")
        if name in page.section_places:
            raise ServerError(message="This alias clashes with another section alias within this page")

    location_string, container, location_integers = location
    location_integers = [int(i) for i in location[2]]
    # location string is either a widget name, or body, head, or svg
    # if a widget_name, container must be given
    # get the part at the current location
    if container is None:
        # not in a widget
        parent_widget = None
        part = page.location_item((location_string, None, location_integers))
    else:
        # so item is in a widget, location_string is the widget name
        parent_widget = page.widgets[location_string]
        part = parent_widget.get_from_container(container, location_integers)


    # If this item is to be placed inside a parent widget container
    if (parent_widget is not None) and (parent_widget.is_container_empty(container)):
        # item is to be set as the first item in a widget container
        new_location = (location_string, container, (0,))
        parent_widget.set_in_container(container, (0,), item)
    elif isinstance(part, tag.Part) and (not hasattr(part, "arg_descriptions")): # not Closed Part and not a widget
        # insert at position 0 inside the part
        new_location = (location_string, container, tuple(location_integers + [0]))
        part.insert(0,item)
    elif (parent_widget is not None) and (len(location_integers) == 1):
        # part is inside a container with parent being the containing div
        # so append after the part by inserting at the right place in the container
        position = location_integers[0] + 1
        new_location = (location_string, container, (position,))
        parent_widget.insert_into_container(container, position, item)
    else:
        # do an append, rather than an insert
        # get parent part
        loc_integers = location_integers[:-1]
        if (location_string == 'head') or (location_string == 'body') or (location_string == 'svg'):
            parent_part = page.location_item((location_string, None, loc_integers))
        else:
            # parent_widget is the containing widget 
            parent_part = parent_widget.get_from_container(container, loc_integers)

        # find location digit
        loc = location_integers[-1] + 1
        new_location = (location_string, container, tuple(location_integers[:-1] + [loc]))
        # insert item at loc in parent_part
        parent_part.insert(loc,item)

    # save the altered page and return the change uuid, and new location
    return proj.save_page(page), new_location


def insert_item_in_section(project, section_name, schange, location, item):
    "Insert the item in the section at location, return the new schange value and new location"
    proj, section = get_proj_section(project, section_name, schange)
    if hasattr(item, 'name') and item.name:
        name = item.name
        if name in section.widgets:
            raise ServerError(message="The name clashes with a widget name already in the section")
    location_string, container, location_integers = location
    location_integers = [int(i) for i in location[2]]
    # location string is either a widget name, or the section name
    # if a widget_name, container must be given
    # get the part at the current location
    if container is None:
        # not in a widget
        parent_widget = None
        if location_string != section_name:
            raise ServerError(message="Invalid location, section name not equal to location string")
        if location_integers:
            part = section.get_location_value(location_integers)
        else:
            part = section
    else:
        # so item is in a widget, location_string is the widget name
        parent_widget = section.widgets[location_string]
        part = parent_widget.get_from_container(container, location_integers)


    # If this item is to be placed inside a parent widget container
    if (parent_widget is not None) and (parent_widget.is_container_empty(container)):
        # item is to be set as the first item in a widget container
        new_location = (location_string, container, (0,))
        parent_widget.set_in_container(container, (0,), item)
    elif isinstance(part, tag.Part) and (not hasattr(part, "arg_descriptions")): # not Closed Part and not a widget
        # insert at position 0 inside the part
        new_location = (location_string, container, tuple(location_integers + [0]))
        part.insert(0,item)
    elif (parent_widget is not None) and (len(location_integers) == 1):
        # part is inside a container with parent being the containing div
        # so append after the part by inserting at the right place in the container
        position = location_integers[0] + 1
        new_location = (location_string, container, (position,))
        parent_widget.insert_into_container(container, position, item)

    else:
        # do an append, rather than an insert
        # get parent part
        loc_integers = location_integers[:-1]
        if parent_widget is None:
            # part not in a widget
            if location_string == section_name:
                if loc_integers:
                    parent_part = section.get_location_value(loc_integers)
                else:
                    parent_part = section
        else:
            parent_part = parent_widget.get_from_container(container, loc_integers)

        # find location digit
        loc = location_integers[-1] + 1
        new_location = (location_string, container, tuple(location_integers[:-1] + [loc]))
        # insert item at loc in parent_part
        parent_part.insert(loc,item)

    # save the altered section, and return the change uuid, and new location
    return proj.add_section(section_name, section), new_location



def del_location_in_page(project, pagenumber, pchange, location):
    "Deletes the item at the given location in the page"
    # raise error if invalid project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != 'TemplatePage') and (page.page_type != 'SVG'):
        raise ServerError(message = "Invalid page")

    location_string, container, location_integers = location

    # location string is either a widget name, or body, head, or svg
    # if a widget_name, container must be given

    if container is None:
        # not in a widget
        if location_string == 'body':
            top = page.body
        elif location_string == 'head':
            top = page.head
        elif location_string == 'svg':
            top = page.svg
        else:
            raise ServerError(message="Given location is invalid")
        # remove the item
        try:
            top.del_location_value(location_integers)
        except Exception:
            raise ServerError(message="Unable to delete item")
        # And save this page copy to the project
        return proj.save_page(page)

    # so item is in a widget, location_string is the widget name
    widget = page.widgets[location_string]
    ident_string = widget.ident_string

    # ident_string is of the form; project_pageidentnumber_body-x-y

    splitstring = ident_string.split("_")
    splitloc = splitstring[2].split("-")
    loc_top = splitloc[0]
    widg_ints = [ int(i) for i in splitloc[1:] ]

    widg_container_ints = list(widget.get_container_loc(container))

    item_location_ints = widg_ints + widg_container_ints + list(location_integers)

    if loc_top == 'body':
        top = page.body
    elif loc_top == 'head':
        top = page.head
    elif loc_top == 'svg':
        top = page.svg
    else:
        raise ServerError(message="Given location is invalid")
    # remove the item
    try:
        top.del_location_value(item_location_ints)
    except Exception:
        raise ServerError(message="Unable to delete item")
    # And save this page copy to the project
    return proj.save_page(page)


def del_location_in_section(project, section_name, schange, location):
    "Deletes the item at the given location"
    # raise error if invalid project
    proj, section = get_proj_section(project, section_name, schange)

    location_string, container, location_integers = location

    if container is None:
        if location_string != section_name:
            raise ServerError(message="Unable to delete item")
        # remove the item
        try:
            section.del_location_value(location_integers)
        except Exception:
            raise ServerError(message="Unable to delete item")
        # And save this section copy to the project
        return proj.add_section(section_name, section)

    # so item is in a widget, location_string is the widget name
    widget = section.widgets[location_string]
    ident_string = widget.ident_string

    # ident_string is sectionname-x-y

    splitstring = ident_string.split("-")
    widg_ints = [ int(i) for i in splitstring[1:] ]

    widg_container_ints = list(widget.get_container_loc(container))

    item_location_ints = widg_ints + widg_container_ints + list(location_integers)

    # remove the item
    try:
        section.del_location_value(item_location_ints)
    except Exception:
        raise ServerError(message="Unable to delete item")
    # And save this section copy to the project
    return proj.add_section(section_name, section)



def set_item_in_page(project, pagenumber, pchange, location, item):
    "Sets an item in the location"

    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != 'TemplatePage') and (page.page_type != 'SVG'):
        raise ServerError(message = "Invalid page")

    location_string, container, location_list = location

    # set item in a page
    if (location_string == 'head'):
        page.head.set_location_value(location_list, item)
    elif (location_string == 'body'):
        page.body.set_location_value(location_list, item)
    elif (location_string == 'svg'):
        page.svg.set_location_value(location_list, item)
    elif container is not None: 
        # location is in widget container
        if location_string not in page.widgets:
            raise ServerError("Location of item not found")
        widget = page.widgets[location_string]
        widget.set_in_container(container, location_list, item)
    else:
        raise ServerError("Location of item not found")
    # And save this page copy to the project
    return proj.save_page(page)


def set_item_in_section(project, section_name, schange, location, item):
    "Sets an item in the location"

    proj, section = get_proj_section(project, section_name, schange)

    location_string, container, location_list = location

    # set item in a section
    if location_string == section_name:
        # part is not embedded in a widget
        section.set_location_value(location_list, item)
    elif container is not None: 
        # location is in widget container
        if location_string not in section.widgets:
            raise ServerError("Location of item not found")
        widget = section.widgets[location_string]
        widget.set_in_container(container, location_list, item)
    else:
        raise ServerError("Location of item not found")
    # And save this section copy to the project
    return proj.add_section(section_name, section)



