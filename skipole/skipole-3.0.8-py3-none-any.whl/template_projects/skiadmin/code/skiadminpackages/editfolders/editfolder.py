

import html

from collections import OrderedDict

from skipole import ValidateError, FailPage, ServerError, GoTo
from skipole import skilift
from skipole.skilift import editpage, editfolder, fromjson
from .. import utils


def edit_root(skicall):
    "Go to edit root folder, with no other call_data contents other than those set here"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # called by responder 3, edit_root link from Root Folder nav button
    # this responder then targets responder 22008 to fill in root folder fields
    utils.clear_call_data(call_data)
    call_data['folder_number'] = 0


def goto_edited_folder(skicall):
    """Called by responder 2001 with requests from various places to to edit a folder
       This responder passes the call to another responder which calls retrieve_edited_folder"""

    call_data = skicall.call_data
    page_data = skicall.page_data
    submit_dict = skicall.submit_dict

    if 'received_data' not in submit_dict:
        raise FailPage(message = "Folder missing")

    # from the folder edit page
    widgfields = submit_dict['received_data']
    if ('ftree','edited_item') in widgfields:
        call_data['edit_folder'] = widgfields['ftree','edited_item']


def retrieve_edited_folder(skicall):
    "Fills in the edit folder page, including the tree of folder contents"

    call_data = skicall.call_data
    page_data = skicall.page_data

    editedprojname = call_data['editedprojname']

    # 'edit_folder' is from a form, not from session data

    if 'edit_folder' in call_data:
        try:
            proj,folder = call_data['edit_folder'].split('_')
            folder_number = int(folder)
        except Exception:
            raise FailPage(message = "Invalid Folder")
        if proj != editedprojname:
            raise FailPage(message = "Invalid Folder")
        del call_data['edit_folder']
        call_data['folder_number'] = folder_number
    elif 'folder_number' in call_data:
        folder_number = call_data['folder_number']
    else:
        raise FailPage(message = "Folder missing")

    info = skilift.item_info(editedprojname, folder_number)

    # info is a named tuple with members
    # 'project', 'project_version', 'itemnumber', 'item_type', 'name', 'brief', 'path', 'label_list', 'change', 'parentfolder_number', 'restricted'

    if (not info) or (info.item_type != "Folder"):
        raise FailPage(message = "Invalid folder")

    call_data['fchange'] = info.change

    contents, dragrows, droprows = _foldertree(editedprojname, folder_number)
    page_data['ftree', 'contents'] = contents

    # old code, was just rows 

    page_data['ftree', 'dragrows'] = dragrows
    page_data['ftree', 'droprows'] = droprows
    page_data['ftree', 'dropident'] = 'drop_rows' # label of responder

    page_data['ftree', 'cols'] = [ ["", ""],
                                   ["", ""],
                                   ["", ""],
                                   ["", ""],
                                   ["edit_action", ""],
                                   ["edit_action", ""],
                                   ["edit_action", ""],
                                   ["no_javascript", "2004"]  ]

    if call_data['folder_number'] == 0:
        page_data[("adminhead","page_head","large_text")] = "Edit Root Folder : %s" % (info.path,)
    else:
        page_data[("adminhead","page_head","large_text")] = "Edit Folder : %s" % (info.path,)

    # set edited folder in the required dictionary
    page_data['ie1:page_ident'] = (info.project, info.itemnumber)
    if 'brief' in call_data:
        page_data['st2:folder_brief'] = call_data['brief']
    else:
        page_data['st2:folder_brief'] = info.brief
    # check if this is rootfolder
    if info.itemnumber == 0:
        # hide certain items if this is the root folder
        page_data['rename_folder','show'] = False
        page_data['sp1:show_parent_restricted'] = False
        page_data['sb1:show_set_restricted'] = False
        page_data['sb2:show_set_unrestricted'] = False
    else:
        # The folder can be given a name
        if 'name' in call_data:
            page_data['rename_folder','input_text'] = call_data['name']
        else:
            page_data['rename_folder', 'input_text'] = info.name
        parent = skilift.item_info(info.project, info.parentfolder_number)
        if parent.restricted:
            page_data['sp1:show_parent_restricted'] = True
            page_data['sb1:show_set_restricted'] = False
            page_data['sb2:show_set_unrestricted'] = False
        else:
            # parent is not restricted
            page_data['sp1:show_parent_restricted'] = False
            if info.restricted:
                # folder currently restricted
                page_data['sb1:show_set_restricted'] = False
                page_data['sb2:show_set_unrestricted'] = True
            else:
                # folder currently unrestricted
                page_data['sb1:show_set_restricted'] = True
                page_data['sb2:show_set_unrestricted'] = False
    # get default page, and list of page names within the folder
    default_page_name, page_names = skilift.folder_page_names(info.project, info.itemnumber)
    if default_page_name:
        page_data['sdd1:selectvalue'] = default_page_name
    else:
        page_data['sdd1:selectvalue'] = "-None-"
    page_data['sdd1:option_list'] = page_names
    if page_names:
        if info.restricted:
            # do not give a choose default page option if the folder has restricted access
            page_data['sdd1:show'] = False
        else:
            page_data['sdd1:option_list'].insert(0,"-None-")
            page_data['sdd1:show'] = True
    else:
        # Only give a default page option if pages are present
        page_data['sdd1:show'] = False


def move_to_folder(skicall):
    "moves item defined by dragrows to folder defined by droprows and refreshes ftree via JSON call"

    call_data = skicall.call_data
    page_data = skicall.page_data

    editedprojname = call_data['editedprojname']

    # folder_number is the top folder of ftree
    if 'folder_number' in call_data:
        folder_number = call_data['folder_number']
    else:
        raise FailPage(message = "Folder missing")

    # item_ident is the item to move
    item_ident = call_data['ftree', 'dragrows']

    if '_' not in item_ident:
        raise FailPage(message="No valid item to move given")

    item_proj, item_num = item_ident.split("_")
    if item_proj != editedprojname:
        raise FailPage(message="No valid item to move given")

    # folder_ident is the target folder
    folder_ident = call_data['ftree', 'droprows']

    if '_' not in folder_ident:
        raise FailPage(message="No valid target folder given")

    folder_proj, folder_num = folder_ident.split("_")
    if folder_proj != editedprojname:
        raise FailPage(message="No valid target folder given")

    try:
        folder_num = int(folder_num)
        item_num = int(item_num)
    except Exception:
        raise FailPage(message="Submission not recognised - integer numbers of item idents are require")

    # call function in skilift.editfolder
    try:
        editfolder.move_to_folder(editedprojname, item_num, folder_num)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = 'Item moved'
    # refresh ftree
    contents, dragrows, droprows = _foldertree(editedprojname, folder_number)
    page_data['ftree', 'contents'] = contents
    page_data['ftree', 'dragrows'] = dragrows
    page_data['ftree', 'droprows'] = droprows
    # this is sent by json to the page


def choose_edit_action(skicall):
    "Choose which action to take when called from ftree"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if ('ftree', 'contents') not in call_data:
        raise FailPage(message = "Requested action not recognised")
    action = call_data['ftree', 'contents']
    try:
        get_field_list = action.split('_')
        project = get_field_list[-2]
        itemnumber = int(get_field_list[-1])
    except Exception:
        raise FailPage(message = "Requested action not recognised")
    if action.startswith('edit_folder_'):
        call_data['edit_folder'] = action[12:]
        raise GoTo(('skiadmin',22008), clear_submitted=True, clear_page_data=True)
    elif action.startswith('add_folder_'):
        call_data['parent'] = action[11:]
        raise GoTo(('skiadmin',22107), clear_submitted=True, clear_page_data=True)
    elif action.startswith('add_page_'):
        call_data['edited_folder'] = action[9:]
        raise GoTo(('skiadmin',22307), clear_submitted=True, clear_page_data=True)
    elif action.startswith('edit_page_'):
        # must find type of page to edit
        try:
            # pinfo is tuple 'name', 'number', 'restricted', 'brief', 'item_type', 'responder', 'enable_cache', 'change'
            pinfo = skilift.page_info(project, itemnumber)
        except Exception:
            raise FailPage(message = "Requested page not recognised")
        call_data['page_number'] = pinfo.number
        call_data['pchange'] = pinfo.change
        if pinfo.item_type == 'CSS':
            raise GoTo(28007, clear_submitted=True, clear_page_data=True)         # css edit page
        elif pinfo.item_type == 'JSON':
            raise GoTo(20407, clear_submitted=True, clear_page_data=True)         # json edit page
        elif pinfo.item_type == 'TemplatePage':
            raise GoTo(23207, clear_submitted=True, clear_page_data=True)          # retrieve template edit page contents
        elif pinfo.item_type == 'SVG':
            raise GoTo(23407, clear_submitted=True, clear_page_data=True)          # svg edit page
        elif pinfo.item_type == 'RespondPage':
            raise GoTo(26007, clear_submitted=True, clear_page_data=True)          # retrieve responder edit page contents
        elif pinfo.item_type == 'FilePage':
            raise GoTo(29007, clear_submitted=True, clear_page_data=True)          # filepage edit page
    # no action recognised
    raise FailPage(message = "Requested action not recognised")



def choose_remove_action(skicall):
    "Choose to remove a page or folder, fills in confirm box"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if ('ftree', 'contents') not in call_data:
        raise FailPage(message = "Requested action not recognised")
    action = call_data['ftree', 'contents']
    try:
        get_field_list = action.split('_')
        project = get_field_list[-2]
        itemnumber = int(get_field_list[-1])
        info = skilift.item_info(project, itemnumber)
    except Exception:
        raise FailPage(message = "Item to remove not recognised")
    if not info:
        raise FailPage(message = "Item to remove not recognised")
    if itemnumber == 0:
        raise FailPage(message = "Cannot delete the root folder")
    # display the modal confirm box
    page_data['page_delete', 'hide'] = False
    page_data['page_delete', 'para_text'] = "Delete %s with ident %s and name %s" % (info.item_type, info.itemnumber, info.name)
    page_data['page_delete', 'get_field2_1'] = project + '_' + str(itemnumber)



def delete_item(skicall):
    "Deletes a folder or page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    try:
        ident = call_data['page_delete','get_field2_1'].split('_')
        project = ident[0]
        itemnumber = int(ident[1])
        info = skilift.item_info(project, itemnumber)
    except Exception:
        raise FailPage(message = "Item to remove not recognised")

    if not info:
        raise FailPage(message = "Item to remove not recognised")

    parentfolder_number = info.parentfolder_number

    if itemnumber == 0:
        raise FailPage(message = "Cannot delete the root folder")

    if info.item_type == 'Folder':
        # call skilift.editfolder.delete_folder
        error = editfolder.delete_folder(project, itemnumber)
        if error:
            raise FailPage(message = "Unable to delete the folder")
        call_data['status'] = 'Folder deleted'
        # get folder to show on ftree
        if "folder_number" in call_data:
            folder_number = call_data["folder_number"]
            if folder_number == itemnumber:
                folder_number = parentfolder_number
                call_data["folder_number"] = parentfolder_number
        else:
            folder_number = parentfolder_number
            call_data["folder_number"] = parentfolder_number
        call_data["fchange"] = editfolder.folderchange(project, folder_number)
        return

    # If not a Folder, must be a page

    # call skilift.editpage.delete_page
    error = editpage.delete_page(project, itemnumber)
    if error:
        raise FailPage(message = "Unable to delete the page")

    # as page is deleted, this will affect any page objects
    # stored in call_data, so clear them

    if 'page_number' in call_data:
        del call_data['page_number']
    if 'page' in call_data:
        del call_data['page']

    # get folder to show on ftree
    if "folder_number" in call_data:
        folder_number = call_data["folder_number"]
    else:
        folder_number = parentfolder_number
        call_data["folder_number"] = parentfolder_number
    call_data["fchange"] = editfolder.folderchange(project, folder_number)
    call_data['status'] = 'Page deleted'


def submit_rename_folder(skicall):
    "rename this folder"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    if 'name' not in call_data:
        raise FailPage(message="No new folder name has been given", widget="rename_folder")
    # Rename the folder
    # call skilift.editfolder.rename_folder which returns a new fchange
    try:
        call_data['fchange'] = editfolder.rename_folder(call_data['editedprojname'], call_data['folder_number'], call_data['fchange'], call_data['name'])
    except ServerError as e:
        raise FailPage(e.message, widget="rename_folder")
    call_data['status'] = 'Folder renamed'


def submit_folder_brief(skicall):
    "set this folders brief"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    project = call_data['editedprojname']
    foldernumber = call_data['folder_number']
    fchange = call_data['fchange']
    if 'brief' not in call_data:
        raise FailPage(message="No folder description available", widget="st2")
    new_brief = call_data['brief']
    if not new_brief:
        raise FailPage(message="No folder brief given", widget="st2")
    # call skilift.editfolder.folder_description which returns a new fchange
    try:
        call_data['fchange'] = editfolder.folder_description(project, foldernumber, fchange, new_brief)
    except ServerError as e:
        raise FailPage(e.message, widget="st2")
    call_data['status'] = 'Folder description set : %s' % (new_brief,)


def submit_default_page(skicall):
    "Set this folder's default page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    project = call_data['editedprojname']
    foldernumber = call_data['folder_number']
    fchange = call_data['fchange']
    if 'selectvalue' not in call_data:
        raise FailPage(message="The page to set as default has not been found", widget="sdd1")
    if call_data['selectvalue'] == "-None-":
        default_page_name = ""
    else:
        default_page_name = call_data['selectvalue']
    try:
        call_data['fchange'] = editfolder.set_default_page(project, foldernumber, fchange, default_page_name)
    except ServerError as e:
        raise FailPage(e.message, widget="sdd1")
    call_data['status'] = 'Default page set'


def submit_restricted(skicall):
    "set this folder as restricted"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    # restrict the folder
    try:
        call_data['fchange'] = editfolder.set_restricted_status(call_data['editedprojname'], call_data['folder_number'], call_data['fchange'], True)
    except ServerError as e:
        raise FailPage(e.message)


def submit_unrestricted(skicall):
    "set this folder as unrestricted"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    # un-restrict the folder
    try:
        call_data['fchange'] = editfolder.set_restricted_status(call_data['editedprojname'], call_data['folder_number'], call_data['fchange'], False)
    except ServerError as e:
        raise FailPage(e.message)


def downloadfolder(skicall):
    "Gets folder, and returns a json dictionary, this will be sent as an octet file to be downloaded"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'folder_number' not in call_data:
        raise FailPage(message = "Folder missing")
    jsonstring =  fromjson.folder_to_json(call_data['editedprojname'], call_data['folder_number'], indent=4)
    line_list = []
    n = 0
    for line in jsonstring.splitlines(True):
        binline = line.encode('utf-8')
        n += len(binline)
        line_list.append(binline)
    page_data['headers'] = [('content-type', 'application/octet-stream'), ('content-length', str(n))]
    return line_list



def _foldertree(projectname, foldernumber):
    """Returns contents list of lists with ftree table fields, with the given foldernumber of the folder at the top of
    the table"""

    finfo = skilift.folder_info(projectname, foldernumber)
    folder_path = skilift.item_info(projectname, foldernumber).path
    folder_ident = projectname + '_' + str(foldernumber)

    #   col 0 - text string, either text to display or button text
    #   col 1 - A 'style' string set on the td cell, if empty string, no style applied
    #   col 2 - Is button? If False only text will be shown, not a button, button class will not be applied
    #           If True a link to link_ident/json_ident will be set with button_class applied to it
    #   col 3 - The get field value of the button link, empty string if no get field

    # This creates a contents of cell's, each row of the table has eight columns
    contents = []
    dragrows = []
    droprows = []

    # first cell is the folder URL, no style, Not a link, no get field
    contents.append( (folder_path, '', False, '') )
 
    # second cell is the folder ident number
    contents.append( (str(finfo.number), '', False, '') )

    # third cell is restricted or not
    if finfo.restricted:
        contents.append( ('R', 'width : 1%;text-align: center;color: black;background-color: red;', False, '') )
    else:
        contents.append( ('', '', False, '') )

    # fourth cell is the folder brief
    if len(finfo.brief)>40:
        contents.append( (html.escape(finfo.brief[:35] + "..."), '', False, '') )
    else:
        contents.append( (html.escape(finfo.brief[:35]), '', False, '') )

    # fifth cell is an Edit link
    # top folder does not have an edit link
    contents.append( ('', '', False, '') )

    # sixth cell is add folder
    contents.append( ('Add Folder', 'width : 1%;text-align: center;', True, 'add_folder_' + folder_ident)    )

    # seventh cell is add page
    contents.append( ('Add Page', 'width : 1%;text-align: center;', True, 'add_page_' + folder_ident) )

    # eighth cell is remove line - but no remove link for the top line
    contents.append( ('', '', False, '') )

    dragrows.append([False, ""])
    droprows.append([True, folder_ident])

    # place all sub pages in rows beneath the folder
    if finfo.contains_pages:
        _show_pages(contents, projectname, foldernumber, dragrows, droprows, 2)
    if finfo.contains_folders:
        _show_folders(contents, projectname, foldernumber, dragrows, droprows, 2)
    return contents, dragrows, droprows


def _show_pages(contents, projectname, foldernumber, dragrows, droprows, indent):
    """Used to create pages  beneath the folder"""

    # pinfo attributes are 'name', 'number', 'restricted', 'brief', 'item_type', 'responder'

    ident = projectname + "_"
    padding = "padding-left : %sem;" % (indent,)

    for pinfo in skilift.pages(projectname, foldernumber):

        page_ident = ident + str(pinfo.number)
        dragrows.append([True, page_ident])
        droprows.append([False, ""])

        # first column is the page name, style includes padding, not a link, no get field
        contents.append( (pinfo.name, padding, False, '') )
 
        # second column is the page ident number, no style, not a link, no get field
        contents.append( (str(pinfo.number), '', False, '') )

        # third column is restricted or not
        if pinfo.restricted:
            contents.append( ('R', 'width : 1%;text-align: center;color: black;background-color: red;', False, '') )
        else:
            contents.append( ('', '', False, '') )

        # fourth cell is the page brief
        if len(pinfo.brief)>40:
            contents.append( (html.escape(pinfo.brief[:35] + "..."), '', False, '') )
        else:
            contents.append( (html.escape(pinfo.brief[:35]), '', False, '') )

        # fifth column is an Edit link
        contents.append( ('Edit', 'width: 1%;text-align: center;', True, 'edit_page_' + page_ident) )

        # sixth column is page type
        # seventh either empty or responder type

        if pinfo.item_type == 'TemplatePage':
            contents.append( ('Template', 'text-align: center;', False, '') )
            contents.append( ('', '', False, '') )
        elif pinfo.item_type == 'RespondPage':
            contents.append( ('Responder', 'text-align: center;', False, '') )
            contents.append( (pinfo.responder, 'text-align: center;', False, '') )
        elif pinfo.item_type == 'CSS':
            contents.append( ('CSS', 'text-align: center;', False, '') )
            contents.append( ('', '', False, '') )
        elif pinfo.item_type == 'JSON':
            contents.append( ('JSON', 'text-align: center;', False, '') )
            contents.append( ('', '', False, '') )
        elif pinfo.item_type == 'SVG':
            contents.append( ('SVG', 'text-align: center;', False, '') )
            contents.append( ('', '', False, '') )
        elif pinfo.item_type == 'FilePage':
            contents.append( ('File', 'text-align: center;', False, '') )
            contents.append( ('', '', False, '') )
        else:
            raise ServerError(message="An unknown page type")

        # eighth column is remove page
        contents.append( ('Remove', 'width : 1%;text-align: center;', True, page_ident) )

    return


def _show_folders(contents, projectname, foldernumber, dragrows, droprows, indent):


    # finfo attributes are 'name', 'number', 'restricted', 'brief', 'contains_pages', 'contains_folders'

    ident = projectname + "_"
    padding = "padding-left : %sem;" % (indent,)

    for finfo in skilift.folders(projectname, foldernumber):

        folder_ident = ident + str(finfo.number)
        dragrows.append([True, folder_ident])
        droprows.append([True, folder_ident])

        # first column is the folder path from parent, with padding style, Not a link, no get field
        contents.append( (finfo.name+"/", padding, False, '') )

        # second column is the folder ident number, no style, not a link, no get field
        contents.append( (str(finfo.number), '', False, '') )

        # third column is restricted or not
        if finfo.restricted:
            contents.append( ('R', 'width : 1%;text-align: center;color: black;background-color: red;', False, '') )
        else:
            contents.append( ('', '', False, '') )

        # fourth cell is the folder brief
        if len(finfo.brief)>40:
            contents.append( (html.escape(finfo.brief[:35] + "..."), '', False, '') )
        else:
            contents.append( (html.escape(finfo.brief[:35]), '', False, '') )

        # fifth column is an Edit link
        contents.append( ('Edit', 'width: 1%;text-align: center;', True, 'edit_folder_' + folder_ident) )

        # sixth column is add folder
        contents.append( ('Add Folder', 'width : 1%;text-align: center;', True, 'add_folder_' + folder_ident) )

        # seventh column is add page
        contents.append( ('Add Page', 'width : 1%;text-align: center;', True, 'add_page_' + folder_ident) )

        # eighth column is remove line - but no remove if folder has contents
        if finfo.contains_pages or finfo.contains_folders:
            contents.append( ('', '', False, '') )
        else:
            contents.append( ('Remove', 'width : 1%;text-align: center;', True, folder_ident) )

        # place all sub pages in rows beneath the subfolder
        if finfo.contains_pages:
            _show_pages(contents, projectname, finfo.number, dragrows, droprows, indent+1)

        if finfo.contains_folders:
            _show_folders(contents, projectname, finfo.number, dragrows, droprows, indent+1)

    return



