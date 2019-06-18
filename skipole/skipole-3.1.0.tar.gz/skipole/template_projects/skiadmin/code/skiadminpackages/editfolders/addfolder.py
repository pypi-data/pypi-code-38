
import os, re

from skipole import ValidateError, FailPage, ServerError

from skipole import skilift
from skipole.skilift import editfolder, fromjson



# a search for anything none-alphanumeric, not a dot and not a underscore and not an hyphen
_ANDH = re.compile('[^\w\.\-]')



def _get_folder_info(project, folder):
    "Given a folder ident string such as number or 'project,number' or 'project_number' return FolderInfo, folder_url"
    try:
        foldernumber = skilift.get_itemnumber(project, folder)
        if foldernumber is None:
            raise FailPage(message="Parent folder not recognised")
        folder_info = skilift.folder_info(project, foldernumber)
        folder_url = skilift.page_path(project, foldernumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    return folder_info, folder_url


def retrieve_add_folder(skicall):
    "Fill in the add a folder page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    # parent is the folder a new folder is to be added to
    # the value in call_data is the string ident submitted by the ftree add_folder button
    # or by a value in session_data
    if 'parent' in call_data:
        parent_info, parent_url = _get_folder_info(project, call_data['parent'])
    elif 'add_to_foldernumber' in call_data:
        parent_info, parent_url = _get_folder_info(project, call_data['add_to_foldernumber'])
    else:
        raise FailPage(message = "Parent folder missing")

    page_data[("adminhead","page_head","large_text")] = "Add folder to : %s" % (parent_url,)

    page_data[('staticpath','input_text')] = os.path.join(project, 'static')

    page_data[('newfolderform','parent')] = project+","+str(parent_info.number)
    call_data['add_to_foldernumber'] = parent_info.number

    # st1: new folder name
    if 'new_folder' in call_data:
        page_data[('foldername','new_folder')] = call_data['new_folder']

    # cb1: restricted checkbox
    if ('checkbox' in call_data) and call_data['checkbox']:
        page_data[('cb1','checked')] = True
    else:
        page_data[('cb1','checked')] = False
    if parent_info.restricted:
        page_data[('cb1','show_restricted')] = False
    else:
        page_data[('cb1','show_restricted')] = True

    # it1: text input for folder brief
    if ('folder_brief' in call_data) and call_data['folder_brief']:
        page_data[('it1','folder_brief')] = call_data['folder_brief']

    # it2: folder ident number
    if 'folder_ident_number' in call_data:
        page_data[('it2','folder_ident_number')] = str(call_data['folder_ident_number'])
    else:
        page_data[('it2','folder_ident_number')] = str(skilift.next_ident_number(project))


def submit_addfolder(skicall):
    """ Creates a folder by making a dictionary similar to:

    {
     "name":"folder_name",
     "ident":999,
     "brief":"brief description of the folder",
     "restricted":False
    }

    And then calling editfolder.make_new_folder.

    Also calls _make_static_folder if folderpath is in call data

"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    folder_dict = {}

    if 'parent' not in call_data:
        raise FailPage(message = "Parent folder missing")
    # the parent value in call_data is the string ident submitted by the button
    parentinfo, parent_url = _get_folder_info(project, call_data['parent'])

    # parentinfo is a named tuple with members
    # 'name', 'number', 'restricted', 'brief', 'contains_pages', 'contains_folders'

    if ('new_folder' not in call_data) or ('checkbox' not in call_data) or ('folder_brief' not in call_data) or ('folder_ident_number' not in call_data):
        raise FailPage("New folder information missing")

    try:
        folder_ident_number = int(call_data['folder_ident_number'])
    except Exception:
        raise FailPage("The Folder Ident number must be an integer")
    if folder_ident_number<1:
        raise FailPage("The Folder Ident number must be a positive integer greater than zero")
    folder_dict["ident"] = folder_ident_number
    folder_dict["brief"] = call_data['folder_brief']
    folder_dict["restricted"] = call_data['checkbox']

    new_folder_name = call_data['new_folder']
    # check name is alphanumric or underscore or dot or hyphen only
    if _ANDH.search(new_folder_name):
        raise FailPage(message = "Folder names must be alphanumric and may also have dots or underscores or hyphens")
    folder_dict["name"] = new_folder_name


    if 'folderpath' in call_data and call_data['folderpath']:
        folderpath = call_data['folderpath']
        folderpath = folderpath.rstrip('/')
        folderpath = folderpath.rstrip('\\')
        if not folderpath:
            raise FailPage("Sorry, the given static folder is invalid.")
        fullpath = os.path.join(skilift.get_projectdir(project), folderpath)
        if not os.path.isdir(fullpath):
            raise FailPage("Sorry, the given static folder location cannot be found.")
        if not call_data['folder_brief']:
            folder_dict["brief"] = "Link to %s" % folderpath
    else:
        folderpath = None
        fullpath = None

    try:
        # create the folder
        editfolder.make_new_folder(project, parentinfo.number, folder_dict)
    except ServerError as e:
        raise FailPage(message = e.message)

    if fullpath:
        # add subfolders and file pages
        _make_static_folder(project, folder_dict, fullpath, folderpath)
        call_data['status'] = 'Static folder tree added'
        return

    call_data['status'] = 'New folder %s added.' % (parent_url + folder_dict["name"] + '/',)


def _make_static_folder(project, folder_dict, fullpath, folderpath):
    """Creates containing sub folders and Filepages pointing to static files within a directory
       of the server"""
    try:
        # loads everything under folderpath as Folders and FilePages
        # ident_dict maps folderpath to newly created folder ident numbers
        ident_dict = {}
        ident_dict[folderpath] = folder_dict["ident"]
        ident = folder_dict["ident"]
        ident_number_list = skilift.ident_numbers(project)
        for root, dirs, files in os.walk(fullpath):
            fpath = root[len(skilift.get_projectdir(project))+1:]
            parent_ident = ident_dict[fpath]
            if files:
                # create files
                for filename in files:
                    new_filepath=os.path.join(fpath, filename)
                    new_page_dict = {"name":filename,
                                     "brief":"Link to %s" % (new_filepath,),
                                     "FilePage": {
                                         "filepath": new_filepath,
                                         }
                                     }
                    if ident:
                        ident +=1
                        if ident not in ident_number_list:
                            new_page_dict["ident"] = ident
                    editfolder.make_new_page(project, parent_ident, new_page_dict)
            if dirs:
                # create folders
                for foldername in dirs:
                    new_folderpath=os.path.join(fpath, foldername)
                    new_folder_dict = {"name":foldername,
                                       "brief":"Link to %s" % (new_folderpath,),
                                       "restricted":False
                                      }
                    if ident:
                        ident +=1
                        if ident not in ident_number_list:
                            new_folder_dict["ident"] = ident
                    ident_dict[new_folderpath] = editfolder.make_new_folder(project, parent_ident, new_folder_dict)
    except ServerError as e:
        raise FailPage(e.message)



def submit_upload_folder(skicall):
    "Copy a folder from uploaded file"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    # add_to_foldernumber is the folder a new folder is to be added to
    if 'add_to_foldernumber' not in call_data:
        raise FailPage(message = "Parent folder missing")

    # get submitted data for new folder
    try:
        addident = int(call_data['addident'])
    except Exception:
        raise FailPage(message = "Addition integer is invalid")
    importname = call_data['importname']
    uploadfile = call_data['uploadfile']
    json_string = uploadfile.decode(encoding='utf-8')
    # create the folder
    try:
        # note: restricted is set to False
        fromjson.create_folder(project, call_data['add_to_foldernumber'], addident, importname, False, json_string)
    except ServerError as e:
        raise FailPage(message = e.message, widget='import_folder')
    del call_data['add_to_foldernumber']
    call_data['status'] = 'New folder and contents added'

