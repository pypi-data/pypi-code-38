

"""Defines widgets which may be used as page footers"""

from string import Template
from .. import skiboot
from .. import tag
from . import Widget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class SimpleFooter(Widget):
    """Defines a div, with a paragraph of text"""

    error_location = (0,0,0)

    arg_descriptions = {
                        'footer_text':FieldArg("text",'', jsonset=True),
                        'para_class':FieldArg("cssclass",""),
                        'error_class':FieldArg("cssclass", ""),
                        'paradiv_class':FieldArg("cssclass",""),
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
         footer_text: The text to appear in the footer
         para_class: css class of the footer text paragraph
         error_class: css class of the error paragraph
        """

        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name="div")
        self[1][0] = tag.Part(tag_name="p")

    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the paragraph"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('paradiv_class'):
            self[1].update_attribs({"class":self.get_field_value('paradiv_class')})
        if self.get_field_value('para_class'):
            self[1][0].update_attribs({"class":self.get_field_value('para_class')})
        if self.get_field_value("footer_text"):
            self[1][0][0] = self.get_field_value("footer_text")
        # set an id in the footer_text paragraph
        self[1][0].insert_id()

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """stores ident in footer text paragraph"""
        return self._make_fieldvalues(textident = self[1][0].get_id()) # ident of the footer_text paragraph

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p>       <!-- Any error text appears here --> </p>
  </div>
  <div>  <!-- with class paradiv_class -->
    <p>  <!-- with class para_class -->
    <!-- footer_text appears in this paragraph -->
    </p>
  </div>
</div>
"""

