


"""Defines widgets to aid in debugging"""

from string import Template
import pprint

from .. import skiboot
from .. import tag
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class ShowEnviron(Widget):
    """This class is a div, followed by a paragraph of toptext, and then
       a <pre> tag with text content showing the environ dictionary.
       On error a paragraph above the toptext paragraph appears with error_class
    """

    error_location = (0,0,0)

    arg_descriptions = {'toptext':FieldArg("text", 'DEBUG MODE IS ON'),
                        'para_class':FieldArg("cssclass",""),
                        'error_class':FieldArg("cssclass", ""),
                        'show':FieldArg("boolean", True)  # set here as this value has a special textblock description
                       }

    def __init__(self, name=None, brief='', **field_args):
        """toptext: The text appearing above environ data
           error_class: If given the class of the error text"""
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name="p", hide_if_empty=True)
        self[2] = tag.Part(tag_name="pre")

    # special widget, not shown if debug is off

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded):
        """Sets self.show False if debug is False"""
        if not skiboot.get_debug():
            self.show = False
            return
        Widget.update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded)

    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('para_class'):
            self[1].update_attribs({"class":self.get_field_value('para_class')})
        self[1].text = self.get_field_value('toptext')
        self[2].text = pprint.pformat(environ)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <p>  <!-- with class para_class -->
  <!-- toptext appears in this paragraph, if there is no toptext the paragraph is not shown -->
  </p>
  <pre>
  <!-- environ variables are displayed here -->
  </pre>
</div>"""


class ShowCallData(Widget):
    """This class is a div, followed by a paragraph of toptext, and then
       a <pre> tag with text content showing the call_data dictionary.
       On error a paragraph above the toptext paragraph appears with error_class
    """

    error_location = (0,0,0)

    arg_descriptions = {'toptext':FieldArg("text", 'DEBUG MODE IS ON'),
                        'para_class':FieldArg("cssclass",""),
                        'error_class':FieldArg("cssclass", ""),
                        'show':FieldArg("boolean", True)  # set here as this value has a special textblock description
                       }

    def __init__(self, name=None, brief='', **field_args):
        """toptext: The text appearing above call_data
           error_class: If given the class of the error text"""
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name="p", hide_if_empty=True)
        self[2] = tag.Part(tag_name="pre")

    # special widget, not shown if debug is off

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded):
        """Sets self.show False if debug is False"""
        if not skiboot.get_debug():
            self.show = False
            return
        Widget.update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded)

    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('para_class'):
            self[1].update_attribs({"class":self.get_field_value('para_class')})
        self[1].text = self.get_field_value('toptext')
        self[2].text = pprint.pformat(call_data)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <p>  <!-- with class para_class -->
  <!-- toptext appears in this paragraph, if there is no toptext the paragraph is not shown -->
  </p>
  <pre>
  <!-- The call_data displayed here -->
  </pre>
</div>"""


class ShowResponders(Widget):
    """This class is a div containing a table with columns
       showing the responders called to access this page
    """

    error_location = (0,0,0)

    arg_descriptions = {'toptext':FieldArg("text", 'DEBUG MODE IS ON'),
                        'para_class':FieldArg("cssclass",""),
                        'error_class':FieldArg("cssclass", ""),
                        'paradiv_class':FieldArg("cssclass",""),
                        'table_class':FieldArg("cssclass",""),
                        'show':FieldArg("boolean", True)  # set here as this value has a special textblock description
                       }

    def __init__(self, name=None, brief='', **field_args):
        "Create the div and table, does not require any arguments"
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name="div")
        self[1][0] = tag.Part(tag_name="p", hide_if_empty=True)
        self[2] = tag.Part(tag_name="table")

    # special widget, not shown if debug is off

    def update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded):
        """Sets self.show False if debug is False"""
        if not skiboot.get_debug():
            self.show = False
            return
        Widget.update(self, page, ident_list, environ, call_data, lang, ident_string, placename, embedded)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Update the table to show responder data"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('paradiv_class'):
            self[1].update_attribs({"class":self.get_field_value('paradiv_class')})
        if self.get_field_value('para_class'):
            self[1][0].update_attribs({"class":self.get_field_value('para_class')})
        self[1][0].text = self.get_field_value('toptext')
        if self.get_field_value('table_class'):
            self[2].attribs = {"class":self.get_field_value('table_class')}
        # The ident_list is the list of responder idents used when calling this page
        if not ident_list:
            self[2][0] = tag.Part(tag_name="tr")
            self[2][0][0] = tag.Part(tag_name="td", text=page.ident.to_comma_str())
            self[2][0][1] = tag.Part(tag_name="td", text='This page')
            self[2][0][2] = tag.Part(tag_name="td", text=page.brief)
            return
        for index, ident in enumerate(ident_list):
            item = skiboot.from_ident(ident)
            self[2][index] = tag.Part(tag_name="tr")
            self[2][index][0] = tag.Part(tag_name="td", text=ident.to_comma_str())
            self[2][index][1] = tag.Part(tag_name="td", text=item.responder.__class__.__name__)
            self[2][index][2] = tag.Part(tag_name="td", text=item.brief)
        last_line = tag.Part(tag_name="tr")
        last_line[0] = tag.Part(tag_name="td", text=page.ident.to_comma_str())
        last_line[1] = tag.Part(tag_name="td", text='This page')
        last_line[2] = tag.Part(tag_name="td", text=page.brief)
        self[2].append(last_line)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <div>  <!-- with class paradiv_class -->
    <p>  <!-- with class para_class -->
    <!-- toptext appears in this paragraph, if there is no toptext the paragraph is not shown -->
    </p>
  </div>
  <table>   <!-- with class table_class -->
   <!-- a row for every Responder page visited, with columns; page ident, responder class, page brief --> 
  </table>
</div>"""


