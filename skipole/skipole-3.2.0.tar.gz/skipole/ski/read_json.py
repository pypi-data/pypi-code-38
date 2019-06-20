


import os, json, importlib, inspect, collections, uuid


from . import skiboot, excepts, folder_class_definition, page_class_definition, tag



def make_part_for_page(page, json_data):
    "Returns object created from json data, the page argument is used to give any items unique names. The object is not inserted, and page remains unchanged"
    if isinstance(json_data, str):
        part_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        part_dict = json_data
    newpart =  _create_part(part_dict, page.proj_ident)
    # ensure widgets and placeholders in newpart have unique names
    name_list = list(page.widgets.keys()) + list(page.section_places.keys())
    newpart.set_unique_names(name_list)
    return newpart


def make_item_for_page(page, json_string):
    "Returns object created from json string, the page argument is used to give any items unique names. The object is not inserted, and page remains unchanged"
    item_list = json.loads(json_string, object_pairs_hook=collections.OrderedDict)
    newitem = _create_item(item_list, page.proj_ident)
    # ensure widgets and placeholders in newitem have unique names
    if hasattr(newitem, 'set_unique_names'):
        name_list = list(page.widgets.keys()) + list(page.section_places.keys())
        newitem.set_unique_names(name_list)
    return newitem


def make_part_for_section(section, json_data):
    "Returns object created from json data, the section argument is used to give any items unique names. The object is not inserted, and section remains unchanged"
    if isinstance(json_data, str):
        part_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        part_dict = json_data
    newpart =  _create_part(part_dict, section.proj_ident)
    # ensure widgets and placeholders in newpart have unique names
    name_list = list(section.widgets.keys()) + list(section.section_places.keys())
    newpart.set_unique_names(name_list)
    # as this is going into a section, remove any placeholders
    _remove_sectionplaceholders(newpart)
    return newpart


def make_item_for_section(section, json_string):
    "Returns object created from json string, the section argument is used to give any items unique names. The object is not inserted, and section remains unchanged"
    item_list = json.loads(json_string, object_pairs_hook=collections.OrderedDict)
    newitem = _create_item(item_list, section.proj_ident)
    # ensure widgets and placeholders in newitem have unique names
    if hasattr(newitem, 'set_unique_names'):
        name_list = list(section.widgets.keys()) + list(section.section_places.keys())
        newitem.set_unique_names(name_list)
    # as this is going into a section, remove any placeholders
    _remove_sectionplaceholders(newitem)
    return newitem


def _remove_sectionplaceholders(part):
    "Given a part - swap out any tag.SectionPlaceHolder for a text string"
    if isinstance(part, tag.Part) or isinstance(part, tag.Section):
        parts = part.parts
        index_list = []
        for index, item in enumerate(parts):
            if isinstance(item, tag.SectionPlaceHolder):
                index_list.append(index)
            if hasattr(item, 'parts'):
                _remove_sectionplaceholders(item)
        for index in index_list:
            parts[index] = "Section Place Holder Removed"


def create_section(proj_ident, section_name, json_data):
    """Builds the section from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        section_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        section_dict = json_data
    section = _create_section(section_dict, proj_ident)
    # as this is going into a section, remove any placeholders
    _remove_sectionplaceholders(section)
    project = skiboot.getproject(proj_ident)
    project.add_section(section_name, section)


def create_templatepage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the template page from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "TemplatePage" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["TemplatePage"]
    page = _create_templatepage(page_name, brief, page_args)
    head = page_dict["head"]
    body = page_dict["body"]
    page.head = _create_item(head, proj_ident)
    page.body = _create_item(body, proj_ident)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_svgpage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the svg page from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "SVG" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["SVG"]
    page = _create_svgpage(page_name, brief, page_args)
    if "svg" in page_dict:
        svg = page_dict["svg"]
        page.svg = _create_item(svg, proj_ident)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_filepage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the file page from the given json string, or dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "FilePage" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["FilePage"]
    page = _create_filepage(page_name, brief, page_args)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_csspage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the css page from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "CSS" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["CSS"]
    page = _create_csspage(page_name, brief, page_args)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_jsonpage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the json page from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "JSON" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["JSON"]
    page = _create_jsonpage(page_name, brief, page_args)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_respondpage(proj_ident, parent_ident, page_ident, page_name, brief, json_data):
    """Builds the respond page from the given json string, or ordered dictionary and adds it to project"""
    if isinstance(json_data, str):
        page_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        page_dict = json_data
    if "RespondPage" not in page_dict:
        raise excepts.ServerError("Invalid file")
    page_args = page_dict["RespondPage"]
    page = _create_respondpage(page_name, brief, page_args, proj_ident)
    parent = skiboot.from_ident(parent_ident, proj_ident)
    parent.add_page(page, page_ident)


def create_folder(proj_ident, parent_ident, addition_number, folder_name, restricted, json_data):
    """Builds the folder and contents from the given json string, or ordered dictionary and adds it to project
       Returns the top folder ident"""
    if isinstance(json_data, str):
        folder_dict = json.loads(json_data, object_pairs_hook=collections.OrderedDict)
    else:
        folder_dict = json_data
    # first check no clash of ident numbers
    project = skiboot.getproject(proj_ident)
    project_numbers = [ident.num for ident in project.identitems.keys()]
    new_numbers = []
    _check_idents_for_create_folder(project_numbers, new_numbers, addition_number, folder_name, folder_dict)
    # all idents ok, now create actual folders and pages and add them to the project

    # get parent
    parent_ident = skiboot.Ident(proj_ident, parent_ident)
    parent = skiboot.get_item(parent_ident)
    if folder_name in parent:
        raise excepts.ServerError("This name already exists in the parent folder")

    # set the parent change value
    parent.change = uuid.uuid4().hex

    if 'brief' in folder_dict:
        brief = folder_dict['brief']
    else:
        brief = "New folder"
    if 'default_page_name' in folder_dict:
        default_page_name = folder_dict['default_page_name']
    else:
        default_page_name = ''
    if not restricted:
        if 'restricted' in folder_dict:
            restricted = folder_dict['restricted']
    topfolder = folder_class_definition.Folder(folder_name, brief, default_page_name, restricted)
    # set the topfolder ident
    topfolder.ident = skiboot.Ident(proj_ident, folder_dict['ident']+addition_number)
    # set the item parentfolder attribute
    topfolder.parentfolder = parent
    item_list = [topfolder]
    # now fill folder contents
    if "folders" in folder_dict:
        for subfolder_name, subfolder in folder_dict['folders'].items():
            item_list.extend(_folder(topfolder, subfolder_name, subfolder, proj_ident, addition_number, restricted))
    if "pages" in folder_dict:
        for page_name, page in folder_dict['pages'].items():
            pageinstance = _page(topfolder, page_name, page, proj_ident, addition_number)
            if pageinstance is not None:
                item_list.append(pageinstance)
    # set this name into the parent
    parent.folders[folder_name] = topfolder.ident
    # item_list has all new folders and pages
    for item in item_list:
        project.identitems[item.ident] = item
    project.clear_cache()
    return topfolder.ident



def _check_idents_for_create_folder(project_numbers, new_numbers, addition_number, folder_name, folder):
    if 'ident' not in folder:
        raise excepts.ServerError("folder ident missing")
    identnum = folder['ident']+addition_number
    if identnum < 1:
        raise excepts.ServerError("Invalid ident number: zero or negative")
    if identnum in project_numbers:
        raise excepts.ServerError("Invalid folder ident number %s for folder %s: already exists in the project" % (identnum, folder_name))
    if identnum in new_numbers:
        raise excepts.ServerError("Invalid folder ident number %s for folder %s: duplicate number" % (identnum, folder_name))
    new_numbers.append(identnum)
    # now do same for sub folders
    if "folders" in folder:
        for subfolder_name, subfolder in folder['folders'].items():
            _check_idents_for_create_folder(project_numbers, new_numbers, addition_number, subfolder_name, subfolder)
    # and check page numbers
    if "pages" in folder:
        for page_name, page in folder['pages'].items():
            if 'ident' not in page:
                raise excepts.ServerError("page ident missing")
            identnum = page['ident']+addition_number
            if identnum < 1:
                raise excepts.ServerError("Invalid ident number: zero or negative")
            if identnum in project_numbers:
                raise excepts.ServerError("Invalid page ident number %s for page %s: already exists in the project" % (identnum, page_name))
            if identnum in new_numbers:
                raise excepts.ServerError("Invalid page ident number %s for page %s: duplicate number" % (identnum, page_name))
            new_numbers.append(identnum)



def read_project(proj_ident, projectfiles):
    "Reads the project.json file and checks version, if ok returns the read project"

    if not proj_ident:
        raise excepts.ServerError("Sorry, the project has not been recognised")

    filepath = os.path.join(projectfiles, proj_ident, "data", "project.json")

    try:
        with open(filepath, 'r') as fp:
            project = json.load(fp, object_pairs_hook=collections.OrderedDict)
    except Exception:
        raise excepts.ServerError("Unable to read file %s" % (filepath,))


    # project created with version = a.b.c
    # this skipole version = d.e.f

    #   The first and second digits may introduce new features
    #   The third digit is only used for refactoring

    # if a > d : The project cannot be read, project created with a later version, which may have introduced new widgets
    # if (a == d) and ( b > e) : The project cannot be read, project created with a later version, which may have introduced new widgets

    # any other combination : the project can be read
    
    if 'skipole' not in project:
        raise excepts.ServerError("Sorry, the project has not been recognised")

    if 'RootFolder' not in project:
        raise excepts.ServerError("Sorry, the project has not been recognised")

    proj_skipole_version = project['skipole']
    proj_tuple_skipole_version = tuple(int(v) for v in proj_skipole_version.split('.'))
    if len(proj_tuple_skipole_version) != 3:
        raise excepts.ServerError("Sorry, the project has not been recognised")
    this_skipole_version = skiboot.version()
    this_tuple_skipole_version = tuple(int(v) for v in this_skipole_version.split('.'))

    if proj_tuple_skipole_version[0] > this_tuple_skipole_version[0]:
        raise excepts.ServerError("Sorry, the project was created with a later version of skipole")

    if (proj_tuple_skipole_version[0] == this_tuple_skipole_version[0]) and (proj_tuple_skipole_version[1] > this_tuple_skipole_version[1]):
        raise excepts.ServerError("Sorry, the project was created with a later version of skipole")

    # update older versions

    # Change multiplier:1 to multiplier:0 in versions 3.1.0 and earlier
    if (proj_tuple_skipole_version[0] <= 3) and (proj_tuple_skipole_version[1] <= 1):
        # get all pages from the rootfolder downwards
        pages = _all_pages(project['RootFolder'])
        for page_dict in pages:
            if "SVG" in page_dict:
                topsvg = page_dict["svg"]
                placeholders = _allparts([[topsvg[0],topsvg[1]]], "SectionPlaceHolder")
                for ph in placeholders:
                    if ("multiplier" in ph) and (ph["multiplier"] == 1):
                        ph["multiplier"] = 0
            elif "TemplatePage" in page_dict:
                tophead = page_dict["body"]
                topbody = page_dict["body"]
                placeholders = _allparts([[tophead[0],tophead[1]]], "SectionPlaceHolder")
                for ph in placeholders:
                    if ("multiplier" in ph) and (ph["multiplier"] == 1):
                        ph["multiplier"] = 0
                placeholders = _allparts([[topbody[0],topbody[1]]], "SectionPlaceHolder")
                for ph in placeholders:
                    if ("multiplier" in ph) and (ph["multiplier"] == 1):
                        ph["multiplier"] = 0
            else:
                continue
    return project



def _all_pages(topfolder):
    """Return list of all page dictionaries in a folder and its sub folders
       Where topfolder is the folder dictionary as read by read_project() """
    # search through folders
    page_list = []
    if "folders" in topfolder:
        for folder in topfolder['folders'].values():
            page_list.extend(_all_pages(folder))
    if "pages" in topfolder:
        for page in topfolder['pages'].values():
            page_list.append(page)
    return page_list


def _allparts(toplist, part_type):
    """Return list of all part dictionaries within toplist that are of type part_type
       Where toplist is the list of [part_type,part_dict] items as read by read_project()"""
    # search through parts
    part_list = []
    for item in toplist:
        item_type, item_dict = item
        if item_type == part_type:
            part_list.append(item_dict)
            if item_type == 'Widget':
                for key in item_dict.keys():
                    if "container_" in key:
                        part_list.extend(_allparts(item_dict[key], part_type))
        elif item_type == 'Part':
            part_list.extend(_allparts(item_dict['parts'], part_type))
        elif item_type == 'Widget':
            for key in item_dict.keys():
                if "container_" in key:
                    part_list.extend(_allparts(item_dict[key], part_type))
    return part_list
 


def create_project(proj_ident, projectfiles):
    """Builds the project from the file project.json, returns a dictionary
          with the following keys
         original_skipole_version
         url
         default_language
         brief
         version
         specialpages - dictionary of label:ident or url
         sections - dictionary of {name:section,..}
         itemlist - list of pages and folders 
         siteroot - the root folder
"""

    project = read_project(proj_ident, projectfiles)
    projectdict = {}

    if 'url' in project:
        projectdict['url'] = project['url']
    else:
        projectdict['url'] = "/"

    if 'default_language' in project:
        projectdict['default_language'] = project['default_language']
    else:
        projectdict['default_language'] = skiboot.default_language()

    if 'brief' in project:
        projectdict['brief'] = project['brief']
    else:
        projectdict['brief'] = "Project %s" % proj_ident

    if 'version' in project:
        projectdict['version'] = project['version']
    else:
        projectdict['version'] = "0.0.0"

    if 'specialpages' in project:
        # dictionary of label:integer or url
        # needs to be a dictionary of label:ident or url
        specialpages = {}
        for label, target in project['specialpages'].items():
            if isinstance(target, int):
                # An ident belonging to this project
                specialpages[label] = skiboot.Ident(proj_ident, target)
            elif ',' in target:
                specialpages[label] = target
            elif '_' in target:
                itemident = skiboot.make_ident(target, proj_ident)
                if itemident is None:
                    specialpages[label] = target
                else:
                    specialpages[label] = itemident
            else:
                # must be a url
                specialpages[label] = target
        projectdict['specialpages'] = specialpages
    else:
        projectdict['specialpages'] = {}

    # ensure all library modules are present
    lib_labels = skiboot.lib_list()
    for lbl in lib_labels:
        if lbl not in projectdict['specialpages']:
            projectdict['specialpages'][lbl] = "lib," + lbl
 

    if 'sections' in project:
        sections = {}
        for section_name, section_part in project['sections'].items():
            section = _create_item(section_part, proj_ident)
            section.widgets = {}
            section.section_places = {}  # currently unused
            embedded = (section_name, '', None)
            section.set_idents(section_name, section.widgets, section.section_places, embedded)
            # now set validator modules in section
            section.load_validator_scriptlinks()
            sections[section_name] = section
        projectdict['sections'] = sections
    else:
        projectdict['sections'] = {}

    # read RootFolder and contents
    rootfolder = project['RootFolder']
    if 'brief' in rootfolder:
        brief = rootfolder['brief']
    else:
        brief = "Root folder"
    if 'default_page_name' in rootfolder:
        default_page_name = rootfolder['default_page_name']
    else:
        default_page_name = 'index'
    siteroot = folder_class_definition.RootFolder(proj_ident, brief, default_page_name)
    # now fill root contents
    item_list = []
    if "folders" in rootfolder:
        for folder_name, folder in rootfolder['folders'].items():
            item_list.extend(_folder(siteroot, folder_name, folder, proj_ident))
    if "pages" in rootfolder:
        for page_name, page in rootfolder['pages'].items():
            pageinstance = _page(siteroot, page_name, page, proj_ident)
            if pageinstance is not None:
                 item_list.append(pageinstance)
    projectdict['itemlist'] = item_list
    # and the root
    projectdict['siteroot'] = siteroot
    return projectdict


def _to_dict(input_dict, proj_ident):
    "If any value in input_dict is an integer, change it to an ident string"
    newdict = {}
    for key, value in input_dict.items():
        if value is True:
            newdict[key] = True
            continue
        if value is False:
            newdict[key] = False
            continue
        if isinstance(value, int):
            newdict[key] = proj_ident + '_' + str(value)
        else:
            newdict[key] = value
    return newdict


def _folder(parent, folder_name, folder_dict, proj_ident, addition_number=0, restricted=False):
    "Create a folder"
    folder_name = folder_name.lower()
    if 'ident' not in folder_dict:
        raise excepts.ServerError("A folder requires an ident")
    ident = skiboot.Ident(proj_ident, folder_dict['ident']+addition_number)
    if 'brief' in folder_dict:
        brief = folder_dict['brief']
    else:
        brief = "New folder"
    if 'default_page_name' in folder_dict:
        default_page_name = folder_dict['default_page_name']
    else:
        default_page_name = 'index'
    if not restricted:
        if 'restricted' in folder_dict:
            restricted = folder_dict['restricted']
    folder = folder_class_definition.Folder(folder_name, brief, default_page_name, restricted)
    # set the folder ident
    folder.ident = ident
    # set the item parentfolder attribute
    folder.parentfolder = parent
    # set this name into the parent
    parent.folders[folder_name] = folder.ident
    page_list = []
    # now fill folder contents
    if "folders" in folder_dict:
        for subfolder_name, subfolder in folder_dict['folders'].items():
            page_list.extend(_folder(folder, subfolder_name, subfolder, proj_ident, addition_number, restricted))
    if "pages" in folder_dict:
        for page_name, page in folder_dict['pages'].items():
            pageinstance = _page(folder, page_name, page, proj_ident, addition_number)
            if pageinstance is not None:
                page_list.append(pageinstance)
    # add folder to page_list
    page_list.append(folder)
    return page_list

def _page(parent, page_name, page_dict, proj_ident, addition_number=0):
    page_name = page_name.lower()
    if 'ident' not in page_dict:
        raise excepts.ServerError("A page ident missing")
    ident = skiboot.Ident(proj_ident, page_dict['ident']+addition_number)
    if 'brief' in page_dict:
        brief = page_dict['brief']
    else:
        brief = ""
    if "FilePage" in page_dict:
        page_args = page_dict["FilePage"]
        page = _create_filepage(page_name, brief, page_args)
    elif "RespondPage" in page_dict:
        page_args = page_dict["RespondPage"]
        page = _create_respondpage(page_name, brief, page_args, proj_ident)
    elif "CSS" in page_dict:
        page_args = page_dict["CSS"]
        page = _create_csspage(page_name, brief, page_args)
    elif "JSON" in page_dict:
        page_args = page_dict["JSON"]
        page = _create_jsonpage(page_name, brief, page_args)
    elif "SVG" in page_dict:
        page_args = page_dict["SVG"]
        page = _create_svgpage(page_name, brief, page_args)
        page.svg = _create_item(page_dict["svg"], proj_ident)
    elif "TemplatePage" in page_dict:
        page_args = page_dict["TemplatePage"]
        page = _create_templatepage(page_name, brief, page_args)
        page.head = _create_item(page_dict["head"], proj_ident)
        page.body = _create_item(page_dict["body"], proj_ident)
    else:
        return
    # set the page ident
    page.ident = ident
    # set the page parentfolder attribute
    page.parentfolder = parent
    # set the name:ident into the parent
    parent.pages[page_name] = page.ident
    if ("TemplatePage" in page_dict) or ("SVG" in page_dict):
        page.set_idents()
    if ("TemplatePage" in page_dict):
        # now set validator modules in page
            page.load_validator_scriptlinks()
    return page


def _create_filepage(page_name, brief, page_args):
    "Create a filepage"
    if 'filepath' in page_args:
        filepath = page_args['filepath']
    else:
        filepath = ''
    if 'mimetype' in page_args:
        mimetype = page_args['mimetype']
    else:
        mimetype = None
    if 'enable_cache' in page_args:
        enable_cache = page_args['enable_cache']
    else:
        enable_cache = False
    return page_class_definition.FilePage(page_name, brief, filepath, mimetype, enable_cache)


def _create_respondpage(page_name, brief, page_args, proj_ident):
    "Create a respondpage"
    responder_name = page_args['class']
    # import module
    mod = importlib.import_module('.ski.responders', 'skipole')
    Responder = None
    for cls in inspect.getmembers(mod, inspect.isclass):
        # cls[0] is responder name, cls[1] is the responder class
        if responder_name == cls[0]:
            Responder = cls[1]
            break
    else:
        raise excepts.ServerError("Responder %s not recognised" % (responder_name,))
    # get the data_args of the responder
    data_args = _to_dict(page_args["original_args"], proj_ident)
    if 'allowed_callers' in data_args:
        # This arg is a list, convert integers to ident strings
        allowed_callers = []
        for value in data_args['allowed_callers']:
            if isinstance(value, int):
                allowed_callers.append(proj_ident + '_' + str(value))
            else:
                allowed_callers.append(value)
        data_args['allowed_callers'] = allowed_callers
    # get the fields of the responder
    fields = dict(page_args["original_fields"])
    # make the responder
    responder=Responder(**data_args)
    # The option of no fields is accepted, as this may be a part constructed page
    if fields:
        responder.set_fields(fields)
    return page_class_definition.RespondPage(page_name, brief, responder)


def _create_csspage(page_name, brief, page_args):
    "Create a CSS page"
    if 'enable_cache' in page_args:
        enable_cache = page_args['enable_cache']
    else:
        enable_cache = False
    # style is an ordered dictionary, no need to convert
    if 'style' in page_args:
        style = page_args["style"]
    else:
        style = {}
    return page_class_definition.CSS(page_name, brief, style, enable_cache)


def _create_jsonpage(page_name, brief, page_args):
    "Create a JSON page"
    if 'enable_cache' in page_args:
        enable_cache = page_args['enable_cache']
    else:
        enable_cache = False
    # content is an ordered dictionary, no need to convert
    if 'content' in page_args:
        content = page_args["content"]
    else:
        content = None
    return page_class_definition.JSON(page_name, brief, content, enable_cache)


def _create_svgpage(page_name, brief, page_args):
    "Create an svg page"
    width = page_args["width"]
    height = page_args["height"]
    if "css_list" in page_args:
        css_list = page_args["css_list"]
    else:
        css_list = []
    if 'enable_cache' in page_args:
        enable_cache = page_args['enable_cache']
    else:
        enable_cache = False
    return page_class_definition.SVG(page_name, brief, width, height, css_list, enable_cache)


def _create_templatepage(page_name, brief, page_args):
    "Create a template page"
    args = {}
    if 'show_backcol' in page_args:
        args['show_backcol'] = page_args["show_backcol"]
    if "last_scroll" in page_args:
        args["last_scroll"] = page_args["last_scroll"]
    if 'interval' in page_args:
        args["interval"] = page_args["interval"]
    if 'interval_target' in page_args:
        args["interval_target"] = page_args["interval_target"]
    if 'lang' in page_args:
        args["lang"] = page_args["lang"]
    if 'backcol' in page_args:
        args["backcol"] = page_args["backcol"]
    if "default_error_widget" in page_args:
        s = page_args["default_error_widget"][0]
        w = page_args["default_error_widget"][1]
        args["default_error_widget"] = skiboot.WidgField(s=s, w=w, f='', i='')
    return page_class_definition.TemplatePage(name=page_name, brief = brief, **args)


def _create_item(item_list, proj_ident):
    "Return the item, be it a Part, ClosedPart etc.."
    itemtype = item_list[0]
    itemdict = item_list[1]
    if itemtype == 'Part':
        return _create_part(itemdict, proj_ident)
    if itemtype == 'ClosedPart':
        return _create_closedpart(itemdict, proj_ident)
    if itemtype == 'Section':
        return _create_section(itemdict, proj_ident)
    if itemtype == 'TextBlock':
        return _create_textblock(itemdict, proj_ident)
    if itemtype == 'SectionPlaceHolder':
        return _create_sectionplaceholder(itemdict, proj_ident)
    if itemtype == 'Widget':
        return _create_widget(itemdict, proj_ident)
    if itemtype == 'ClosedWidget':
        return _create_widget(itemdict, proj_ident)
    if itemtype == 'HTMLSymbol':
        return _create_htmlsymbol(itemdict, proj_ident)
    if itemtype == 'Comment':
        return _create_comment(itemdict, proj_ident)
    if itemtype == 'Text':
        return itemdict


def _create_part(part_dict, proj_ident):
    "Returns a Part"
    tag_name = part_dict["tag_name"]
    if 'brief' in part_dict:
        brief = part_dict["brief"]
    else:
        brief = ''
    show = part_dict["show"]
    hide_if_empty = part_dict["hide_if_empty"]
    if "attribs" in part_dict:
        attribs = dict(part_dict["attribs"])
    else:
        attribs = {}
    # create the part
    part = tag.Part(tag_name, attribs, show=show, hide_if_empty=hide_if_empty, brief=brief)
    # now the Part contents in a list
    parts = part_dict["parts"]
    for index,item_list in enumerate(parts):
        part[index] = _create_item(item_list, proj_ident)
    return part


def _create_closedpart(part_dict, proj_ident):
    "Returns a ClosedPart"
    tag_name = part_dict["tag_name"]
    if 'brief' in part_dict:
        brief = part_dict["brief"]
    else:
        brief = ''
    show = part_dict["show"]
    if "attribs" in part_dict:
        attribs = dict(part_dict["attribs"])
    else:
        attribs = {}
    return tag.ClosedPart(tag_name, attribs, show=show, brief=brief)


def _create_section(part_dict, proj_ident):
    "Returns a Section"
    tag_name = part_dict["tag_name"]
    if 'brief' in part_dict:
        brief = part_dict["brief"]
    else:
        brief = ''
    show = part_dict["show"]
    hide_if_empty = part_dict["hide_if_empty"]
    if "attribs" in part_dict:
        attribs = dict(part_dict["attribs"])
    else:
        attribs = {}
    # create the section
    section = tag.Section(tag_name, attribs, show=show, hide_if_empty=hide_if_empty, brief=brief)
    # now the section contents in a list
    parts = part_dict["parts"]
    for index,item_list in enumerate(parts):
        part = _create_item(item_list, proj_ident)
        # as this is going into a section, remove any placeholders
        _remove_sectionplaceholders(part)
        section[index] = part
    return section



def _create_textblock(part_dict, proj_ident):
    "Creates a TextBlock"
    textref = part_dict["textref"]
    project = ''
    if "project" in part_dict:
        if part_dict["project"] != proj_ident:
            project = part_dict["project"]
    if "failmessage" in part_dict:
        failmessage = part_dict["failmessage"]
    else:
        failmessage=''
    show = part_dict["show"]
    escape = part_dict["escape"]
    linebreaks = part_dict["linebreaks"]
    if "replace_strings" in part_dict:
        replace_strings = part_dict["replace_strings"]
    else:
        replace_strings = []
    return tag.TextBlock(textref=textref, project=project, failmessage=failmessage, escape=escape, linebreaks=linebreaks, replace_strings=replace_strings, show=show)


def _create_sectionplaceholder(part_dict, proj_ident):
    "Creates a sectionplaceholder"
    section_name = part_dict['section_name']
    placename = part_dict['placename']
    if 'brief' in part_dict:
        brief = part_dict['brief']
    else:
        brief = "Section %s with alias %s" % (section_name, placename)
    if 'multiplier' in part_dict:
        multiplier = part_dict['multiplier']
    else:
        multiplier = 0
    if 'mtag' in part_dict:
        mtag = part_dict['mtag']
    else:
        mtag = "div"    
    return tag.SectionPlaceHolder(section_name=section_name, placename=placename, multiplier=multiplier, mtag=mtag, brief=brief)


def _create_htmlsymbol(part_dict, proj_ident):
    "Creates an html symbol"
    text = part_dict['text']
    return tag.HTMLSymbol(text=text)


def _create_comment(part_dict, proj_ident):
    "Creates a comment"
    text = part_dict['text']
    return tag.Comment(text=text)


def _create_widget(part_dict, proj_ident):
    "Returns a Widget"
    mod_name, widg_class_name = part_dict['class'].split(".")
    # import module
    try:
        mod = importlib.import_module('skipole.ski.widgets.'+mod_name)
    except Exception:
        print("ERROR: Unable to import widget %s.%s" % (mod_name, widg_class_name))
        raise excepts.ServerError("Error reading file")
    for cls in inspect.getmembers(mod, inspect.isclass):
        # cls[0] is widget class name, cls[1] is the widget class
        if widg_class_name == cls[0]:
            Widg = cls[1]
            break
    else:
        print("ERROR: Widget %s.%s not found" % (mod_name, widg_class_name))
        raise excepts.ServerError("Error reading file")
    # so Widg contains the widget class, must now instanciate it
    if 'name' in part_dict:
        name = part_dict['name']
    else:
        name = None
    if 'brief' in part_dict:
        brief = part_dict['brief']
    else:
        brief = ''
    if 'fields' in part_dict:
        fields = _to_dict(part_dict['fields'], proj_ident)
    else:
        fields = {}
    widg = Widg(name=name, brief=brief, **fields)
    # widg may have contents
    if widg.can_contain():
        for cont in range(widg.len_containers()):
            container = "container_%s" % (cont,)
            if container in part_dict:
                item_list = part_dict[container]
                # item_list may be an empty list
                if not item_list:
                    # if an empty list, place an empty string in the container
                    widg.append_to_container(cont, '')
                    continue
                # test for list until all projects have containers changed to lists
                if isinstance(item_list[0], list):
                    for itempart in item_list:
                        part = _create_item(itempart, proj_ident)
                        widg.append_to_container(cont, part)
                else:
                    # can be removed once projects converted
                    part = _create_item(item_list, proj_ident)
                    widg.append_to_container(cont, part)
    if "set_names" in part_dict:
        fields_names = part_dict["set_names"]
        for field, name in fields_names.items():
            widg.set_name(field, name)
    if "validators" in part_dict:
        val_dict = part_dict["validators"]
        for field_name, val_list in val_dict.items():
            _get_validators(widg, field_name, val_list, proj_ident)
    return widg


def _get_validators(widget, field_name, val_list, proj_ident):
    "Add validators in val_list to widget.field_name"
    for validator in val_list:
        val_class = validator['class']
        # now write the validator fields
        if "message" in validator:
            message = validator["message"]
        else:
            message=''
        if "message_ref" in validator:
            message_ref = validator["message_ref"]
        else:
            message_ref = ''
        if "displaywidget" in validator:
            displaywidget = validator["displaywidget"]
        else:
            displaywidget = None
        if "allowed_values" in validator:
            allowed_values = validator["allowed_values"]
        else:
            allowed_values = []
        if "val_args" in validator:
            val_args = validator["val_args"]
        else:
            val_args = {}
        mod_name, val_class_name = val_class.split('.')
        try:
            mod = importlib.import_module('skipole.ski.validators.'+mod_name)
        except Exception:
            print("ERROR: Unable to import validator %s.%s" % (mod_name, val_class_name))
            raise excepts.ServerError("Error reading file")
        # get Validator class
        for cls in inspect.getmembers(mod, inspect.isclass):
            # cls[0] is validator class name, cls[1] is the validator class
            if val_class_name == cls[0]:
                Val = cls[1]
                break
        else:
            print("ERROR: Validator %s.%s not found" % (mod_name, val_class_name))
            raise excepts.ServerError("Error reading file")
        # create the validator
        val = Val(message=message, message_ref=message_ref, displaywidget=displaywidget, allowed_values=allowed_values, **val_args)
        # add validator to widget
        widget.add_validator(field_name, val)

