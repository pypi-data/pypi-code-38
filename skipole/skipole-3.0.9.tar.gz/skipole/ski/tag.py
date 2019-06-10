

"""
This module defines the classes:

Part which holds an html tag, with attributes and contents.

ClosedPart which is also a tag, with name and attributes, but no contents, such as <tag_name att="attribute" />.

Widget which inherits from Part and can be subclassed to create widgets
"""

import html, copy, uuid

from collections import OrderedDict

from urllib.parse import quote, quote_plus

from . import skiboot
from .excepts import ValidateError, ServerError


def expand_text(text, escape=True, linebreaks=True, replace_strings=[]):
    "Sets any replace string, expands any newlines in text to linebreaks, and applies html.escape to text"
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    if replace_strings:
        try:
            newtext = text % tuple(replace_strings)
        except Exception:
            # unable to complete the replace, so carry on
            pass
        else:
            # no errors, set text to newtext
            text = newtext
    if escape:
        text = html.escape(text)
    if not linebreaks:
        return text
    # linebreaks must be true
    return "<br />".join(text.split("\n"))


def make_dictionary(input_dict, proj_ident):
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
            output_dict[key] = make_list(val, proj_ident)
        elif isinstance(val, dict):
            output_dict[key] = make_dictionary(val, proj_ident)
        elif val is True:
            output_dict[key] = True
        elif val is False:
            output_dict[key] = False
        elif isinstance(val, TextBlock):
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


def make_list(input_list, proj_ident):
    """Used by other functions, takes input_list and returns a list with items converted"""
    if not input_list: return []
    output_list = []
    for item in input_list:
        if item is None:
            output_list.append(None)
        elif item is '':
            output_list.append('')
        elif isinstance(item, list):
            output_list.append(make_list(item, proj_ident))
        elif isinstance(item, dict):
            output_list.append(make_dictionary(item, proj_ident))
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


class ParentPart(object):
    "The parent of Part and Closedpart objects"

    def __init__(self, tag_name, attribs, show, brief):
        # self.name is only set if a part is also a widget
        self.name=None

        self.tag_name = tag_name
        self._attribs = {}
        self.hide_if_empty = False

        # set when set_idents is called on the containing page
        self.ident_string = ''


        # self.brief is a string describing what this part does
        self.brief = brief

        if attribs:
            self.set_attribs(attribs)

        # set show to False if this part is not to be shown
        self.show = show
        self._error = ""

        # embedded is a tuple of section name, parent widget name, parent widget container integer
        # If not within a section, section name is an empty string.
        # If not in a widget, the widget name is empty string and container integer is set to None
        # if not in a container, the container integer is None
        self.embedded = ('','', None)

        # If this is in a section, this is set
        self.placename = ''

        # parts contains a list of sub parts, always empty for a closedpart
        self.parts = []

    def set_idents(self, ident_string, widgets, section_places, embedded=('','',None)):
        """Sets self.ident_string in this and sub parts, called when a page is saved,
             embedded is (section_name, parent_widget_name, parent_widget_container)"""
        self.ident_string = ident_string
        parent_container = None
        # is this part in a widget, and container not set
        if embedded[1] and (embedded[2] is None):
            # get the widget
            parent_widget = widgets[embedded[1]]
            # check the parent_widget containers
            for cont in range(parent_widget.len_containers()):
                parent_container_string = parent_widget.get_container_string_loc(cont)
                if parent_container_string:
                    container_ident_string = parent_widget.ident_string + '-' + parent_container_string
                else:
                    container_ident_string = parent_widget.ident_string
                if self.ident_string.startswith(container_ident_string):
                    parent_container = cont
                    break
        if parent_container is None:
            self.embedded = embedded
        else:
            self.embedded = (embedded[0], embedded[1], parent_container)
        if self.name:
            # parts beneath this named widget will be within this widget
            embedded_parts = (embedded[0], self.name, None)
            # add the widget to the widgets dictionary
            widgets[self.name] = self
        else:
            embedded_parts = self.embedded
        for index, part in enumerate(self.parts):
            if hasattr(part, "set_idents"):
                part_ident_string = ident_string + "-" + str(index)
                part.set_idents(part_ident_string, widgets, section_places, embedded_parts)

    def set_unique_names(self, name_list):
        "Ensures this item, and sub items have a unique name"
        if self.name:
            number = 2
            new_name = self.name
            while new_name in name_list:
                new_name = self.name + str(number)
                number += 1
            self.name = new_name 
            name_list.append(self.name)
        for index, part in enumerate(self.parts):
            if hasattr(part, "set_unique_names"):
                part.set_unique_names(name_list)


    @property
    def proj_ident(self):
        if not self.ident_string:
            return ''
        return self.ident_string.split('_')[0]

    def insert_id(self, id_string=''):
        """Adds the id_string to the part attributes. If no id_string given
           but the part has a name, sets the id to the part name, otherwise
           sets the id to self.ident_string"""
        if id_string:
            self.update_attribs({"id": id_string})
            return
        if self.name:
            # This only applies to named widgets
            if self.placename:
                full_id = self.placename + '-' + self.name
                self.update_attribs({"id": full_id})
            else:
                self.update_attribs({"id": self.name})
            return
        if self.ident_string:
            self.update_attribs({"id": self.ident_string})

    def get_id(self):
        return self.get_attrib_value('id')

    def get_class(self):
        return self.get_attrib_value('class')

    def set_class(self, value):
        if (not value) and ('class' in self._attribs):
            del self._attribs['class']
        else:
            self._attribs['class'] = value

    def set_hide(self, value=True):
        "If True, Sets display:none !important into style, if False removes it"
        if value:
            attribs = self._attribs
            if 'style' not in attribs:
                self._attribs['style'] = "display:none !important;"
                return
            # An existing style is in place
            style = self._attribs['style']
            style_list = style.split(';')
            # ensure no empty items
            style_list = [item for item in style_list if item]
            if "display:none !important" in style_list:
                # "display:none !important" already set
                return
            #  remove existing displays
            if "display:none" in style_list:
                # "display:none" already set, remove it so it can be replaced
                style_list.remove("display:none")
            if "display:block" in style_list:
                # "display:block" already set, remove it so it can be replaced
                style_list.remove("display:block")
            if "display:block !important" in style_list:
                # "display:block !important" already set, remove it so it can be replaced
                style_list.remove("display:block !important")
            # append display:none !important;
            if not style_list:
                self._attribs['style'] = "display:none !important;"
                return
            style_list.append("display:none !important;")
            self._attribs['style'] = ";".join(style_list)
        else:
            attribs = self._attribs
            if 'style' not in attribs:
                return
            # An existing style is in place
            style = self._attribs['style']
            style_list = style.split(';')
            style_list = [item for item in style_list if item]
            if "display:none !important" in style_list:
                style_list.remove("display:none !important")
            if "display:none" in style_list:
                style_list.remove("display:none")
            if style_list:
                self._attribs['style'] = ";".join(style_list)
            else:
                del self._attribs['style']

    def set_block(self):
        "Sets display:block !important into style"
        attribs = self._attribs
        if 'style' not in attribs:
            self._attribs['style'] = "display:block !important;"
            return
        # An existing style is in place
        style = self._attribs['style']
        style_list = style.split(';')
        # ensure no empty items
        style_list = [item for item in style_list if item]
        if "display:block !important" in style_list:
            # "display:block !important" already set
            return
        #  remove existing displays
        if "display:block" in style_list:
            # "display:block" already set, remove it so it can be replaced
            style_list.remove("display:block")
        if "display:none" in style_list:
            # "display:none" already set, remove it so it can be replaced
            style_list.remove("display:none")
        if "display:none !important" in style_list:
            # "display:none !important" already set, remove it so it can be replaced
            style_list.remove("display:none !important")
        # append display:block !important;
        if not style_list:
            self._attribs['style'] = "display:block !important;"
            return
        style_list.append("display:block !important;")
        self._attribs['style'] = ";".join(style_list)

    def get_attribs(self):
        return self._attribs.copy()

    def set_attribs(self, attribs):
        self._attribs = {}
        if attribs:
            for att,val in attribs.items():
                if val:
                    self._attribs[att]=val
                else:
                    self._attribs[att]=''

    def del_attribs(self):
        self._attribs = {}

    attribs = property(get_attribs, set_attribs, del_attribs)

    @property
    def attributes_string(self):
        "Returns a string showing the attributes"
        str_attribs = ''
        for att,val in self._attribs.items():
            if val:
                if val[0] == '{':
                    value = self._expand_label(str(val))
                else:
                    value = str(val)
                str_attribs += " {att!s}=\"{val!s}\"".format(att=att, val=html.escape(value))
            else:
                str_attribs += " {att!s}=\"\"".format(att=att)
        return str_attribs

    def _expand_label(self, valstring):
        "If valstring starts with a  label in the form {label}, substitute url here"
        if valstring[0] != '{':
            return valstring
        proj_ident = self.proj_ident
        if not proj_ident:
            return valstring
        end = valstring.find('}')
        if end == -1:
            return valstring
        label = valstring[1:end]
        if label:
            url = skiboot.get_url(label, proj_ident)
            if url:
                return quote(url, safe='/:?&=')+valstring[end+1:]
        return valstring

    def has_attrib(self, name):
        "If this attrib exists, return True otherwise False"
        return name in self._attribs

    def get_attrib_value(self, name):
        """Get an attribute value, given its name, if it does not exist, return None"""
        if name not in self._attribs:
            return None
        return self._attribs[name]

    def del_one_attrib(self, attrib):
        "deletes an attribute"
        if attrib in self._attribs:
            del self._attribs[attrib]


    def update_attribs(self, attribs):
        "Updates attributes with the dictionary given in the attribs argument"
        for att,val in attribs.items():
            self._attribs[att]=val


    def make_get_url(self, page, url, get_fields={}, force_ident=False):
        "returns url, including the page ident_data for a get link"
        if not url:
            raise ServerError("URL is invalid")
        if not page.ident_data_string:
            return url
        getstring = ''
        for key, val in get_fields.items():
            if not val:
                continue
            getstring += "&" + quote_plus(key) + "=" + quote_plus(str(val))
            force_ident = True
        if not force_ident:
            return url
        return url + "?ident=" + quote_plus(page.ident_data_string) + getstring
 

    def show_error(self, message="", *args, **nargs):
        """If a message is given, sets self._error
        """
        # update attribute with  data-status="error"
        self.update_attribs({'data-status':'error'})
        if message:
            self._error = message
        self.show = True


    def __bool__(self):
        return True


    def string_indent(self, n=2):
        """Returns a text string to illustrate the element, indented by
           n spaces."""
        display_list = self.__str__().splitlines()
        if n == 2:
            return '  ' + '\n  '.join(display_list)
        sp = ' ' * n
        sp_n = '\n' + sp
        return sp + sp_n.join(display_list)

    def outline(self, proj_ident):
        """To be overwritten by child classes, returns a list defining the part used when creating JSON files representing the part"""
        return ['Text', str(self)]



class Part(ParentPart):
    """
    Defines a tagged part, such as a section, or paragraph with attributes and contents, the contents
    may be other Parts. The __str__ method returns the string of the tag.

    **instance attributes:**

    *attribs*
      A dictionary of attributes, key is attribute name, value is attribute value


    *parts*
      A list of sub parts

    *show*
      A True or false flag, normally True, which indicates the tag will be shown,
      if false the __str__ method returns an empty string

    *tag_name*
      such as 'p'

    *text*
      Text to place between the openning and closing tags - only inserted
      if the Part contains no sub parts.
    """

    # for formatting; any tag with these names will have its end tag put on
    # a new line
    tag_list = ["div", "head", "body", "nav", "section", "header", "footer", "form", "table", "tr", "svg"]

    def __init__(self, tag_name="div", attribs=None, text="", show=True, hide_if_empty=False, brief=''):
        ParentPart.__init__(self, tag_name=tag_name, attribs=attribs, show=show, brief=brief)
        # self.htmlescaped is True where a part string contents should be escaped
        # False where the string contents is further html
        self.htmlescaped=True
        # self.linebreaks is True where a part string contents newlines should be
        # changed to linebreaks
        self.linebreaks=True
        # self.parts is a list of sub parts
        if text:
            self.parts = [text]
        self.hide_if_empty = hide_if_empty

    def make_js(self, page, ident_list, environ, call_data, lang):
        "Auto generates the javascript for any containing widgets"
        if not self.parts: return
        if not self.show: return
        for part in self.parts:
            if hasattr(part, 'make_js'):
                part.make_js(page, ident_list, environ, call_data, lang)


    def get_text(self):
        "equivalent to getting self[0]"
        if self.parts:
            return self.parts[0]
        else:
            return ''

    def set_text(self, text):
        "equivalent to setting self[0]"
        if self.parts:
            self.parts[0]=text
        else:
            self.parts = [text]

    text = property(get_text, set_text, doc="Equivalent to self[0]; note may not be text despite this attributes name")

        
    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename='', embedded=('','',None)):
        "Override this to change run time information in this part and its sub parts"
        if placename:
            self.placename = placename
        if not self.ident_string:
            # item is a dynamic part, newly created within a widget
            self.embedded = embedded
            self.ident_string = ident_string
        try:
            if self._error:
                if isinstance(self._error, TextBlock):
                    self._error.update(page, ident_list, environ, call_data, lang, self.ident_string, self.placename, embedded)
                return
            for index, part in enumerate(self.parts):
                part_ident_string = self.ident_string + "-" + str(index)
                if hasattr(part, "update"):
                    part.update(page, ident_list, environ, call_data, lang, part_ident_string, self.placename, embedded)
        except ValidateError as e:
            if not e.ident_list:
                e.ident_list = ident_list
            raise


    def __setitem__(self, part_index, part_obj):
        "Sets sub part, part_index must be an integer"
        if not isinstance(part_index, int):
            raise TypeError('indeces must be integers')
        # so its an integer
        len_parts = len(self.parts)
        if part_index > len_parts:
            raise ValidateError("part index too large")
        if part_index == len_parts:
            self.parts.append(part_obj)
            return
        self.parts[part_index] = part_obj


    def append(self, part_obj):
        "Sets sub part"
        self.parts.append(part_obj)

    def __getitem__(self, part_index):
        "Returns the part object for the given index, part_index must be an integer"
        return self.parts[part_index]


    def __delitem__(self, part_index):
        "Deletes a part, part_index must be an integer"
        del self.parts[part_index]

    def clear(self):
        self.parts = []


    def set_location_value(self, location_list, value):
        "Set a value in the part at this position, location_list being either an integer, a tuple/list of indexes"
        if isinstance(location_list, str):
            try:
                location_list = int(location_list)
            except Exception:
                raise TypeError('Invalid location')
        if isinstance(location_list, int):
            self[location_list] = value
            return
        if not location_list:
            raise TypeError('Invalid location')
        if len(location_list) == 1:
            self[location_list[0]] = value
            return
        part = self
        for i in location_list[:-1]:
            part = part[i]
        part[location_list[-1]]= value

    def insert_location_value(self, location_list, value):
        "Inserts a value in the part at this position, location_list being either an integer, a tuple/list of indexes"
        if isinstance(location_list, str):
            try:
                location_list = int(location_list)
            except Exception:
                raise TypeError('Invalid location')
        if isinstance(location_list, int):
            self.insert(location_list, value)
            return
        if not location_list:
            raise TypeError('Invalid location')
        if len(location_list) == 1:
            self.insert(location_list[0], value)
            return
        part = self
        for i in location_list[:-1]:
            part = part[i]
        part.insert(location_list[-1], value)

    def get_location_value(self, location_list):
        "Get a value in the part at this position, location_list being either an integer, a tuple/list of indexes"
        if isinstance(location_list, str):
            try:
                location_list = int(location_list)
            except Exception:
                raise TypeError('Invalid location')
        if isinstance(location_list, int):
            return self.parts[location_list]
        if not location_list:
            raise TypeError('Empty location')
        part = self
        for i in location_list:
            part = part.parts[i]
        return part

    def del_location_value(self, location_list):
        "Deletes the value at this position, location_list being either an integer, a tuple/list of indexes"
        if isinstance(location_list, str):
            try:
                location_list = int(location_list)
            except Exception:
                raise TypeError('Invalid location')
        if isinstance(location_list, int):
            del self[location_list]
            return
        if not location_list:
            raise TypeError('Invalid location')
        if len(location_list) == 1:
            del self[location_list[0]]
            return
        part = self
        for i in location_list[:-1]:
            part = part.parts[i]
        del part[location_list[-1]]

    def __len__(self):
        return len(self.parts)

    def __iter__(self):
        return self.parts.__iter__()

    def __bool__(self):
        return bool(self.parts)

    def insert(self, index, part_obj):
        "Inserts a sub part at index position, index must be an integer"
        self.parts.insert(index, part_obj)


    def data(self):
        "Returns the part as a list"
        if not self.show:
            return []
        if self._error:
            if self.name:
                # insert data-status=error if this is a named widget.
                return ["<span data-status=\"error\">", expand_text(self._error), "</span>"]
            else:
                return ["<span>", expand_text(self._error), "</span>"]

        content = []
        for part in self.parts:
            if isinstance(part, str):
                if part:
                    if (self.tag_name == 'script') or not self.htmlescaped:
                        # append the string without applying html escape or inserting <br />
                        content.append(part)
                    elif (self.tag_name == 'pre') or (self.tag_name == 'textarea'):
                        # append the string, escape html but do not insert <br />
                        content.append(html.escape(part))
                    else:
                        # append the string, escape html and insert <br />  if self.linebreaks is True
                        content.append(expand_text(part, linebreaks=self.linebreaks))
            elif hasattr(part, 'data'):
                content.extend(part.data())
            else:
                str_part = str(part)
                if str_part:
                    content.append(str_part)
            if self.tag_name == "head":
                content.append("\n")
        if (not content) and self.hide_if_empty:
            return []
        # this creates some new lines around head and body tags
        if self.tag_name == "head":
            start_tag = "<{tag_name}{str_attribs}>\n".format(tag_name=self.tag_name, str_attribs=self.attributes_string)
            end_tag = "</{tag_name}>\n".format(tag_name=self.tag_name)
        elif self.tag_name == "body":
            start_tag = "<{tag_name}{str_attribs}>\n".format(tag_name=self.tag_name, str_attribs=self.attributes_string)
            end_tag = "\n</{tag_name}>".format(tag_name=self.tag_name)
        else:
            start_tag = "<{tag_name}{str_attribs}>".format(tag_name=self.tag_name, str_attribs=self.attributes_string)
            end_tag = "</{tag_name}>".format(tag_name=self.tag_name)
        partbytes = [start_tag]
        partbytes.extend(content)
        partbytes.append(end_tag)
        return partbytes


    def outline(self, proj_ident):
        "Creates a list of ['Part', dictionary]"
        part_dict = OrderedDict()
        part_dict["tag_name"] = self.tag_name
        if self.brief:
            part_dict["brief"] = self.brief
        part_dict["show"] = self.show
        part_dict["hide_if_empty"] = self.hide_if_empty
        if self.attribs:
            part_attribs = OrderedDict(sorted(self.attribs.items(), key=lambda t: t[0]))
            part_dict["attribs"] = make_dictionary(part_attribs, proj_ident)
        # now the Part contents in a list
        parts = []
        for item in self.parts:
            if hasattr(item, 'outline'):
                parts.append(item.outline(proj_ident))
            else:
                # must be a text string
                parts.append(['Text', str(item)])
        part_dict["parts"] = parts
        return ['Part', part_dict]


    def __repr__(self):
        return '<' + self.tag_name + '>'

    def __str__(self):
        "Returns a text string to illustrate the element"
        content = ""
        for part in self.parts:
            if isinstance(part, str):
                if part:
                    if (self.tag_name == 'pre') or (self.tag_name == 'script'):
                        content += part
                    elif self.tag_name == 'textarea':
                        content += html.escape(part)
                    else:
                        content += expand_text(part, linebreaks = self.linebreaks)
            elif isinstance(part, Part):
                content += part.string_indent()
            elif isinstance(part, ClosedPart):
                content += part.string_indent()
            else:
                content += str(part)
        start_tag = "\n<{tag_name}{str_attribs}>".format(tag_name=self.tag_name, str_attribs=self.attributes_string)
        if self.tag_name in self.tag_list:
            end_tag = "\n</{tag_name}>".format(tag_name=self.tag_name)
        else:
            end_tag = "</{tag_name}>".format(tag_name=self.tag_name)
        return start_tag+content+end_tag


class ClosedPart(ParentPart):
    """
    Defines a closed tagged part ending in />

    **instance attributes:**

    *attribs*
      A dictionary of attributes, key is attribute name, value is attribute value

    *show*
      A True or false flag, normally True, which indicates the tag will be shown,
      if false the __str__ method returns an empty string

    *tag_name*
      such as 'br'
    """

    def __init__(self, tag_name="br", attribs=None, show=True, brief=''):
        ParentPart.__init__(self, tag_name=tag_name, attribs=attribs, show=show, brief=brief)


    def make_js(self, page, ident_list, environ, call_data, lang):
        "Auto generates the javascript for this part, normally overwritten by child widgets"
        pass

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename='', embedded=('','',None)):
        "Override this to change run time information in this part"
        if placename:
            self.placename = placename
        if not self.ident_string:
            # item is a dynamic part, newly created within a widget
            self.embedded = embedded
            self.ident_string = ident_string
        if self._error:
            if isinstance(self._error, TextBlock):
                self._error.update(page, ident_list, environ, call_data, lang, ident_string, placename, embedded)

    def data(self):
        "Returns the part as a list"
        if not self.show:
            return []
        if self._error:
            if self.name:
                # insert data-status=error if this is a named widget.
                return ["<span data-status=\"error\">", expand_text(self._error), "</span>"]
            else:
                return ["<span>", expand_text(self._error), "</span>"]
        parttext = "<{tag_name}{str_attribs} />".format(tag_name=self.tag_name, str_attribs=self.attributes_string)
        return [parttext]


    def outline(self, proj_ident):
        "Creates a list of ['ClosedPart', dictionary]"
        part_dict = OrderedDict()
        part_dict["tag_name"] = self.tag_name
        if self.brief:
            part_dict["brief"] = self.brief
        part_dict["show"] = self.show
        if self.attribs:
            part_attribs = OrderedDict(sorted(self.attribs.items(), key=lambda t: t[0]))
            part_dict["attribs"] = make_dictionary(part_attribs, proj_ident)
        return ['ClosedPart', part_dict]


    def __repr__(self):
        return '<' + self.tag_name + ' />'


    def __str__(self):
        "Returns a text string to illustrate the element"
        return "\n<{tag_name}{str_attribs} />".format(tag_name=self.tag_name, str_attribs=self.attributes_string)


class Section(Part):
    "This is essentially a Part, but with extra widget dictionary and change attribute"

    def __init__(self, tag_name="div", attribs=None, text="", show=True, hide_if_empty=False, brief=''):
        "As a Part but also has self.widgets"
        Part.__init__(self, tag_name=tag_name, attribs=attribs, text=text, show=show, hide_if_empty=hide_if_empty, brief=brief)
        # self.widgets is a widget name -> widget dictionary
        self.widgets = {}
        # self.validator_scriptlinks is a list of validator module ski_name's
        # calculated when the section is saved, and used when the section is imported
        # into a page to add links to the validator js modules in the page head
        self._validator_scriptlinks = []
        # currently unused, though passed to parts in set_idents
        self.section_places = {}
        # the change uuid is regenerated
        # whenever the item is stored in the database
        self.change = uuid.uuid4().hex

    @property
    def validator_scriptlinks(self):
        return self._validator_scriptlinks

    def load_validator_scriptlinks(self):
        "Called when section saved to database"
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

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename='', embedded=('','',None)):
        "Override this to change run time information in this part and its sub parts"
        if placename:
            self.placename = placename
        if not self.ident_string:
            # item is a dynamic part, newly created within a widget
            self.embedded = embedded
            self.ident_string = ident_string
        try:
            if self._error:
                if isinstance(self._error, TextBlock):
                    self._error.update(page, ident_list, environ, call_data, lang, self.ident_string, self.placename, embedded)
                return
            for index, part in enumerate(self.parts):
                part_ident_string = self.ident_string + "-" + str(index)
                if hasattr(part, "update"):
                    part.update(page, ident_list, environ, call_data, lang, part_ident_string, self.placename, embedded)
        except ValidateError as e:
            if not e.ident_list:
                e.ident_list = ident_list
            raise

    def location_item(self, location):
        "Returns the part or widget at location"
        location_string, container_number, location_list = location
        if not location_string:
            return
        if container_number is None:
            # Not in a widget
            if location_list:
                return self.get_location_value(location_list)
            else:
                return self
        else:
            # location string must be a widget name
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

    def outline(self, proj_ident):
        "Creates a list of ['Section', dictionary]"
        part, part_dict = Part.outline(self, proj_ident)
        return ['Section', part_dict]


class SectionPlaceHolder(object):
    "Instance of this is added to a part, and acts as the placeholder for a section"

    def __init__(self, section_name, placename, multiplier=1, mtag="div", brief=''):
        self.brief = brief
        self.section_name = section_name
        self.placename = placename
        self.mtag = mtag
        self.ident_string = ''
        try:
            mult = int(multiplier)
        except Exception:
            mult = 1
        if mult<1:
            mult = 1
        self.multiplier=mult

    def section_value(self):
        "Returns section name if section name exists in the project, otherwise None"
        if not self.ident_string:
            return
        proj_ident = self.ident_string.split('_')[0]
        proj = skiboot.getproject(proj_ident)
        if proj is None:
            return
        if self.section_name in proj.list_section_names():
            return self.section_name

    def get_section(self):
        if not self.ident_string:
            return
        proj_ident = self.ident_string.split('_')[0]
        proj = skiboot.getproject(proj_ident)
        if proj is None:
            return
        if self.section_name not in proj.list_section_names():
            return
        return proj.section(self.section_name)

    @property
    def pagepart(self):
        """pagepart is typically head, body or svg.
           ident_string normally starts project_pageident_head-0-... etc
        """
        if not self.ident_string:
            return ''
        page_list = self.ident_string.split('_', 2)
        part_list = page_list[2].split('-', 1)
        return part_list[0]

    @property
    def ident_list(self):
        if not self.ident_string:
            return []
        ident_list = self.ident_string.split('-')
        return [ int(p) for p in ident_list[1:] ]


    def set_idents(self, ident_string, widgets, section_places, embedded):
        "This is called when the page is added to a folder, adds this placeholder to the page section_places dictionary "
        self.ident_string = ident_string
        # add this placeholder to the page section_places dictionary
        section_places[self.placename] = self

    def set_unique_names(self, name_list):
        "Ensures this item has a unique name"
        number = 2
        new_name = self.placename
        while new_name in name_list:
            new_name = self.placename + str(number)
            number += 1
        self.placename = new_name 
        name_list.append(self.placename)

    def outline(self, proj_ident):
        """Creates a list of ['SectionPlaceHolder', dictionary]"""
        part_dict = OrderedDict()
        if self.brief:
            part_dict["brief"] = self.brief
        if self.section_name:
            part_dict["section_name"] = self.section_name
        if self.placename:
            part_dict["placename"] = self.placename
        part_dict["multiplier"] = self.multiplier
        part_dict["mtag"] = self.mtag
        return ['SectionPlaceHolder', part_dict]


    def __str__(self):
        return ''


class TextBlock(object):

    def __init__(self, textref='', project='', failmessage=None, escape=True, linebreaks=True, replace_strings=[], show = True):
        # Note project is either '' for a textblock defined in this project, or the proj_ident of a sub project
        self.project = project
        # set show to False if this textblock is not to be shown
        self.show = show
        self.textref = textref
        self._displayedtext = ""
        self._failmessage = failmessage
        self.linebreaks=linebreaks
        self.escape=escape
        # uses the % operator
        self.replace_strings=replace_strings
        self._show_failmessage = False
        # error message
        self._error_message = ''

    def __bool__(self):
        "True if a reference have been set"
        if self.textref:
            return True
        else:
            return False

    def show_error(self, message, message_ref):
        "Called by a widget containing this textblock if the widget wishes to display an error"
        self._error_message = message
        self.textref = message_ref
        # on error, do not place any replace strings
        self.replace_strings=[]

    def failmessage_set(self):
        "Returns True if failmessage has been set, False otherwise"
        return bool(self._failmessage)

    def get_failmessage(self):
        if self._failmessage:
            return self._failmessage
        if self.textref:
            return "failed to read textblocks with ref " + self.textref
        return "failed to read textblocks"

    def set_failmessage(self, message):
        self._failmessage = message

    failmessage = property(get_failmessage, set_failmessage)

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placeholder, embedded):
        if self.project:
            proj_ident = self.project
        else:
            proj_ident = page.ident.proj
        self._show_failmessage = False
        if self._error_message: return
        if not self.textref:
            self._show_failmessage = True
            return
        proj = skiboot.getproject(proj_ident)
        if proj is None:
            self._show_failmessage = True
            return
        result = proj.textblocks.get_text(self.textref, lang)
        if result is None:
            self._show_failmessage = True
        else:
            self._displayedtext = result


    def exists(self, proj_ident=''):
        "Returns true if textref is available in the project"
        if not self.textref:
            return False
        if proj_ident:
            proj = skiboot.getproject(proj_ident)
        elif self.project:
            proj = skiboot.getproject(self.project)
        else:
            return False
        if proj is None:
            return False
        return proj.textblocks.textref_exists(self.textref)


    def outline(self, proj_ident):
        "Creates a list of ['TextBlock', dictionary]"
        part_dict = OrderedDict()
        part_dict["textref"] = self.textref
        if self.project and (self.project != proj_ident):
            part_dict["project"] = self.project
        if self.failmessage:
            part_dict["failmessage"] = self.failmessage
        part_dict["show"] = self.show
        part_dict["escape"] = self.escape
        part_dict["linebreaks"] = self.linebreaks
        if self.replace_strings:
            part_dict["replace_strings"] = make_list(self.replace_strings, proj_ident)
        return ['TextBlock', part_dict]

  
    def __str__(self):
        "Returns the text"
        if self._error_message:
            return expand_text(self._error_message, escape=self.escape, linebreaks=self.linebreaks)
        if self._show_failmessage:
            return expand_text(self.failmessage, escape=self.escape, linebreaks=self.linebreaks)
        return expand_text(self._displayedtext, escape=self.escape, linebreaks=self.linebreaks, replace_strings=self.replace_strings)


class HTMLSymbol(object):

    def __init__(self, text=''):
        self.text=text

    def __bool__(self):
        "True if text has been set"
        return bool(self.text)

    def outline(self, proj_ident):
        """Creates a list of ['HTMLSymbol', {'text':text}]"""
        part_dict = OrderedDict()
        part_dict["text"] = self.text
        return ['HTMLSymbol', part_dict]

    def __str__(self):
        "Returns the text"
        return self.text


class Comment(object):

    def __init__(self, text=''):
        self._text=text.replace("--", "  ")

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text=text.replace("--", "  ")

    text = property(get_text, set_text, doc="Text of the comment, not including <!-- and --> parts")

    def outline(self, proj_ident):
        """Creates a list of ['Comment', {'text':text}]"""
        part_dict = OrderedDict()
        part_dict["text"] = self._text
        return ['Comment', part_dict]

    def __bool__(self):
        "True if text has been set"
        return bool(self._text)

    def __str__(self):
        "Returns the text"
        return  "\n<!--" + self._text + "-->\n"

