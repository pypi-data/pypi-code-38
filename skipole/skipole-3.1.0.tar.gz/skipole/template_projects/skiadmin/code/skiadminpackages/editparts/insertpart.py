

"Functions to insert an html tage"

from skipole import FailPage, ValidateError, GoTo, ServerError

from skipole.skilift import item_info, editpage, editsection


def retrieve_insert(skicall):
    "Fills in the insert an html element page header"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'page_number' in call_data:
        pageinfo = item_info(project, call_data['page_number'])
        if (pageinfo.item_type != "TemplatePage") and (pageinfo.item_type != "SVG"):
            raise FailPage("Invalid page")
        # Fill in header
        page_data[("adminhead","page_head","large_text")] = "Insert an HTML element into %s,%s" % (project, call_data['page_number'])
    elif 'section_name' in call_data:
        page_data[("adminhead","page_head","large_text")] = "Insert an HTML element into section " + call_data['section_name']
    else:
        raise FailPage("Insertion page/section for html element is missing")


def create_insert(skicall):
    "Creates the html element"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    try:
        part_top, container, location_integers = call_data['location']
        if call_data['newopenclosed'] == 'open':
            opentag = True
        else:
            opentag = False

        if 'page_number' in call_data:
            pagenumber = call_data['page_number']
            page_info = item_info(project, pagenumber)
            if page_info is None:
                raise FailPage("Page to edit not identified")

            if (page_info.item_type != "TemplatePage") and (page_info.item_type != "SVG"):
                raise FailPage("Page not identified")

            # page to go back to
            target = None
            if part_top == 'head':
                target = "page_head"
            elif part_top == 'body':
                target = "page_body"
            elif part_top == 'svg':
                target = "page_svg"

            if container is not None:
                target = "back_to_container"

            if target is None:
                raise FailPage("Invalid location")

            call_data['pchange'] = editpage.create_html_element_in_page(project,
                                                                        pagenumber,
                                                                        call_data['pchange'],
                                                                        call_data['location'],
                                                                        call_data['newpartname'],
                                                                        call_data['newbrief'],
                                                                        opentag)

        elif 'section_name' in call_data:
            section_name = call_data['section_name']

            if container is not None:
                target = "back_to_container"
            else:
                target = "back_to_section"

            call_data['schange'] = editsection.create_html_element_in_section(project,
                                                                              section_name,
                                                                              call_data['schange'],
                                                                              call_data['location'],
                                                                              call_data['newpartname'],
                                                                              call_data['newbrief'],
                                                                              opentag)

        else:
            raise FailPage("Either a page or section must be specified")

    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = 'New tag inserted'
    raise GoTo(target = target, clear_submitted=True)


def file_new_part(skicall):
    "Create new part from uploaded file"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = None
    section_name = None

    try:
        part_top, container, location_integers = call_data['location']

        if 'page_number' in call_data:
            pagenumber = call_data['page_number']
            page_info = item_info(project, pagenumber)
            if page_info is None:
                raise FailPage("Page to edit not identified")

            if (page_info.item_type != "TemplatePage") and (page_info.item_type != "SVG"):
                raise FailPage("Page not identified")

            # page to go back to
            target = None
            if part_top == 'head':
                target = "page_head"
            elif part_top == 'body':
                target = "page_body"
            elif part_top == 'svg':
                target = "page_svg"

            if container is not None:
                target = "back_to_container"

            if target is None:
                raise FailPage("Invalid location")

        elif 'section_name' in call_data:
            section_name = call_data['section_name']

            if container is not None:
                target = "back_to_container"
            else:
                target = "back_to_section"

        else:
            raise FailPage("Either a page or section must be specified")

        # get file contents
        file_contents = call_data["uploadpart", "action"]
        json_string = file_contents.decode(encoding='utf-8')
        # create the part
        if pagenumber:
            call_data['pchange'] = editpage.create_part_in_page(project, pagenumber, call_data['pchange'], call_data['location'], json_string)
        else:
            call_data['schange'] = editsection.create_part_in_section(project, section_name, call_data['schange'], call_data['location'], json_string)
    except ServerError as e:
        raise FailPage(message = e.message)

    call_data['status'] = 'New block created'
    raise GoTo(target = target, clear_submitted=True)


