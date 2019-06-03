


"""Functions for editing a section"""

import re

from collections import OrderedDict

from ..ski import skiboot, tag, read_json
from ..ski.excepts import ServerError

from . import project_loaded, get_proj_section, get_proj_page, insert_item_in_page, del_location_in_section, insert_item_in_section

from .info_tuple import PlaceHolderInfo, SectionElement, SectionTextBlock


# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')



def list_section_names(project=None):
    """Returns a list of section names in the project"""
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        return ()
    return proj.list_section_names()


def placeholder_info(project, pagenumber, location):
    """location is a tuple or list consisting of three items:
       a string (such as head or widget name)
       a container integer, such as 0 for widget container 0, or None if not in container
       a tuple or list of location integers
       returns None if placeholder not found, otherwise returns a namedtuple with items
       project, pagenumber, section_name, alias, brief, multiplier, mtag
    """
    proj, page = get_proj_page(project, pagenumber)
    part = page.location_item(location)
    if part is None:
        return

    if part.__class__.__name__ != "SectionPlaceHolder":
        return

    if hasattr(part, 'brief'):
        brief = part.brief
    else:
        brief = None

    if hasattr(part, 'section_name'):
        section_name = part.section_name
    else:
        section_name = None

    if hasattr(part, 'placename'):
        alias = part.placename
    else:
        alias = None

    if hasattr(part, 'multiplier'):
        multiplier = part.multiplier
    else:
        multiplier = None

    if hasattr(part, 'mtag'):
        mtag = part.mtag
    else:
        mtag = None

    return PlaceHolderInfo(project, pagenumber, section_name, alias, brief, multiplier, mtag)


def edit_placeholder(project, pagenumber, pchange, location, section_name, alias, brief, multiplier, mtag):
    """Given a placeholder at project, pagenumber, location
       sets the values section_name, alias, brief, multiplier, mtag, returns page change uuid """
    # raise error if invalid project
    if project is None:
        project = skiboot.project_ident()
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="The edited project is invalid")

    location_string, container_number, location_list = location

    part = None

    if pagenumber is None:
        raise ServerError(message="The page containing this section seems to be invalid")

    ident = skiboot.find_ident(pagenumber, project)
    if not ident:
        raise ServerError(message="The page containing this section seems to be invalid")
    page = skiboot.get_item(ident)
    if not page:
        raise ServerError(message="The page containing this section seems to be invalid")
    if (page.page_type != "TemplatePage") and (page.page_type != "SVG"):
        raise ServerError(message="The page type containing this section seems to be invalid")
    if page.change != pchange:
        raise ServerError(message="The page has been changed prior to this submission, someone else may be editing this project")
    part = page.location_item(location)
    if part is None:
        raise ServerError(message="Cannot find the section placeholder")

    if part.__class__.__name__ != "SectionPlaceHolder":
        raise ServerError(message="The edited location does not seem to be a section placeholder")

    # is placename unique
    if alias != part.placename:
        if alias in page.widgets:
            raise ServerError(message="Duplicate name in the page - a widget has this assigned")
        if alias in page.section_places:
            raise ServerError(message="This name clashes with a section alias already within this page")
    part.section_name = section_name
    part.placename = alias
    part.brief = brief
    part.multiplier = multiplier
    part.mtag = mtag

    # save the altered page, and return the page.change uuid
    return proj.save_page(page)



def new_placeholder(project, pagenumber, pchange, location, section_name, alias, brief):
    """Create a new placeholder at project, pagenumber, location
       with section_name, alias, brief returns page change uuid and new location"""
    # create new placeholder
    newplaceholder = tag.SectionPlaceHolder(section_name=section_name,
                                            placename=alias,
                                            brief=brief)
    # call skilift.insert_item_in_page to insert the item, save the page and return pchange and new location
    return insert_item_in_page(project, pagenumber, pchange, location, newplaceholder)


def sectionchange(project, section_name):
    """Returns the section change

       Given a project name, and an existing section name within the project,
       returns a 'change' uuid associated  with the section. A new random uuid
       is generated every time a section is edited, and is therefore a measure
       that a given section both exists, and has not changed since the last time
       it was accessed.
       The project must be currently loaded as either the root project or a sub-project.
       Returns None if no section with this name is found."""
    # raise error if invalid project
    project_loaded(project)
    if not isinstance(section_name, str):
         raise ServerError(message="Given section_name is invalid")
    proj = skiboot.getproject(project)
    section = proj.section(section_name, makecopy=False)
    if section is None:
        return
    return section.change


def del_location(project, section_name, schange, location):
    "Deletes the item at the given location in the section, returns new schange"
    return del_location_in_section(project, section_name, schange, location)


def move_location(project, section_name, schange, from_location, to_location):
    """Move an item in the given section from one spot to another, defined by its location
       Returns new section change uuid"""
    # raise error if invalid project
    proj, section = get_proj_section(project, section_name, schange)

    if to_location == from_location:
        # no movement
        return schange

    from_location_string, from_container, from_location_integers = from_location
    to_location_string, to_container, to_location_integers = to_location

    if (from_location_string != to_location_string) or (from_container != to_container):
        raise ServerError(message="Unable to move")

    if from_container is None:
        if from_location_string != section_name:
            raise ServerError(message="Unable to move item")
        # location integers are integers within the section, move it 
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
                return schange
            if len(to_location_integers) == i:
                up = True
                break
        if up:
            # move in the upwards direction
            #    delete it from original location
            #    insert it into new location
            try:
                # get the part at from_location_integers
                part = section.get_location_value(from_location_integers)
                # delete part from current location
                section.del_location_value(from_location_integers)
                # and insert it in the new location
                section.insert_location_value(to_location_integers, part)
            except Exception:
                raise ServerError(message="Unable to move item")
        else:
            # move in the downwards direction
            #    insert it into new location
            #    delete it from original location
            try:
                # get the part at from_location_integers
                part = section.get_location_value(from_location_integers)
                # and insert it in the new location
                section.insert_location_value(to_location_integers, part)
                # delete part from current location
                section.del_location_value(from_location_integers)
            except Exception:
                raise ServerError(message="Unable to move item")
        # And save this section copy to the project
        return proj.add_section(section_name, section)

    # part is within a widget, so get its location relative to the section
    widget = section.widgets[from_location_string]
    ident_string = widget.ident_string

    # ident_string is sectionname-x-y

    splitstring = ident_string.split("-")
    widg_ints = [ int(i) for i in splitstring[1:] ]

    widg_container_ints = list(widget.get_container_loc(from_container))

    from_location_ints = widg_ints + widg_container_ints + list(from_location_integers)
    to_location_ints = widg_ints + widg_container_ints + list(to_location_integers)

    # and move this item by calling this function again
    return move_location(project, section_name, schange, (section_name, None, from_location_ints), (section_name, None, to_location_ints))


def create_new_section(project, section_name, tag_name, brief):
    "Create a new section, return new section change on success, raises a ServerError on failure"
    # raise error if invalid project
    if not section_name:
        raise ServerError(message = "Section name missing")
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="The edited project is invalid")
    section_list = proj.list_section_names()
    if section_name in section_list:
        raise ServerError(message = "Section name already exists")
    section_lower_name = section_name.lower()
    if (section_lower_name == 'body') or (section_lower_name == 'head') or (section_lower_name == 'svg'):
        raise ServerError(message="Unable to create the section, the name given is reserved")
    if _AN.search(section_name):
        raise ServerError(message="Invalid section name, alphanumeric and underscore only")
    if section_name[0] == '_':
        raise ServerError(message="Invalid section name, must not start with an underscore")
    if section_name.isdigit():
        raise ServerError(message="Unable to create the section, the name must include some letters")
    # creates and adds the section
    return proj.add_section(section_name, tag.Section(tag_name=tag_name, brief=brief))


def delete_section(project, section_name):
    "delete this section, return None on success, raises a ServerError on failure"
    # raise error if invalid project
    project_loaded(project)
    proj = skiboot.getproject(project)
    if proj is None:
        raise ServerError(message="The edited project is invalid")
    section_list = proj.list_section_names()
    if section_name not in section_list:
        raise ServerError(message="Section name does not exists")
    proj.delete_section(section_name)


def create_html_comment_in_section(project, section_name, schange, location, text="comment here"):
    "Creates a new html comment in the given section, returns the new schange and comment location"
    com = tag.Comment(text)
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, com)
    return new_schange, new_location


def create_html_symbol_in_section(project, section_name, schange, location, text="&nbsp;"):
    "Creates a new html symbol in the given section, returns the new schange and symbol location"
    sym = tag.HTMLSymbol(text)
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, sym)
    return new_schange, new_location


def create_html_element_in_section(project, section_name, schange, location, name, brief, opentag = True):
    "Creates a new html element in the given section, returns the new schange"
    if opentag:
        newpart = tag.Part(tag_name=name, brief=brief)
    else:
        newpart = tag.ClosedPart(tag_name=name, brief=brief)
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, newpart)
    return new_schange


def create_part_in_section(project, section_name, schange, location, json_data):
    """Builds the part from the given json string or ordered dictionary, and adds it to project either inserted into the html element
       currently at the given part location, or if not an element that can accept contents, inserted after the element.
       Returns new schange value"""
    proj, section = get_proj_section(project, section_name, schange)
    try:
        newpart = read_json.make_part_for_section(section, json_data)
    except Exception:
        raise ServerError("Unable to create part")
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, newpart)
    return new_schange


def create_item_in_section(project, section_name, schange, location, json_string):
    """Builds the item from the given json string, and adds it to project either inserted into the html element
       currently at the given location, or if not an element that can accept contents, inserted after the element.
       Returns new schange value"""
    proj, section = get_proj_section(project, section_name, schange)
    try:
        newitem = read_json.make_item_for_section(section, json_string)
    except Exception:
        raise ServerError("Unable to create item")
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, newitem)
    return new_schange



def section_element(project, section_name, schange, location):
    """Return a SectionElement tuple for the html element at the given location"""

    proj, section = get_proj_section(project, section_name, schange)
    part = section.location_item(location)

    if part is None:
        raise ServerError("The item at the location has not been found")

    if hasattr(part, '__class__'):
        part_type = part.__class__.__name__
    else:
        raise ServerError("The item at the location must be an html element")

    if (part_type != "Part") and (part_type != "ClosedPart"):
        # part_type is normally a Part or ClosedPart, but may also be a Section
        if (part_type == "Section"):
            # however, in the special case where it is a section, there must be no location digits
            # a section cannot contain another section
            if location[2]:
                raise ServerError("The item at the location cannot be a Section!")
        else:
            # Not a section either
            raise ServerError("The item at the location must be an html element")

    tag_name = part.tag_name
    brief = part.brief
    show = part.show
    hide_if_empty = part.hide_if_empty
    attribs = OrderedDict(sorted(part.attribs.items(), key=lambda t: t[0]))

    return SectionElement(project, section_name, schange, location, part_type, tag_name, brief, show, hide_if_empty, attribs)


def edit_section_element(project, section_name, schange, location, tag_name, brief, hide_if_empty, attribs):
    """Given an element at project, section_name, location
       sets the element values, returns section change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    part = section.location_item(location)
    part.tag_name = tag_name
    part.brief = brief
    part.attribs = OrderedDict(sorted(attribs.items(), key=lambda t: t[0]))
    if part.__class__.__name__ == "Part":
        part.hide_if_empty = hide_if_empty
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def del_attrib(project, section_name, schange, location, attribute):
    """Given an element at project, section_name, location
       deletes the given attribute, returns sceetion change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    part = section.location_item(location)
    part.del_one_attrib(attribute)
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def get_text(project, section_name, schange, location):
    """Return a text string from the page at the given location"""
    proj, section = get_proj_section(project, section_name, schange)
    text = section.location_item(location)
    if not isinstance(text, str):
        raise ServerError("Item at this location is not identified as a text string")
    return text


def get_symbol(project, section_name, schange, location):
    """Return a symbol from the section at the given location"""
    proj, section = get_proj_section(project, section_name, schange)
    sym = section.location_item(location)
    if not isinstance(sym, tag.HTMLSymbol):
        raise ServerError("Item at this location is not identified as a HTML Symbol")
    return sym.text


def edit_section_symbol(project, section_name, schange, location, text):
    """Given a symbol at project, section_name, location
       sets the symbol, returns section change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    sym = section.location_item(location)
    if not isinstance(sym, tag.HTMLSymbol):
        raise ServerError("Item at this location is not identified as a HTML Symbol")
    sym.text = text
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)


def get_comment(project, section_name, schange, location):
    """Return a comment from the section at the given location"""
    proj, section = get_proj_section(project, section_name, schange)
    com = section.location_item(location)
    if not isinstance(com, tag.Comment):
        raise ServerError("Item at this location is not identified as a HTML comment")
    return com.text


def edit_section_comment(project, section_name, schange, location, text):
    """Given a comment at project, section_name, location
       sets the comment, returns section change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    com = section.location_item(location)
    if not isinstance(com, tag.Comment):
        raise ServerError("Item at this location is not identified as a HTML comment")
    com.text = text
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)
 

def section_textblock(project, section_name, schange, location):
    """Return a SectionTextBlock tuple for the textblock at the given location"""
    proj, section = get_proj_section(project, section_name, schange)
    tblock = section.location_item(location)
    if not isinstance(tblock, tag.TextBlock):
        raise ServerError("Item at this location is not identified as a TextBlock")
    return SectionTextBlock(project, section_name, schange, location, tblock.textref, tblock.project, tblock.failmessage, tblock.escape, tblock.linebreaks)


def create_textblock_in_section(project, section_name, schange, location, textref, failmessage, escape, linebreaks, tblock_project=''):
    "Creates a new textblock in the given section, returns the new schange and location"
    tblock = tag.TextBlock(textref=textref, project=tblock_project, failmessage=failmessage, escape=escape, linebreaks=linebreaks)
    # call skilift.insert_item_in_section to insert the item, save the section and return schange
    new_schange, new_location = insert_item_in_section(project, section_name, schange, location, tblock)
    return new_schange, new_location


def edit_section_textblock(project, section_name, schange, location, textref, tblock_project, failmessage, escape, linebreaks):
    """Given an textblock at project, section_name, location
       sets the textblock values, returns section change uuid """
    proj, section = get_proj_section(project, section_name, schange)
    tblock = section.location_item(location)
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
    # save the altered section, and return the section.change uuid
    return proj.add_section(section_name, section)

