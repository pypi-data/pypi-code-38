

"Functions implementing css editing"


import collections

from skipole import ValidateError, FailPage, ServerError

from skipole. import skilift
from skipole.skilift import editpage

from .. import utils


def retrieve_edit_csspage(skicall):
    "Retrieves widget data for the edit css page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # clears any session data, keeping page_number, pchange and any status message
    utils.clear_call_data(call_data, keep=["page_number", "pchange", "status"])

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
        str_pagenumber = str(pagenumber)
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    try:
        pageinfo = skilift.page_info(project, pagenumber)
        if pageinfo.item_type != 'CSS':
            raise FailPage(message = "Invalid page")

        call_data['pchange'] = pageinfo.change

        selectors = list(editpage.css_style(project, pagenumber).keys())
    except ServerError as e:
        raise FailPage(message = e.message)

    # fills in the data for editing page name, brief, parent, etc., 
    page_data[("adminhead","page_head","large_text")] = pageinfo.name
    page_data[('page_edit','p_ident','page_ident')] = (project,str_pagenumber)
    page_data[('page_edit','p_name','page_ident')] = (project,str_pagenumber)
    page_data[('page_edit','p_description','page_ident')] = (project,str_pagenumber)
    page_data[('page_edit','p_rename','input_text')] = pageinfo.name
    page_data[('page_edit','p_parent','input_text')] = "%s,%s" % (project, pageinfo.parentfolder_number)
    page_data[('page_edit','p_brief','input_text')] = pageinfo.brief
    # create the contents for the selectortable
    contents = []

    if selectors:
        max_selector_index = len(selectors) - 1
        for index,selector in enumerate(selectors):
            if index:
                up = True
            else:
                # first item (index zero) has no up button
                up = False
            if index < max_selector_index:
                down = True
            else:
                # last item has no down button
                down = False 
            contents.append([selector, selector, selector, selector, selector, True, up, down, True])
        page_data["selectortable:contents"] = contents
    else:
        page_data["selectortable:show"] = False

    page_data['enable_cache:radio_checked'] = pageinfo.enable_cache


def retrieve_edit_selector(skicall):
    "Retrieves widget data for the edit selector page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
        str_pagenumber = str(pagenumber)
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    if 'edit_selector' not in call_data:
        raise FailPage(message="No selector given")

    try:
        pageinfo = skilift.page_info(project, pagenumber)
        if pageinfo.item_type != 'CSS':
            raise FailPage(message = "Invalid page")
        edit_selector = call_data['edit_selector']
        property_string = editpage.css_selector_properties(project, pagenumber, edit_selector)
    except ServerError as e:
        raise FailPage(message = e.message)

    call_data['extend_nav_buttons'] = [['back_to_css_page', 'CSS Page', True, '']]    # label to 8003

    if 'status' in call_data:
        status_text = call_data['status']
    else:
        status_text = 'Edit selector : %s' % (edit_selector,)

    page_data.update({("adminhead","page_head","large_text"):"Edit CSS page : %s" % (pageinfo.name,),
                      ("adminhead","page_head","small_text"):status_text,
                      ('selectorname','para_text'):"Selector : %s" % (edit_selector,),
                      ('p_ident','page_ident'):(project,str_pagenumber),
                      ('properties','hidden_field1'):edit_selector,
                      ('properties','input_text'):property_string })



def retrieve_print_csspage(skicall):
    "Retrieves widget data for the print css page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    try:
        pageinfo = skilift.item_info(project, pagenumber)
        if pageinfo.item_type != 'CSS':
            raise FailPage(message = "Invalid page")
        page_string = editpage.page_string(project, pagenumber)
    except ServerError as e:
        raise FailPage(message = e.message)
    page_data['page_details:para_text'] = "/**************************\n\nIdent:%s,%s\nPath:%s\n%s" % (project, pagenumber, pageinfo.path, pageinfo.brief)
    page_data['page_contents:para_text'] = page_string


def submit_new_selector(skicall):
    "Sets new selector"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    pchange = call_data['pchange']
    if not 'new_selector' in call_data:
        raise FailPage(message="No new selector given")
    new_selector = call_data['new_selector']
    if not new_selector:
        raise FailPage(message="No selector given")
    try:
        style = editpage.css_style(project, pagenumber)
        if new_selector in style:
            raise FailPage(message="Selector already exists")
        # Set the selector
        style[new_selector] = []
        call_data['pchange'] = editpage.set_css_style(project, pagenumber, pchange, style)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = 'Selector \"%s\" added.' % (new_selector,)


def submit_delete_selector(skicall):
    "Deletes selector"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    pchange = call_data['pchange']
    if 'remove_selector' not in call_data:
        raise FailPage(message="No selector to delete given")
    remove_selector = call_data['remove_selector']
    if not remove_selector:
        raise FailPage(message="No selector given")
    try:
        style = editpage.css_style(project, pagenumber)
        if remove_selector not in style:
            raise FailPage(message="Selector to remove is not present")
        # Remove the selector
        del style[remove_selector]
        call_data['pchange'] = editpage.set_css_style(project, pagenumber, pchange, style)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = 'Selector deleted'


def submit_selector_properties(skicall):
    "Sets the selector properties"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    pchange = call_data['pchange']
    if 'edit_selector' not in call_data:
        raise FailPage(message="No selector to edit given")
    edit_selector = call_data['edit_selector']
    if 'properties' not in call_data:
        raise FailPage(message="No properties to set given")
    property_string = call_data['properties']
    property_list = property_string.split(';')
    properties = []
    for item in property_list:
        if not item:
            continue
        if ':' not in item:
            continue
        pair = item.split(':')
        if len(pair) != 2:
            raise FailPage(message="Invalid properties")
        a = pair[0].strip()
        b = pair[1].strip()
        properties.append([a,b])
    if not properties:
        raise FailPage(message="Invalid properties")
    try:
        style = editpage.css_style(project, pagenumber)
        style[edit_selector] = properties
        call_data['pchange'] = editpage.set_css_style(project, pagenumber, pchange, style)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = 'Properties set'
        

def move_selector_up(skicall):
    "Moves selector upwards"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    pchange = call_data['pchange']
    if 'up_selector' not in call_data:
        raise FailPage(message="No selector to move up given")
    up_selector = call_data['up_selector']
    if not up_selector:
        raise FailPage(message="No selector given")
    try:
        style = editpage.css_style(project, pagenumber)
        if up_selector not in style:
            raise FailPage(message="Selector to move up is not present")
        selector_list = list(style.keys())
        # Move the selector up
        idx = selector_list.index(up_selector)
        if not idx:
            # idx cannot be zero
            raise FailPage(message="Selector already at top")
        selector_list[idx-1], selector_list[idx] = selector_list[idx], selector_list[idx-1]
        new_style = collections.OrderedDict([(selector,style[selector]) for selector in selector_list])
        call_data['pchange'] = editpage.set_css_style(project, pagenumber, pchange, new_style)
    except ServerError as e:
        raise FailPage(message=e.message)


def move_selector_down(skicall):
    "Moves selector downwardswards"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    if not pagenumber:
        raise FailPage(message = "Invalid page")
    pchange = call_data['pchange']
    if 'down_selector' not in call_data:
        raise FailPage(message="No selector to move down given")
    down_selector = call_data['down_selector']
    if not down_selector:
        raise FailPage(message="No selector given")
    try:
        style = editpage.css_style(project, pagenumber)
        if down_selector not in style:
            raise FailPage(message="Selector to move down is not present")
        # Move the selector down
        selector_list = list(style.keys())
        idx = selector_list.index(down_selector)
        if idx == len(selector_list) -1:
            # idx cannot be last element
            raise FailPage(message="Selector already at end")
        selector_list[idx+1], selector_list[idx] = selector_list[idx], selector_list[idx+1]
        new_style = collections.OrderedDict([(selector,style[selector]) for selector in selector_list])
        call_data['pchange'] = editpage.set_css_style(project, pagenumber, pchange, new_style)
    except ServerError as e:
        raise FailPage(message=e.message)


def submit_cache(skicall):
    "Sets cache true or false"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if 'cache' not in call_data:
        raise FailPage(message="No cache instruction given")
    try:
        # Set the page cache
        if call_data['cache'] == 'True':
            enable_cache = True
            message = "Cache Enabled"
        else:
            enable_cache = False
            message = "Cache Disabled"
        call_data['pchange'] = editpage.page_enable_cache(project, pagenumber, pchange, enable_cache)
    except ServerError as e:
        raise FailPage(message=e.message)
    call_data['status'] = message


