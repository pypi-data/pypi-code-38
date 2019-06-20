

"Functions to edit and insert a section placeholder"

import re

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w_]')

from skipole import FailPage, ValidateError, GoTo, ServerError
from skipole.skilift import part_info, editsection, item_info


def retrieve_editplaceholder(skicall):
    "Fills in the edit placeholder page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # a skilift.part_tuple is (project, pagenumber, page_part, section_name, name, location, part_type, brief)

    if 'part_tuple' in call_data:
        part_tuple = call_data['part_tuple']
        project = part_tuple.project
        pagenumber = part_tuple.pagenumber
        location = part_tuple.location
    else:
        project = call_data['editedprojname']
        pagenumber = call_data['page_number']
        location = call_data['location']
 
    # Fill in header
    page_data[("adminhead","page_head","large_text")] = "Edit Section place holder"

    # header done, now page contents

    # get placholderinfo
    placeholder = editsection.placeholder_info(project, pagenumber, location)
    if placeholder is None:
        raise FailPage("Section Place Holder not found")

    # get current sections
    section_list = editsection.list_section_names(project)

    if not section_list:
        page_data[('editsection','option_list')] = ['-None-']
        page_data[('editsection','selectvalue')] = '-None-'
        page_data[("nosection", "show")] = True
    elif placeholder.section_name in section_list:
        page_data[('editsection','option_list')] = section_list[:]
        page_data[('editsection','selectvalue')] = placeholder.section_name
    else:
        page_data[('editsection','option_list')] = ['-None-'] + section_list
        page_data[('editsection','selectvalue')] = '-None-'
        page_data[("nosection", "show")] = True

    page_data[("brief", "input_text")] = placeholder.brief
    page_data[("placename", "input_text")] = placeholder.alias
    page_data[("multiplier", "input_text")] = str(placeholder.multiplier)
    page_data[("mtag", "input_text")] = placeholder.mtag

    # set session data
    call_data['location'] = location


def set_placeholder(skicall):
    "Sets the placeholder section name, brief, or placename"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    location = call_data['location']
    pchange = call_data['pchange']

    call_data['part_tuple'] = part_info(project, pagenumber, None, location)

    # get current sections
    section_list = editsection.list_section_names(project)

    # get placholderinfo
    placeholder = editsection.placeholder_info(project, pagenumber, location)

    section_name = placeholder.section_name
    alias = placeholder.alias
    brief = placeholder.brief
    multiplier = placeholder.multiplier
    mtag = placeholder.mtag

    if 'new_section_name' in call_data:
        if call_data['new_section_name'] == '-None-':
            raise FailPage(message='Section name not set')
        if not section_list:
            raise FailPage(message='No sections found')
        if call_data['new_section_name'] not in section_list:
            raise FailPage(message='Section not found')
        section_name = call_data['new_section_name']
        message = 'New section name set'
    elif 'placeholder_brief' in call_data:
        brief = call_data["placeholder_brief"]
        message = 'New description set'
    elif 'multiplier' in call_data:
        try:
            multiplier = int(call_data["multiplier"])
        except Exception:
            raise FailPage(message='Invalid multiplier, should be an integer of 0 or above')
        if multiplier < 0:
           raise FailPage(message='Invalid multiplier, should be an integer of 0 or above')
        message = 'New multiplier set'
    elif 'placename' in call_data:
        placename = call_data['placename']
        if placename == alias:
            call_data['status'] = 'Alias not changed'
            return
        if not placename:
            raise FailPage("Invalid alias")
        lower_placename = placename.lower()
        if (lower_placename == 'body') or (lower_placename == 'head') or (lower_placename == 'svg')  or (lower_placename == 'show_error'):
            raise FailPage(message="Unable to set alias, the given value is reserved")
        if _AN.search(placename):
            raise FailPage(message="Invalid alias, alphanumeric and underscore only")
        if placename[0] == '_':
            raise FailPage(message="Invalid alias, must not start with an underscore")
        if placename.isdigit():
            raise FailPage(message="Unable to set alias, the value must include some letters")
        alias = placename
        message = 'New alias set'
    elif 'mtag' in call_data:
        mtag = call_data["mtag"]
        message = 'New multiplier container tag set'
    else:
        raise FailPage("A new placeholder value to edit has not been found")

    # call editsection.edit_placeholder from skilift, which returns a new pchange
    try:
        call_data['pchange'] = editsection.edit_placeholder(project, pagenumber, pchange, location, section_name, alias, brief, multiplier, mtag)
    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = message


def retrieve_insert(skicall):
    "Fills in the insert a placeholder page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    if 'page_number' not in call_data:
        raise FailPage("Page to edit not identified")

    pagenumber = call_data['page_number']
    page_info = item_info(project, pagenumber)
    if page_info is None:
        raise FailPage("Page to edit not identified")

    if (page_info.item_type != "TemplatePage") and (page_info.item_type != "SVG"):
        raise FailPage("Page not identified")

    # Fill in header
    page_data[("adminhead","page_head","large_text")] = "Insert Section place holder"

    # get current sections
    section_list = editsection.list_section_names(project)
    if not section_list:
        page_data[("nosection", "show")] = True
        page_data[("descript", "show")] = False
        page_data[("placename","show")] = False
        return

    page_data[('sectionname','option_list')] = section_list[:]
    page_data[('sectionname','selectvalue')] = section_list[0]


def create_insert(skicall):
    "Creates the section placeholder"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    if 'page_number' not in call_data:
        raise FailPage("Page to edit not identified")
    pagenumber = call_data['page_number']
    page_info = item_info(project, pagenumber)
    if page_info is None:
        raise FailPage("Page to edit not identified")

    if (page_info.item_type != "TemplatePage") and (page_info.item_type != "SVG"):
        raise FailPage("Page not identified")

    # create the item

    if 'newsectionname' not in call_data:
        raise FailPage(message = "Missing section name")
    section_name=call_data['newsectionname']

    # get current sections
    section_list = editsection.list_section_names(project)
    if section_name not in section_list:
        raise FailPage(message = "Unknown section name")

    if 'newplacename' not in call_data:
        raise FailPage(message = "Missing section alias")

    alias=call_data['newplacename']

    if _AN.search(alias):
        raise FailPage(message="Invalid alias")

    try:
        call_data['pchange'], call_data['location'] = editsection.new_placeholder(project, pagenumber, call_data['pchange'], call_data['location'], section_name, alias, call_data['newbrief'])
    except ServerError as e:
        raise FailPage(e.message)

    call_data['status'] = "Section placeholder inserted"


