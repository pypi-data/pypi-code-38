


from collections import OrderedDict

from . import skiboot, excepts, tag



def templatepage_to_OD(proj_ident, page):
    """Returns an OrderedDictionary of the template page"""
    proj = skiboot.getproject(proj_ident)
    ident = page.ident
    page_dict = OrderedDict()
    page_dict["name"] = page.name
    page_dict["version"] = proj.version
    # stores the version of this skipole
    page_dict["skipole"] = skiboot.version()
    page_dict["ident"] = ident.num
    if page.brief:
        page_dict["brief"] = page.brief
    return _create_templatepage(page_dict, page, ident, proj_ident)


def svg_to_OD(proj_ident, page):
    """Returns an OrderedDictionary of the svg page"""
    proj = skiboot.getproject(proj_ident)
    ident = page.ident
    page_dict = OrderedDict()
    page_dict["name"] = page.name
    page_dict["version"] = proj.version
    # stores the version of this skipole
    page_dict["skipole"] = skiboot.version()
    page_dict["ident"] = ident.num
    if page.brief:
        page_dict["brief"] = page.brief
    return _create_svgpage(page_dict, page, ident, proj_ident)


def folder_to_OD(proj_ident, folder):
    """Returns an OrderedDictionary of the folder"""
    proj = skiboot.getproject(proj_ident)
    ident = folder.ident
    if ident.num:
        folder_dict = _create_folder(ident, proj_ident)
        folder_name = folder.name
    else:
        folder_dict = _create_root_folder(proj_ident)
        folder_dict["ident"] = 0
        folder_dict.move_to_end("ident", last=False)
        folder_name = proj_ident + "_root"
    # stores the version of this skipole
    folder_dict["skipole"] = skiboot.version()
    folder_dict.move_to_end("skipole", last=False)
    folder_dict["version"] = proj.version
    folder_dict.move_to_end("version", last=False)
    folder_dict["name"] = folder_name
    folder_dict.move_to_end("name", last=False)
    return folder_dict


def project_to_OD(proj_ident=None):
    """Returns an OrderedDictionary of the project"""
    if proj_ident is None:
        proj_ident = skiboot.project_ident()
    # proj is the actual Project instance to be dumped
    proj = skiboot.getproject(proj_ident)

    # create a big ordered dictionary
    project = OrderedDict()

    project["url"] = proj.url
    project["default_language"] = proj.default_language
    brief = proj.brief
    if not brief:
        project["brief"] = "Project : %s" % (proj_ident,)
    else:
        project["brief"] = brief
    project["version"] = proj.version

    # stores the version of this skipole
    project["skipole"] = skiboot.version()

    specialpages = {}
    specpages = proj.special_pages
    if specpages:
        for label, target in specpages.items():
            if isinstance(target, skiboot.Ident):
                if target.proj == proj_ident:
                    specialpages[label] = target.num
                else:
                    specialpages[label] = str(target)
            else:
                specialpages[label] = target
        project["specialpages"] = OrderedDict(sorted(specialpages.items(), key=lambda t: t[0]))
    else:
        project["specialpages"] = OrderedDict()

    sections = OrderedDict()
    projsections = proj.sections
    if projsections:
        for section_name, section in projsections.items():
            sections[section_name] = section.outline(proj_ident)
        project["sections"] = OrderedDict(sorted(sections.items(), key=lambda t: t[0]))
    else:
        project["sections"] = OrderedDict()

    # add rootfolder to the project
    project["RootFolder"] = _create_root_folder(proj_ident)

    return project


def _create_root_folder(proj_ident):
    "Creates a dictionary for the root folder"
    if proj_ident is None:
        proj_ident = skiboot.project_ident()
    proj = skiboot.getproject(proj_ident)
    # rootfolder is the OrderedDict to return
    rootfolder = OrderedDict()
    root = proj.root
    brief = root.brief
    if not brief:
        rootfolder["brief"] = "Root folder"
    else:
        rootfolder["brief"] = brief
    default_page_name = root.default_page_name
    if default_page_name:
        rootfolder["default_page_name"] = default_page_name
    rootfolder["restricted"] = False
    # folders in root
    root_folders = OrderedDict()
    folders = root.folders
    if folders:
        for foldername, ident in folders.items():
            root_folders[foldername] = _create_folder(ident, proj_ident)
        rootfolder["folders"] = OrderedDict(sorted(root_folders.items(), key=lambda t: t[0]))
    else:
        rootfolder["folders"] = OrderedDict()
    # pages in root
    root_pages = {}
    pages = root.pages
    if pages:
        for pagename, ident in pages.items():
            root_pages[pagename] = _create_page(ident, proj_ident)
        rootfolder["pages"] = OrderedDict(sorted(root_pages.items(), key=lambda t: t[0]))
    else:
        rootfolder["pages"] = OrderedDict()
    return rootfolder


def _create_folder(ident, proj_ident):
    "Creates a dictionary for the folder"
    proj = skiboot.getproject(proj_ident)
    folder_dict = OrderedDict()
    folder = proj.identitems[ident]

    folder_dict["ident"] = ident.num
    if folder.brief:
        folder_dict["brief"] = folder.brief
    if folder.default_page_name:
        folder_dict["default_page_name"] = folder.default_page_name
    folder_dict["restricted"] = folder.restricted

    # folders in this folder
    sub_folders = {}
    folders = folder.folders
    if folders:
        for foldername, folderident in folders.items():
            sub_folders[foldername] = _create_folder(folderident, proj_ident)
        folder_dict["folders"] = OrderedDict(sorted(sub_folders.items(), key=lambda t: t[0]))
    else:
        folder_dict["folders"] = OrderedDict()

    # pages in this folder
    pages_dict = {}
    pages = folder.pages
    if pages:
        for pagename, pageident in pages.items():
            pages_dict[pagename] = _create_page(pageident, proj_ident)
        folder_dict["pages"] = OrderedDict(sorted(pages_dict.items(), key=lambda t: t[0]))
    else:
        folder_dict["pages"] = OrderedDict()

    return folder_dict


def _create_page(ident, proj_ident):
    "Creates a dictionary for the page"
    proj = skiboot.getproject(proj_ident)
    page_dict = OrderedDict()
    page = proj.identitems[ident]
    page_dict["ident"] = ident.num
    if page.brief:
        page_dict["brief"] = page.brief
    if page.page_type == 'FilePage':
        return _create_filepage(page_dict, page, ident, proj_ident)
    elif page.page_type == 'RespondPage':
        return _create_respondpage(page_dict, page, ident, proj_ident)
    elif page.page_type == 'CSS':
        return _create_csspage(page_dict, page, ident, proj_ident)
    elif page.page_type == 'JSON':
        return _create_jsonpage(page_dict, page, ident, proj_ident)
    elif page.page_type == 'SVG':
        return _create_svgpage(page_dict, page, ident, proj_ident)
    elif page.page_type == 'TemplatePage':
        return _create_templatepage(page_dict, page, ident, proj_ident)
    else:
        return OrderedDict()


def _make_dictionary(input_dict, proj_ident):
    """Used by other functions, takes input_dict and returns
       an ordered dict, with TextBlocks, idents converted for json compatability"""
    output_dict = OrderedDict()
    if not input_dict: return output_dict
    for key, val in input_dict.items():
        if val is None:
            output_dict[key] = None
        elif val is '':
            output_dict[key] = ""
        elif isinstance(val, list):
            output_dict[key] = _make_list(val, proj_ident)
        elif isinstance(val, dict):
            output_dict[key] = _make_dictionary(val, proj_ident)
        elif val is True:
            output_dict[key] = True
        elif val is False:
            output_dict[key] = False
        elif isinstance(val, tag.TextBlock):
            output_dict[key] = val.textref
        elif isinstance(val, skiboot.Ident):
            if val.proj == proj_ident:
                # ident is this project, put the number only
                output_dict[key] = val.num
            else:
                # ident is another project, put the full ident
                output_dict[key] = [val.proj, val.num]
        else:
            output_dict[key] = str(val)
    return output_dict


def _make_list(input_list, proj_ident):
    """Used by other functions, takes input_list and returns a list with items converted"""
    if not input_list: return []
    output_list = []
    for item in input_list:
        if item is None:
            output_list.append(None)
        elif item is '':
            output_list.append('')
        elif isinstance(item, list):
            output_list.append(_make_list(item, proj_ident))
        elif isinstance(item, dict):
            output_list.append(_make_dictionary(item, proj_ident))
        elif item is True:
            output_list.append(True)
        elif item is False:
            output_list.append(False)
        elif isinstance(item, skiboot.Ident):
            if item.proj == proj_ident:
                output_list.append(item.num)
            else:
                # ident is another project, put the full ident
                output_list.append([item.proj, item.num])
        else:
            output_list.append(str(item))
    return output_list


def _create_filepage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the filepage"
    page_args = OrderedDict()
    page_args["filepath"] = page.filepath
    page_args["enable_cache"] = page.enable_cache
    if page.mimetype:
        page_args["mimetype"] = page.mimetype

    page_dict["FilePage"] = page_args
    return page_dict


def _create_respondpage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the respondpage"
    page_args = OrderedDict()
    page_args["class"] = page.responder.__class__.__name__
    original_args = OrderedDict(sorted(page.responder.original_args().items(), key=lambda t: t[0]))
    page_args["original_args"] = _make_dictionary(original_args, proj_ident)
    original_fields = OrderedDict(sorted(page.responder.original_fields().items(), key=lambda t: t[0]))
    page_args["original_fields"] = _make_dictionary(original_fields, proj_ident)
    page_dict["RespondPage"] = page_args
    return page_dict


def _create_csspage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the page"
    page_args = OrderedDict()
    page_args["enable_cache"] = page.enable_cache
    page_args["style"] = _make_dictionary(page.style, proj_ident)
    page_dict["CSS"] = page_args
    return page_dict


def _create_jsonpage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the page"
    page_args = OrderedDict()
    page_args["enable_cache"] = page.enable_cache
    page_args["content"] = OrderedDict()
    if page.content:
        page_args["content"] = _make_dictionary(page.content, proj_ident)
    page_dict["JSON"] = page_args
    return page_dict


def _create_svgpage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the page"
    page_args = OrderedDict()
    page_args["enable_cache"] = page.enable_cache
    page_args["width"] = str(page.width)
    page_args["height"] = str(page.height)
    if page.css_list:
        page_args["css_list"] = _make_list(page.css_list, proj_ident)
    page_dict["SVG"] = page_args
    page_dict["svg"] = page.svg.outline(proj_ident)

    return page_dict


def _create_templatepage(page_dict, page, ident, proj_ident):
    "Creates a dictionary for the page"
    page_args = OrderedDict()

    page_args["show_backcol"] = page.show_backcol
    page_args["last_scroll"] = page.last_scroll
    page_args["interval"] = page.interval

    # convert page.interval_target to ident, label or None
    interval_target = skiboot.make_ident_or_label(page.interval_target, proj_ident)
    if isinstance(interval_target, skiboot.Ident):
        if interval_target.proj == proj_ident:
            page_args["interval_target"] = interval_target.num
        else:
            # ident is another project, put the full ident
            page_args["interval_target"] = interval_target.to_comma_str()
    else:
        # interval_target is label or None
        page_args["interval_target"] = interval_target

    page_args["lang"] = page.lang
    if page.backcol:
        page_args["backcol"] = page.backcol

    if page.default_error_widget:
        page_args["default_error_widget"] = page.default_error_widget.sw_tuple()

    page_dict["TemplatePage"] = page_args
    page_dict["head"] = page.head.outline(proj_ident)
    page_dict["body"] = page.body.outline(proj_ident)

    return page_dict


