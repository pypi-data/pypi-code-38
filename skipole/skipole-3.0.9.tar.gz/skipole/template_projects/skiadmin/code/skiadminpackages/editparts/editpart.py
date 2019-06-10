
"Functions implementing part editing"

import json

from skipole import skilift
from skipole.skilift import fromjson, editpage, editsection
from skipole import FailPage, ValidateError, GoTo, ServerError


def retrieve_editpart(skicall):
    "Fills in the edit a part page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # a skilift.part_tuple is (project, pagenumber, page_part, section_name, name, location, part_type, brief)

    pagenumber = None
    section_name = None

    if 'part_tuple' in call_data:
        part_tuple = call_data['part_tuple']
        project = part_tuple.project
        location = part_tuple.location
        pagenumber = part_tuple.pagenumber
        section_name = part_tuple.section_name
    else:
        project = call_data['editedprojname']
        location = call_data['location']
        if 'page_number' in call_data:
            pagenumber = call_data['page_number']
        else:
            section_name = call_data['section_name']

    if (pagenumber is None) and (section_name is None):
        raise ValidateError("Page/section not identified")

    call_data['location'] = location

    part = None

    try:
        if pagenumber:
            call_data['page_number'] = pagenumber
            pchange = call_data['pchange']
            part = editpage.page_element(project, pagenumber, pchange, location)
        else:
            call_data['section_name'] = section_name
            schange = call_data['schange']
            part = editsection.section_element(project, section_name, schange, location)

        if part is None:
            raise FailPage("Part not identified")
    except ServerError as e:
        raise FailPage(e.message)

    # Fill in header
    page_data[("adminhead","page_head","large_text")] = "Edit the html element."

    # header done, now page contents

    if part.part_type == "Part":
        ending = ">"
    else:
        ending = " />"

    atts_list = []
    vals_list = []
    if part.attribs:
        for att in part.attribs:
            atts_list.append(att)
        # sort atts_list
        atts_list.sort()
        attstring = ""
        for att in atts_list:
            vals_list.append(part.attribs[att])
            attstring += " %s = \"%s\"" % (att, part.attribs[att])
        page_data[('tag_para','para_text')] = "Element tag : <%s%s%s" % (part.tag_name, attstring, ending)
    else:
        page_data[('tag_para','para_text')] = "Element tag : <%s%s" % (part.tag_name, ending)

    # list table of attributes, widget tables.Table2_1
    # contents = list of lists, each inner has five elements
    # col 0 is the text to place in the first column,
    # col 1 is the text to place in the second column,
    # col 2, 3, 4 are the three get field contents of the link
    if len(atts_list):
        page_data[('attribs_list_para','show')] = True
        page_data[('attribs_list','show')] = True
        contents = []
        for index, att in enumerate(atts_list):
            row = [ att, vals_list[index], att]
            contents.append(row)
        page_data['attribs_list', 'contents'] = contents
    else:
        page_data[('attribs_list_para','show')] = False
        page_data[('attribs_list','show')] = False

    # input form to change the tag name
    page_data[('tag_input','input_text')] = part.tag_name

    # input form to change the tag brief
    page_data[('tag_brief','input_text')] = part.brief

    if part.part_type == "Part":
        if part.hide_if_empty:
            page_data[('hidecheck','checked')] = True
        else:
            page_data[('hidecheck','checked')] = False
    else:
        page_data[('set_to_hide','show')] = False
        page_data[('para_to_hide','show')] = False
        page_data[('para_to_hide2','show')] = False
        page_data['partdownload', 'show'] = False
        page_data['aboutdownload', 'show'] = False


def set_tag(skicall):
    "Sets the part tag name, or brief, adds an attribute"

    call_data = skicall.call_data
    page_data = skicall.page_data

    pagenumber = None
    section_name = None

    project = call_data['editedprojname']
    location = call_data['location']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
        pchange = call_data['pchange']
    else:
        section_name = call_data['section_name']
        schange = call_data['schange']

    if (pagenumber is None) and (section_name is None):
        raise ValidateError("Page/section not identified")

    try:
        if pagenumber:
            part = editpage.page_element(project, pagenumber, pchange, location)
        else:
            part = editsection.section_element(project, section_name, schange, location)

        if part is None:
            raise FailPage("Part not identified")

        message = "A new value to edit has not been found"

        if 'tag_name' in call_data:
            tag_name = call_data["tag_name"]
            message = 'New tag set'
        else:
            tag_name = part.tag_name

        if 'tag_brief' in call_data:
            brief = call_data["tag_brief"]
            message = 'New description set'
        else:
            brief = part.brief

        attribs = part.attribs

        if 'attrib' in call_data:
            if 'val' not in call_data:
                raise FailPage("The attribute value has not been found")
            attribs.update({call_data["attrib"]:call_data["val"]})
            message = 'Attribute updated'

        if 'hide_if_empty' in call_data:
            hide = call_data['hide_if_empty']
            if hide == 'hide':
                hide_if_empty = True
                message = 'Element will be hidden if no content within it.'
            else:
                hide_if_empty = False
                message = 'Element will be shown even if no content within it.'
        else:
            hide_if_empty = part.hide_if_empty

        if pagenumber:
            call_data['pchange'] = editpage.edit_page_element(project, pagenumber, pchange, location, tag_name, brief, hide_if_empty, attribs)
        else:
            call_data['schange'] = editsection.edit_section_element(project, section_name, schange, location, tag_name, brief, hide_if_empty, attribs)

    except ServerError as e:
        raise FailPage(e.message)

    call_data['status'] = message


def remove_tag_attribute(skicall):
    "Removes the given tag attribute"

    call_data = skicall.call_data
    page_data = skicall.page_data

    pagenumber = None
    section_name = None

    project = call_data['editedprojname']
    location = call_data['location']
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
        pchange = call_data['pchange']
    else:
        section_name = call_data['section_name']
        schange = call_data['schange']

    if (pagenumber is None) and (section_name is None):
        raise ValidateError("Page/section not identified")

    try:
        if pagenumber:
            part = editpage.page_element(project, pagenumber, pchange, location)
        else:
            part = editsection.section_element(project, section_name, schange, location)

        if part is None:
            raise FailPage("Part not identified")

        if ('attribs_list','contents') not in call_data:
            raise FailPage("A Tag attribute to remove has not been found")

        if pagenumber:
            call_data['pchange'] = editpage.del_attrib(project, pagenumber, pchange, location, call_data['attribs_list','contents'])
        else:
            call_data['schange'] = editsection.del_attrib(project, section_name, schange, location, call_data['attribs_list','contents'])

    except ServerError as e:
        raise FailPage(e.message)


def downloadpart(skicall):
    "Gets part, and returns a json dictionary, this will be sent as an octet file to be downloaded"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        pagenumber = None

    if 'section_name' in call_data:
        section_name = call_data['section_name']
    else:
        section_name = None   

    part_info = skilift.part_info(project, pagenumber, section_name, call_data['location'])

    if not part_info:
        raise FailPage("Part not identified")

    parttext, part_dict = fromjson.item_outline(project, pagenumber, section_name, call_data['location'])
    # set version and skipole as the first two items in the dictionary
    versions = skilift.versions(project)
    part_dict["skipole"] = versions.skipole
    part_dict.move_to_end('skipole', last=False)
    part_dict["version"] = versions.project
    part_dict.move_to_end('version', last=False)
    jsonstring = json.dumps(part_dict, indent=4, separators=(',', ':'))
    line_list = []
    n = 0
    for line in jsonstring.splitlines(True):
        binline = line.encode('utf-8')
        n += len(binline)
        line_list.append(binline)
    page_data['headers'] = [('content-type', 'application/octet-stream'), ('content-length', str(n))]
    return line_list
