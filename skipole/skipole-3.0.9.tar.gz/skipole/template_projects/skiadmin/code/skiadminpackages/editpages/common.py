

from skipole import ValidateError, FailPage, ServerError, GoTo

from skipole.skilift import get_itemnumber
from skipole.skilift.editpage import rename_page, page_description, new_parent



def submit_rename_page(skicall):
    "rename this page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    if 'page_number' not in call_data:
        raise FailPage(message = "Page missing")
    if 'new_name' not in call_data:
        raise FailPage(message="No new page name has been given")
    # Rename the page
    # call skilift.editpage.rename_page which returns a new pchange
    try:
        call_data['pchange'] = rename_page(call_data['editedprojname'], call_data['page_number'], call_data['pchange'], call_data['new_name'])
    except ServerError as e:
        raise FailPage(e.message)
    page_data['page_edit','p_rename','set_input_accepted'] = True
    call_data['status'] = 'Page renamed'



def submit_new_parent(skicall):
    "Gives a page a new parent"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'parent_ident' in call_data:
        raise FailPage(message="No parent ident given")
    parent_ident = call_data['parent_ident']
    new_parent_number = get_itemnumber(project, parent_ident)
    if new_parent_number is None:
        raise FailPage(message="No valid parent ident given")
    try:
        call_data['pchange'] = new_parent(project, pagenumber, pchange, new_parent_number)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = 'Page moved'


def submit_page_brief(skicall):
    "Sets new page brief"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'page_brief' in call_data:
        raise FailPage(message="No page brief given", widget="p_brief")
    new_brief = call_data['page_brief']
    if not new_brief:
        raise FailPage(message="No page brief given", widget="p_brief")
    # call skilift.editpage.page_description which returns a new pchange
    try:
        call_data['pchange'] = page_description(project, pagenumber, pchange, new_brief)
    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = 'Page brief set: %s' % (new_brief,)


def goto_edit(skicall):

    call_data = skicall.call_data
    page_data = skicall.page_data


    caller_num = skicall.caller_ident[1]
    if caller_num == 28009:
        raise GoTo(28007)         # css edit page
    elif caller_num == 20409:
        raise GoTo(20407)         # json edit page
    elif caller_num == 23209:
        raise GoTo(23207)          # retrieve template edit page contents
    elif caller_num == 23409:
        raise GoTo(23407)          # svg edit page
    elif caller_num == 26009:
        raise GoTo(26007)          # retrieve responder edit page contents
    elif caller_num == 29009:
        raise GoTo(29007)          # filepage edit page
    else:
        raise GoTo('admin_home', clear_page_data=True)
