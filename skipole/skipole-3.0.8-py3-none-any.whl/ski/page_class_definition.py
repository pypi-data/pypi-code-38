


"""
This module defines the page objects
"""


import os, mimetypes, copy, collections, json, re, uuid, pprint
from string import Template
from urllib.parse import quote

from . import skiboot
from .tag import Part, ClosedPart, TextBlock, Section
from .widgets import links
from .excepts import ValidateError, ServerError, SkiError

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')


class ParentPage(object):

    def __init__(self, name="", brief = "New Page"):
        """Initiates a ParentPage instance

        name: a url friendly page name
        """
        # self._parentfolder_ident is set when a page is added to a folder.
        self._parentfolder_ident = None
        if name:
            self._name = name.lower()
        else:
            self._name = ""
        self.ident = None
        self.status = '200 OK'
        self.headers = [('content-type', 'text/html')]
        self.brief = brief
        # the change is a uuid which alters whenever the page changes
        self.change = uuid.uuid4().hex
        self.ident_data = ''
        # Set by end_call
        self.session_cookie = ()
        self.language_cookie = ()

    def get_name(self):
        "The page name"
        return self._name

    def set_name(self, name):
        "Ensure name is lower case"
        self._name = name.lower()

    name = property(get_name, set_name)

    @property
    def page_type(self):
        return self.__class__.__name__

    @property
    def ident_data_string(self):
        if not self.ident:
            return
        if self.ident_data:
            return str(self.ident) + '_' + self.ident_data
        return str(self.ident)

    @property
    def proj_ident(self):
        return self.ident.proj

    @property
    def project(self):
        if self.ident:
            return skiboot.getproject(proj_ident=self.ident.proj) 

    def copy(self, name, brief):
        "Returns a deepcopy of this page, with new name and brief, parentfolder and ident are None"
        copy_page = copy.deepcopy(self.project.get_item(self.ident))
        copy_page._parentfolder_ident = None
        copy_page.ident = None
        copy_page.name = name
        copy_page.brief = brief
        copy_page.change = uuid.uuid4().hex
        return copy_page

    def root(self):
        "Returns the page root folder"
        if self.ident():
            proj = self.project()
            if proj is None:
                return
            return proj.root


    def get_parentfolder(self):
        "Uncopied parent folder"
        if self._parentfolder_ident is None:
            return None
        return skiboot.get_item(self._parentfolder_ident)

    def set_parentfolder(self, parentfolder):
        "Warning, this does not set this page into the parents pages dictionary, it just sets this parentfolder attribute"
        if parentfolder is None:
            self._parentfolder_ident = None
        else:
            self._parentfolder_ident = parentfolder.ident

    parentfolder = property(get_parentfolder, set_parentfolder)

    def get_folder(self):
        "folder is an alias of parentfolder"
        return self.get_parentfolder()

    def set_folder(self, parentfolder):
        "folder is an alias of parentfolder"
        self.set_parentfolder(parentfolder)

    folder = property(get_folder, set_folder)

    @property
    def parentfolder_ident(self):
        "Returns the parentfolder ident"
        return self._parentfolder_ident

    @property
    def url(self):
        if self._parentfolder_ident is None:
            return ""
        return self._parentfolder_ident.url() + self.name


    def parent_list(self):
        "returns a list of (name, identnumber) starting at root"
        p_list = self.parentfolder.parent_list()
        p_list.append((self.name, self.ident.num))
        return p_list


    @property
    def restricted(self):
        "returns restricted status of parentfolder"
        parentfolder = self.parentfolder
        if parentfolder is None:
            return True
        return parentfolder.restricted

    def update(self, environ, call_data, lang, ident_list=[]):
        "override"
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def show_error(self, error_messages=None):
        """override"""
        pass

    def set_values(self, page_data):
        """Checks for special page template values"""
        if ('status' in page_data):
            if page_data['status']:
                self.status = page_data['status']
            del page_data['status']
        if ('headers' in page_data):
            if page_data['headers']:
                self.headers = page_data['headers']
            del page_data['headers']
        if ('ident_data' in page_data):
            if page_data['ident_data']:
                ident_data = page_data['ident_data']
                if not isinstance(ident_data, str):
                    ident_data = str(ident_data)
                if _AN.search(ident_data):
                    raise ServerError("ERROR - Invalid ident_data in page_data")
                # set ident_data in page
                self.ident_data = ident_data
            del page_data['ident_data']

    def import_sections(self, page_data=None):
        "Only used by Template and SVG, everything else just returns"
        return


    def get_status(self):
        "Returns (status, headers)"
        return self.status, self.headers

    def __eq__(self, other):
        return self.ident == other.ident

    def __ne__(self, other):
        return self.ident != other.ident

    def __bool__(self):
        return True


class TemplatePageAndSVG(ParentPage):
    "Acts as parent to template pages and svg pages"


    def __init__(self, name="", brief = "New Page"):
        """Initiates a TemplatePageAndSVG instance
        """
        ParentPage.__init__(self, name=name, brief=brief)
        # self.widgets is a widget name -> widget dictionary
        self.widgets = {}
        # self.section_places is a page section name -> SectionPlaceHolder dictionary
        self.section_places = {}
        # dictionary of sections, page section name -> section
        # this is filled in when the sections are imported
        self.sections = {}


    def set_values(self, page_data):
        """Sets the widget fields to the given values.
           page_data is either a dictionary of
           {(pagesectionname,widgetname,fieldname):value, ..}
           or a dictionary of
           {'pagesectionname-widgetname:fieldname':value, ..}
           or a dictionary of
          {WidgField_object:value, ..}
           or a dictionary of
          {pagesectionname:value, ..}

           NOTE : currently untested, but this should work with index as well
           so if the widgfield is of format (pagesectionname,widgetname,fieldname,index)
           or 'pagesectionname-widgetname:fieldname-index' then the single indexed field value
           should be updated
           """
        ParentPage.set_values(self, page_data)
        for widgfield, value in page_data.items():
            # could be the special case of setting a section show or class value
            if self._check_section_parameters(widgfield, value):
                continue
            widget, fieldname = self.widget_from_field(widgfield)
            if (widget is not None) and fieldname:
                widget.set_value(fieldname, value)


    def _check_section_parameters(self, widgfield, value):
        """Checks special case of ('pagesectionname','show'),
                               or ('pagesectionname','hide')
                               or ('pagesectionname','section_class')"""
        if isinstance(widgfield, str) and (':' in widgfield):
            widglist = widgfield.split(':')
            if len(widglist) != 2:
                return False
            sectionname, field = widglist
        elif (isinstance(widgfield, list) or isinstance(widgfield, tuple)) and (len(widgfield) == 2):
            sectionname, field = widgfield
        else:
            return False
        if sectionname not in self.sections:
            return False
        if (field == 'show') and ((value is True) or (value is False)):
            self.sections[sectionname].show = value
            return True
        if field == 'section_class':
            self.sections[sectionname].set_class(value)
            return True
        if field == 'hide':
            self.sections[sectionname].set_hide(value)
            return True
        return False


    def widget_from_field(self, widgfield):
        """Return the (widget, fieldname) given a widgfield, which is either a string of
         pagesectionname-widgetname:fieldname or a list/tuple or cfg.WidgField object, if widget not found in the page,
         (None, fieldname) will be returned.
        If widget is found, but the fieldname is not in the widget, return (widget, None)
        The widget returned is the actual widget instance in the page, and fieldname is the widgets field name
        Please note - if the given widgfield has an index, fieldname will be 'fieldname-index'"""
        if not widgfield:
            raise ValidateError(message = "Invalid field given to page.widget_from_field method")
        widg_field = skiboot.make_widgfield(widgfield)
        # widg_field is now a WidgField object with s, w, f and i attributes
        if (not widg_field.w) or (not widg_field.f):
            raise ValidateError(message = "Field %s not recognised" % (widgfield,))
        widget = self.widget_from_name(widg_field.s, widg_field.w)
        if widg_field.f == 'show_error':
            return widget, 'show_error'
        # check is the fieldname in the widget
        if widget is not None:
            if not widget.is_fieldname_in_widget(widg_field.f):
                return widget, None
        if widg_field.i:
            fieldname = widg_field.f + '-' + widg_field.i
        else:
            fieldname = widg_field.f
        return widget, fieldname

    def widget_from_name(self, section_name, widgetname):
        """Return the widget given a widgetname, if widget not found in the page, None will be returned
           This should only be called after sections have been imported and returns the actual widget in the page"""
        if not section_name:
            # widget is not in a section, should be local to this page
            return self.widgets.get(widgetname)
        if section_name not in self.sections:
            return None
        sectionpart = self.sections[section_name]
        return sectionpart.widgets.get(widgetname)


    def copy_widget_from_name(self, section_name, widgetname):
        """Return the widget given a widgetname, if widget not found in the page or section, None will be returned
           This can be called before or after sections have been imported and returns a copy of the widget"""
        if not section_name:
            # widget is not in a section, should be local to this page
            widget = self.widgets.get(widgetname)
        elif section_name in self.sections:
            section = self.sections[section_name]
            widget = section.widgets.get(widgetname)
        elif section_name in self.section_places:
            # self.section_places is a page section name -> SectionPlaceHolder dictionary
            sectionplaceholder = self.section_places.get(section_name)
            if not sectionplaceholder:
                return
            section = sectionplaceholder.get_section()
            widget = section.widgets.get(widgetname)
        elif "_" in section_name:
            result = self.widget_from_multiplier(section_name, widgetname)
            if result:
                sectionplaceholder,widget = result
            else:
                widget = None
        else:
            return
        if widget is None:
            return
        return copy.deepcopy(widget)


    def widget_from_multiplier(self, section_name, widgetname):
        """Return (sectionplaceholder, widget) if section_name is a multiplied section, such as name_3, return None on failure"""
        if "_" not in section_name:
            return
        sname, snumber = section_name.rsplit('_', 1)
        try:
            snumber = int(snumber)
        except Exception:
            return
        # 0 is not allowed, snumber must be greater than zero
        if snumber<1:
            return
        sectionplaceholder = self.section_places.get(sname)
        if not sectionplaceholder:
            return
        section = sectionplaceholder.get_section()
        return sectionplaceholder, section.widgets.get(widgetname)


    def append_scriptlink(self, label):
        """Used to append a scriptlink to head, overridden in class Page"""
        pass

    def import_sections(self, page_data=None):
        "Imports the project sections into the page"
        self.sections = {}
        for placename, placeholder in self.section_places.items():
            # get top part of placeholder location
            pagepart = placeholder.pagepart
            if pagepart == 'head':
                toppart = self.head
            elif pagepart == 'body':
                toppart = self.body
            elif pagepart == 'svg':
                toppart = self.svg
            else:
                raise ServerError(message = 'Invalid section placeholder in page %s' % (self.ident,))

            if page_data and (placename,'multiplier') in page_data:
                try:
                    multiplier = int(page_data[placename,'multiplier'])
                except Exception:
                    pass
                else:
                    if multiplier > 0:
                        placeholder.multiplier = multiplier
            if placeholder.multiplier > 1:
                for m in range(placeholder.multiplier):
                    self._import_multiplied_section(m, placeholder, toppart, page_data)
                continue
            section_name = placeholder.section_name
            sectionpart = self.project.section(section_name)
            # sectionpart is a tag.Section
            if isinstance(sectionpart, Section):
                # gives sectionpart and subparts an ident of page_ident_name_locationnumbers
                # and sets sectionpart into self.sections
                sectionpart.widgets = {}
                sectionpart.section_places = {}
                sectionpart.set_idents(str(self.ident) + '_' + placename, sectionpart.widgets, sectionpart.section_places, embedded=(section_name,'',None))
                # If no id placed in the top tag, inserts the section placename
                if not sectionpart.has_attrib('id'):
                    sectionpart.insert_id(id_string=placename)
                self.sections[placename] = sectionpart
            else:
                continue
            # Set section widgets field displaynames
            for widget in sectionpart.widgets.values():
                # Note - this is called on named widgets only
                widget.set_placename(section_name, placename)
            # insert sectionpart at the point where the placeholder is
            toppart.set_location_value(placeholder.ident_list, sectionpart)
            # add section scriptlinks
            if self.page_type == 'TemplatePage':
                if sectionpart.validator_scriptlinks:
                    for link_label in sectionpart.validator_scriptlinks:
                        self.append_scriptlink(link_label)
                for widget in sectionpart.widgets.values():
                    # get 'ski_modulename'
                    link_label = "ski_" + widget.__class__.__module__.split(".")[-1]
                    # add a link in the page head to the widget module javascript file
                    self.append_scriptlink(link_label)


    def _import_multiplied_section(self, m, placeholder, toppart, page_data):
        "If a placeholder has a multiplier, import its section multiple times inside a div"
        placename = placeholder.placename + "_" + str(m)
        section_name = placeholder.section_name
        sectionpart = self.project.section(section_name)
        # sectionpart is a tag.Section
        if isinstance(sectionpart, Section):
            # gives sectionpart and subparts an ident of page_ident_name_locationnumbers
            # and sets sectionpart into self.sections
            sectionpart.widgets = {}
            sectionpart.section_places = {}
            sectionpart.set_idents(str(self.ident) + '_' + placename, sectionpart.widgets, sectionpart.section_places, embedded=(section_name,'',None))
            # If no id placed in the top tag, inserts the section placename
            if not sectionpart.has_attrib('id'):
                sectionpart.insert_id(id_string=placename)
            self.sections[placename] = sectionpart
        else:
            return
        # Set section widgets field displaynames
        for widget in sectionpart.widgets.values():
            # Note - this is called on named widgets only
            widget.set_placename(section_name, placename)
        # now the sectionpart has to be set within a div which is set at the placeholder location
        if m == 0:
            topdiv = Part(tag_name=placeholder.mtag)
            if page_data:
                if (placeholder.placename,'show') in page_data:
                    topdiv.show = bool(page_data[placeholder.placename,'show'])
                if (placeholder.placename,'section_class') in page_data:
                    topdiv.set_class(page_data[placeholder.placename,'section_class'])
                if (placeholder.placename,'multiplier_tag') in page_data:
                    topdiv.tag_name = page_data[placeholder.placename,'multiplier_tag']
                if self.page_type == 'TemplatePage':
                    # hide not relevant to svg
                    if (placeholder.placename,'hide') in page_data:
                        topdiv.set_hide(bool(page_data[placeholder.placename,'hide']))
            topdiv.insert_id(id_string=placeholder.placename)
            topdiv[0] = sectionpart
            toppart.set_location_value(placeholder.ident_list, topdiv)
        else:
            location = placeholder.ident_list[:]
            location.append(m)
            toppart.insert_location_value(location, sectionpart)
        # add section scriptlinks
        if self.page_type == 'TemplatePage':
            if sectionpart.validator_scriptlinks:
                for link_label in sectionpart.validator_scriptlinks:
                    self.append_scriptlink(link_label)
            for widget in sectionpart.widgets.values():
                # get 'ski_modulename'
                link_label = "ski_" + widget.__class__.__module__.split(".")[-1]
                # add a link in the page head to the widget module javascript file
                self.append_scriptlink(link_label)


class TemplatePage(TemplatePageAndSVG):
    """A template page object
    """

    def __init__(self, name="",
                       brief = "New Page",
                       show_backcol=False,
                       backcol="#FFFFFF",
                       last_scroll=True,
                       default_error_widget=None,
                       lang=None,
                       interval = 0,
                       interval_target=None):
        """Initiates a Page instance

        name: a url friendly page name
        brief: description of the page
        show_backcol: True if colour can be placed in the html tag
        backcol: The colour to place in the html tag
        last_scroll: True if the page is to remember its last scroll position
        default_error_widget: widget name to display errors, if no other widget specified in the error call
        lang: language string to place in the html tag
        interval: Time interval in integer seconds for repeated call for JSON update, 0 if not used.
        interval_target: ident or label (not URL) to call for the JSON update 
        """

        TemplatePageAndSVG.__init__(self, name=name, brief=brief)
        # set up page head
        self.head = Part(tag_name="head")
        self.head.brief = "The head section of the page"
        # Set up the page body
        self.body = Part(tag_name="body")
        self.body.brief = "The body section of the page"

        # html lang setting
        if lang is None:
            self.lang = skiboot.default_language()
        else:
            self.lang = lang

        # ERROR MESSAGES
        # This widget is the default widget where errors are displayed, if no other error location is specified
        if default_error_widget is None:
            self._default_error_widget = skiboot.WidgField(s='', w="top_error", f='', i='')
        else:
            self.default_error_widget = default_error_widget
        # flag if any error present
        self.page_in_error = False
        # store errors as they arrive
        # self.stored_errors will be a dictionary with key widgetname (of the widget to show the error)
        # and value being the message to be displayed by the widget
        self.stored_errors = {}

        self.show_backcol = show_backcol
        self.backcol = backcol

        # A list of appended script links in head
        self._headlinks = []

        # Used to hold javascript created at run time
        self._js = ''

        # A javscript string for each widgfield
        self._scriptcontents = ''

        # last scroll is True if the page is to be restored to the last scrolled position
        self.last_scroll = last_scroll

        # if requesting a json target to be called at regular intervals,
        # self.interval is the time in seconds, and self.interval_target
        # is the target url
         
        self.interval = interval
        if interval_target:
            self.interval_target = interval_target
        else:
            self.interval_target = None

        # self.validator_scriptlinks is a list of validator module ski_name's
        # calculated when the page is saved, and used 
        # to add links to the validator js modules in the page head
        self._validator_scriptlinks = []

        # These will be added to the page javascript within the jquery $(document).ready(function() {
        self._add_storage = ''
        self._add_jscript = ''

    @property
    def validator_scriptlinks(self):
        return self._validator_scriptlinks

    def load_validator_scriptlinks(self):
        "Called when page saved to database"
        self._validator_scriptlinks = []
        val_modules = []
        for widget in self.widgets.values():
            for field in widget.fields.values():
                val_list = field.val_list
                for val in val_list:
                    mod_name = val.__class__.__module__.split(".")[-1]
                    if mod_name not in val_modules:
                        val_modules.append(mod_name)
        for mod_name in val_modules:
            link_label = 'ski_' + mod_name
            if link_label not in self._validator_scriptlinks:
                self._validator_scriptlinks.append(link_label)

    def import_sections(self, page_data=None):
        "Imports javascript modules used by widgets and validators"
        if self._validator_scriptlinks:
            for link_label in self._validator_scriptlinks:
                        self.append_scriptlink(link_label)
        for widget in self.widgets.values():
            # get 'ski_modulename'
            link_label = "ski_" + widget.__class__.__module__.split(".")[-1]
            # add a link in the page head to the widget module javascript file
            self.append_scriptlink(link_label)
        # import sections using parent method
        TemplatePageAndSVG.import_sections(self, page_data)



    def location_item(self, location):
        "Returns the part or widget at location"
        location_string, container_number, location_list = location
        if not location_string:
            return
        if container_number is None:
            # Not in a widget
            if location_string == 'body':
                if not location_list:
                    return self.body
                return self.body.get_location_value(location_list)
            elif location_string == 'head':
                if not location_list:
                    return self.head
                return self.head.get_location_value(location_list)
            # not found
            return
        # location string must be a widget name
        # so part is within a widget container within the page
        if location_string not in self.widgets:
            return
        widget = self.widgets.get(location_string)
        if widget is None:
            return
        if widget.can_contain():
            if not location_list:
                # return the container
                return widget.container_part(container_number)
            else:
                return widget.get_from_container(container_number, location_list)
        # part not found
        return

    def set_default_error_widget(self, errorwidget):
        "Widget only, no field information"
        self._default_error_widget = skiboot.make_widgfield(errorwidget, widgetonly=True)

    def get_default_error_widget(self):
        return self._default_error_widget

    default_error_widget = property(get_default_error_widget, set_default_error_widget)

    def append_scriptlink(self, label):
        """Used to append a scriptlink to head"""
        if label not in self._headlinks:
            self._headlinks.append(label)
            # create a scriptlink
            scriptlink = Part(tag_name = "script", attribs={"src":"{" + label + "}"}, brief='script link to %s' % (label,))
            self.head.append(scriptlink)

    def add_javascript(self, contents):
        "Adds contents to self._scriptcontents"
        self._scriptcontents += contents


    def make_js(self, ident_list, environ, call_data, lang):
        "Auto generates the javascript for this page, sets into self._js, called after head and body updates"
        # for each part in the page body, get its associated javascript, and add to scriptcontents
        # send self, plus call arguments so part.make_js has all data necessary
        self.body.make_js(self, ident_list, environ, call_data, lang)
        # The start of the script is created in the .data function
        scriptmiddle = """
// Widget functions
$(document).ready(function(){
"""
        if self._add_storage:
            scriptmiddle += self._add_storage
        scriptend = self._add_jscript
        if self.last_scroll:
            # restore to last store position
            scriptend += """
  SKIPOLE.restorepagepos();
"""
        # and if a regular refresh is required
        if self.interval:
            interval = self.interval * 1000
            intervalurl = ''
            intervalurl = skiboot.get_url(self.interval_target, self.proj_ident)
            if intervalurl:
                intervalurl = quote(intervalurl, safe='/:?&=')
                scriptend += """
  setInterval( SKIPOLE.refreshjson, %s, "%s");
""" % (interval, intervalurl)
        # and set an event to store window position on unload
        scriptend += """
  if(typeof(Storage) !== "undefined") {
    $(window).on('unload', function(){
      // on unloading, store the x and y position of the window
      sessionStorage.setItem('%s_y', $(window).scrollTop().toString());
      sessionStorage.setItem('%s_x', $(window).scrollLeft().toString());
    });
  }
});
""" % (self.ident, self.ident)
        self._js = scriptmiddle + self._scriptcontents + scriptend


    def update(self, environ, call_data, lang, ident_list=[]):
        "Updates page and body parts, lang is a tuple of (language, default_language)"
        # show all errors on the page
        self._show_errors_on_update()
        self.body.update(self, ident_list, environ, call_data, lang, str(self.ident)+"_body")
        # update page head parts (done last as previous updates may change css)
        self.head.update(self, ident_list, environ, call_data, lang, str(self.ident)+"_head")
        # create javascript for widgets, this is set into self._js and appended
        # to self.head in the data function
        self.make_js(ident_list, environ, call_data, lang)
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)


    def set_idents(self):
        """Each widget adds its ident, to itself, and to the self.widgets dictionary
           Each sectionplaceholder adds its ident, to itself, and to the self.section_places dictionary
           This is called when the page is created and added to a folder, it is also
           called when an existing page is edited, and the page saved"""
        self.widgets = {}
        self.section_places = {}
        self.body.set_idents(str(self.ident)+"_body", self.widgets, self.section_places)
        self.head.set_idents(str(self.ident)+"_head", self.widgets, self.section_places)


    def validate(self, widgfield, value, environ, lang, form_data, call_data, page_data):
        """Given a widgfield, its value and other parameters, call its widget validate function
           which returns (value, error_list)"""
        if not widgfield:
            raise ValidateError(message = "Invalid widget-field, unable to validate")
        widg_field = skiboot.make_widgfield(widgfield)

        # widg_field is now a WidgField object with s, w, f and i attributes
        if (not widg_field.w) or (not widg_field.f):
            raise ValidateError(message = "Field %s not recognised" % (widgfield,))

        # Find the widget in this page, to call its validate function
        widget = None

        if widg_field.s:
            # self.section_places is a page section name -> SectionPlaceHolder dictionary
            sectionplaceholder = self.section_places.get(widg_field.s)
            if sectionplaceholder:
                sectionpart = sectionplaceholder.get_section()
                widget = sectionpart.widgets.get(widg_field.w)
            elif "_" in widg_field.s:
                result = self.widget_from_multiplier(widg_field.s, widg_field.w)
                if result:
                    sectionplaceholder, widget = result                
        else:
            # widget is not in a section, should be local to this page
            widget = self.widgets.get(widg_field.w)

        if widget is None:
            raise ValidateError(message = "Widget %s not found in page %s" % (widg_field.w, self.ident))

        # check is the fieldname in the widget
        if not widget.is_fieldname_in_widget(widg_field.f):
            raise ValidateError(message = "Field %s not found in widget %s, page %s" % (widg_field.f, widg_field.w, self.ident))

        # validate
        newvalue, error_list = widget.validate(widg_field, value, environ, lang, form_data, call_data, self.ident)

        # errors in same section as the errored widget need s value changing
        if widg_field.s:
            for error in error_list:
                if error.section == sectionplaceholder.section_name:
                    error.section = widg_field.s

        return newvalue, error_list


    def show_error(self, error_messages=[]):
        """Stores the errors to display on the page in dictionary self.stored_errors.
           These are subsequently set on the widgets during the page update by _show_errors_on_update().
           Any fields which are just to be flagged as errored, via the widgets mark_field_in_error are set here.
           error_messages is a list of ErrorMessage instances (class defined in excepts)"""
        # an ErrorMessage has attributes message,
        #                                section,
        #                                widget,
        self.page_in_error = True
        for e in error_messages:
            # e is an instance of ErrorMessage
            if e.widget:
                displaywidget = skiboot.WidgField(s=e.section, w=e.widget, f='', i='')
            else:
                # use page default error location 
                displaywidget = self.default_error_widget
            if not displaywidget:
                # nowhere to display an error
                continue
            if displaywidget not in self.stored_errors:
                self.stored_errors[displaywidget] = e.message
            else:
                # displaywidget is already in self.stored_errors
                # existing messages have priority
                # unless existing message is an empty string
                if not self.stored_errors[displaywidget]:
                    self.stored_errors[displaywidget] = e.message

                
    def _show_errors_on_update(self):
        """Called on page update to show all stored errors"""
        if not self.page_in_error:
            # show_error never called - so no error condition
            return
        # if no error widget or message given, show the page default error widget
        if not self.stored_errors:
            widget = self.widget_from_name(self.default_error_widget.s, self.default_error_widget.w)
            if widget is None:
                return
            widget.show_error(message='')
            return
        # There are stored messages, so call the errored widgets
        for displaywidget, message in self.stored_errors.items():
            if not displaywidget:
                continue
            widget = self.widget_from_name(displaywidget.s, displaywidget.w)
            if widget is None:
                continue
            widget.show_error(message)

    def set_values(self, page_data):
        """Checks for special page template values, then passes on to parent set_values to set the widgets"""
        if 'last_scroll' in page_data:
            self.last_scroll = bool(page_data['last_scroll'])
            del page_data['last_scroll']
        if 'lang' in page_data:
            if isinstance(page_data['lang'], 'tuple') or isinstance(page_data['lang'], 'list'):
                self.lang = page_data['lang'][0]
            else:
                self.lang = page_data['lang']
            del page_data['lang']
        if 'show_backcol' in page_data:
            self.show_backcol = bool(page_data['show_backcol'])
            del page_data['show_backcol']
        if 'backcol' in page_data:
            self.backcol = page_data['backcol']
            del page_data['backcol']
        if 'body_class' in page_data:
            self.body.update_attribs({'class':page_data['body_class']})
            del page_data['body_class']
        if 'show_error' in page_data:
            page_data[self._default_error_widget.set_field(f='show_error')] = page_data['show_error']
            del page_data['show_error']
        if 'add_jscript' in page_data:
            self._add_jscript = page_data['add_jscript']
            del page_data['add_jscript']
        if ('localStorage' in page_data) or ('sessionStorage' in page_data):
            self._add_storage += """  if (typeof(Storage) !== "undefined") {
"""
            if 'localStorage' in page_data:
                for key,val in page_data['localStorage'].items():
                    escapedval = json.dumps(val)
                    self._add_storage += """    localStorage.setItem("%s", %s);
""" % (key,escapedval)
                del page_data['localStorage']
            if 'sessionStorage' in page_data:
                for key,val in page_data['sessionStorage'].items():
                    escapedval = json.dumps(val)
                    self._add_storage += """    sessionStorage.setItem("%s", %s);
""" % (key,escapedval)
                del page_data['sessionStorage']
            self._add_storage += """    }
"""
        TemplatePageAndSVG.set_values(self, page_data)

    def data(self):
        "Returns the page as a list of binary strings"
        # set data into the page
        page_javascript = """// javascript for skipole project %s page ident %s
//<![CDATA[
SKIPOLE.identdata = '%s';
SKIPOLE.default_error_widget = '%s';
SKIPOLE.widget_register = {};
"""  % (self.ident.proj, self.ident.num, self.ident_data_string, self.default_error_widget)

        # set a list of section alias names, to include section alias, and multiplied section alias
        section_alias_list = list(self.sections.keys())
        for alias in self.section_places.keys():
            if alias not in section_alias_list:
                section_alias_list.append(alias)

        page_javascript += "SKIPOLE.sections =  " + str(section_alias_list) + ";\n"

        # append javascript to page head
        self.head.append(Part(tag_name="script", text=page_javascript + self._js + "//]]>\n"))

        topstring = "<!DOCTYPE HTML>\n<html"
        if self.show_backcol:
            back = " style=\"background-color: %s;\"" % self.backcol
            topstring += back
        if self.lang:
            topstring += " lang=\"%s\"" % self.lang
        topstring += ">\n"
        topbytes = topstring.encode('ascii', 'xmlcharrefreplace')

        docbytes = [topbytes]
        docbytes.extend(d.encode('ascii', 'xmlcharrefreplace') for d in self.head.data())
        docbytes.extend(d.encode('ascii', 'xmlcharrefreplace') for d in self.body.data())
        docbytes.append("\n</html>".encode('ascii', 'xmlcharrefreplace'))
        return docbytes

    def __str__(self):
        "Returns the page as a string"
        topstring = "<!DOCTYPE HTML>\n<html"
        if self.show_backcol:
            back = " style=\"background-color: %s;\"" % self.backcol
            topstring += back
        if self.lang:
            topstring += " lang=\"%s\"" % self.lang
        topstring += ">"
        return topstring + str(self.head) + str(self.body) + "\n</html>"

    def __repr__(self):
        if self.ident:
            return "Template Page ident %s" % (self.ident,)
        else:
            return "Template Page name %s" % (self.name,)


class RespondPage(ParentPage):


    def __init__(self, name, brief = "New RespondPage", responder=None):
        ParentPage.__init__(self, name=name, brief=brief)
        # A responder is an instance of the Respond class
        # - or more usually, an instance of a child of the Respond class
        self.responder = responder

    def call_responder(self, skicall, form_data, caller_ident, ident_list, rawformdata, error_dict=None):
        """Checks for circulating calls, then updates ident_list with this pages ident,
           then calls the respond objects call method, note rawformdata is a cgi.FieldStorage object"""
        if self.responder is None:
            raise ServerError(message = "No responder has been assigned to this page")
        if self.ident in ident_list:
            raise ServerError(message="Circulating call to Respond page: ident %s in %s" % (self.ident, ident_list))
        ident_list.append(self.ident)
        proj = self.ident.proj

        # create submit_dict
        if error_dict:
            skicall.submit_dict = {"responder_brief":self.brief, "number":self.ident.num, 'error_dict':error_dict}
        else:
            skicall.submit_dict = {"responder_brief":self.brief, "number":self.ident.num, 'error_dict':{}}

        page = self.responder(skicall, form_data, caller_ident, ident_list, proj, rawformdata, error_dict)
        return page

    def set_values(self, page_data):
        return

    def __repr__(self):
        if self.ident:
            return "Respond Page ident %s" % (self.ident,)
        else:
            return "Respond Page name %s" % (self.name,)



class SVG(TemplatePageAndSVG):
    """An SVG image
    """

    def __init__(self, name="", brief = "New SVG Page", width="100", height="100", css_list=[], enable_cache=False):
        """Initiates a Page instance

        name: a url friendly page name
        """
        TemplatePageAndSVG.__init__(self, name=name, brief=brief)
        self.css_list = [skiboot.make_ident(ident) for ident in css_list]
        self.svg = Part(tag_name="svg", attribs = {"xmlns":"http://www.w3.org/2000/svg",
                                                   "baseProfile":"full",
                                                   "version":"1.1",
                                                   "width":width,
                                                   "height":height})
        self.svg.brief = "The svg section of the page"
        # enable_cache flag
        self._enable_cache = False
        self.enable_cache = enable_cache

    def set_enable_cache(self, enable_cache):
        "Sets enable cache in header"
        if enable_cache:
            self._enable_cache = True
            self.headers = [('content-type', 'image/svg+xml'), ('cache-control', 'max-age=3600')]
        else:
            self._enable_cache = False
            self.headers = [('content-type', 'image/svg+xml'),
                                              ('cache-control','no-cache, no-store, must-revalidate'),
                                              ('Pragma', 'no-cache'),
                                              ( 'Expires', '0') ]


    def get_enable_cache(self):
        return self._enable_cache

    enable_cache = property(get_enable_cache, set_enable_cache)


    def location_item(self, location):
        "Returns the part or widget at location"
        location_string, container_number, location_list = location
        if not location_string:
            return
        if container_number is None:
            # Not in a widget
            if location_string == 'svg':
                if not location_list:
                    return self.svg
                return self.svg.get_location_value(location_list)
            # not found
            return
        # location string must be a widget name
        # so part is within a widget container within the page
        if location_string not in self.widgets:
            return
        widget = self.widgets.get(location_string)
        if widget is None:
            return
        if widget.can_contain():
            if not location_list:
                # return the container
                return widget.container_part(container_number)
            else:
                return widget.get_from_container(container_number, location_list)
        # part not found
        return



    def get_width(self):
        return self.svg.get_attrib_value("width")

    def set_width(self, width):
        self.svg.update_attribs({"width":width})

    width = property(get_width, set_width)

    def get_height(self):
        return self.svg.get_attrib_value("height")

    def set_height(self, height):
        self.svg.update_attribs({"height":height})

    height = property(get_height, set_height)

    def update(self, environ, call_data, lang, ident_list=[]):
        "Updates svg parts"
        ident_string = str(self.ident)+"_svg"
        self.svg.update(self, ident_list, environ, call_data, lang, ident_string)
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)

    def add_javascript(self, contents):
        "Currently not used"
        pass

    def set_idents(self):
        """Each widget adds its ident, to itself, and to the self.widgets dictionary
           Each sectionplaceholder adds its ident, to itself, and to the self.section_places dictionary
           This is called when the page is created and added to a folder, it is also
           called when an existing page is edited"""
        self.widgets = {}
        self.section_places = {}
        self.svg.set_idents(str(self.ident)+"_svg", self.widgets, self.section_places)

    def show_error(self, error_messages=None):
        """Currently not used"""
        return


    def set_values(self, page_data):
        """Checks for special svg page template values, then passes on to parent set_values to set the widgets"""
        if 'enable_cache' in page_data:
            self.enable_cache = bool(page_data['enable_cache'])
            del page_data['enable_cache']
        if 'width' in page_data:
            self.width = page_data['width']
            del page_data['width']
        if 'height' in page_data:
            self.height = page_data['height']
            del page_data['height']
        TemplatePageAndSVG.set_values(self, page_data)


    def data(self):
        "Returns the page as a list of binary strings"

        # note xmls initial dtd statements and stuff left out as per
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Getting_Started

        svg_list = self.svg.data()
        return [d.encode('ascii', 'xmlcharrefreplace') for d in svg_list]


    def __str__(self):
        return str(self.svg)

    def __repr__(self):
        if self.ident:
            return "SVG Page ident %s" % (self.ident,)
        else:
            return "SVG Page name %s" % (self.name,)


class FilePage(ParentPage):
    """A page representing a file to be downloaded to the user.
    """

    def __init__(self, name="", brief="", filepath="", mimetype=None, enable_cache=False):
        "If no filepath given, assumes a file of the same name under the project static folder"
        if not brief:
            brief = "Link to %s" % filepath
        ParentPage.__init__(self, name=name, brief=brief)
        self.filepath = filepath
        self._filepath_relative_to_project_files = None
        self._mimetype = mimetype
        self._enable_cache = False
        self.enable_cache = enable_cache
        # flag for headers auto set
        self._headers_flag = True
        # environ, set by the update methon
        self._environ = None

    def set_enable_cache(self, enable_cache):
        "Sets enable cache in header"
        if enable_cache:
            self._enable_cache = True
            self.headers = [('cache-control', 'max-age=3600')]
        else:
            self._enable_cache = False
            self.headers = [ ('cache-control','no-cache, no-store, must-revalidate'),
                                              ('Pragma', 'no-cache'),
                                              ( 'Expires', '0')]

    def get_enable_cache(self):
        return self._enable_cache

    enable_cache = property(get_enable_cache, set_enable_cache)

    def get_filepath(self):
        # self._filepath is a list of path parts
        if (not self._filepath):
            self._filepath = [self.proj_ident, "static"]
            self._filepath.append(self.name)
        return os.sep.join(self._filepath)

    def set_filepath(self, path):
        if path:
            if ('/' in path) and ('\\' in path):
                raise ValidateError("Invalid path")
            if '/' in path:
                self._filepath = path.strip('/').split('/')
            elif '\\' in path:
                self._filepath = path.strip('\\').split('\\')
            else:
                self._filepath = [path]
        else:
            self._filepath = []
        for item in self._filepath:
            if (not item) or (item == '.') or (item == '..'):
                self._filepath = []
                raise ValidateError("Invalid path")

    filepath = property(get_filepath, set_filepath)

    def get_mimetype(self):
        if self._mimetype: return self._mimetype
        # self._mimetype not set, so guess it
        if self.filepath:
            name = os.path.basename(self.filepath)
        else:
            name=self.name
        mimetypes.init()
        t, e = mimetypes.guess_type(name, strict=False)
        if t:
            return t

    def set_mimetype(self, mt):
        self._mimetype = mt

    mimetype = property(get_mimetype, set_mimetype)

    def set_values(self, page_data):
        "Only values allowed: status, headers, mimetype, filepath, enable_cache"
        if 'filepath' in page_data:
            self.filepath = page_data['filepath']
        if 'mimetype' in page_data:
            self._mimetype = page_data['mimetype']
        if 'enable_cache' in page_data:
            self.enable_cache = bool(page_data['enable_cache'])
        if ('headers' in page_data) and page_data['headers']:
            # headers have not been auto set, they are set specifically by the user
            self._headers_flag = False
        ParentPage.set_values(self, page_data)


    def update(self, environ, call_data, lang, ident_list=[]):
        """"If filepath set, then this is the file returned, if not, then projectfiles/project/static/name is returned"""
        self._environ = environ
        mimetype = self.mimetype
        if mimetype and self._headers_flag:
            # only add mimetype if headers auto set, not if headers specified in page_data
            self.headers.append(('content-type', mimetype))
        # get length of file
        filepath = self.filepath
        if not filepath:
            raise ServerError(message="Filepath not set")
        try:
            self._filepath_relative_to_project_files = os.path.join(skiboot.projectfiles(self.proj_ident), filepath)
            if self._headers_flag:
                # only add content-length if headers auto set, not if headers specified in page_data
                self.headers.append(('content-length', str(os.path.getsize(self._filepath_relative_to_project_files))))
        except Exception:
            raise ServerError(message="Unable to open file %s" % (self.name,))
        # if a session cookie is specified, add it even if headers have been user set
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)


    def _readfile(self, size=1024):
        "Return a generator reading the file"
        with open(self._filepath_relative_to_project_files, "rb") as f:
            data = f.read(size)
            while data:
                yield data
                data = f.read(size)


    def data(self):
        "returns an iterator reading the file"
        if not self._filepath:
            return ["<!DOCTYPE HTML>\n<html>ERROR:NO FILEPATH SET\n</html>".encode('ascii', 'xmlcharrefreplace')]
        try:
            size = 1024
            if 'wsgi.file_wrapper' in self._environ:
                f = open(self._filepath_relative_to_project_files, "rb")
                return self._environ['wsgi.file_wrapper'](f, size)
            else:
                return self._readfile(size)
        except IOError:            
            return ["<!DOCTYPE HTML>\n<html>ERROR:UNABLE TO OPEN FILE\n</html>".encode('ascii', 'xmlcharrefreplace')]


    def __str__(self):
        return self.filepath

    def __repr__(self):
        if self.ident:
            return "File Page ident %s" % (self.ident,)
        else:
            return "File Page name %s" % (self.name,)


class CSS(ParentPage):
    """A CSS object represents a css file
    """


    def __init__(self, name="", brief="New CSS Page", style=collections.OrderedDict(), enable_cache=False):
        "style held as ordered dictionary each value being a list of lists"
        ParentPage.__init__(self, name=name, brief=brief)

        # self.style is a dictionary with keys being css selectors
        # and values being a list of two element lists
        # acting as css declaration blocks.

        self.style = style
        self.colour_substitution = {}
        # enable_cache flag
        self._enable_cache = False
        self.enable_cache = enable_cache
        # imports
        self.imports = []

    def set_enable_cache(self, enable_cache):
        "Sets enable cache in header"
        if enable_cache:
            self._enable_cache = True
            self.headers = [('content-type', 'text/css'), ('cache-control', 'max-age=3600')]
        else:
            self._enable_cache = False
            self.headers = [('content-type', 'text/css'),
                            ('cache-control','no-cache, no-store, must-revalidate'),
                            ('Pragma', 'no-cache'),
                            ( 'Expires', '0')]

    def get_enable_cache(self):
        return self._enable_cache

    enable_cache = property(get_enable_cache, set_enable_cache)


    def set_values(self, page_data):
        """enable_cache, @import, status, headers and ident_data"""
        if 'enable_cache' in page_data:
            self.enable_cache = bool(page_data['enable_cache'])
            del page_data['enable_cache']
        if '@import' in page_data:
            if isinstance(page_data['@import'], list):
                self.imports = page_data['@import']
            elif isinstance(page_data['@import'], str):
                self.imports = [page_data['@import']]
            del page_data['@import']
        ParentPage.set_values(self, page_data)


    def selector_list(self):
        return list(self._style.keys())

    def selector_properties(self, selector):
        "Returns the property strings of the selector"
        style_text = ""
        if selector not in self._style:
            return ""
        value = self._style[selector]
        if value:
            # value is a list of two element lists
            # created value_list, which is value, sorted by the first element in each sub list
            value_list = sorted(value, key=lambda val : val[0])
            for a,b in value_list:
                style_text += "{a} : {b};\n".format(a=a, b=b)
        return style_text

    # property style is a dictionary of lists
    def get_style(self):
        return self._style

    def set_style(self, style):
        if isinstance(style, collections.OrderedDict):
            self._style = style
        elif isinstance(style, dict):
            self._style = collections.OrderedDict([(selector,value) for selector,value in style.items()])
        else:
            self._style = collections.OrderedDict()

    style = property(get_style, set_style)

    def write(self, filepath):
        "Writes a css file to the given filepath"
        if not self._style:
            return
        with open(filepath, "w") as f:
            f.write(self.__str__())

    def data(self):
        "Returns the page as a list of binary strings"
        if not self._style:
            return []
        style_binary = ["@charset \"UTF-8\";\n".encode('UTF-8')]
        if self.imports:
            for imp in self.imports:
                style_binary.append("@import : {imp};\n".format(imp=imp.strip(';')).encode('UTF-8'))
        for selector,value in self._style.items():
            if value:
                style_binary.append("\n{selector} {{".format(selector=selector).encode('UTF-8'))
                # value is a list of two element lists
                # created value_list, which is value, sorted by the first element in each sub list
                value_list = sorted(value, key=lambda val : val[0])
                for a,b in value_list:
                    if self.colour_substitution and ('$' in b):
                        c = Template(b)
                        b= c.safe_substitute(self.colour_substitution)
                    style_binary.append("\n{a} : {b};".format(a=a, b=b).encode('UTF-8'))
                style_binary.append("}\n".encode('UTF-8'))
        return style_binary

    def __str__(self):
        "Returns the css page as a string"
        if not self._style:
            return ""
        style_text = ""
        if self.imports:
            for imp in self.imports:
                style_text += "@import : {imp};\n".format(imp=imp.strip(';'))
        for selector, value in self._style.items():
            if value:
                style_text += """
{selector} {{""".format(selector=selector)
                # value is a list of two element lists
                # created value_list, which is value, sorted by the first element in each sub list
                value_list = sorted(value, key=lambda val : val[0])
                for a,b in value_list:
                    style_text += "\n{a} : {b};".format(a=a, b=b)
                style_text += "}\n"
        return style_text

    def __repr__(self):
        if self.ident:
            return "CSS Page ident %s" % (self.ident,)
        else:
            return "CSS Page name %s" % (self.name,)


class JSON(ParentPage):
    """A JSON object represents dynamically created json data
    """

    def __init__(self, name="", brief="New JSON Page", content=None, enable_cache=False):
        "content held as ordered dictionary"
        ParentPage.__init__(self, name=name, brief=brief)
        if content:
            self.content = content
        else:
            self.content = collections.OrderedDict()
        # enable_cache flag
        self._enable_cache = False
        self.enable_cache = enable_cache
        # setting jsondict overrides self.content
        self.jsondict = None

    def set_enable_cache(self, enable_cache):
        "Sets enable cache in header"
        if enable_cache:
            self._enable_cache = True
            self.headers = [('content-type', 'application/json'), ('cache-control', 'max-age=3600')]
        else:
            self._enable_cache = False
            self.headers = [('content-type', 'application/json'),
                                             ('cache-control','no-cache, no-store, must-revalidate'),
                                              ('Pragma', 'no-cache'),
                                              ( 'Expires', '0')]

    def get_enable_cache(self):
        return self._enable_cache

    enable_cache = property(get_enable_cache, set_enable_cache)

    def add_widgfield(self, widgfield, value):
        "Add widgfield and value to self.content"
        # ensure widgfield is a skiboot.WidgField object
        fld = skiboot.make_widgfield(widgfield)
        if not fld:
            return
        self.content[str(fld)] = value

    def del_widgfield(self, widgfield):
        "Removes widgfield from self.content"
        # ensure widgfield is a skiboot.WidgField object
        fld = skiboot.make_widgfield(widgfield)
        if not fld:
            return
        strfld = str(fld)
        if strfld in self.content:
            del self.content[strfld]

    def set_values(self, page_data):
        """Sets json content"""
        if not page_data:
            return
        if 'localStorage' in page_data:
            self.content["localStorage"] = page_data['localStorage']
            del page_data['localStorage']
        if 'sessionStorage' in page_data:
            self.content["sessionStorage"] = page_data['sessionStorage']
            del page_data['sessionStorage']
        if "JSONtoHTML" in page_data:
            url = skiboot.find_ident_or_url(page_data["JSONtoHTML"], proj_ident=self.proj_ident)
            if url:
                self.content["JSONtoHTML"] = url
                return
            del page_data["JSONtoHTML"]
        ParentPage.set_values(self, page_data)
        for field, item in page_data.items():
            if field == 'lang':
                if isinstance(item, 'tuple') or isinstance(item, 'list'):
                    self.content['lang'] = item[0]
                else:
                    self.content['lang'] = item
            elif isinstance(field, str):
                self.content[field] = item
            else:
                widgfield = str(skiboot.make_widgfield(field))
                self.content[widgfield] = item

    def update(self, environ, call_data, lang, ident_list=[]):
        "Adds session_cookie, and also ident_list if debug mode is on"
        if self.session_cookie:
            self.headers.append(self.session_cookie)
        if self.language_cookie:
            self.headers.append(self.language_cookie)
        if skiboot.get_debug():
            # include environ, call_data and ident_list in json file
            self.content['environ'] = pprint.pformat(environ)
            if call_data:
                self.content['call_data'] = pprint.pformat(call_data)
            if not ident_list:
                self.content['ident_list'] = [[self.ident.to_comma_str(), 'This page', self.brief]]
                return
            idents = []
            for ident in ident_list:
                item = skiboot.from_ident(ident)
                idents.append([ident.to_comma_str(), item.responder.__class__.__name__, item.brief])
            idents.append([self.ident.to_comma_str(), 'This page', self.brief])
            self.content['ident_list'] = idents

    def show_error(self, error_messages=None):
        """Sets show error in page data"""
        if not error_messages:
            # send a default page error
            self.content["show_error"] = ""
            return
        for e in error_messages:
            # e is an instance of ErrorMessage
            if e.widget:
                displaywidget = str(skiboot.WidgField(s=e.section, w=e.widget, f='show_error', i=''))
            else:
                displaywidget = "show_error"
            self.content[displaywidget] = e.message

    def data(self):
        "Returns the page as a list of binary strings"
        if self.jsondict is not None:
            return [json.dumps(self.jsondict).encode('UTF-8')]
        if self.ident_data:
            self.content['ident_data'] = self.ident_data
        elif 'ident_data' in self.content:
            del self.content['ident_data']
        return [json.dumps(self.content).encode('UTF-8')]

    def __str__(self):
        "Returns the json page as a string"
        if self.jsondict is not None:
            return json.dumps(self.jsondict)
        if self.ident_data:
            self.content['ident_data'] = self.ident_data
        elif 'ident_data' in self.content:
            del self.content['ident_data']
        return json.dumps(self.content)

    def __repr__(self):
        if self.ident:
            return "JSON Page ident %s" % (self.ident,)
        else:
            return "JSON Page name %s" % (self.name,)

