

"""Functions for editing a folder"""

from ..ski import skiboot, read_json
from ..ski.excepts import ServerError

from . import project_loaded, item_info, ident_exists


def _get_folder(project, foldernumber):
    """On success return (deep copy of folder, empty string)
       on failure return (None, failure string)"""
    if not project_loaded(project, error_if_not=False):
        return None, "Given project is not loaded"
    if not isinstance(foldernumber, int):
        return None, "Given foldernumber is not an integer"
    ident = skiboot.Ident.to_ident((project, foldernumber))
    if ident is None:
        return None, "Invalid project, foldernumber"
    folder = skiboot.from_ident(ident, project)
    if folder is None:
        return None, "Invalid Folder"
    if folder.page_type != 'Folder':
        return None, "Item is not a Folder"
    return folder, ""


def folderchange(project, foldernumber):
    """Returns the folder change UUID string

       Given a project name, and the integer ident number of a folder within the project,
       returns a 'change' uuid associated  with the folder. A new random uuid is generated
       every time a folder is changed, and is therefore a measure that a given folder both
       exists, and has not changed since the last time it was accessed.
       The project must be currently loaded as either the root project or a sub-project.
       Returns None if no folder with this foldernumber is found."""
    # raise error if invalid project
    project_loaded(project)
    info = item_info(project, foldernumber)
    if not info:
        return
    if info.item_type != "Folder":
        return
    return info.change


def rename_folder(project, foldernumber, fchange, newname):
    """Rename the folder, return folder change uuid on success, raises ServerError on failure

       Given a project name, the integer ident number of a folder within the project,
       the folder change uuid and a new folder name, it changes the folder name and
       returns a new uuid on success, or raises a ServerError on failure.
       The project must be currently loaded as either the root project or a sub-project."""
    if not newname:
        raise ServerError(message="No new folder name given")
    # get a copy of the folder, which can have a new name set
    # and can then be saved to the project
    folder, error_message = _get_folder(project, foldernumber)
    if folder is None:
        raise ServerError(message=error_message)
    if folder.ident.num == 0:
        raise ServerError(message="Cannot rename the root folder")
    if folder.change != fchange:
        raise ServerError(message="The folder has been changed prior to this submission, someone else may be editing this project")
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="Project not loaded")
    # Rename the folder
    folder.name = newname
    # And save this folder copy to the project
    return proj.save_folder(folder)


def delete_folder(project, foldernumber):
    "delete this folder, return None on success, error message on failure"
    folder, error_message = _get_folder(project, foldernumber)
    if folder is None:
        return error_message
    editedproj = skiboot.getproject(project)
    if editedproj is None:
        return "Project not loaded"
    if folder.page_type != "Folder":
        return "Invalid folder"
    if folder.ident.num == 0:
        return "Cannot delete the root folder"
    if len(folder):
        return "Cannot delete a folder with contents"
    try:
        # delete the folder from the project
        editedproj.delete_item(folder.ident)
    except ServerError as e:
        return e.message


def folder_description(project, foldernumber, fchange, brief):
    "Set a folder brief description, return folder change uuid on success, raises ServerError on failure"
    if not brief:
        return "No new folder name given"
    # get a copy of the folder, which can have a new brief set
    # and can then be saved to the project
    folder, error_message = _get_folder(project, foldernumber)
    if folder is None:
        return error_message
    if folder.change != fchange:
        raise ServerError(message="The folder has been changed prior to this submission, someone else may be editing this project")
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="Project not loaded")
    # Set the folder brief
    folder.brief = brief
    # save the altered folder, and return the folder.change uuid
    return proj.save_folder(folder)


def set_default_page(project, foldernumber, fchange, default_page_name):
    "set new default page on this folder, return folder change uuid on success, raises ServerError on failure"
    # get a copy of the folder
    # which can then be saved to the project
    folder, error_message = _get_folder(project, foldernumber)
    if folder is None:
        raise ServerError(message=error_message)
    if folder.change != fchange:
        raise ServerError(message="The folder has been changed prior to this submission, someone else may be editing this project")
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="Project not loaded")
    if not default_page_name:
        default_page_name = ''
    elif default_page_name not in folder.pages:
        raise ServerError(message="The page to set as default has not been found in this folder")
    folder.default_page_name = default_page_name
    # save the altered folder, and return the folder.change uuid
    return proj.save_folder(folder)


def set_restricted_status(project, foldernumber, fchange, restricted):
    """set restricted True, set this folder restricted, or unrestricted if False.
       r, return folder change uuid on success, raises ServerError on failure"""
    # get a copy of the folder
    # which can then be saved to the project
    if foldernumber == 0:
        return "Cannot change the root folder restricted status"
    folder, error_message = _get_folder(project, foldernumber)
    if folder is None:
        raise ServerError(message=error_message)
    if folder.change != fchange:
        raise ServerError(message="The folder has been changed prior to this submission, someone else may be editing this project")
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="Project not loaded")
    if restricted:
        # set folder and sub items as retricted
        restricted_list = folder.set_restricted()
        if not restricted_list:
            raise ServerError(message="No action taken")
        # And save this folder copy to the project
        for f in restricted_list:
            proj.save_folder(f)
        return folderchange(project, foldernumber)
    # unset restricted if parent is not restricted
    if folder.parentfolder.restricted:
        raise ServerError(message="Parent folder is restricted, cannot set this folder as unrestricted")
    # un-restrict the folder
    status = folder.set_unrestricted()
    if not status:
        raise ServerError(message="Failed to set unrestricted")
    # And save this folder copy to the project
    # save the altered folder, and return the folder.change uuid
    return proj.save_folder(folder)


def _check_parent_number(project, parent_number):
    "Checks parent_number is a Folder and returns parentinfo"
    project_loaded(project)
    if not isinstance(parent_number, int):
        raise ServerError(message="parent_number is not an integer")
    parentinfo = item_info(project, parent_number)
    if not parentinfo:
        raise ServerError(message = "Invalid parent folder")
    # parentinfo is a named tuple with members
    # 'project', 'project_version', 'itemnumber', 'item_type', 'name', 'brief', 'path', 'label_list', 'change', 'parentfolder_number', 'restricted'

    if parentinfo.item_type != "Folder":
        raise ServerError(message = "The parent with this ident number is not a folder")
    return parentinfo


def move_to_folder(project, item_number, new_folder_number):
    "Moves a given item - a folder or page, to a new parent folder"
    project_loaded(project)
    if not isinstance(item_number, int):
        raise ServerError(message="item_number is not an integer")
    if not isinstance(new_folder_number, int):
        raise ServerError(message="new parent folder number is not an integer")

    item = skiboot.from_ident(item_number, proj_ident=project)
    if not item:
        raise ServerError(message="No valid item to move given")

    folder = skiboot.from_ident(new_folder_number, proj_ident=project)
    if not folder:
        raise ServerError(message="No valid target folder given")

    if folder.page_type != 'Folder':
        raise ServerError(message="Target item is not a folder")

    old_parent = item.parentfolder
    if old_parent == folder:
       raise ServerError(message="Parent folder unchanged?")

    if item.name in folder:
        raise ServerError(message="The folder already contains an item with this name")

    editedproj = skiboot.getproject(project)
    editedproj.save_item(item, folder.ident)


def make_new_folder(project, parent_number, folder_dict):
    """Creates a new folder, raise ServerError on failure, returns new folder ident number
    folder_dict is something like:

    {
     "name":"folder_name",
     "ident":999,
     "brief":"brief description of the folder",
     "restricted":False
    }

    if ident not given, this function chooses the next free ident number.
    """
    parentinfo = _check_parent_number(project, parent_number)
    if 'ident' not in folder_dict:
        editedproj = skiboot.getproject(project)
        folder_dict['ident'] = editedproj.max_ident_num+1
    elif ident_exists(project, folder_dict['ident']):
        raise ServerError(message = "An item with this ident number already exists")

    # create the folder
    ident = read_json.create_folder(project, parent_number, 0, folder_dict["name"], parentinfo.restricted, folder_dict)
    return ident.num


def make_new_page(project, parent_number, page_dict):
    """Creates a new page, raise ServerError on failure, returns new page ident number
    page_dict is something like:

    {
    "name":"normalize.css",
    "ident": 1002,
    "brief": "From necolas.github.io/normalize.css/",
    "FilePage": {
        "filepath": "newproj/static/css/normalize.css",
        "enable_cache": True,
        "mimetype": "text/css"
        }
    }

    if ident not given, this function chooses the next free ident number.
    """
    parentinfo = _check_parent_number(project, parent_number)
    if 'ident' in page_dict:
        # check it is an integer
        if not isinstance(page_dict['ident'], int):
            raise ServerError(message = "The new page ident number must be an integer")
    else:
        # no ident given, get next free number
        editedproj = skiboot.getproject(project)
        page_dict['ident'] = editedproj.max_ident_num+1
    if ident_exists(project, page_dict['ident']):
        raise ServerError(message = "An item with this ident number already exists")
    # create the page
    if "SVG" in page_dict:
        read_json.create_svgpage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    elif "TemplatePage" in page_dict:
        read_json.create_templatepage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    elif "FilePage" in page_dict:
        read_json.create_filepage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    elif "CSS" in page_dict:
        read_json.create_csspage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    elif "JSON" in page_dict:
        read_json.create_jsonpage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    elif "RespondPage" in page_dict:
        read_json.create_respondpage(project, parent_number, page_dict['ident'], page_dict['name'], page_dict['brief'], page_dict)
    else:
        raise ServerError("page data not recognized")
    return page_dict['ident']


def copy_page(project, pagenumber, foldernumber, new_page_number, new_name, brief):
    """Copy an existing page given by pagenumber, to a new page number with new name and brief into the folder given by foldernumber
       return the folder.change uuid"""
    if not isinstance(new_page_number, int):
        raise ServerError(message = "The new page ident number must be an integer")
    orig_page = skiboot.from_ident(pagenumber, project)
    if orig_page.page_type == "Folder":
        raise ServerError("Invalid item to be copied")
    parentinfo = _check_parent_number(project, foldernumber)
    folder = skiboot.from_ident(parentinfo.itemnumber, project)
    # create new page
    new_page = orig_page.copy(name=new_name, brief = brief)
    # add page to parent folder
    folder.add_page(new_page, new_page_number)
    return folder.change


