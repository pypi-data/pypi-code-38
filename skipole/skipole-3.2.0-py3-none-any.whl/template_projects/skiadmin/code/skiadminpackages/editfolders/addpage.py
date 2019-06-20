


import os, inspect, re

from skipole import ValidateError, FailPage, ServerError

from skipole import skilift
from skipole.skilift import fromjson, editfolder, editresponder, editpage

from .. import utils, css_styles

# a search for anything none-alphanumeric, not a dot and not an underscore
_AND = re.compile('[^\w\.]')

# a search for anything none-alphanumeric, not a dot and not a underscore and not an hyphen
_ANDH = re.compile('[^\w\.\-]')


def retrieve_add_page(skicall):

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'edited_folder' not in call_data:
        raise FailPage(message = "Folder missing")

    try:
        foldernumber = skilift.get_itemnumber(project, call_data['edited_folder'])
        if foldernumber is None:
            raise FailPage(message="Parent folder not recognised")
        folder_info = skilift.folder_info(project, foldernumber)
        folder_url = skilift.page_path(project, foldernumber)
    except ServerError as e:
        raise FailPage(message=e.message)

    page_data[("adminhead","page_head","large_text")] = "Add page to : %s" % (folder_url,)
    page_data['st1:parent'] = project + "_" + str(foldernumber)

    # rb1: page type checked
    if 'radio_checked' in call_data:
        page_data['rb1:radio_checked'] = call_data['radio_checked']

    page_data[('rb1','radio_values')] = ['page', 'responder', 'svg', 'css', 'json', 'file', 'copy']
    page_data[('rb1','radio_text')] = ['Template page',
                                           'Responder',
                                           'SVG Image page',
                                           'CSS page',
                                           'JSON page',
                                           'File Link page',
                                           'Copy an existing page']

    # st1: new page name
    if 'new_page' in call_data:
        page_data['it4:new_page'] = call_data['new_page']

    # it2: text input for page brief
    if ('page_brief' in call_data) and call_data['page_brief']:
        page_data['it2:page_brief'] = call_data['page_brief']

    # it3: page ident number
    if 'page_ident_number' in call_data:
        page_data['it3:page_ident_number'] = str(call_data['page_ident_number'])
    else:
        page_data['it3:page_ident_number'] = str(skilift.next_ident_number(project))


def _common_page_items(skicall):
    "Returns project, parent foldernumber, new pagenumber, new_name, new_brief"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'edited_folder' not in call_data:
        raise FailPage(message = "Folder missing")
    foldernumber = skilift.get_itemnumber(project, call_data['edited_folder'])
    if foldernumber is None:
        raise FailPage(message="Parent folder not recognised")
    # skilift.folder_info raises a ServerError if this is not a folder
    try:
        folder_info = skilift.folder_info(project, foldernumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # Get the new page number
    try:
        # pagenumber could be number or "project,number" or "project_number"
        page_ident = call_data['page_ident_number']
        if page_ident.startswith(project):
            if ',' in page_ident:
                page_ident = page_ident.split(',')[-1]
            elif '_' in page_ident:
                page_ident = page_ident.split('_')[-1]
        pagenumber = int(page_ident)
    except Exception:
        raise FailPage(message = "The page number is invalid")
    if pagenumber < 1:
        raise FailPage(message = "The page number is invalid")
    # Get the new page name
    if 'new_page' not in call_data:
        raise FailPage(message = "The name of the new page has not been found")
    new_name = call_data['new_page']
    # check name is alphanumric, dot or underscore only
    if _ANDH.search(new_name):
        raise FailPage(message = "Names must be alphanumric, and may contain dot or underscore or hyphen")
    # Get the new page brief
    if 'page_brief' in call_data:
        new_brief = call_data['page_brief']
    else:
        new_brief = 'New Page'

    return project, foldernumber, pagenumber, new_name, new_brief


def submit_new_template(skicall):
    "Create a new template page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # create page dictionary
    page_dict = _create_templatepagedict(project, new_name, pagenumber, new_brief)
    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
        pchange = editpage.pagechange(project, pagenumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data for edit page
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['page_number'] = pagenumber
    call_data['pchange'] = pchange
    call_data['status'] = 'Page %s added' % (new_name,)


def _create_templatepagedict(project, name, pagenumber, brief):
    "Returns a dictionary for a new template page"
    backcol = fromjson.get_defaults(project, key="backcol")
    if backcol:
        page_args = {"backcol":backcol}
    else:
        page_args = {}
    page_dict = {"name":name,
                 "ident":pagenumber,
                 "brief":brief,
                 "TemplatePage":page_args,
                 "head":["Part",_head_dict(project, pagenumber)],
                 "body":["Part",_body_dict(project)]
                }
    return page_dict


def _head_dict(project, pagenumber):
    "Returns a dictionary defining the new page head"
    # create the title tag
    title = ["Part", {
                      "tag_name":"title",
                      "brief":"The page title element",
                      "show":True,
                      "hide_if_empty":False,
                      "parts":[ ["Text", "Page " + str(pagenumber)] ]
                     } ]

    # The head dictionary
    head = {
            "tag_name":"head",
            "brief":"The head section of the page",
            "show":True,
            "hide_if_empty":False,
            "parts":[
                        ["ClosedPart", {
                                        "tag_name":"meta",
                                        "brief":"The charset meta declaration",
                                        "show":True,
                                        "attribs":{"charset":"utf-8"}
                                        } ],
                        ["ClosedPart", {
                                        "tag_name":"meta",
                                        "brief":"The viewport meta declaration",
                                        "show":True,
                                        "attribs":{
                                                    "content":"width=device-width, initial-scale=1",
                                                    "name":"viewport"
                                                  }
                                        } ],
                        title,
                    ]
           }

    # append CSS links to the parts list
    css_links = fromjson.get_defaults(project, key="css_links")
    if css_links:
        for label in css_links:
            csslink = ["ClosedPart", {
                                      "tag_name":"link",
                                      "brief":"css link to " + label,
                                      "show":True,
                                      "attribs":{
                                                  "href":"{" + label + "}",
                                                  "rel":"stylesheet",
                                                  "type":"text/css"
                                                 }
                                      } ]
            head["parts"].append(csslink)

    # append Javascript links to the parts list
    js_links = fromjson.get_defaults(project, key="js_links")
    if js_links:
        for label in js_links:
            jslink = ["Part", {
                               "tag_name":"script",
                               "brief":"script link to " + label,
                               "show":True,
                               "hide_if_empty":False,
                               "attribs":{
                                           "src":"{" + label +"}"
                                         },
                               "parts":[]
                              } ]
            head["parts"].append(jslink)

    return head


def _body_dict(project):
    "Returns a dictionary defining the new page body"
    # The body dictionary
    body = {
            "tag_name":"body",
            "brief":"The body section of the page",
            "show":True,
            "hide_if_empty":False,
            "parts":[]
        }
    # if a default body class has been set
    body_class = fromjson.get_defaults(project, key="body_class")
    if body_class:
        body["attribs"] = {"class":body_class}
    return body


def submit_new_svg(skicall):
    """ Creates a new svg page by making a dictionary similar to:

    {
     "name":"page_name",
     "ident":999,
     "brief":"brief description of the page",
     "SVG":{
         "enable_cache":False,
         "width":"100",
         "height":"100"
        }
    }

    And then calling editfolder.make_new_page(project, parent_number, page_dict)

"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    if 'width' in call_data:
        width = call_data['width']
    else:
        width = '100'
    if 'height' in call_data:
        height = call_data['height']
    else:
        height = '100'
    # create a new page dictionary
    page_dict = {"name":new_name,
                 "ident":pagenumber,
                 "brief":new_brief,
                 "SVG":{
                        "enable_cache":False,
                        "width":width,
                        "height":height
                        }
                }

    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
        pchange = editpage.pagechange(project, pagenumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data for edit page
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['page_number'] = pagenumber
    call_data['pchange'] = pchange
    call_data['status'] = 'SVG %s added' % (new_name,)


def retrieve_new_svg(skicall):
    "Retrieve data for creating a new SVG page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)

    parent_url = skilift.page_path(project, foldernumber)

    page_data[("adminhead","page_head","large_text")] = "Add SVG image page to : %s" % (parent_url,)

    # information paragraphs
    page_data[('page_name_text','para_text')] = "New page name : " + new_name
    page_data[('page_brief_text','para_text')] = "Description   : " + new_brief

    # information hidden fields
    page_data[('dimensions','hidden_field1')] = str(foldernumber)
    page_data[('dimensions','hidden_field2')] = new_name
    page_data[('dimensions','hidden_field3')] = new_brief
    page_data[('dimensions','hidden_field4')] = str(pagenumber)


def submit_new_css(skicall):
    """ Creates a new css page by making a dictionary similar to:

    {
     "name":"page_name",
     "ident":999,
     "brief":"brief description of the page",
     "CSS":{
         "enable_cache":False,
         "style":{}
        }
    }

    And then calling editfolder.make_new_page(project, parent_number, page_dict)

"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # create a new page dictionary
    page_dict = {"name":new_name,
                 "ident":pagenumber,
                 "brief":new_brief,
                 "CSS":{
                        "enable_cache":False
                       }
                }
    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
        pchange = editpage.pagechange(project, pagenumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data for edit page
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['page_number'] = pagenumber
    call_data['pchange'] = pchange
    call_data['status'] = 'CSS page %s added' % (new_name,)


def submit_new_json(skicall):
    """Create a new json page by making a dictionary similar to:

    {
     "name":"page_name",
     "ident":999,
     "brief":"brief description of the page",
     "JSON":{
            "enable_cache":False,
            "content":{}
        }
    }

    And then calling editfolder.make_new_page(project, parent_number, page_dict)
"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # create a new page dictionary
    page_dict = {"name":new_name,
                 "ident":pagenumber,
                 "brief":new_brief,
                 "JSON":{
                        "enable_cache":False
                       }
                }
    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    # Currently, after adding a json page, go back to edit folder
    call_data['status'] = 'JSON page %s added' % (new_name,)


def submit_new_file(skicall):
    """Create a new file page by making a dictionary similar to:

    {
     "name":"page_name",
     "ident":999,
     "brief":"brief description of the page",
     "FilePage":{
         "enable_cache":False,
         "filepath": "project/static/filename"
        }
    }

    And then calling editfolder.make_new_page(project, parent_number, page_dict)
"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # get the submitted filepath this page links to
    filepath = call_data['filepath']
    # create a new page dictionary
    page_dict = {"name":new_name,
                 "ident":pagenumber,
                 "brief":new_brief,
                 "FilePage":{
                        "enable_cache":False,
                        "filepath": filepath
                       }
                }
    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
        pchange = editpage.pagechange(project, pagenumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data for edit page
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['page_number'] = pagenumber
    call_data['pchange'] = pchange
    call_data['status'] = 'File link page %s added' % (new_name,)


def retrieve_new_file(skicall):
    "Gets data for a create filepage"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)

    parent_url = skilift.page_path(project, foldernumber)

    page_data[("adminhead","page_head","large_text")] = "Add File Link page to : %s" % (parent_url,)

    # information paragraphs
    page_data['page_name_text:para_text'] = "New page name : " + new_name
    page_data['page_brief_text:para_text'] = "Description   : " + new_brief

    # information hidden fields
    page_data['setfilepath','pagename'] = new_name
    page_data['setfilepath','pagebrief'] = new_brief
    page_data['setfilepath','pageident'] = str(pagenumber)

    # top descriptive text
    page_data['top_text:para_text'] = """The filepath set here should be relative to the projectfiles folder, so for a file
called myfile in the static directory, the path should be %s""" % (os.path.join(project, 'static', "myfile"),)

    # the submit filepath text input
    page_data['setfilepath:input_text'] = os.path.join(project, 'static', new_name)
    page_data['setfilepath:parent'] = str(foldernumber)


def submit_new_responder(skicall):
    """Create a new responder page by making a dictionary similar to:

    {
     "name":"page_name",
     "ident":999,
     "brief":"brief description of the page",
     "RespondPage":{
         "class":"ResponderClass",
         "original_args": {},
         "original_fields": {}
        }
    }

    And then calling editfolder.make_new_page(project, parent_number, page_dict)
"""

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # responder class name
    responder_class = call_data['responder_class']
    # create a new page dictionary
    page_dict = {"name":new_name,
                 "ident":pagenumber,
                 "brief":new_brief,
                 "RespondPage":{
                    "class":responder_class,
                    "original_args": {},
                    "original_fields": {}
                    }
                }
    # create the new page
    try:
        pagenumber = editfolder.make_new_page(project, foldernumber, page_dict)
        fchange = editfolder.folderchange(project, foldernumber)
        pchange = editpage.pagechange(project, pagenumber)
    except ServerError as e:
        raise FailPage(message=e.message)
    # clear and re-populate call_data for edit page
    utils.clear_call_data(call_data)
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['page_number'] = pagenumber
    call_data['pchange'] = pchange
    call_data['status'] = 'Responder %s - type %s added' % (new_name, responder_class)



def retrieve_new_responder(skicall):
    "Gets data for a create respondpage"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)

    parent_url = skilift.page_path(project, foldernumber)

    page_data[("adminhead","page_head","large_text")] = "Add a responder page to : %s" % (parent_url,)

    # information paragraphs
    page_data['page_name_text:para_text'] = "New page name : " + new_name
    page_data['page_brief_text:para_text'] = "Description   : " + new_brief

    # get a list of lists, each inner being [responder name, module name] from skilift.editresponder
    responderlist = editresponder.list_responders()

    # Create a list of 1) the responder class name, being the text to place on a button
    #                  2) the textblock reference describing the responder

    page_data['responderlinks','buttons'] =[]
    for responder in responderlist:
        rbutton = [responder[0],   "responders." + responder[1] + "." + responder[0]]
        page_data['responderlinks','buttons'].append(rbutton)

    # the hidden fields
    page_data['responderlinks:hidden_field1'] = str(foldernumber)
    page_data['responderlinks:hidden_field2'] = new_name
    page_data['responderlinks:hidden_field3'] = new_brief
    page_data['responderlinks:hidden_field4'] = str(pagenumber)


def submit_copy_page(skicall):
    "Copy a page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, new_page_number, new_name, new_brief = _common_page_items(skicall)
    # Get the page to be copied
    if 'copyident' not in call_data:
        raise FailPage(message = "The ident of the page to be copied has not been found", widget='copyident')
    pagenumber = call_data['copyident']
    try:
        fchange = editfolder.copy_page(project, pagenumber, foldernumber, new_page_number, new_name, new_brief)
    except ServerError as e:
        raise FailPage(e.message)
    edited_folder = call_data['edited_folder']
    utils.clear_call_data(call_data)
    call_data['fchange'] = fchange
    call_data['edited_folder'] = edited_folder
    call_data['folder_number'] = foldernumber
    call_data['status'] = 'Page %s added' % (new_name,)


def retrieve_new_copypage(skicall):
    "Gets data for a create a page copy"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    parent_url = skilift.page_path(project, foldernumber)

    page_data[("adminhead","page_head","large_text")] = "Add a page copy to : %s" % (parent_url,)

    # information paragraphs
    page_data['page_name_text:para_text'] = "New page name : " + new_name
    page_data['page_brief_text:para_text'] = "Description   : " + new_brief

    # information hidden fields
    page_data['copyident','pagename'] = new_name
    page_data['copyident','pagebrief'] = new_brief
    page_data['copyident','pageident'] = str(pagenumber)
    page_data['copyident','parent'] = str(foldernumber)

    page_data['upload','pagename'] = new_name
    page_data['upload','pagebrief'] = new_brief
    page_data['upload','pageident'] = str(pagenumber)
    page_data['upload','parent'] = str(foldernumber)

    # top descriptive text
    page_data['top_text:para_text'] = """To copy a page, either the ident number of an existing page to be copied is required, alternatively - a previously downloaded page definition file can be uploaded."""

    # the submit ident text input
    if 'copyident' in call_data:
        page_data['copyident','input_text'] = call_data['copyident']


def submit_upload_page(skicall):
    "Copy a page from uploaded file"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # first get submitted data for the new page
    project, foldernumber, pagenumber, new_name, new_brief = _common_page_items(skicall)
    # get uploaded file contents
    if "upload" not in call_data:
        raise FailPage("upload missing from call data")
    file_contents = call_data["upload"]
    json_string = file_contents.decode(encoding='utf-8')
    # create the page
    try:
        fromjson.create_page(project, foldernumber, pagenumber, new_name, new_brief, json_string)
        fchange = editfolder.folderchange(project, foldernumber)
    except ServerError as e:
        raise FailPage(message = e.message)
    edited_folder = call_data['edited_folder']
    utils.clear_call_data(call_data)
    call_data['edited_folder'] = edited_folder
    call_data['folder_number'] = foldernumber
    call_data['fchange'] = fchange
    call_data['status'] = 'Page %s added' % (new_name,)



