

import os, random, collections

from skipole import skilift
from skipole.skilift import off_piste, fromjson, editpage

from .. import utils, css_styles
from skipole import FailPage, ValidateError, ServerError, GoTo


def retrieve_index_data(skicall):
    "Retrieves all field data for admin index page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # clears any session data
    utils.clear_call_data(call_data)

    project = call_data['editedprojname']

    projectinfo = skilift.project_info(project)

    page_data["projversion", "input_text"] = projectinfo.version
    page_data["brief:input_text"] = projectinfo.brief
    page_data["brief:bottomtext"] = "Current value: " + projectinfo.brief
    page_data["deflang:input_text"] = projectinfo.default_language
    page_data["deflang:bottomtext"] = "Current value: " + projectinfo.default_language

    if "root_path" in call_data:
        # "root_path" is set in call_data, so return it
        page_data["rtpath:input_text"] = call_data["root_path"]
    else:
        # "root_path" not in call_data, so return the current root_path
        page_data["rtpath:input_text"] = projectinfo.path

    if skilift.get_debug():
        page_data["debugstatus", "para_text"] = "Debug mode is ON"
        page_data["debugtoggle", "button_text"] = "Set Debug OFF"
    else:
        page_data["debugstatus", "para_text"] = "Debug mode is OFF"
        page_data["debugtoggle", "button_text"] = "Set Debug ON"

    # create table of projects
    subprojects = projectinfo.subprojects
    col1 = []
    col2 = []
    col3 = []
    for proj, suburl in subprojects.items():
        projinfo = skilift.project_info(proj)
        col1.append(proj)
        col2.append(suburl)
        col3.append(projinfo.brief)
    # append the final row showing this edited project
    col1.append(project)
    col2.append(projectinfo.path)
    col3.append(projectinfo.brief)
    page_data['subs','col1'] = col1
    page_data['subs','col2'] = col2
    page_data['subs','col3'] = col3


    ctable = []
    for proj, suburl in subprojects.items():
        projinfo = skilift.project_info(proj)
        ctable.append([proj, suburl, projinfo.brief, proj, '', proj, '', True, True])
    # append the final row showing this edited project
    ctable.append([project, projectinfo.path, projectinfo.brief, '', '', '', '', False, False])
    page_data["projtable:contents"] = ctable

    # list directories under projects_dir()
    page_data['sdd1:option_list'] = []

    # sdd1 must be deleted
    page_data['sdd1:show_add_project'] = False
    page_data['sdd1:selectvalue'] = ''


def _clear_index_input_accepted(page_data):
    "Used by JSON to remove set_input_accepted flags from input fields"
    page_data['deflang','set_input_accepted'] = False
    page_data['projversion','set_input_accepted'] = False
    page_data['rtpath','set_input_accepted'] = False
    page_data['brief','set_input_accepted'] = False


def retrieve_help(skicall):
    "Uses skicall.textblock_text to get text help for the admin pages"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # clears any session data
    utils.clear_call_data(call_data)
    page_data.clear()
    caller_ident = call_data['caller_ident']
    if not caller_ident:
        return
    textref = 'page.' + str(caller_ident[1])
    text = skicall.textblock(textref)
    if not text:
        text = "No help text for page %s has been found" % caller_ident[1]
    page_data[("adminhead","show_help","para_text")] = "\n" + text
    page_data[("adminhead","show_help","hide")] = False


def get_text(skicall):
    """Finds any widget submitting 'get_field' with value of a textblock ref, returns
       page_data with key widget with field 'div_content' and value the textblock text"""

    page_data = skicall.page_data

    if 'received' not in skicall.submit_dict:
        return
    received_widgfields = skicall.submit_dict['received']
    for key, val in received_widgfields.items():
        if isinstance(key, tuple) and (key[-1] == 'get_field'):
            text = skicall.textblock(val)
            if text is None:
                continue
            text = text.replace('\n', '\n<br />')
            if len(key) == 3:
                page_data[(key[0], key[1],'div_content')] = text
                page_data[(key[0], key[1],'hide')] = False
            elif len(key) == 2:
                page_data[(key[0],'div_content')] = text
                page_data[(key[0],'hide')] = False


def retrieve_colour_data(skicall):
    "Retrieves all field data for admin colour page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # get default admin background color from project data
    adminbackcol = skicall.proj_data['adminbackcol']
    # get individual admin colors from project data
    colours = skicall.proj_data['colours']

    page_data["colhextest", "input_text"] = adminbackcol
    admincol = css_styles.hex_int(adminbackcol)
    page_data["red","input_text"] = str(admincol[0])
    page_data["green","input_text"] = str(admincol[1])
    page_data["blue","input_text"] = str(admincol[2])
    admin_h,admin_s,admin_l = css_styles.rgb_hsl(*admincol)
    page_data["hue","input_text"] = str(int(admin_h*360))
    page_data["saturation","input_text"] = str(int(admin_s*100))
    page_data["lightness","input_text"] = str(int(admin_l*100))



    l5_color = colours['w3_theme_l5_color']
    l5_background_color = colours['w3_theme_l5_background_color']
    l4_color = colours['w3_theme_l4_color']
    l4_background_color = colours['w3_theme_l4_background_color']
    l3_color = colours['w3_theme_l3_color']
    l3_background_color = colours['w3_theme_l3_background_color']
    l2_color = colours['w3_theme_l2_color']
    l2_background_color = colours['w3_theme_l2_background_color']
    l1_color = colours['w3_theme_l1_color']
    l1_background_color = colours['w3_theme_l1_background_color']
    d1_color = colours['w3_theme_d1_color']
    d1_background_color = colours['w3_theme_d1_background_color']
    d2_color = colours['w3_theme_d2_color']
    d2_background_color = colours['w3_theme_d2_background_color']
    d3_color = colours['w3_theme_d3_color']
    d3_background_color = colours['w3_theme_d3_background_color']
    d4_color = colours['w3_theme_d4_color']
    d4_background_color = colours['w3_theme_d4_background_color']
    d5_color = colours['w3_theme_d5_color']
    d5_background_color = colours['w3_theme_d5_background_color']
    light_color = colours['w3_theme_light_color']
    light_background_color = colours['w3_theme_light_background_color']
    dark_color = colours['w3_theme_dark_color']
    dark_background_color = colours['w3_theme_dark_background_color']
    action_color = colours['w3_theme_action_color']
    action_background_color = colours['w3_theme_action_background_color']
    theme_color = colours['w3_theme_color']
    theme_background_color = colours['w3_theme_background_color']
    text_color = colours['w3_text_theme_color']
    border_color = colours['w3_border_theme_color']
    hover_color = colours['w3_hover_theme_hover_color']
    hover_background_color = colours['w3_hover_theme_hover_background_color']
    hover_text_color = colours['w3_hover_text_theme_color']
    hover_border_color = colours['w3_hover_border_theme_hover_color']


    # l5_color
    page_data["l5_color","inputcol","label"] = "w3-theme-l5 color:"
    page_data["l5_color","inputcol","input_text"] = l5_color
    page_data["l5_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l5_color,l5_background_color)
    page_data["l5_color", "boxcol","set_html"] = l5_color

    # l5_background_color
    page_data["l5_background_color","inputcol","label"] = "w3-theme-l5 background color:"
    page_data["l5_background_color","inputcol","input_text"] = l5_background_color
    page_data["l5_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l5_background_color, l5_color)
    page_data["l5_background_color", "boxcol","set_html"] = l5_background_color

    # l4_color
    page_data["l4_color","inputcol","label"] = "w3-theme-l4 color:"
    page_data["l4_color","inputcol","input_text"] = l4_color
    page_data["l4_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l4_color,l4_background_color)
    page_data["l4_color", "boxcol","set_html"] = l4_color

    # l4_background_color
    page_data["l4_background_color","inputcol","label"] = "w3-theme-l4 background color:"
    page_data["l4_background_color","inputcol","input_text"] = l4_background_color
    page_data["l4_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l4_background_color,l4_color)
    page_data["l4_background_color", "boxcol","set_html"] = l4_background_color

    # l3_color
    page_data["l3_color","inputcol","label"] = "w3-theme-l3 color:"
    page_data["l3_color","inputcol","input_text"] = l3_color
    page_data["l3_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l3_color,l3_background_color)
    page_data["l3_color", "boxcol","set_html"] = l3_color

    # l3_background_color
    page_data["l3_background_color","inputcol","label"] = "w3-theme-l3 background color:"
    page_data["l3_background_color","inputcol","input_text"] = l3_background_color
    page_data["l3_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l3_background_color,l3_color)
    page_data["l3_background_color", "boxcol","set_html"] = l3_background_color

    # l2_color
    page_data["l2_color","inputcol","label"] = "w3-theme-l2 color:"
    page_data["l2_color","inputcol","input_text"] = l2_color
    page_data["l2_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l2_color,l2_background_color)
    page_data["l2_color", "boxcol","set_html"] = l2_color

    # l2_background_color
    page_data["l2_background_color","inputcol","label"] = "w3-theme-l2 background color:"
    page_data["l2_background_color","inputcol","input_text"] = l2_background_color
    page_data["l2_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l2_background_color,l2_color)
    page_data["l2_background_color", "boxcol","set_html"] = l2_background_color

    # l1_color
    page_data["l1_color","inputcol","label"] = "w3-theme-l1 color:"
    page_data["l1_color","inputcol","input_text"] = l1_color
    page_data["l1_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l1_color,l1_background_color)
    page_data["l1_color", "boxcol","set_html"] = l1_color

    # l1_background_color
    page_data["l1_background_color","inputcol","label"] = "w3-theme-l1 background color:"
    page_data["l1_background_color","inputcol","input_text"] = l1_background_color
    page_data["l1_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (l1_background_color,l1_color)
    page_data["l1_background_color", "boxcol","set_html"] = l1_background_color

    # d1_color
    page_data["d1_color","inputcol","label"] = "w3-theme-d1 color:"
    page_data["d1_color","inputcol","input_text"] = d1_color
    page_data["d1_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d1_color,d1_background_color)
    page_data["d1_color", "boxcol","set_html"] = d1_color

    # d1_background_color
    page_data["d1_background_color","inputcol","label"] = "w3-theme-d1 background color:"
    page_data["d1_background_color","inputcol","input_text"] = d1_background_color
    page_data["d1_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d1_background_color,d1_color)
    page_data["d1_background_color", "boxcol","set_html"] = d1_background_color

    # d2_color
    page_data["d2_color","inputcol","label"] = "w3-theme-d2 color:"
    page_data["d2_color","inputcol","input_text"] = d2_color
    page_data["d2_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d2_color,d2_background_color)
    page_data["d2_color", "boxcol","set_html"] = d2_color

    # d2_background_color
    page_data["d2_background_color","inputcol","label"] = "w3-theme-d2 background color:"
    page_data["d2_background_color","inputcol","input_text"] = d2_background_color
    page_data["d2_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d2_background_color,d2_color)
    page_data["d2_background_color", "boxcol","set_html"] = d2_background_color

    # d3_color
    page_data["d3_color","inputcol","label"] = "w3-theme-d3 color:"
    page_data["d3_color","inputcol","input_text"] = d3_color
    page_data["d3_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d3_color,d3_background_color)
    page_data["d3_color", "boxcol","set_html"] = d3_color

    # d3_background_color
    page_data["d3_background_color","inputcol","label"] = "w3-theme-d3 background color:"
    page_data["d3_background_color","inputcol","input_text"] = d3_background_color
    page_data["d3_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d3_background_color,d3_color)
    page_data["d3_background_color", "boxcol","set_html"] = d3_background_color

    # d4_color
    page_data["d4_color","inputcol","label"] = "w3-theme-d4 color:"
    page_data["d4_color","inputcol","input_text"] = d4_color
    page_data["d4_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d4_color,d4_background_color)
    page_data["d4_color", "boxcol","set_html"] = d4_color

    # d4_background_color
    page_data["d4_background_color","inputcol","label"] = "w3-theme-d4 background color:"
    page_data["d4_background_color","inputcol","input_text"] = d4_background_color
    page_data["d4_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d4_background_color,d4_color)
    page_data["d4_background_color", "boxcol","set_html"] = d4_background_color

    # d5_color
    page_data["d5_color","inputcol","label"] = "w3-theme-d5 color:"
    page_data["d5_color","inputcol","input_text"] = d5_color
    page_data["d5_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d5_color,d5_background_color)
    page_data["d5_color", "boxcol","set_html"] = d5_color

    # d5_background_color
    page_data["d5_background_color","inputcol","label"] = "w3-theme-d5 background color:"
    page_data["d5_background_color","inputcol","input_text"] = d5_background_color
    page_data["d5_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (d5_background_color,d5_color)
    page_data["d5_background_color", "boxcol","set_html"] = d5_background_color


    # light_color
    page_data["light_color","inputcol","label"] = "w3-theme-light color:"
    page_data["light_color","inputcol","input_text"] = light_color
    page_data["light_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (light_color,light_background_color)
    page_data["light_color", "boxcol","set_html"] = light_color

    # light_background_color
    page_data["light_background_color","inputcol","label"] = "w3-theme-light background color:"
    page_data["light_background_color","inputcol","input_text"] = light_background_color
    page_data["light_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (light_background_color,light_color)
    page_data["light_background_color", "boxcol","set_html"] = light_background_color

    # dark_color
    page_data["dark_color","inputcol","label"] = "w3-theme-dark color:"
    page_data["dark_color","inputcol","input_text"] = dark_color
    page_data["dark_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (dark_color,dark_background_color)
    page_data["dark_color", "boxcol","set_html"] = dark_color

    # dark_background_color
    page_data["dark_background_color","inputcol","label"] = "w3-theme-dark background color:"
    page_data["dark_background_color","inputcol","input_text"] = dark_background_color
    page_data["dark_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (dark_background_color,dark_color)
    page_data["dark_background_color", "boxcol","set_html"] = dark_background_color

    # action_color
    page_data["action_color","inputcol","label"] = "w3-theme-action color:"
    page_data["action_color","inputcol","input_text"] = action_color
    page_data["action_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (action_color,action_background_color)
    page_data["action_color", "boxcol","set_html"] = action_color

    # action_background_color
    page_data["action_background_color","inputcol","label"] = "w3-theme-action background color:"
    page_data["action_background_color","inputcol","input_text"] = action_background_color
    page_data["action_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (action_background_color,action_color)
    page_data["action_background_color", "boxcol","set_html"] = action_background_color

    # theme_color
    page_data["theme_color","inputcol","label"] = "w3-theme color:"
    page_data["theme_color","inputcol","input_text"] = theme_color
    page_data["theme_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (theme_color,theme_background_color)
    page_data["theme_color", "boxcol","set_html"] = theme_color

    # theme_background_color
    page_data["theme_background_color","inputcol","label"] = "w3-theme background color:"
    page_data["theme_background_color","inputcol","input_text"] = theme_background_color
    page_data["theme_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (theme_background_color,theme_color)
    page_data["theme_background_color", "boxcol","set_html"] = theme_background_color

    # text_color
    page_data["text_color","inputcol","label"] = "w3-text-theme color:"
    page_data["text_color","inputcol","input_text"] = text_color
    page_data["text_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (text_color,theme_background_color)
    page_data["text_color", "boxcol","set_html"] = text_color

    # border_color
    page_data["border_color","inputcol","label"] = "w3-border-theme color:"
    page_data["border_color","inputcol","input_text"] = border_color
    page_data["border_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (border_color,theme_background_color)
    page_data["border_color", "boxcol","set_html"] = border_color

    # hover_color
    page_data["hover_color","inputcol","label"] = "w3-hover-theme:hover color:"
    page_data["hover_color","inputcol","input_text"] = hover_color
    page_data["hover_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (hover_color,hover_background_color)
    page_data["hover_color", "boxcol","set_html"] = hover_color

    # hover_background_color
    page_data["hover_background_color","inputcol","label"] = "w3-hover-theme:hover background color:"
    page_data["hover_background_color","inputcol","input_text"] = hover_background_color
    page_data["hover_background_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (hover_background_color,hover_color)
    page_data["hover_background_color", "boxcol","set_html"] = hover_background_color

    # hover_text_color
    page_data["hover_text_color","inputcol","label"] = "w3-hover-text-theme:hover color:"
    page_data["hover_text_color","inputcol","input_text"] = hover_text_color
    page_data["hover_text_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (hover_text_color,hover_background_color)
    page_data["hover_text_color", "boxcol","set_html"] = hover_text_color

    # hover_border_color
    page_data["hover_border_color","inputcol","label"] = "w3-hover-border-theme:hover color:"
    page_data["hover_border_color","inputcol","input_text"] = hover_border_color
    page_data["hover_border_color", "boxcol", "style"] = "float: right; width: 20em; background-color: %s; color: %s; border: solid white 2px; padding: 5px;" % (hover_border_color,hover_background_color)
    page_data["hover_border_color", "boxcol","set_html"] = hover_border_color


def goto_edit_item(skicall):
    "Goes to the edit page, folder etc depending on the item submitted"

    call_data = skicall.call_data
    page_data = skicall.page_data

    edited_item = call_data["edited_item"]
    project = call_data['editedprojname']

    # clear call data
    utils.clear_call_data(call_data)

    itemnumber = skilift.get_itemnumber(project, edited_item)
    if itemnumber is None:
        raise FailPage(message="Item not found")

    item = skilift.item_info(project, itemnumber)
    if item is None:
        raise FailPage(message="Item not found")

    if item.item_type == "Folder":
        call_data['folder_number'] = itemnumber
        call_data['fchange'] = item.change
        raise GoTo(target=22008, clear_submitted=True)

    call_data['page_number'] = itemnumber
    call_data['pchange'] = item.change

    if item.item_type == "TemplatePage":
        raise GoTo(target=23207, clear_submitted=True)
    elif item.item_type == "RespondPage":
        raise GoTo(target=26007, clear_submitted=True)
    elif item.item_type == "FilePage":
        raise GoTo(target=29007, clear_submitted=True)
    elif item.item_type == "CSS":
        raise GoTo(target=28007, clear_submitted=True)
    elif item.item_type == "JSON":
        raise GoTo(target=20407, clear_submitted=True)
    elif item.item_type == "SVG":
        raise GoTo(target=23407, clear_submitted=True)

    del call_data['page_number']
    del call_data['pchange']
    raise FailPage(message="Item not found")
    

def submit_language(skicall):
    "Sets the default language of the edited project"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if "default_language" not in call_data:
        raise FailPage(message = 'Invalid call')
    try:
        skilift.set_proj_default_language(project, call_data["default_language"])
    except ServerError as e:
        raise FailPage(message = e.message)
    _clear_index_input_accepted(page_data)
    page_data['deflang','set_input_accepted'] = True
    call_data['status'] = 'Language set'


def submit_brief(skicall):
    "Sets the brief description of the edited project"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if ('brief','input_text') not in call_data:
        raise FailPage(message='Invalid call')
    try:
        skilift.set_proj_brief(project, call_data['brief','input_text'])
    except ServerError as e:
        raise FailPage(message = e.message)
    call_data['editedprojbrief'] = call_data['brief','input_text']
    page_data['brief','set_input_accepted'] = True
    call_data['status'] = 'Project brief set'


def set_version(skicall):
    "Sets the version of the edited project"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if ('projversion','input_text') not in call_data:
        raise FailPage(message='Invalid call')
    try:
        skilift.set_proj_version(project, call_data['projversion','input_text'])
    except ServerError as e:
        raise FailPage(message = e.message)
    _clear_index_input_accepted(page_data)
    call_data['editedprojversion'] = call_data['projversion','input_text']
    page_data['projversion','set_input_accepted'] = True
    page_data["adminhead","page_head","large_text"] = "Project: %s version: %s" % (project,call_data['projversion','input_text'])
    call_data['status'] = 'Project version set'


def debugtoggle(skicall):

    call_data = skicall.call_data
    page_data = skicall.page_data

    if skilift.get_debug():
        skilift.set_debug(False)
        page_data["debugtoggle", "button_text"] = "Set Debug ON"
        call_data['status'] = 'Debug mode set OFF'
    else:
        skilift.set_debug(True)
        page_data["debugtoggle", "button_text"] = "Set Debug OFF"
        call_data['status'] = 'Debug mode set ON'


def _submit_saveproject(skicall):
    "save the project textblock and project.json files"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    projinfo = skilift.project_info(project)
    # Create textblock json files
    accesstextblocks = skilift.get_accesstextblocks(project)
    accesstextblocks.save()
    # create project.json
    fromjson.project_to_json(project)


def json_submit_saveproject(skicall):
    "save the project textblock and project.json files"

    call_data = skicall.call_data
    page_data = skicall.page_data

    _submit_saveproject(skicall)
    page_data[("saveresult","para_text")] = "Project data saved to JSON files"
    page_data[("saveresult","show_para")] = True
    # clears any session data
    utils.clear_call_data(call_data)
    call_data['status'] = "Project data saved to JSON files"


def html_submit_saveproject(skicall):
    "save the project textblock and project.json files"
    call_data = skicall.call_data
    page_data = skicall.page_data

    _submit_saveproject(skicall)
    # clears any session data
    utils.clear_call_data(call_data)
    call_data['status'] = "Project data saved to JSON files"


def submit_hex_color(skicall):
    "set palette background color - from hex"

    call_data = skicall.call_data
    page_data = skicall.page_data

    adminproj = call_data['adminproj']
    palette = css_styles.hex_int(call_data['hexcol'].lower())
    adminbackcol = css_styles.int_hex(*palette)
    # generate colours
    colours = css_styles.get_colours(*palette)
    # set test colours in proj_data
    skilift.set_proj_data(adminproj, 'adminbackcol', adminbackcol)
    skilift.set_proj_data(adminproj, 'colours', colours)
    # set test colours in defaults.json
    fromjson.set_defaults(adminproj, key="backcol", value=adminbackcol)
    ordered_colours = collections.OrderedDict(sorted(colours.items(), key=lambda t: t[0]))
    fromjson.set_defaults(adminproj, key="colours", value=ordered_colours)
    # change name of 220 to avoid css cache
    pchange = editpage.pagechange(adminproj, 220)
    if pchange is None:
        raise ServerError(message="Admin page 220, label w3-theme-ski has not been found")
    newname = "w3-theme-ski-" + str(random.randint(10000, 99999)) + ".css"
    editpage.rename_page(adminproj, 220, pchange, newname)


def set_colour(skicall):
    "sets individual colour string"

    call_data = skicall.call_data
    page_data = skicall.page_data

    adminproj = call_data['adminproj']
    # get colors from project data
    colours = skilift.get_proj_data(adminproj, 'colours')
    if call_data["l5_color","inputcol","input_text"]:
        colours['w3_theme_l5_color'] = call_data["l5_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l5 color set'
    elif call_data["l5_background_color","inputcol","input_text"]:
        colours['w3_theme_l5_background_color'] = call_data["l5_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l5 background color set'
    elif call_data["l4_color","inputcol","input_text"]:
        colours['w3_theme_l4_color'] = call_data["l4_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l4 color set'
    elif call_data["l4_background_color","inputcol","input_text"]:
        colours['w3_theme_l4_background_color'] = call_data["l4_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l4 background color set'
    elif call_data["l3_color","inputcol","input_text"]:
        colours['w3_theme_l3_color'] = call_data["l3_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l3 color set'
    elif call_data["l3_background_color","inputcol","input_text"]:
        colours['w3_theme_l3_background_color'] = call_data["l3_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l3 background color set'
    elif call_data["l2_color","inputcol","input_text"]:
        colours['w3_theme_l2_color'] = call_data["l2_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l2 color set'
    elif call_data["l2_background_color","inputcol","input_text"]:
        colours['w3_theme_l2_background_color'] = call_data["l2_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l2 background color set'
    elif call_data["l1_color","inputcol","input_text"]:
        colours['w3_theme_l1_color'] = call_data["l1_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l1 color set'
    elif call_data["l1_background_color","inputcol","input_text"]:
        colours['w3_theme_l1_background_color'] = call_data["l1_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-l1 background color set'
    elif call_data["d5_color","inputcol","input_text"]:
        colours['w3_theme_d5_color'] = call_data["d5_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d5 color set'
    elif call_data["d5_background_color","inputcol","input_text"]:
        colours['w3_theme_d5_background_color'] = call_data["d5_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d5 background color set'
    elif call_data["d4_color","inputcol","input_text"]:
        colours['w3_theme_d4_color'] = call_data["d4_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d4 color set'
    elif call_data["d4_background_color","inputcol","input_text"]:
        colours['w3_theme_d4_background_color'] = call_data["d4_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d4 background color set'
    elif call_data["d3_color","inputcol","input_text"]:
        colours['w3_theme_d3_color'] = call_data["d3_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d3 color set'
    elif call_data["d3_background_color","inputcol","input_text"]:
        colours['w3_theme_d3_background_color'] = call_data["d3_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d3 background color set'
    elif call_data["d2_color","inputcol","input_text"]:
        colours['w3_theme_d2_color'] = call_data["d2_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d2 color set'
    elif call_data["d2_background_color","inputcol","input_text"]:
        colours['w3_theme_d2_background_color'] = call_data["d2_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d2 background color set'
    elif call_data["d1_color","inputcol","input_text"]:
        colours['w3_theme_d1_color'] = call_data["d1_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d1 color set'
    elif call_data["d1_background_color","inputcol","input_text"]:
        colours['w3_theme_d1_background_color'] = call_data["d1_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-d1 background color set'
    elif call_data["light_color","inputcol","input_text"]:
        colours['w3_theme_light_color'] = call_data["light_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-light color set'
    elif call_data["light_background_color","inputcol","input_text"]:
        colours['w3_theme_light_background_color'] = call_data["light_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-light background color set'
    elif call_data["dark_color","inputcol","input_text"]:
        colours['w3_theme_dark_color'] = call_data["dark_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-dark color set'
    elif call_data["dark_background_color","inputcol","input_text"]:
        colours['w3_theme_dark_background_color'] = call_data["dark_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-dark background color set'
    elif call_data["action_color","inputcol","input_text"]:
        colours['w3_theme_action_color'] = call_data["action_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-action color set'
    elif call_data["action_background_color","inputcol","input_text"]:
        colours['w3_theme_action_background_color'] = call_data["action_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme-action background color set'
    elif call_data["theme_color","inputcol","input_text"]:
        colours['w3_theme_color'] = call_data["theme_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme color set'
    elif call_data["theme_background_color","inputcol","input_text"]:
        colours['w3_theme_background_color'] = call_data["theme_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-theme background color set'
    elif call_data["text_color","inputcol","input_text"]:
        colours['w3_text_theme_color'] = call_data["text_color","inputcol","input_text"]
        call_data['status'] = 'w3-text-theme color set'
    elif call_data["border_color","inputcol","input_text"]:
        colours['w3_border_theme_color'] = call_data["boder_color","inputcol","input_text"]
        call_data['status'] = 'w3-border-theme color set'
    elif call_data["hover_color","inputcol","input_text"]:
        colours['w3_hover_theme_hover_color'] = call_data["hover_color","inputcol","input_text"]
        call_data['status'] = 'w3-hover-theme:hover color set'
    elif call_data["hover_background_color","inputcol","input_text"]:
        colours['w3_hover_theme_hover_background_color'] = call_data["hover_background_color","inputcol","input_text"]
        call_data['status'] = 'w3-hover-theme:hover background color set'
    elif call_data["hover_text_color","inputcol","input_text"]:
        colours['w3_hover_text_theme_color'] = call_data["hover_text_color","inputcol","input_text"]
        call_data['status'] = 'w3-hover-text-theme:hover color set'
    elif call_data["hover_border_color","inputcol","input_text"]:
        colours['w3_hover_border_theme_hover_color'] = call_data["hover_border_color","inputcol","input_text"]
        call_data['status'] = 'w3-hover-border-theme:hover color set'
    else:
        # no colour recognised
        return
    # etc for each colour
    # Then set colours into project data
    skilift.set_proj_data(adminproj, 'colours', colours)
    # set test colours in defaults.json
    fromjson.set_defaults(adminproj, key="colours", value=colours)
    # change name of 220 to avoid css cache
    pchange = editpage.pagechange(adminproj, 220)
    if pchange is None:
        raise ServerError(message="Admin page 220, label w3-theme-ski has not been found")
    newname = "w3-theme-ski-" + str(random.randint(10000, 99999)) + ".css"
    editpage.rename_page(adminproj, 220, pchange, newname)


def ski_theme(skicall):
    "set colours into the w3-theme-ski.css page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    adminproject = call_data['adminproj']
    colours = skilift.get_proj_data(adminproject, 'colours')
    if not colours:
        return {}
    return colours


def set_widgets_css(skicall):
    "sets default css classes into widgets"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data["editedprojname"]
    off_piste.set_widget_css_to_default(project)
    call_data['status'] = 'Widget CSS classes set'



