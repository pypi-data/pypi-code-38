

"""
This module defines a number of functions and classes used throughout
the program.
"""

import os, copy, collections

# Configuration defaults

_CFG = {
"version"         : "3.1.0",             # The skipole version
"default_language": 'en',                # The default language of the project
"debug"           : False                # The debug mode, True shows exceptions on server error
}

# create a dictionary of all projects, {proj_ident:project}
PROJECT_REGISTER = {}

_LIB_LABELS = ["skipole_js", "jquery_core",
               "ski_basic", "ski_checkbox", "ski_confirm", "ski_debug_tools", "ski_dropdown", "ski_error_messages",
               "ski_footers", "ski_headers", "ski_info", "ski_inputforms", "ski_inputtables",
               "ski_inputtext", "ski_links", "ski_lists", "ski_logins", "ski_paras", "ski_paths", "ski_radio", "ski_svgbasics", "ski_svggraphs", "ski_svgmeters",
               "ski_tables", "ski_textarea", "ski_upload"]

_SYS_LABELS = ["url_not_found", "validate_error", "server_error", "redirector", "no_javascript", "general_json"]


Info = collections.namedtuple('Info', ['project', 'project_version', 'ident', 'item_type', 'name', 'brief', 'path', 'label_list', 'change', 'parentfolder_ident', 'restricted'])


def add_to_project_register(project):
    "Adds the project to a list of all projects"
    global PROJECT_REGISTER
    PROJECT_REGISTER[project.proj_ident] = project


def project_register():
    "Return a dictionary of all projects"
    global PROJECT_REGISTER
    return PROJECT_REGISTER

def project_ident_register():
    "Return a list of all project idents"
    global PROJECT_REGISTER
    return list(PROJECT_REGISTER.keys())

def root_project():
    "Return the root project"
    global PROJECT_REGISTER
    for proj in PROJECT_REGISTER.values():
        if proj.rootproject:
            return proj

def projectfiles(proj_ident=None):
    """Returns the directory entry where projectfiles can be found for a given project
       If proj_ident is None, then returns projectfiles for the root project"""
    proj = getproject(proj_ident)
    if proj is None:
        return
    return proj.projectfiles

def lib_list():
    "Returns list of library labels"
    return _LIB_LABELS

def sys_list():
    "Returns list of system page labels"
    return _SYS_LABELS

def is_project(proj_ident):
    "Returns True if this project is in the site, False otherwise"
    if proj_ident in PROJECT_REGISTER:
        return True
    return False

def get_debug():
    "Returns the debug mode"
    return _CFG["debug"]

def set_debug(mode):
    "Sets debug mode"
    global _CFG
    _CFG["debug"] = bool(mode)


def getproject(proj_ident):
    """Returns the project given by the proj_ident
       If the project does not exist, return None"""
    if proj_ident in PROJECT_REGISTER:
        return PROJECT_REGISTER[proj_ident]

def project_ident(proj_ident=None):
    "Returns the given project ident, if it is None, returns current site root project ident"
    if proj_ident is None:
        return root_project().proj_ident
    return proj_ident

def projectdir(proj_ident=None):
    "Returns projectfiles/proj_ident"
    return os.path.join(projectfiles(proj_ident), project_ident(proj_ident))

def projectstatic(proj_ident=None):
    "Returns projectfiles/proj_ident/static"
    return os.path.join(projectdir(proj_ident), 'static')

def projectdata(proj_ident=None):
    "Returns projectfiles/proj_ident/data"
    return os.path.join(projectdir(proj_ident), 'data')

def projectcode(proj_ident=None):
    "Returns projectfiles/proj_ident/code"
    return os.path.join(projectdir(proj_ident), 'code')


def project_json(proj_ident=None):
    "Returns projectfiles/proj_ident/data/project.json"
    return os.path.join(projectdata(proj_ident), "project.json")

def project_defaults(proj_ident=None):
    "Returns projectfiles/proj_ident/data/defaults.json"
    return os.path.join(projectdata(proj_ident), "defaults.json")

def project_main(proj_ident=None):
    "Returns projectfiles/proj_ident/data/__main__.py"
    return os.path.join(projectdata(proj_ident), "__main__.py")

def default_language():
    "Returns the default language"
    return _CFG["default_language"]

def version():
    "Returns the version string"
    return _CFG["version"]

    

# These functions deal with page and folder 'idents'.  They are defined here
# as they are common functions used everywhere.

def from_ident(ident, proj_ident=None):
    """given an Ident, or a string version of ident, or item with ident attribute, return deepcopy of page or folder."""
    ident = Ident.to_ident(ident, proj_ident)
    if ident is None:
        return
    project = getproject(ident.proj)
    if project is None:
        return
    item = project.get_item(ident)
    return copy.deepcopy(item)


def item_info(ident):
    """Returns a namedtuple of item information
          None if not found, tuple has contents:
          project, project_version, ident, item_type, name, brief, path, label_list, change, parentfolder_ident, restricted
       note: project is the project name
             parentfolder_ident is the parent folder ident or None if this is root
             ident is this item ident"""

    project = getproject(ident.proj)
    if project is None:
        return
    item = project.get_item(ident)
    if item is None:
        return

    if item.name is None:
        name = ''
    else:
        name = item.name
    special_pages = project.special_pages
    label_list = []
    for label, value in special_pages.items():
        if ident == value:
            label_list.append(label)
    return Info(ident.proj,
                project.version,
                ident,
                item.page_type,
                name,
                item.brief,
                item.url,
                label_list,
                item.change,
                item.parentfolder_ident,
                item.restricted
               )


def get_item(ident):
    """Gets uncopied page or folder, without importing sections and returns it
        Returns None if not found. Requires full ident object"""
    project = getproject(ident.proj)
    if project is None:
        return None
    return project.get_item(ident)


def get_url(label_url_ident, proj_ident=None):
    "Returns a url given a page ident, url or label, if not found, return None"
    if (label_url_ident is not 0) and (not label_url_ident):
        return
    result = find_ident_or_url(label_url_ident, proj_ident)
    if isinstance(result, Ident):
        return result.url()
    return result


def ident_from_path(path, proj_ident=None):
    project = getproject(proj_ident)
    if project is None:
        return
    return project.root.ident_from_path(path)


def ident_exists(ident, proj_ident=None):
    "Return True if ident exists, False otherwise, ident can be a string form of ident"
    ident = Ident.to_ident(ident, proj_ident)
    if ident is None:
        return False
    project = getproject(ident.proj)
    if project is None:
        return False
    return ident.num in project.ident_numbers


def ident_exists_strict(ident):
    "Returns ident if it exists, None otherwise, ident must be an Ident object"
    if not isinstance(ident, Ident):
        return
    project = getproject(ident.proj)
    if project is None:
        return
    if ident.num in project.ident_numbers:
        return ident


# usefull functions
    

def mergedict(dict1, dict2):
    "returns a dictionary, which is the update of two dictionaries"
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict

def mergedicttostyle(style_dict, key, add_dict):
    "Returns a new style_dict, with the dictionary of the key item updated with add_dict"
    if key in style_dict:
        new_sub_dict = mergedict(style_dict[key], add_dict)
    else:
        new_sub_dict = add_dict.copy()
    new_dict = style_dict.copy()
    new_dict[key] = new_sub_dict
    return new_dict


def make_ident_or_label_or_url(item, proj_ident=None):
    """Given an item, be it integer, string or Ident, return an Ident object
       If the item is an integer, the returned Ident object
       will have its proj set to the proj_ident if given, otherwise current project
       If item is a not convertable to an ident - then return the string,
       which should be a label or url"""
    if isinstance(item, str) and ('/' in item):
        # must be a url
        return item
    ident = Ident.to_ident(item, proj_ident)
    if ident is None:
        # not convertable to ident, must be a label
        return item
    return ident


def make_ident_or_label(item, proj_ident=None):
    """Given an item, be it integer, string or Ident, return an Ident object
       or label - not a url.
       If the item is an integer, the returned Ident object
       will have its proj set to the proj_ident if given, otherwise current project
       If item is a not convertable to an ident - then return the string,
       which should be a label, if string contains /, return None"""
    if isinstance(item, str) and ('/' in item):
        # a url - return None
        return
    ident = Ident.to_ident(item, proj_ident)
    if ident is None:
        # not convertable to ident, must be a label
        return item
    return ident



def make_ident(item, proj_ident=None):
    """Just calls Ident.to_ident"""
    return Ident.to_ident(item, proj_ident)


def find_ident(item, proj_ident=None):
    """Given any item makes an attempt to find an Ident
       existing in the project, item could have an ident attribute,
       or be an ident in string or integer or Ident form
       or label, or tuple of form (project,ident) or (project,label).
       If no existing ident or if a url found instead, returns None"""

    ident_or_url = find_ident_or_url(item, proj_ident)
    if isinstance(ident_or_url, Ident):
        return ident_or_url
    # ident_or_url may be a URL or None, in this case return None
    return



def find_ident_or_url(item, proj_ident=None):
    """Given any item makes an attempt to find an Ident or url
       existing in the project, item could have an ident attribute,
       or be an ident in string or integer or Ident form
       or label, or tuple of form (project,ident) or (project,label).
       If no existing ident or url found, returns None"""

    if item is 0:
        return ident_exists_strict(Ident.to_ident(item, proj_ident))

    if not item:
        return

    if isinstance(item, Ident):
        return ident_exists_strict(item)

    if isinstance(item, str):
        item = item.strip()
        if not item:
            return
        if '/' in item:
            # its a url
            return item
        if item.isdigit():
            # string integer
            return ident_exists_strict(Ident.to_ident(item, proj_ident))
        # could be 'project,number' or 'project,label', 
        if ',' in item:
            item_parts = item.split(',')
            if len(item_parts) != 2:
                return
            if item_parts[1].isdigit():
                return ident_exists_strict(Ident.to_ident(item, proj_ident))
            # may be 'project,label' - so find [project,label]
            return find_ident_or_url(item_parts, proj_ident=proj_ident)
        # could be case of 'project_number'
        if '_' in item:
            item_parts = item.split('_')
            if (len(item_parts) == 2) and item_parts[1].isdigit():
                return ident_exists_strict(Ident.to_ident(item, proj_ident))

        # item is a label
        project = getproject(proj_ident)
        if project is None:
            return
        special_pages = project.special_pages
        if item not in special_pages:
            return
        target = special_pages[item]
        # target is either an Ident, url, or 'proj,label' string
        if isinstance(target, Ident):
            return ident_exists_strict(target)
        if '/' in target:
            # so item is a label pointing to this url
            return target
        if ',' in target:
            # so item is a label pointing to project,newitem
            target_parts = target.split(',')
            return find_ident_or_url(target_parts[1], proj_ident=target_parts[0])

    if not ( (isinstance(item, tuple)) or (isinstance(item, list)) ):
        # not a tuple or a list, so maybe integer - try to convert to ident
        return ident_exists_strict(Ident.to_ident(item, proj_ident))

    # test for [project, newitem]

    # item is a tuple or list
    if len(item) != 2:
        # invalid, return None
        return

    proj = item[0].strip()

    project = getproject(proj)
    if project is None:
        return

    return find_ident_or_url(item[1], proj_ident=proj)




# Each folder and page has an instance of Ident
class Ident(collections.namedtuple('Ident', ['proj','num'])):
    __slots__ = ()

    @classmethod
    def to_ident(cls, item, proj_ident=None):
        """Given an ident, be it tuple, integer, string or Ident, return an Ident object
           If the item is just an integer, the returned Ident object
           will have its proj set to the proj_ident if given, otherwise current project
           If an Ident object cannot be created, return None"""
        # Deal with cases where proj_ident is not needed
        if isinstance(item, cls):
            return item
        if isinstance(item, str):
            # first deal with case of a string ident myproj_num
            if '_' in item:
                item = item.split('_')
            elif ',' in item:
                item = item.split(',')
            else:
                # could be a string integer
                try:
                    item = int(item)
                except Exception:
                    # don't know what it is, return None
                    return
        if isinstance(item, tuple) or isinstance(item, list):
            if len(item) == 2:
                try:
                    num = int(item[1])
                except Exception:
                    # don't know what it is, return None
                    return
                if item[0] and isinstance(item[0], str):
                    return cls(item[0], num)
                else:
                    return
            else:
                # list, but not of length two, don't know what it is
                return
        if hasattr(item, 'ident') and (isinstance(item.ident, cls)):
            return item.ident
        if isinstance(item, int):
            # project not derived from item, therefore need to use proj_ident
            # proj_ident must be either an Ident instance, string or None
            if isinstance(proj_ident, cls):
                proj = proj_ident.proj
            elif proj_ident:
                proj = proj_ident
            else:
                proj = root_project().proj_ident
            return cls(proj, item)

    def item(self):
        """Return page or folder with this ident. 
           If folder or respond page return the item, any other page, return a deep copy
           If not found, return None."""
        project = getproject(self.proj)
        if project is None:
            return
        try:
            item = project[self]
        except Exception:
            return
        return item


    def name(self):
        """Returns the name of the page or folder with this ident
           If item is root, or item not found, returns None"""
        if self.num is 0:
            return None
        item = get_item(self)
        if item is None:
            return
        return item.name

    def url(self):
        "Returns the url of the page or folder with this ident"
        item = get_item(self)
        if item is None:
            return
        return item.url

    def widg_ident(self, widgname):
        """Given a widget name, if this ident is the ident of a page, and the widget
           is in the page, return the widgets ident, if the ident is not that of a page
           or the widget name is not found in the page, return an empty string"""
        item = get_item(self)
        if ((item.page_type == 'TemplatePage') or (item.page_type == 'SVG')) and (widgname in item.widgets):
            return item.widgets[widgname]
        return ''

    def to_tuple(self):
        return (self.proj, self.num)

    def to_comma_str(self):
        return self.proj + "," + str(self.num)

    def __str__(self):
        return self.proj + "_" + str(self.num)

    def __add__(self, other):
        "An ident can be added to a integer or tuple to give a string"
        if isinstance(other, Ident):
            raise TypeError("An Ident cannot be added to another Ident")
        if isinstance(other, tuple) or isinstance(other, list):
            return self.__str__() + '_' + '_'.join(str(i) for i in other)
        return self.__str__() + '_' + str(other)

#
# Defines functions and class WidgField which is a named tuple with attributes s,w,f,i
# for section name, widget name, field name, index value
# section name could be empty if widget is not in a section
# index value is used for widgfield dictionaries, and can be empty if not applicable
# widgfield has string sectionname-widgetname:fieldname-index
#

def make_widgfield(field, widgetonly=False):
    """Given a string field, of the form sectionname-widgetname:fieldname-index, (set by widgets)
       or of the form sectionname-widgetname:fieldname.index, (set by browser, ie image x,y coordinates)
       or a list or tuple, of form (sectionname, widgetname, fieldname, index)
       Note: if index given, tuple must have four elements, if three given they will
       be assumed as (sectionname, widgetname, fieldname)
       returns a named tuple of the form WidgField(s=sectionname, w=widgetname, f=fieldname, i=index)
       If field is already a WidgField, just returns it"""
    if not field:
        return WidgField(s='', w='', f='', i='')
    if widgetonly:
        if isinstance(field, WidgField):
            return WidgField(s=field.s, w=field.w, f='', i='')
        if isinstance(field, str) and (',' in field):
            field = [ item.strip() for item in field.split(',') ]
        if isinstance(field, list) or isinstance(field, tuple):
            if len(field) == 1:
                return WidgField(s='', w=field[0], f='', i='')
            if len(field) >= 2:
                return WidgField(s=field[0], w=field[1], f='', i='')
        # so should be a string
        if ':' in field:
            field = field.split(':')[0]
        if not field:
            return WidgField(s='', w='', f='', i='')
        if '-' in field:
            sectionname, widgetname = field.split("-", 1)
            return WidgField(s=sectionname, w=widgetname, f='', i='')
        else:
            # widgetname only
            return WidgField(s='', w=field, f='', i='')
    # not just a widget, could be widget and field
    if isinstance(field, WidgField):
        return field
    if isinstance(field, str) and (',' in field):
        field = [ item.strip() for item in field.split(',') ]
    if isinstance(field, list) or isinstance(field, tuple):
        if len(field) == 1:
            return WidgField(s='', w=field[0], f='', i='')
        if len(field) == 2:
            return WidgField(s='', w=field[0], f=field[1], i='')
        if len(field) == 3:
            return WidgField(s=field[0], w=field[1], f=field[2], i='')
        return WidgField(s=field[0], w=field[1], f=field[2], i=field[3])
    # so should be a string
    if ':' not in field:
        if '-' in field:
            sectionname, widgetname = field.split("-", 1)
            return WidgField(s=sectionname, w=widgetname, f='', i='')
        else:
            # widgetname only, no section, field or index
            return WidgField(s='', w=field, f='', i='')
    sectionwidgetname, field_index = field.split(":", 1)
    if '-' in sectionwidgetname:
        sectionname, widgetname = sectionwidgetname.split("-", 1)
    else:
        sectionname = ''
        widgetname = sectionwidgetname
    # field index separated by - or by .
    if '-' in field_index:
        fieldname, index = field_index.split("-", 1)
    elif '.' in field_index:
        fieldname, index = field_index.split(".", 1)
    else:
        fieldname = field_index
        index=''
    return WidgField(s=sectionname, w=widgetname, f=fieldname, i=index)


def list_widgfield(widgfield, widgfield_dict):
    """Converts a widgfield (with no i value), and a dictionary to a list of
       of widgfield,value tuples, with each widgfield in the tuple having i set to the key
       and the list is sorted by key"""
    if widgfield.i:
        return [(widgfield, widgfield_dict)]
    return sorted([(widgfield._replace(i=key), val) for key, val in widgfield_dict.items()], key=lambda tup: tup[0].i)


class WidgField(collections.namedtuple('WidgField', 's w f i')):
    __slots__ = ()

    def set_field(self, f='', i=''):
        "Returns a copy of self, with new field and index set"
        return WidgField(s=self.s, w=self.w, f=f, i=i)

    def set_index(self, i=''):
        "Returns a copy of self, with new index set"
        return WidgField(s=self.s, w=self.w, f=self.f, i=i)

    def __bool__(self):
        if self.s or self.w or self.f or self.i:
            return True
        return False

    def __str__(self):
        "returns sectionname-widgetname:fieldname-index"
        if self.s:
            val = self.s + '-' + self.w
        else:
            val = self.w
        if self.f:
             val = val + ':' + self.f
        if self.i:
            val = val + '-' + self.i
        return val

    def to_tuple(self):
        "returns tuple of (self.s, self.w, self.f, self.i)"
        return (self.s, self.w, self.f, self.i)

    def to_tuple_no_i(self):
        "returns tuple of (self.s, self.w, self.f) if self.s or (self.w, self.f) if no self.s"
        if self.s:
            return (self.s, self.w, self.f)
        return (self.w, self.f)

    def sw_tuple(self):
        "returns tuple of (self.s, self.w)"
        if self.s:
            return (self.s, self.w)
        return ('',self.w)

    def to_str_tuple(self):
        "returns sectionname,widgetname,fieldname,index"
        if self.s:
            val = self.s + ',' + self.w
        else:
            val = self.w
        if self.f:
             val = val + ',' + self.f
        if self.i:
            val = val + ',' + self.i
        return val


