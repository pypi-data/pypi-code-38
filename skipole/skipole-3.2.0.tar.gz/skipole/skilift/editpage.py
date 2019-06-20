

"""Functions for editing a page"""

from collections import OrderedDict

from ..ski import skiboot, tag, read_json, dump_project
from ..ski.excepts import ServerError

from . import project_loaded, item_info, get_proj_page, del_location_in_page, insert_item_in_page

from .info_tuple import PageElement, PageTextBlock, WidgFieldInfo


def pagechange(project, pagenumber):
    """Returns the page change uuid

       Given a project name, and the integer ident number of a page within the project,
       it returns a 'change' uuid associated  with the page. A new random uuid is generated
       every time a page is changed, and is therefore a measure that a given page both exists,
       and has not changed since the last time it was accessed.
       The project must be currently loaded as either the root project or a sub-project.
       Returns None if no page with this pagenumber is found."""
    # raise error if invalid project
    project_loaded(project)
    info = item_info(project, pagenumber)
    if not info:
        return
    if info.item_type == "Folder":
        return
    return info.change


def rename_page(project, pagenumber, pchange, newname):
    """Rename the given page.

       Given a project name, the integer ident number of a page within the project,
       the page change uuid and a new page name, it changes the page name and returns
       a new uuid on success, or raises a ServerError on failure.
       The project must be currently loaded as either the root project or a sub-project."""
    if not newname:
        raise ServerError(message="No new page name given")
    # get a copy of the page, which can have a new name set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    # Rename the page
    page.name = newname
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_description(project, pagenumber, pchange, brief):
    "Set a page brief description"
    if not brief:
        return "No new page name given"
    # get a copy of the page, which can have a new brief set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    # Set the page brief
    page.brief = brief
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_string(project, pagenumber):
    "Returns a string of the page, may be usefull for diagnostics"
    proj, page = get_proj_page(project, pagenumber)
    return str(page)


def page_language(project, pagenumber, pchange, language):
    "Sets language in the page html tag"
    # get a copy of the page, which can have a new language set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    # Set the page language
    page.lang = language
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def get_page_backcol(project, pagenumber, pchange):
    """Returns tuple, first element True if the background colour is set in the html tag
                      second element being the background colour string"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    return page.show_backcol, page.backcol


def page_backcol(project, pagenumber, pchange, show_backcol, backcol):
    """Sets the backcolour and enables/disables it in the html tag"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    page.show_backcol = show_backcol
    page.backcol = backcol
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_last_scroll(project, pagenumber, pchange, last_scroll):
    "Sets last_scroll flag in the page"
    # get a copy of the page, which can be edited
    # and then saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    # Set the page last_scroll
    page.last_scroll = last_scroll
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def get_page_interval(project, pagenumber, pchange):
    """Returns tuple, first element is the refresh interval, or 0 if target does not exist
                      second element being the interval target, or None if not set"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    if page.interval != 0:
        if page.interval_target is None:
            return 0, None
        interval_target = page.interval_target
        # if interval target is an ident of this project, only return an integer
        if isinstance(interval_target, skiboot.Ident):
            if interval_target.proj == project:
                interval_target = str(interval_target.num)
            else:
                # ident is another project, put the full ident
                interval_target = interval_target.to_comma_str()
        return page.interval, interval_target
    else:
        return 0, None


def page_interval(project, pagenumber, pchange, interval, interval_target):
    """Sets the refresh interval and target"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    interval_target = skiboot.make_ident_or_label(interval_target, project)
    # set page attributes
    if (interval == 0) or (not interval_target):
        page.interval = 0
        page.interval_target = None
    else:
        page.interval = interval
        page.interval_target = interval_target
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_default_error_widget(project, pagenumber, pchange, default_error_widget):
    "Sets default_error_widget in the page"
    # get a copy of the page, which can be edited
    # and then saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "TemplatePage":
        raise ServerError(message = "Invalid page type")
    page.default_error_widget = default_error_widget
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_enable_cache(project, pagenumber, pchange, enable_cache):
    "Sets enable cache in the page"
    # get a copy of the page, which can be edited
    # and then saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != "SVG") and (page.page_type != "JSON") and (page.page_type != "FilePage") and (page.page_type != "CSS"):
        raise ServerError(message = "Invalid page type")
    page.enable_cache = enable_cache
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def new_parent(project, pagenumber, pchange, new_parent_number):
    "Gives a page a new parent folder"

    # get a copy of the page, which is to have a new parent folder set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if not isinstance(new_parent_number, int):
        raise ServerError(message="Given new_parent_number is not an integer")
    ident = skiboot.Ident.to_ident((project, new_parent_number))
    if ident is None:
        raise ServerError(message="Invalid project, new_parent_number")
    folder = skiboot.from_ident(ident, project)
    if folder is None:
        raise ServerError(message="Invalid Folder")
    if folder.page_type != 'Folder':
        raise ServerError(message="Item is not a page")
    old_parent = page.parentfolder
    if old_parent == folder:
        raise ServerError(message="Parent folder unchanged?")
    if page.name in folder:
        raise ServerError(message="The folder already contains an item with this name")
    return proj.save_page(page, folder.ident)


def delete_page(project, pagenumber):
    "delete this page, return None on success, error message on failure"
    try:
        proj, page = get_proj_page(project, pagenumber)
        # delete the page from the project
        proj.delete_item(page.ident)
    except ServerError as e:
        return e.message



def del_location(project, pagenumber, pchange, location):
    "Deletes the item at the given location in the page, returns new pchange"
    return del_location_in_page(project, pagenumber, pchange, location)


def move_location(project, pagenumber, pchange, from_location, to_location):
    """Move an item in the given page from one spot to another, defined by its location
       Returns new page change uuid"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if to_location == from_location:
        # no movement
        return pchange

    from_location_string, from_container, from_location_integers = from_location
    to_location_string, to_container, to_location_integers = to_location

    if (from_location_string != to_location_string) or (from_container != to_container):
        raise ServerError(message="Unable to move")

    location_string = from_location_string

    if from_container is None:
        # item to move is not in a widget
        if (location_string != 'head') and (location_string != 'body') and (location_string != 'svg'):
            raise ServerError(message="Unable to move item")
        # location integers are integers within the page, move it 
        up = False
        i = 0
        while True:
            if to_location_integers[i] < from_location_integers[i]:
                up = True
                break
            if to_location_integers[i] > from_location_integers[i]:
                # up is False
                break
            # so this digit is the same
            i += 1
            if len(from_location_integers) == i:
                # from location integers exhausted and equal to to_location! Trying to move an item under itself
                return pchange
            if len(to_location_integers) == i:
                up = True
                break
        if up:
            # move in the upwards direction
            #    delete it from original location
            #    insert it into new location
            try:
                # get top part such as head, body, svg
                top_part = page.location_item((location_string, None, ()))
                # get the part at from_location_integers
                part = top_part.get_location_value(from_location_integers)
                # delete part from top part location
                top_part.del_location_value(from_location_integers)
                # and insert it in the new location
                top_part.insert_location_value(to_location_integers, part)
            except Exception:
                raise ServerError(message="Unable to move item")
        else:
            # move in the downwards direction
            #    insert it into new location
            #    delete it from original location
            try:
                # get top part such as head, body, svg
                top_part = page.location_item((location_string, None, ()))
                # get the part at from_location_integers
                part = top_part.get_location_value(from_location_integers)
                # and insert it in the new location
                top_part.insert_location_value(to_location_integers, part)
                # delete part from current location
                top_part.del_location_value(from_location_integers)
            except Exception:
                raise ServerError(message="Unable to move item")
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

    widg_container_ints = list(widget.get_container_loc(from_container))

    from_location_ints = widg_ints + widg_container_ints + list(from_location_integers)
    to_location_ints = widg_ints + widg_container_ints + list(to_location_integers)

    # and move this item by calling this function again
    return move_location(project, pagenumber, pchange, (loc_top, None, from_location_ints), (loc_top, None, to_location_ints))


def css_style(project, pagenumber):
    "Return CSS style of a page, as an ordered Dictionary"
    proj, page = get_proj_page(project, pagenumber)
    if page.page_type != "CSS":
        raise ServerError(message = "Invalid page type")
    return page.style


def set_css_style(project, pagenumber, pchange, style):
    "Sets style in the CSS Page"
    # get a copy of the page, which can have a new style set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "CSS":
        raise ServerError(message = "Invalid page type")
    # Set the page style
    page.style = style
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def css_selector_properties(project, pagenumber, selector):
    "Return selctor properties of a CSS style of a page, as a string"
    proj, page = get_proj_page(project, pagenumber)
    if page.page_type != "CSS":
        raise ServerError(message = "Invalid page type")
    return page.selector_properties(selector)


def file_parameters(project, pagenumber):
    "Return filepath,mimetype of a page"
    proj, page = get_proj_page(project, pagenumber)
    if page.page_type != "FilePage":
        raise ServerError(message = "Invalid page type")
    return (page.filepath, page.mimetype)


def json_contents(project, pagenumber):
    "Return contents dictionary of a JSON page, where keys are WidgFieldInfo tuples"
    proj, page = get_proj_page(project, pagenumber)
    if page.page_type != "JSON":
        raise ServerError(message = "Invalid page type")
    contents = {}
    if page.content:
        for widgfield,value in page.content.items():
            wf = skiboot.make_widgfield(widgfield)
            if not wf:
                continue
            contents[WidgFieldInfo(wf.to_tuple_no_i(), str(wf), wf.to_str_tuple())] = value
    return contents


def remove_json_widgfield(project, pagenumber, pchange, str_widgfield):
    "Remove the given widgfield from the JSON page"
    # get a copy of the page, which can be edited
    # and then saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "JSON":
        raise ServerError(message = "Invalid page type")
    if str_widgfield in page.content:
        page.del_widgfield(str_widgfield)
    else:
        raise ServerError(message="Widgfield not recognised")
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def add_json_widgfield(project, pagenumber, pchange, str_widgfield, value):
    "Add the given widgfield and value to a JSON page"
    # get a copy of the page, which can be edited
    # and then saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "JSON":
        raise ServerError(message = "Invalid page type")
    page.add_widgfield(str_widgfield, value)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def create_html_comment_in_page(project, pagenumber, pchange, location, text="comment here"):
    "Creates a new html comment in the given page, returns the new pchange and comment location"
    com = tag.Comment(text)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, com)
    return new_pchange, new_location


def create_html_symbol_in_page(project, pagenumber, pchange, location, text="&nbsp;"):
    "Creates a new html symbol in the given page, returns the new pchange and symbol location"
    sym = tag.HTMLSymbol(text)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, sym)
    return new_pchange, new_location


def create_html_element_in_page(project, pagenumber, pchange, location, name, brief, opentag = True):
    "Creates a new html element in the given page, returns the new pchange"
    if opentag:
        newpart = tag.Part(tag_name=name, brief=brief)
    else:
        newpart = tag.ClosedPart(tag_name=name, brief=brief)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, newpart)
    return new_pchange


def create_part_in_page(project, pagenumber, pchange, location, json_data):
    """Builds the part from the given json string or ordered dictionary, and adds it to project either inserted into the html element
       currently at the given part location, or if not an element that can accept contents, inserted after the element.
       Returns new pchange value"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != "TemplatePage") and (page.page_type != "SVG"):
        raise ServerError(message = "Invalid page type")
    try:
        newpart = read_json.make_part_for_page(page, json_data)
    except Exception:
        raise ServerError("Unable to create part")
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, newpart)
    return new_pchange


def create_item_in_page(project, pagenumber, pchange, location, json_string):
    """Builds the item from the given json string, and adds it to project either inserted into the html element
       currently at the given location, or if not an element that can accept contents, inserted after the element.
       Returns new pchange value"""

    proj, page = get_proj_page(project, pagenumber, pchange)
    if (page.page_type != "TemplatePage") and (page.page_type != "SVG"):
        raise ServerError(message = "Invalid page type")
    try:
        newitem = read_json.make_item_for_page(page, json_string)
    except Exception:
        raise ServerError("Unable to create item")
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, newitem)
    return new_pchange


def page_element(project, pagenumber, pchange, location):
    """Return a PageElement tuple for the html element at the given location"""

    proj, page = get_proj_page(project, pagenumber, pchange)
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
        raise ServerError("The item at the location has not been found")

    if hasattr(part, '__class__'):
        part_type = part.__class__.__name__
    else:
        raise ServerError("The item at the location must be an html element")

    if (part_type != "Part") and (part_type != "ClosedPart"):
        raise ServerError("The item at the location must be an html element")

    tag_name = part.tag_name
    brief = part.brief
    hide_if_empty = part.hide_if_empty
    attribs = OrderedDict(sorted(part.attribs.items(), key=lambda t: t[0]))

    return PageElement(project, pagenumber, pchange, location, page_part, part_type, tag_name, brief, hide_if_empty, attribs)


def edit_page_element(project, pagenumber, pchange, location, tag_name, brief, hide_if_empty, attribs):
    """Given an element at project, pagenumber, location
       sets the element values, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    part = page.location_item(location)
    part.tag_name = tag_name
    part.brief = brief
    part.attribs = OrderedDict(sorted(attribs.items(), key=lambda t: t[0]))
    if part.__class__.__name__ == "Part":
        part.hide_if_empty = hide_if_empty
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def del_attrib(project, pagenumber, pchange, location, attribute):
    """Given an element at project, pagenumber, location
       deletes the given attribute, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    part = page.location_item(location)
    part.del_one_attrib(attribute)
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def get_text(project, pagenumber, pchange, location):
    """Return a text string from the page at the given location"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    text = page.location_item(location)
    if not isinstance(text, str):
        raise ServerError("Item at this location is not identified as a text string")
    return text


def get_symbol(project, pagenumber, pchange, location):
    """Return a symbol from the page at the given location"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    sym = page.location_item(location)
    if not isinstance(sym, tag.HTMLSymbol):
        raise ServerError("Item at this location is not identified as a HTML Symbol")
    return sym.text


def edit_page_symbol(project, pagenumber, pchange, location, text):
    """Given a symbol at project, pagenumber, location
       sets the symbol, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    sym = page.location_item(location)
    if not isinstance(sym, tag.HTMLSymbol):
        raise ServerError("Item at this location is not identified as a HTML Symbol")
    sym.text = text
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def get_comment(project, pagenumber, pchange, location):
    """Return a comment from the page at the given location"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    com = page.location_item(location)
    if not isinstance(com, tag.Comment):
        raise ServerError("Item at this location is not identified as a HTML comment")
    return com.text


def edit_page_comment(project, pagenumber, pchange, location, text):
    """Given a comment at project, pagenumber, location
       sets the comment, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    com = page.location_item(location)
    if not isinstance(com, tag.Comment):
        raise ServerError("Item at this location is not identified as a HTML comment")
    com.text = text
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_textblock(project, pagenumber, pchange, location):
    """Return a PageTextBlock tuple for the textblock at the given location"""
    proj, page = get_proj_page(project, pagenumber, pchange)
    tblock = page.location_item(location)
    if not isinstance(tblock, tag.TextBlock):
        raise ServerError("Item at this location is not identified as a TextBlock")
    return PageTextBlock(project, pagenumber, pchange, location, tblock.textref, tblock.project, tblock.failmessage, tblock.escape, tblock.linebreaks)


def create_textblock_in_page(project, pagenumber, pchange, location, textref, failmessage, escape, linebreaks, tblock_project=''):
    "Creates a new textblock in the given page, returns the new pchange and location"
    tblock = tag.TextBlock(textref=textref, project=tblock_project, failmessage=failmessage, escape=escape, linebreaks=linebreaks)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange
    new_pchange, new_location = insert_item_in_page(project, pagenumber, pchange, location, tblock)
    return new_pchange, new_location


def edit_page_textblock(project, pagenumber, pchange, location, textref, tblock_project, failmessage, escape, linebreaks):
    """Given an textblock at project, pagenumber, location
       sets the textblock values, returns page change uuid """
    proj, page = get_proj_page(project, pagenumber, pchange)
    tblock = page.location_item(location)
    if not isinstance(tblock, tag.TextBlock):
        raise ServerError("Item at this location is not identified as a TextBlock")
    tblock.textref = textref
    tblock.failmessage = failmessage
    tblock.escape = escape
    tblock.linebreaks = linebreaks
    if project == tblock_project:
        tblock.project = ''
    else:
        tblock.project = tblock_project
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_filepath(project, pagenumber, pchange, filepath):
    "Sets filepath in the FilePage"
    # get a copy of the page, which can have a new filepath set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "FilePage":
        raise ServerError(message = "Invalid page type")
    # Set the page filepath
    page.filepath = filepath
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)


def page_mimetype(project, pagenumber, pchange, mimetype):
    "Sets mimetype in the FilePage"
    # get a copy of the page, which can have a new mimetype set
    # and can then be saved to the project
    proj, page = get_proj_page(project, pagenumber, pchange)
    if page.page_type != "FilePage":
        raise ServerError(message = "Invalid page type")
    # Set the page mimetype
    page.mimetype = mimetype
    # save the altered page, and return the page.change uuid
    return proj.save_page(page)

