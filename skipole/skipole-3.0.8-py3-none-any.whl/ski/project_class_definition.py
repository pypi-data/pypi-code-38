

"""
This module defines the WSGIApplication class and SkiCall class
"""


import copy, os, cgi, collections, html, pprint, json, shutil, uuid, sys, traceback, re

from http import cookies

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')

from . import skiboot, read_json
from .excepts import ValidateError, ServerError, FailPage, ErrorMessage, GoTo, PageError
from .. import textblocks


# ServerError raised in this module use codes 9000 to 9100


class WSGIApplication(object):
    """The WSGIApplication - an instance being a callable WSGI application"""

    def __init__(self, project, projectfiles=None, proj_data={}, start_call=None, submit_data=None, end_call=None, url="/"):
        """Initiates a Project instance"""
        if _AN.search(project):
            raise ServerError(message="Error: Invalid project name, alphanumeric only")
        if '_' in project:
            raise ServerError(message="Error: Invalid project name, alphanumeric only (no underscore).")
        self._proj_ident = project
        self.projectfiles = projectfiles
        self.proj_data = proj_data
        self.start_call = start_call
        self.submit_data = submit_data
        self.end_call = end_call

        # initially, sub projects can be added
        self.rootproject = True

        self.brief = "Project %s" % project
        self.version = "0.0.0"
        # The url of the root folder
        url=url.strip("/").lower()
        if url:
            self.url = "/" + url + "/"
        else:
            self.url = "/"
        # The root Folder
        self.root = None
        # dictionary of special pages, key = label: value = page ident
        self.special_pages = {}
        # dictionary of sections, key = name: value = section
        self.sections = {}

        # an ordered dictionary of {proj_ident: url,...}, ordered by length of url
        self._subproject_paths = collections.OrderedDict()
        # self.subprojects is a dictionary of sub projects {proj_ident: Project instance,.....}
        self.subprojects = {}

        # dictionary of idents: to folder or page, apart from root
        # note keys are full Ident instances, values are  folder or page instances
        self.identitems = {}

        # Create an instance of the AccessTextBlocks class for this project
        self.textblocks = textblocks.AccessTextBlocks(self._proj_ident, projectfiles, skiboot.default_language())

        # maintain a cach dictionary of paths against idents {path:ident}
        self._paths = {}

        # load project from json files
        self.load_from_json()

        # and add this project to the project register
        skiboot.add_to_project_register(self)


    def __call__(self, environ, start_response):
        "Defines this projects callable as the wsgi application"
        status, headers, data = self.respond(environ)
        start_response(status, headers)
        return iter(data)

    def set_default_language(self, language):
        "Sets the project default language"
        self.textblocks.default_language = language

    def get_default_language(self):
        "Returns the project default language"
        return self.textblocks.default_language

    default_language = property(get_default_language, set_default_language)

    def clear_cache(self):
        "clear the cache of paths"
        self._paths = {}


    def load_from_json(self):
        "Loads project with data saved in project.json file"
        projectdict = read_json.create_project(self._proj_ident, self.projectfiles)
        self.default_language = projectdict['default_language']
        self.brief = projectdict['brief']
        self.version = projectdict['version']
        self.special_pages = projectdict['specialpages']
        self.sections = projectdict['sections']
        self.root = projectdict['siteroot']
        itemlist = projectdict['itemlist']
        self.identitems = {}
        if itemlist:
            for item in itemlist:
                self.identitems[item.ident] = item


    @property
    def max_ident_num(self):
        "Returns the maximum identnumber currently in use"
        maxnum = 0
        for ident in self.identitems:
            if ident.num > maxnum:
                    maxnum = ident.num
        return maxnum

    def list_section_names(self):
        "Returns a list of section names, alphabetacily ordered"
        if not self.sections:
            return []
        s = [ name for name in self.sections ]
        s.sort()
        return s

    def widget_from_section(self, section_name, widget_name):
        "Returns the widget from the project section"
        # get the section part with the given name
        section = self._get_section(section_name)
        if section is None:
            return None
        # find widget in the section with the given name
        if widget_name in section.widgets:
            return section.widgets[widget_name]

    def section(self, section_name, makecopy=True):
        "Returns a section, or a deep copy of a section, or None if the section name is not found"
        if section_name not in self.sections:
            return
        section = self.sections[section_name]
        if not makecopy:
            return section
        if section is None:
            return None
        return copy.deepcopy(section)
 

    def add_section(self, name, section):
        "Adds a section to the project, returns section.change uuid"
        # and save the section
        section.widgets = {}
        section.section_places = {}  # currently unused
        embedded = (name, '', None)
        section.set_idents(name, section.widgets, section.section_places, embedded)
        # set validators in section
        section.load_validator_scriptlinks()
        # set the section change number
        section.change = uuid.uuid4().hex
        self.sections[name] = section
        return section.change


    def delete_section(self, name):
        "Deletes a section"
        if name in self.sections:
            del self.sections[name]

    @property
    def ident_numbers(self):
        "return a list of ident numbers"
        num_list = [ ident.num for ident in self.identitems ]
        # insert the root
        num_list.insert(0,0)
        num_list.sort()
        return num_list

    def __getitem__(self, ident):
        """given an Ident, or a string version of ident, return page or folder. 
              If folder or respond page return the item, any other page, return a deep copy
              of the item. If item not found, return None"""
        ident = skiboot.Ident.to_ident(ident, proj_ident=self._proj_ident)
        if ident is None:
            return
        if ident.proj != self._proj_ident:
            return
        if ident.num == 0:
            return self.root
        if ident not in self.identitems:
            return
        item = self.identitems[ident]
        if item is None:
            return
        if item.page_type == 'Folder':
            return item
        if item.page_type == 'RespondPage':
            return item
        return copy.deepcopy(item)

    def add_item(self, parent_ident, item, ident=None):
        """Adds a new page or folder to the project, returns the item ident"""

        # check ident
        if ident is None:
            ident = skiboot.Ident(self._proj_ident, self.max_ident_num+1)
        else:
            ident = skiboot.make_ident(ident, self._proj_ident)
            if ident is None:
                raise ServerError(message="Sorry. Invalid ident", code=9000)
            if ident.num == 0:
                # cannot add the root folder
                raise ServerError(message="Sorry. Unable to add a new root", code=9001)
            if ident.proj != self._proj_ident:
                # must be in this project
                raise ServerError(message="Sorry. Invalid ident", code=9002)
            if ident in self.identitems:
                # ident must not exist
                raise ServerError(message="Sorry. The given ident already exists", code=9003)

        # check parent folder
        if parent_ident.proj != self._proj_ident:
            raise ServerError(message="Invalid parent ident", code=9004)
        parent = self.get_item(parent_ident)
        if parent is None:
            raise ServerError(message="Parent folder not found: Error in add_item method of Project class.", code=9005)
        if parent.page_type != 'Folder':
            raise ServerError(message="Parent not a folder", code=9006)

        if item.name in parent.pages:
            raise ServerError(message="Sorry, a page with that name already exists in the parent folder", code=9007)
        if item.name in parent.folders:
            raise ServerError(message="Sorry, a folder with that name already exists in the parent folder", code=9008)

        # set the item ident
        item.ident = ident

        # set this item name into the parent
        if item.page_type == 'Folder':
            if parent.restricted:
                item.set_restricted()
            parent.folders[item.name] = item.ident
        # if the page is a template or svg page, then set its idents
        # and store its widgets in the page's widgets dictionary and sectionplaceholders
        # in the page's sections directory
        elif (item.page_type == 'TemplatePage') or (item.page_type == 'SVG'):
            item.set_idents()
            parent.pages[item.name] = item.ident
            # now set validator modules in page
            if item.page_type == 'TemplatePage':
                item.load_validator_scriptlinks()
        else:
            parent.pages[item.name] = item.ident

        # set the parent change value
        parent.change = uuid.uuid4().hex
        item.parentfolder = parent

        # and finally, add the item
        self.identitems[item.ident] = item
        self.clear_cache()
        return item.ident


    def delete_item(self, itemident):
        """Deletes the page or folder with the given ident from the database."""
        #############  TO DO - if folder has contents, recursivly delete contents ########
        if itemident.num == 0:
            # cannot delete the root folder
            raise ServerError(message="Cannot delete the root folder", code=9009)
        if itemident.proj != self._proj_ident:
            # Must belong to this project
            raise ServerError(message="Cannot delete this item (does not belong to this project)", code=9010)
        if itemident not in self.identitems:
            raise ServerError(message="Item not found", code=9011)
        # get the item
        item = self.identitems[itemident]
        # get the items parent folder
        parentfolder = item.parentfolder
        if item.name in parentfolder.pages:
            del parentfolder.pages[item.name]
        if item.name in parentfolder.folders:
            del parentfolder.folders[item.name]
        parentfolder.change = uuid.uuid4().hex
        # del the item
        del self.identitems[itemident]
        self.clear_cache()


    def save_item(self, item, new_parent_ident=None):
        """Saves the page or folder - used to save an altered item, not to add a new one
           If new_parent_ident is not None, indicates the item has moved to a different folder
           returns the items new change uuid"""
        if item.page_type == 'Folder':
            return self.save_folder(item, new_parent_ident)
        else:
            return self.save_page(item, new_parent_ident)


    def save_page(self, item, new_parent_ident=None):
        """Saves the page - used to save an altered page, not to add a new one
           If new_parent_ident is not None, indicates the page has moved to a different folder
           Returns the new page.change uuid"""
        if item.page_type == 'Folder':
            raise ServerError(message="Invalid item, not a page.", code=9012)
        item_ident = item.ident
        if item_ident is None:
            raise ServerError(message="Unable to save page - no ident set", code=9013)
        if self._proj_ident != item_ident.proj:
            raise ServerError(message="Unable to save page - invalid ident", code=9014)
        if item_ident not in self.identitems:
            raise ServerError(message="This page ident does not exist", code=9015)
        old_parent = self.identitems[item_ident].parentfolder
        old_name = self.identitems[item_ident].name
        if new_parent_ident is not None:
            # So its a parent folder change
            if new_parent_ident.num is 0:
                # new parent is root
                new_parent = self.root
            else:
                new_parent = self.identitems[new_parent_ident]
            if new_parent == old_parent:
                new_parent_ident = None
        if (item.page_type == 'TemplatePage') or (item.page_type == 'SVG'):
            item.set_idents()
        # now set validator modules in page
        if item.page_type == 'TemplatePage':
            item.load_validator_scriptlinks()
        item.change = uuid.uuid4().hex
        if (old_name == item.name) and (new_parent_ident is None):
            # no folder change
            self.identitems[item_ident] = item
            self.clear_cache()
            return item.change
        if new_parent_ident is None:
            # so just a name change
            if item.name in old_parent.pages:
                raise ServerError(message="Sorry, a page with that name already exists", code=9016)
            if item.name in old_parent.folders:
                raise ServerError(message="Sorry, a folder with that name already exists", code=9017)
            if old_name in old_parent.pages:
                del old_parent.pages[old_name]
            old_parent.pages[item.name] = item_ident
            old_parent.change = uuid.uuid4().hex
            self.identitems[item_ident] = item
            self.clear_cache()
            return item.change
        # change of folder
        if item.name in new_parent.pages:
            raise ServerError(message="Sorry, a page with that name already exists", code=9018)
        if item.name in new_parent.folders:
            raise ServerError(message="Sorry, a folder with that name already exists", code=9019)
        if old_name in old_parent.pages:
            del old_parent.pages[old_name]
            old_parent.change = uuid.uuid4().hex
        new_parent.pages[item.name] = item_ident
        new_parent.change = uuid.uuid4().hex
        item.parentfolder = new_parent
        self.identitems[item_ident] = item
        self.clear_cache()
        return item.change


    def save_folder(self, item, new_parent_ident=None):
        """Saves the folder - used to save an altered folder, not to add a new one
           If new_parent_ident is not None, indicates the folder has moved to a different parent folder
           Returns the new folder.change uuid"""
        if item.page_type != 'Folder':
            raise ServerError(message="Invalid item, not a folder.", code=9020)
        item_ident = item.ident
        if item_ident is None:
            raise ServerError(message="Unable to save folder - no ident set", code=9021)
        if self._proj_ident != item_ident.proj:
            raise ServerError(message="Unable to save folder - invalid ident", code=9022)
        if item_ident.num == 0:
            if new_parent_ident:
                raise ServerError(message="Root folder cannot have new parent", code=9023)
            item.change = uuid.uuid4().hex
            self.root = item
            self.clear_cache()
            return item.change
        if item_ident not in self.identitems:
            raise ServerError(message="This folder ident does not exist", code=9024)
        old_parent = self.identitems[item_ident].parentfolder
        old_name = self.identitems[item_ident].name
        if new_parent_ident is not None:
            # So its a parent folder change
            if new_parent_ident.num is 0:
                # new parent is root
                new_parent = self.root
            else:
                new_parent = self.identitems[new_parent_ident]
            if new_parent == old_parent:
                new_parent_ident = None
        item.change = uuid.uuid4().hex
        if (old_name == item.name) and (new_parent_ident is None):
            # no parent folder change
            self.identitems[item_ident] = item
            self.clear_cache()
            return item.change
        if new_parent_ident is None:
            # so just a name change
            if item.name in old_parent.pages:
                raise ServerError(message="Sorry, a page with that name already exists", code=9025)
            if item.name in old_parent.folders:
                raise ServerError(message="Sorry, a folder with that name already exists", code=9026)
            if old_name in old_parent.folders:
                del old_parent.folders[old_name]
            old_parent.folders[item.name] = item_ident
            old_parent.change = uuid.uuid4().hex
            self.identitems[item_ident] = item
            self.clear_cache()
            return item.change
        # change of folder
        # A folder cannot be moved into a sub folder of itself

        folder_list = new_parent.parent_list()
        # folder list is a list of (name, identnumber) starting at root
        folder_ident_numbers = [ identnumber for name,identnumber in folder_list ]
        if item.ident.num in folder_ident_numbers:
            # item is a parent of new_parent
            raise ServerError(message="Sorry, a folder cannot be moved into a subfolder of itself.", code=9027)
        if item.name in new_parent.pages:
            raise ServerError(message="Sorry, a page with that name already exists", code=9028)
        if item.name in new_parent.folders:
            raise ServerError(message="Sorry, a folder with that name already exists", code=9029)
        if old_name in old_parent.folders:
            del old_parent.folders[old_name]
            old_parent.change = uuid.uuid4().hex
        new_parent.folders[item.name] = item_ident
        new_parent.change = uuid.uuid4().hex
        item.parentfolder = new_parent
        self.identitems[item_ident] = item
        self.clear_cache()
        return item.change



    def get_item(self, ident):
        """given an ident (Ident object or integer), return a
           folder or page from the database, if not found, return None.
           Note: the item is returned without copying and without sections imported"""
        if isinstance(ident, int):
            ident = skiboot.Ident(self._proj_ident, ident)
        elif ident.proj != self._proj_ident:
            return None
        if ident.num == 0:
            return self.root
        if ident not in self.identitems:
            return None
        return self.identitems[ident]


    def __iter__(self):
        "This iterator does not return the root folder"
        for ident in self.identitems:
            yield ident

    def __contains__(self, item):
        "Checks if this project contains folder, page or ident"
        if hasattr(item, 'ident'):
            ident = item.ident
        else:
            ident = skiboot.Ident.to_ident(item, self._proj_ident)
        if ident in self.identitems:
            return True
        if (ident.proj == self._proj_ident) and (ident.num is 0):
            return True
        return False

    def __len__(self):
        "This length does not include the root"
        return len(self.identitems)

    def __bool__(self):
        return True

    def set_special_page(self, label, target):
        "Sets a special page"
        if not label:
            raise ServerError(message="Sorry, a special page label must be given", code=9030)
        if not target:
            raise ServerError(message="Sorry, a label target must be given", code=9031)
        if isinstance(target, str) and ( '/' in target ):
                # item is a url
                item = target
        elif isinstance(target, str) and ( ',' in target ) and not (target.split(',')[1].isdigit()):
            if len(target.split(',')) == 2:
                # item points to a subproject label
                item = target
        else:
            item = skiboot.make_ident(target, self._proj_ident)
            if not item:
                raise ServerError(message="Sorry, the page target is not recognised", code=9032)
        self.special_pages[label] = item


    def delete_special_page(self, label):
        "Deletes a special page"
        if label in self.special_pages:
            del self.special_pages[label]

    def _system_page(self, label):
        """Returns the system page with the given label, if not found, returns None"""
        # label must be one of the system pages
        if label not in skiboot.sys_list():
            return
        if label not in self.special_pages:
            return
        target = self.special_pages[label]
        ident = skiboot.find_ident(target, proj_ident=self._proj_ident)
        if ident is None:
            return
        return ident.item()


    def labels(self):
        "Returns the special pages dictionary as a dictionary of labels with url's and tuples"
        labels_dict = {}
        for key, val in self.special_pages.items():
            if isinstance(val, str):
                labels_dict[key] = val
            else:
                labels_dict[key] = val.to_tuple()
        return labels_dict


    def label_value(self, key):
        "Returns the url or tuple associated with the label"
        val = self.special_pages.get(key)
        if val is None:
            return
        labels_dict = {}
        if isinstance(val, str):
            return val
        else:
            return val.to_tuple()


    def _redirect_to_url(self, url, environ, call_data, page_data, lang):
        "Return status, headers, page.data() of the redirector page, with fields set to url"
        if '/' not in url:
            raise ServerError(message="Invalid target url, must contain at least one /", code=9033)
        page = self._system_page('redirector')
        if (not page) or (page.page_type != "TemplatePage"):
            page_text = "<!DOCTYPE HTML>\n<html>\n<p>Page Redirect request. Please try: <a href=%s>%s</a></p>\n</html>" % (url, url)
            return '200 OK', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]
        # create an ErrorMessage with the url as the message
        err = ErrorMessage(message=html.escape(url))
        # import any sections
        page.import_sections()
        page.show_error(error_messages=[err])
        # update head and body parts
        if page_data:
            page.set_values(page_data)
        page.update(environ, call_data, lang)
        status, headers = page.get_status()
        return status, headers, page.data()



    def read_form_data(self, rawformdata, caller_page):
        """Reads raw form data from the environ and returns a dictionary with keys as skiboot.WidgField objects and values as
           the form values.  Where input fields have indexed names, the skiboot.WidgField object still
           has i set to empty string, but the value is given as a dictionary with indexes as keys"""
        # rawformdata is the data obtained from environ
        # form_data is a dictionary of data returned, without the caller ident
        # and after a set of checks
        if not rawformdata:
            return {}
        if not caller_page:
            return {}
        form_data = {}
        for field in rawformdata.keys():
            # get fields and values from the rawformdata and store them in form_data
            # with keys as skiboot.WidgField objects, and values as field values
            # in the case of indexed fields, the values are dictionaries
            if field == 'ident':
                continue
            if ':' not in field:
                # All widgfields have a : in them to separate widget name from field name
                raise ValidateError(message="Form data not accepted, (invalid field %s)" % (field,))
            widgfield = skiboot.make_widgfield(field)
            # get fields and values from the rawformdata and store them in form_data
            widget = caller_page.copy_widget_from_name(widgfield.s, widgfield.w)
            if widget is None:
                raise ValidateError(message="Form data not accepted, (unexpected field %s)" % (field,))
            if isinstance(rawformdata[field], list):
                # fieldvalue is a list of items
                fieldvalue = [ item.value.strip() for item in rawformdata[field] ]
            else:
                fieldvalue = rawformdata[field].value.strip()
            if widget.is_senddict(widgfield.f):
                # field sends a dictionary, must have an index appended to the name
                # this part removes the index from the field name, and creates a form value of a dictionary with the index as keys
                fieldindex = widgfield.i
                if not fieldindex:
                    raise ValidateError(message="Form data not accepted, (invalid dictionary field %s)" % (field,))
                widgfieldnoindex = widgfield._replace(i='')
                if widgfieldnoindex in form_data:
                    form_data[widgfieldnoindex][fieldindex] = fieldvalue
                else:
                    form_data[widgfieldnoindex] = {fieldindex:fieldvalue}
            else:
                if widgfield.i:
                    raise ValidateError(message="Form data not accepted, (unexpected dictionary field %s)" % (field,))
                form_data[widgfield] = fieldvalue
        return form_data


    def _url_not_found(self, environ, path, lang):
        "Used to return the url not found page"
        page = self._system_page("url_not_found")
        if not page:
            page_text = "<!DOCTYPE HTML>\n<html>\nERROR:UNKNOWN URL\n</html>"
            return '404 Not Found', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]
        if page.page_type == "TemplatePage":
            # create an ErrorMessage with the path as the message
            err = ErrorMessage(message=html.escape(path))
            # import any sections
            page.import_sections()
            page.show_error(error_messages=[err])
            # update head and body parts
            page.update(environ, {}, lang)
            status, headers = page.get_status()
            return '404 Not Found', headers, page.data()
        if page.page_type == "FilePage":
            page.update(environ, {}, lang)
            status, headers = page.get_status()
            return '404 Not Found', headers, page.data()
        # Either TemplatePage or FilePage - nothing else allowed
        page_text = "<!DOCTYPE HTML>\n<html>\nERROR:UNKNOWN URL\n</html>"
        return '404 Not Found', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]


    def respond(self, environ):
        "called from the project top script"
        # get cookies
        try:
            cookiemorsals = cookies.SimpleCookie(environ["HTTP_COOKIE"])
        except Exception:
            cookiemorsals = None
        if cookiemorsals:
            received_cookies = {item:m.value for item,m in cookiemorsals.items()}
        else:
            received_cookies = {}
        if 'language' in received_cookies:
            language = received_cookies["language"]
        else:
            if "HTTP_ACCEPT_LANGUAGE" in environ:
                language_list = environ["HTTP_ACCEPT_LANGUAGE"].split(',')
                language = language_list[0]
            else:
                language = self.default_language
        lang = (language, self.default_language)
        try:
            # The tuple s_h_data is the tuple to return, start with it as None
            s_h_data = None

            if 'PATH_INFO' in environ:
                path = environ['PATH_INFO'].lower()
            else:
                raise ServerError(message="Invalid path", code=9034)

            # the path must start with this root project url
            if (path.find(self.url) != 0) and (path + "/" != self.url):
                # path does not start with the root, so send URL NOT FOUND
                return self._url_not_found(environ, path, lang)

            # This is the root project, check if the call is for a page in any sub project
            for proj, projurl in self._subproject_paths.items():
                if (path.find(projurl) == 0) or (path + "/" == projurl):
                    # this url is within a sub project
                    subproj = self.subprojects[proj]
                    s_h_data = subproj.proj_respond(environ, projurl, path, lang, received_cookies)
                    break
            else:
                # the call is for a page in this root project
                s_h_data = self.proj_respond(environ, self.url, path, lang, received_cookies)

            if s_h_data is None:
                # No page to return has been found, 
                return self._url_not_found(environ, path, lang)

            return s_h_data

        except ServerError as e:
            page = self._system_page("server_error")
            if (not page) or (page.page_type != "TemplatePage"):
                # make a temp page
                text_start = "<!DOCTYPE HTML>\n<html>\n<p>SERVER ERROR</p>\n<p>Error code : %s</p>\n" % (e.code,)
                if e.message:
                    page_text = text_start + "<p>%s</p>\n</html>" % (html.escape(e.message),)
                else:
                    page_text = text_start + "</html>"
                return '500 Internal Server Error', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]
            # import any sections
            page.import_sections()
            # show message passed by the exception
            page.show_error([e.errormessage])
            # if ServerError code, set it into the widget
            if e.code:
                if e.section:
                    page_data = {(e.section, e.widget, 'code'):str(e.code)}
                elif e.widget:
                    page_data = {(e.widget, 'code'):str(e.code)}
                elif page.default_error_widget.s:
                    page_data = {(page.default_error_widget.s, page.default_error_widget.w, 'code'):str(e.code)}
                elif page.default_error_widget.w:
                    page_data = {(page.default_error_widget.w, 'code'):str(e.code)}
                else:
                    page_data = None
                if page_data:
                    page.set_values(page_data)
            # update head and body parts
            page.update(environ, {}, lang, e.ident_list)
            status, headers = page.get_status()
            # return page data
            return e.status, headers, page.data()


    def proj_respond(self, environ, projurl, path, lang, received_cookies):
        """projurl is the url of this project
           path is the url called
           Calls start call, and depending on the returned page, calls the project status_headers_data method"""

        # ident_data is a data string returned with the page ident, which consists of "project_pagenumber_identdata"
        # where project,pagenumber is the caller page ident

        caller_page = None
        ident_data = None

        try:
            # get the caller_page, from the ident field of submitted data
            # which could be None if no ident received
            rawformdata = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
            if rawformdata and ('ident' in rawformdata):
                # form data has been submitted - so get the ident field
                if not hasattr(rawformdata['ident'], 'value'):
                    raise ValidateError(message="Form data not accepted, caller page ident not recognised")
                else:
                    # rawformdata has 'ident' with attribute 'value'
                    # get the caller page ident, and the ident_data received from the 'ident' field

                   # Note: caller_page could belong to another project, so get it using ident.item() method
                   # which will query the right project

                    ident_parts = rawformdata['ident'].value.split('_', 2)
                    ident_items = len(ident_parts)
                    try:
                        if ident_items == 2:
                            caller_page = skiboot.Ident(ident_parts[0], int(ident_parts[1])).item()
                        elif ident_items == 3:
                            caller_page = skiboot.Ident(ident_parts[0], int(ident_parts[1])).item()
                            ident_data = ident_parts[2]
                    except Exception:
                        caller_page = None
                    if caller_page is None:
                       raise ValidateError(message="Form data not accepted, (received ident is not valid)")
                    if caller_page.page_type != 'TemplatePage':
                        raise ValidateError(message="Form data not accepted, (caller page ident is not a template page)")
        except ValidateError as e:
            page = self._system_page("validate_error")
            if (not page) or (page.page_type != "TemplatePage"):
                # make a temp page
                if e.message:
                    page_text = "<!DOCTYPE HTML>\n<html>\n<p>VALIDATION ERROR</p>\n<p>%s</p>\n</html>" % (html.escape(e.message),)
                else:
                    page_text = "<!DOCTYPE HTML>\n<html>\n<p>VALIDATION ERROR</p>\n</html>"
                return '400 Bad Request', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]
            # import any sections
            page.import_sections()
            # show message passed by the exception
            page.show_error([e.errormessage])
            # update head and body parts
            page.update(environ, {}, lang, e.ident_list)
            status, headers = page.get_status()
            # return page data
            return e.status, headers, page.data()

        # so caller_page could be either given, or could be None

        # get the called ident, could be None
        ident = self.page_ident_from_path(projurl, path)

        # now call the project start_call function
        try:
            if caller_page:
                caller_page_ident = caller_page.ident
            else:
                caller_page_ident = None
            # start_call could return a different page ident, or None
            pident, skicall = self.proj_start_call(environ,
                                                   path,
                                                   ident,
                                                   caller_page_ident,
                                                   received_cookies,
                                                   ident_data,
                                                   lang)
        except Exception:
            message = "Invalid exception in start_call function."
            if skiboot.get_debug():
                message += "\n"
                exc_type, exc_value, exc_traceback = sys.exc_info()
                str_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for item in str_list:
                    message += item
            raise ServerError(message, code=9035)

        if pident is None:
            # URL NOT FOUND and start_call does not divert
            return None

        # pident is the ident of the diverted page or a label or url string

        # get the page from pident
        if isinstance(pident, str):
            # either a label, or url
            if '/' in pident:
                # get redirector page
                return self._redirect_to_url(pident, environ, skicall.call_data, skicall.page_data, skicall.lang)
            else:
                # no '/' in pident so must be a label
                pident = skiboot.find_ident_or_url(pident, self._proj_ident)
                if not pident:
                    raise ServerError(message="Returned page ident from start_call not recognised", code=9036)
                if isinstance(pident, str):
                    # must be a url, get redirector page
                    return self._redirect_to_url(pident, environ, skicall.call_data, skicall.page_data, skicall.lang)

        # so pident must be an ident
        if not isinstance(pident, skiboot.Ident):
            raise ServerError(message="Invalid ident returned from start_call", code=9037)

        # pident is the ident returned from start_call, may be in a different project
        page = pident.item()
        if page is None:
            raise ServerError(message="Invalid ident returned from start_call", code=9038)
        if page.page_type == 'Folder':
            page = page.default_page
            if not page:
                raise ServerError(message="Invalid ident returned from start_call", code=9039)

        # read any submitted data from rawformdata, and place in form_data
        try:
            form_data = {}
            if rawformdata and (caller_page is not None) and (page.page_type == "RespondPage"):
                form_data = self.read_form_data(rawformdata, caller_page)

            # so form_data only available if
                # rawformdata has been submitted
                # and caller_page is known, so widgets can be extracted
                # and the destination is a RespondPage

                # otherwise form_data is empty (though rawformdata is retained)
        

            # dependent on wether the requested page is in this project or a sub project,
            # call status_headers_data() to find the final page to return to the client

            # ident_list retains list of idents called during a call to ensure no circulating calls
            ident_list = []
            # initially no errors, e_list is a list of errors to be shown
            e_list = []

            if page.ident.proj != self._proj_ident:
                # page returned from start_call is in another project
                subproj = self.subprojects.get(page.ident.proj)
                return subproj.status_headers_data(skicall, environ, received_cookies, rawformdata, caller_page, page, ident_list, e_list, form_data)
                
            # call status_headers_data to return status, headers and data to the top script
            return self.status_headers_data(skicall, environ, received_cookies, rawformdata, caller_page, page, ident_list, e_list, form_data)

        except ValidateError as e:
            page = self._system_page("validate_error")
            if (not page) or (page.page_type != "TemplatePage"):
                # make a temp page
                if e.message:
                    page_text = "<!DOCTYPE HTML>\n<html>\n<p>VALIDATION ERROR</p>\n<p>%s</p>\n</html>" % (html.escape(e.message),)
                else:
                    page_text = "<!DOCTYPE HTML>\n<html>\n<p>VALIDATION ERROR</p>\n</html>"
                return '400 Bad Request', [('content-type', 'text/html')], [page_text.encode('ascii', 'xmlcharrefreplace')]
            # import any sections
            page.import_sections()
            # show message passed by the exception
            page.show_error([e.errormessage])
            # update head and body parts
            page.update(environ, skicall.call_data, skicall.lang, e.ident_list)
            status, headers = page.get_status()
            # return page data
            return e.status, headers, page.data()


    def proj_start_call(self, environ, path, ident, caller_ident, received_cookies, ident_data, lang):
        """Calls the appropriate project start_call function
           ident is the ident of the page being called, could be None if not recognised
           Returns new called_ident, dictionaries 'call_data', 'page_data' and new tuple lang"""

        if not caller_ident:
            tuple_caller_ident = ()
        else:
            tuple_caller_ident = caller_ident.to_tuple()

        if ident is None:
            called_ident = None
        else:
            called_ident = ident.to_tuple()

        if (ident_data is not None) and _AN.search(ident_data):
            ident_data = None

        try:
            # create the SkiCall object
            skicall = SkiCall(environ = environ,
                              path = path,
                              project = self._proj_ident,
                              rootproject = self.rootproject,
                              caller_ident = tuple_caller_ident,
                              received_cookies = received_cookies,
                              ident_data = ident_data,
                              lang = lang,
                              proj_data = self.proj_data)

            # the skicall object is changed in place, with call_data and page_data
            # being set by the users own start_call function
            new_called_ident = self.start_call(called_ident, skicall)

            # convert returned tuple to an Ident object
            if isinstance(new_called_ident, int):
                new_called_ident = (self._proj_ident, new_called_ident)
            if isinstance(new_called_ident, tuple):
                new_called_ident = skiboot.make_ident(new_called_ident, self._proj_ident)
            # could be a label
        except ServerError as e:
            raise e
        except Exception:
            if skiboot.get_debug():
                exc_type, exc_value, exc_traceback = sys.exc_info()
                str_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                message = ''
                for item in str_list:
                    message += item
                raise ServerError(message, code=9040)
            raise ServerError("Error in start_call", code=9041)
        return new_called_ident, skicall


    def status_headers_data(self, skicall, environ, received_cookies, rawformdata, caller_page, page, ident_list, e_list, form_data):
        """calls responders until it can return status, headers, page.data()"""

        try:
            while page.page_type == 'RespondPage':
                ident = page.ident
                if page.responder is None:
                    raise ServerError(message="Respond page %s does not have any responder set" % (page.url,), code=9042)
                try: 
                    page = page.call_responder(skicall, form_data, caller_page, ident_list, rawformdata)
                    if isinstance(page, str):
                        # must be a url
                        skicall.call_data.clear()
                        skicall.page_data.clear()
                        # get redirector page
                        return self._redirect_to_url(page, environ, skicall.call_data, skicall.page_data, skicall.lang)
                except PageError as ex:
                    # a jump to a page has occurred, with a list of errors
                    page = ex.page
                    if isinstance(page, str):
                        # must be a url
                        skicall.call_data.clear()
                        skicall.page_data.clear()
                        # get redirector page
                        return self._redirect_to_url(page, environ, skicall.call_data, skicall.page_data, skicall.lang)
                    if page.ident in ident_list:
                        raise ServerError(message="Invalid Failure page: can cause circulating call", code=9043)
                    # show the list of errors on the page
                    e_list = ex.e_list
                except GoTo as ex:
                    if ex.clear_submitted:
                        form_data.clear()
                    if ex.clear_page_data:
                        skicall.page_data.clear()
                    if ex.clear_errors:
                        ex.e_list = []
                    target = skiboot.find_ident_or_url(ex.target, ex.proj_ident)
                    # target is either an Ident, a URL or None
                    if not target:
                        raise ServerError(message="GoTo exception target not recognised", code=9044)
                    if isinstance(target, skiboot.Ident):
                        if target == ident:
                            raise ServerError(message="GoTo exception page ident %s invalid, can cause circulating call" % (target,), code=9045)
                        if target in ident_list:
                            raise ServerError(message="GoTo exception page ident %s invalid, can cause circulating call" % (target,), code=9046)
                        page = target.item()
                        if not page:
                            raise ServerError(message="GoTo exception page ident %s not recognised" % (target,), code=9047)
                        if page.page_type == 'Folder':
                            raise ServerError(message="GoTo exception page ident %s is a Folder, must be a page." % (target,), code=9048)
                    else:
                        # target is a URL
                        skicall.call_data.clear()
                        return self._redirect_to_url(target, environ, skicall.call_data, skicall.page_data, skicall.lang)
                    
                    # A divert to a fail page may lead to a GoTo exception which can therefore
                    # have an e_list
                    # show the list of errors on the page
                    e_list = ex.e_list

                # it is possible that a jump to a page in another project has been made
                if page.ident.proj != self._proj_ident:
                    subproj = skiboot.getproject(proj_ident=page.ident.proj)
                    return subproj.status_headers_data(skicall, environ, received_cookies, rawformdata, caller_page, page, ident_list, e_list, form_data)
                
        except (ServerError, ValidateError) as e:
            e.ident_list = ident_list
            raise e

        # the page to be returned to the client is now 'page'
        # and 'e_list' is a list of errors to be shown on it

        # call the user function end_call
        try:
            skicall.project = self._proj_ident
            skicall.proj_data = self.proj_data
            skicall.rootproject = self.rootproject
            try:
                session_string = self.end_call(page.ident.to_tuple(), page.page_type, skicall)
                if session_string:
                    # set cookie in target_page
                    page.session_cookie = "Set-Cookie", "%s=%s; Path=%s" % (skicall.project, session_string, skiboot.root_project().url)
            except FailPage as e:
                page.show_error([e.errormessage])
            finally:
                if skicall._lang_cookie:
                    page.language_cookie = skicall._lang_cookie
        except GoTo as e:
            raise ServerError("Invalid GoTo exception in end_call", code=9049)
        except Exception:
            message = "Invalid exception in end_call function."
            if skiboot.get_debug():
                message += "\n"
                exc_type, exc_value, exc_traceback = sys.exc_info()
                str_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for item in str_list:
                    message += item
            raise ServerError(message, code=9050)

        # import any sections
        page.import_sections(skicall.page_data)
        if e_list:
            # show the list of errors on the page
            page.show_error(e_list)
        # now set the widget fields
        if skicall.page_data:
            page.set_values(skicall.page_data)
        page.update(environ, skicall.call_data, skicall.lang, ident_list)
        status, headers = page.get_status()
        return status, headers, page.data()


    def page_ident_from_path(self, projurl, path):
        """Tests if ident exists in the cache, return it, if not, call self.root.page_ident_from_path
           and cach the result, then return the ident. If no ident found, or if ident within a restricted folder, return None."""
        if path in self._paths:
            return self._paths[path]
        ident = None
        strip_path = path.strip("/")
        if not strip_path:
            pathlist = []
        else:
            pathlist = strip_path.split("/")
        strip_projurl = projurl.strip("/")
        # The projurl must be removed from the pathlist before the call to self.root.page_ident_from_path()
        if (not strip_projurl):
            # no projurl to remove
            ident = self.root.page_ident_from_path(self.identitems, pathlist)
        else:
            # strip_projurl may be something like "lib", remove the projurl from the pathlist
            projurl_list = strip_projurl.split("/")
            for item in projurl_list:
                if not pathlist:
                    # invalid call, the pathlist must start with the projurl
                    return
                if item == pathlist[0]:
                    pathlist.pop(0)
                else:
                    # invalid call, the pathlist must start with the projurl
                    return
            ident = self.root.page_ident_from_path(self.identitems, pathlist)
        if ident is not None:
            self._paths[path] = ident
        return ident


    @property
    def proj_ident(self):
        return self._proj_ident

    @property
    def subproject_paths(self):
        "property getter to return an ordered dictionary of sub project {ident:path,...}"
        if not self.rootproject:
            # sub project do not themselves contain further sub projects
            return collections.OrderedDict()
        return self._subproject_paths.copy()


    def list_of_subproject_idents(self):
        "Returns a list of subproject idents"
        return [i for i in self.subproject_paths]

    def add_project(self, proj, url=None):
        """Add a project to self, returns the url
           proj is the sub project application.
           This adds a reference to the project to the subproject_paths, returns the sub project path"""
        if not self.rootproject:
           raise ValidateError(message="Cannot add to a sub project")
        proj_id = proj.proj_ident

        # get a copy of the {proj_id:url} subproject_paths dictionary, and this projects url
        sub_paths = self._subproject_paths.copy()

        if (proj_id == self._proj_ident) or (proj_id in sub_paths):
            raise ValidateError(message="Project already exits")

        this_url = self.url

        if url is None:
            url = proj.url.strip("/").lower()
            if not url:
                url = proj_id.lower()
        else:
            url=url.strip("/").lower()
            if not url:
                raise ValidateError(message="Invalid URL passed to add_project, it must be a path longer than the root application path")
        url = "/" + url + "/"
        # Ensure url starts with this project url
        if not url.startswith(this_url):
            raise ValidateError(message="Invalid URL passed to add_project, it must be a path longer than the root application path")
        # add this ident and url to subproject_paths
        sub_paths[proj_id] = url
        # save new subproject_paths dictionary
        self._subproject_paths = collections.OrderedDict(sorted(sub_paths.items(), key=lambda t: len(t[1].strip("/").split("/")), reverse=True))
        # add the subproject to this project
        proj.rootproject = False
        proj.url = url
        proj._subproject_paths = collections.OrderedDict()
        proj.subprojects = {}
        self.subprojects[proj_id] = proj
        return url


    @property
    def root_ident(self):
        'provides a root_ident attribute'
        return skiboot.Ident(self._proj_ident, 0)

    def next_ident(self):
        "Returns next Ident available by incrementing the maximum existing ident number"
        return skiboot.Ident(self._proj_ident, self.max_ident_num+1)

    def __repr__(self):
        return "WSGIApplication(\'%s\', \'%s\', \'%s\', start_call, submit_data, end_call, \'%s\')" % (self.proj_ident, self.projectfiles, self.proj_data, self.url)


class SkiCall(object):

    def __init__(self, environ, path, project, rootproject, caller_ident, received_cookies, ident_data, lang, proj_data):

        self.environ = environ
        self.path = path
        self.project = project
        self.rootproject = rootproject
        self.caller_ident = caller_ident
        self.received_cookies = received_cookies
        self.ident_data = ident_data
        self._lang = lang
        self._lang_cookie = None
        self.proj_data = proj_data

        self._projectfiles = skiboot.projectfiles(project)

        self.ident_list = []
        self.submit_list = []
        self.submit_dict = {}
        self.call_data = {}
        self.page_data = {}


    @property
    def projectfiles(self):
        "Returns the projectfiles string"
        return self._projectfiles

    @property
    def lang(self):
        "Returns the lang tuple"
        return self._lang

    def get_language(self):
        "Returns the language string"
        return self._lang[0]

    def set_language(self, language):
        "Sets the language string and creates a language cookie with a persistance of 30 days"
        if language:
            self._lang = (language, self._lang[1])
            self._lang_cookie = "Set-Cookie", "language=%s; Path=%s; Max-Age=2592000" % (language_string, skiboot.root_project().url)

    language = property(get_language, set_language)

    @property
    def accesstextblocks(self):
        "Returns the project instance of the AccessTextBlocks class"
        this_project = skiboot.getproject(proj_ident=self.project)
        return this_project.textblocks

    def textblock(self, textref, project=None):
        """This method returns the textblock text, given a textblock reference string,
           If project is not given assumes this project, if given, project must exist as either the root,
           or a sub project of the root.
           If no textblock is found, returns None."""
        if project is None:
            project = self.project
        proj = skiboot.getproject(project)
        if proj is None:
            return
        return proj.textblocks.get_text(textref, self.lang)

    def label_value(self, label, project=None):
        """Given a label, returns the associated ident or URL
           If project is not given assumes this project, if given, project must exist as either the root,
           or a sub project of the root.
           If no label is found, returns None."""
        if project is None:
            project = self.project
        proj = skiboot.getproject(project)
        if proj is None:
            return
        return proj.label_value(label)


    def projectpaths(self):
        """Returns a dictionary of project name : project path

           This method returns a dictionary of project names as keys with the project paths as values."""
        all_projects = skiboot.project_register()
        return {proj_ident:proj.url for proj_ident, proj in all_projects.items()}


