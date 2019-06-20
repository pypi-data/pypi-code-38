

"""Contains commonly used error display widgets"""

from string import Template

from .. import skiboot
from .. import tag
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class ErrorCode(Widget):
    """A div containing a paragraph, with an error code, and a second paragraph containing text,
       if an error is raised, then the text is changed
       for the error_message and the error_class given to the paragraph"""

    error_location = (1,0)

    arg_descriptions = {'para_text':FieldArg("text", "", jsonset=True),
                        'para_class':FieldArg("cssclass", ""),
                        'code_class':FieldArg("cssclass", ""),
                        'error_class':FieldArg("cssclass", ""),
                        'pre_line':FieldArg("boolean", True),
                        'code':FieldArg("integer", "0")
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        para_text: The text appearing in the paragraph
        para_class: The class of the paragraph
        error_class: The class of the error text - which provides the appearance via CSS
                     replaces para_class on error.
        pre_line: If True, sets style="white-space: pre-line;" into the paragraph which preserves
                  new line breaks
        code: integer code number
        """
        # pass fields to Widget
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name='p')
        self[0][0] = ''
        self[1] = tag.Part(tag_name='p')
        # do not insert <br /> - leave that to pre_line
        self[1].linebreaks=False
        self[1][0] = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value('code_class'):
            self[0].update_attribs({"class":self.get_field_value('code_class')})
        if self.get_field_value("code"):
            self[0][0] = "Error code : " + str(self.get_field_value("code"))
        else:
            self[0][0] = "Error code : 0"
        if self.get_field_value("pre_line"):
            self[1].attribs={"style":"white-space: pre-line;"}
        if self.get_field_value('para_class'):
            self[1].update_attribs({"class":self.get_field_value('para_class')})
        # self[1][0] could be set by an error message
        if not self.error_status:
            self[1][0] = self.get_field_value("para_text")
        if self.error_status and self.get_field_value('error_class'):
            self[1].update_attribs({"class":self.get_field_value('error_class')})

            
    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets fieldvalues"""
        return self._make_fieldvalues('para_class', 'error_class')


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
    <p> <!-- with class code_class -->
        Error code : n
        <!-- with n set to the number given in field 'code' -->
    </p>
    <p style = "white-space: pre-line;">
    <!-- with class para_class, and style set if pre_line is True -->
    <!-- and class changed to error_class on error -->
        <!-- set with para_text, replaced by error message on error -->
    </p>
</div>"""




class ErrorDiv(Widget):
    """A div containing a div with paragraph containing error text - normally both div's are hidden.
       though the outer one can be displayed if required
       Can contain further html / widgets after the error div
       On displaying an error, the both div's are shown, and paragraph text set to error message."""

    _container = ((1,),)

    error_location = (0,0,0)

    arg_descriptions = {
                        'hide':FieldArg("boolean", True, jsonset=True),
                        'error_class':FieldArg("cssclass", ""),
                        'container_class':FieldArg("cssclass", '')
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        error_class: The CSS class of the paragraph
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The location 1, is available as a container
        self[1] = tag.Part(tag_name="div")
        self[1][0] = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if self.get_field_value('error_class'):
            self[0].attribs = {'class':self.get_field_value('error_class')}
        if self.error_status:
            self.update_attribs({"style":"display: block;"})
            self[0].del_one_attrib("style")
        # the div holding the container
        if self.get_field_value('container_class'):
            self[1].attribs = {"class": self.get_field_value('container_class')}

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class, normally hidden -->
  <div>  !-- class set to error_class -->
    <p> <!-- error message appears in this paragraph --> </p>
  </div>
  <div>  <!-- this div has the class attribute set to container_class -->
    <!-- container 0 for further html -->
  </div>
</div>"""


class ErrorPara(Widget):
    """A paragraph containing error text - normally hidden, displayed on error"""

    error_location = 0

    arg_descriptions = {
                        'hide':FieldArg("boolean", True, jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        """
        Widget.__init__(self, name=name, tag_name="p", brief=brief, **field_args)
        self[0] = self.error_message

    def _build(self, page, ident_list, environ, call_data, lang):
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<p>  <!-- with widget id and class widget_class, normally hidden,
          shown when an error is displayed. -->
  <!-- error message appears in this paragraph -->
</p>
"""


class ErrorClear1(Widget):
    """A div - normally used for modal background containing a div with a paragraph
         of text or error message and a clear button with three optional get fields.
         The 'clear' button hides the widget without making a call if javascript is available
         if not, then the link is called."""

    error_location = (0,0,0,0)

    arg_descriptions = {'hide':FieldArg("boolean", True, jsonset=True),
                        'para_text':FieldArg("text", "", jsonset=True),
                        'pre_line':FieldArg("boolean", True),
                        'boxdiv_class':FieldArg("cssclass", ""),
                        'error_class':FieldArg("cssclass", ""),
                        'buttondiv_class':FieldArg("cssclass", ""),
                        'buttondiv_style':FieldArg("cssstyle", ""),
                        'button_class':FieldArg("cssclass", ""),
                        'link_ident':FieldArg("url", ''),
                        'get_field1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field3':FieldArg("text","", valdt=True, jsonset=True),
                        'button_text':FieldArg("text", "Clear"),
            }


    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        para_text: The text appearing in the paragraph, replaced on error by error message
        pre_line: If True, sets style="white-space: pre-line;" into the paragraph which preserves
                  new line breaks
        boxdiv_class: class of the box holding paragraph and button
        error_class: The CSS class of the div holding the paragraph
        buttondiv_class: The class of the div holding the button
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div")
        # The location 0,0 is the div holding the text paragraph
        self[0][0] = tag.Part(tag_name="div")
        self[0][0][0] = tag.Part(tag_name="p")
        # do not set any linebreaks, leave that to pre-line
        self[0][0][0].linebreaks = False
        self[0][0][0][0] = ''
        # div holding buttons
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = tag.Part(tag_name="a", attribs={"role":"button"})

    def _build(self, page, ident_list, environ, call_data, lang):
        "build the box"
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if self.get_field_value("boxdiv_class"):
            self[0].update_attribs({"class":self.get_field_value('boxdiv_class')})
        if self.get_field_value("error_class"):
            self[0][0].update_attribs({"class":self.get_field_value('error_class')})
        if self.get_field_value("buttondiv_class"):
            self[0][1].update_attribs({"class":self.get_field_value('buttondiv_class')})
        if self.get_field_value("buttondiv_style"):
            self[0][1].update_attribs({'style':self.get_field_value("buttondiv_style")})

        if self.get_field_value("pre_line"):
            self[0][0][0].attribs={"style":"white-space: pre-line;"}

        if not self.error_status:
            self[0][0][0][0] = self.get_field_value("para_text")

        # button
        if self.get_field_value('button_class'):
            self[0][1][0].update_attribs({"class":self.get_field_value('button_class')})
        if not self.get_field_value("link_ident"):
            self[0][1][0][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident"), proj_ident=page.proj_ident)
            if not url:
                self[0][1][0][0] = "Warning: broken link"
            else:
                if self.get_field_value("button_text"):
                    self[0][1][0][0] = self.get_field_value("button_text")
                else:
                    self[0][1][0][0] = url
                # create a url for the href
                get_fields = {self.get_formname("get_field1"):self.get_field_value("get_field1"),
                                            self.get_formname("get_field2"):self.get_field_value("get_field2"),
                                            self.get_formname("get_field3"):self.get_field_value("get_field3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][1][0].update_attribs({"href": url})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a click event handler on the a button"""
        jscript = """  $("#{ident} a").click(function (e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident = self.get_id())
        return jscript


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- With boxdiv_class -->
    <div> <!-- With class set by error_class -->
      <p style = "white-space: pre-line;"> <!-- style set if pre_line is True -->
        <!-- para_text or error message appears in this paragraph -->
      </p>
    </div>
    <div>    <!-- with class set by buttondiv_class and style by buttondiv_style -->
      <a role="button" href="#">
        <!-- With class set by button_class, and the href link will be the url of the link_ident with the three get_fields -->
        <!-- the button will show the button_text -->
      </a>
    </div>
  </div>
</div>"""


class ErrorClear2(Widget):
    """A div - normally used for modal background containing a div with a paragraph
         of error message and an X button with three optional get fields.
         The 'X' button hides the widget without making a call if javascript is available
         if not, then the link is called."""

    error_location = (0,1,0,0)

    arg_descriptions = {'hide':FieldArg("boolean", True, jsonset=True),
                        'pre_line':FieldArg("boolean", True),
                        'boxdiv_class':FieldArg("cssclass", ""),
                        'error_class':FieldArg("cssclass", ""),
                        'buttondiv_class':FieldArg("cssclass", ""),
                        'buttondiv_style':FieldArg("cssstyle", ""),
                        'button_class':FieldArg("cssclass", ""),
                        'link_ident':FieldArg("url", ''),
                        'get_field1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field3':FieldArg("text","", valdt=True, jsonset=True)
            }


    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        pre_line: If True, sets style="white-space: pre-line;" into the paragraph which preserves
                  new line breaks
        boxdiv_class: class of the box holding paragraph and button
        error_class: The CSS class of the div holding the paragraph
        buttondiv_class: The class of the div holding the button
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div")
        # div holding X button
        self[0][0] = tag.Part(tag_name="div")
        self[0][0][0] = tag.Part(tag_name="a", attribs={"role":"button"})
        self[0][0][0][0] = tag.HTMLSymbol("&times;")
        # The location 0,1 is the div holding the text
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = tag.Part(tag_name="p")
        # do not set any linebreaks, leave that to pre-line
        self[0][1][0].linebreaks = False
        self[0][1][0][0] = ''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the box"
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if self.get_field_value("boxdiv_class"):
            self[0].update_attribs({"class":self.get_field_value('boxdiv_class')})
        # buttondiv
        if self.get_field_value("buttondiv_class"):
            self[0][0].update_attribs({"class":self.get_field_value('buttondiv_class')})
        if self.get_field_value("buttondiv_style"):
            self[0][0].update_attribs({'style':self.get_field_value("buttondiv_style")})
        # inner div
        if self.get_field_value("error_class"):
            self[0][1].update_attribs({"class":self.get_field_value('error_class')})
        # paragraph
        if self.get_field_value("pre_line"):
            self[0][1][0].attribs={"style":"white-space: pre-line;"}
        if not self.error_status:
            self[0][1][0][0] = self.get_field_value("show_error")
        # insert an id into the paragraph for setting the error text
        self[0][1][0].insert_id()
        # button
        if self.get_field_value('button_class'):
            self[0][0][0].update_attribs({"class":self.get_field_value('button_class')})
        if not self.get_field_value("link_ident"):
            self[0][1][0][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident"), proj_ident=page.proj_ident)
            if url:
                # create a url for the href
                get_fields = {self.get_formname("get_field1"):self.get_field_value("get_field1"),
                              self.get_formname("get_field2"):self.get_field_value("get_field2"),
                              self.get_formname("get_field3"):self.get_field_value("get_field3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][0][0].update_attribs({"href": url})
            else:
                self[0][1][0][0] = "Warning: broken link"


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a click event handler on the a button"""
        jscript = """  $("#{ident} a").click(function (e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident = self.get_id())
        # return this javascript and the paragraph id
        return jscript + self._make_fieldvalues(para_id=self[0][1][0].get_id())


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- With boxdiv_class -->
    <div>    <!-- with class set by buttondiv_class and style by buttondiv_style -->
      <a role="button" href="#">
        <!-- With class set by button_class, and the href link will be the url of the link_ident with the three get_fields -->
        <!-- the button will show the &times; symbol -->
      </a>
    </div>
    <div> <!-- With class set by error_class -->
      <p style = "white-space: pre-line;"> <!-- style set if pre_line is True -->
        <!-- error message appears in this paragraph -->
      </p>
    </div>
  </div>
</div>"""


