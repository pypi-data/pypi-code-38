


"""Contains widgets displaying confirm/cancel messages and buttons"""


from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict



class ConfirmBox1(Widget):
    """A div with a paragraph of text and two buttons, each with three optional get fields."""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'hide':FieldArg("boolean", False, jsonset=True),
                        'boxdiv_class':FieldArg("cssclass", ""),
                        'paradiv_class':FieldArg("cssclass", ""),
                        'para_class':FieldArg("cssclass", ""),
                        'buttondiv_class':FieldArg("cssclass", ""),
                        'para_text':FieldArg("text", "", jsonset=True),

                        'button1_class':FieldArg("cssclass", ""),
                        'button1_style':FieldArg("cssstyle", ""),
                        'link_ident1':FieldArg("url", ''),
                        'json_ident1':FieldArg("url", ''),
                        'get_field1_1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field1_2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field1_3':FieldArg("text","", valdt=True, jsonset=True),
                        'button_text1':FieldArg("text", "Cancel"),

                        'button2_class':FieldArg("cssclass", ""),
                        'button2_style':FieldArg("cssstyle", ""),
                        'link_ident2':FieldArg("url", ''),
                        'json_ident2':FieldArg("url", ''),
                        'get_field2_1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field2_2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field2_3':FieldArg("text","", valdt=True, jsonset=True),
                        'button_text2':FieldArg("text", "Confirm")
            }


    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        boxdiv_class: class of the box holding paragraph and buttons
        paradiv_class: The class of the div containing the paragraph
        para_class: The class of the paragraph
        buttondiv_class: The class of the div holding the buttons
        json_ident1: The url, ident or label to link by button1, expecting a json file to be returned
        json_ident2: The url, ident or label to link by button2, expecting a json file to be returned
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div")
        # The location 0,0 is the div containing the paragraph
        self[0][0] = tag.Part(tag_name="div")
        self[0][0][0] = tag.Part(tag_name="p")
        self[0][0][0][0] = ''
        # div holding buttons
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = tag.Part(tag_name="a", attribs={"role":"button"})
        self[0][1][1] = tag.Part(tag_name="a", attribs={"role":"button"})
        self._jsonurl1 =''
        self._jsonurl2 =''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the box"
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if self.get_field_value("boxdiv_class"):
            self[0].update_attribs({"class":self.get_field_value('boxdiv_class')})
        if self.get_field_value("buttondiv_class"):
            self[0][1].update_attribs({"class":self.get_field_value('buttondiv_class')})
        if self.get_field_value("paradiv_class"):
            self[0][0].update_attribs({"class":self.get_field_value('paradiv_class')})
        if self.get_field_value("para_class"):
            self[0][0][0].update_attribs({"class":self.get_field_value('para_class')})
        if self.get_field_value("para_text"):
            self[0][0][0][0] = self.get_field_value('para_text')
        # button1
        if self.get_field_value('button1_class'):
            self[0][1][0].update_attribs({"class":self.get_field_value('button1_class')})
        if self.get_field_value('button1_style'):
            self[0][1][0].update_attribs({"style":self.get_field_value('button1_style')})
        if self.get_field_value("json_ident1"):
            self._jsonurl1 = skiboot.get_url(self.get_field_value("json_ident1"), proj_ident=page.proj_ident)
        if not self.get_field_value("link_ident1"):
            self[0][1][0][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident1"), proj_ident=page.proj_ident)
            if not url:
                self[0][1][0][0] = "Warning: broken link"
            else:
                if self.get_field_value("button_text1"):
                    self[0][1][0][0] = self.get_field_value("button_text1")
                else:
                    self[0][1][0][0] = url
                # create a url for the href
                get_fields = {self.get_formname("get_field1_1"):self.get_field_value("get_field1_1"),
                                            self.get_formname("get_field1_2"):self.get_field_value("get_field1_2"),
                                            self.get_formname("get_field1_3"):self.get_field_value("get_field1_3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][1][0].update_attribs({"href": url})
        # button2
        if self.get_field_value('button2_class'):
            self[0][1][1].update_attribs({"class":self.get_field_value('button2_class')})
        if self.get_field_value('button2_style'):
            self[0][1][1].update_attribs({"style":self.get_field_value('button2_style')})
        if self.get_field_value("json_ident2"):
            self._jsonurl2 = skiboot.get_url(self.get_field_value("json_ident2"), proj_ident=page.proj_ident)
        if not self.get_field_value("link_ident2"):
            self[0][1][1][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident2"), proj_ident=page.proj_ident)
            if not url:
                self[0][1][1][0] = "Warning: broken link"
            else:
                if self.get_field_value("button_text2"):
                    self[0][1][1][0] = self.get_field_value("button_text2")
                else:
                    self[0][1][1][0] = url
                # create a url for the href
                get_fields = {self.get_formname("get_field2_1"):self.get_field_value("get_field2_1"),
                              self.get_formname("get_field2_2"):self.get_field_value("get_field2_2"),
                              self.get_formname("get_field2_3"):self.get_field_value("get_field2_3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][1][1].update_attribs({"href": url})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a click event handler"""
        if not (self._jsonurl1 or self._jsonurl2):
            return
        jscript = """  $("#{ident} a").click(function (e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident = self.get_id())
        if self._jsonurl1 and self._jsonurl2:
            return jscript + self._make_fieldvalues( url1=self._jsonurl1, url2=self._jsonurl2)
        elif self._jsonurl1:
            return jscript + self._make_fieldvalues( url1=self._jsonurl1)
        else:
            return jscript + self._make_fieldvalues( url2=self._jsonurl2)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- With boxdiv_class -->
    <div> <!-- With paradiv_class -->
      <p> <!-- With class set by para_class -->
          <!-- para_text shown here -->
      </p>
    </div>
    <div>    <!-- with class set by buttondiv_class -->
      <a role="button" href="#">
        <!-- With class set by button1_class, and the href link will be the url of the link_ident1 with the three get_fields -->
        <!-- the button will show the button_text1 -->
      </a>
      <a role="button" href="#">
        <!-- With class set by button2_class, and the href link will be the url of the link_ident2 with the three get_fields -->
        <!-- the button will show the button_text2 -->
      </a>
    </div>
  </div>
</div>"""


class ConfirmBox2(Widget):
    """A div - normally used for modal background containing a  div with a paragraph
         of text and two buttons, each with three optional get fields.
         The 'cancel' button1 hides the widget without making a call if javascript is available
         if not, then the link is called."""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'hide':FieldArg("boolean", False, jsonset=True),
                        'boxdiv_class':FieldArg("cssclass", ""),
                        'paradiv_class':FieldArg("cssclass", ""),
                        'para_class':FieldArg("cssclass", ""),
                        'buttondiv_class':FieldArg("cssclass", ""),
                        'para_text':FieldArg("text", "", jsonset=True),

                        'button1_class':FieldArg("cssclass", ""),
                        'button1_style':FieldArg("cssstyle", ""),
                        'link_ident1':FieldArg("url", ''),
                        'get_field1_1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field1_2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field1_3':FieldArg("text","", valdt=True, jsonset=True),
                        'button_text1':FieldArg("text", "Cancel"),

                        'button2_class':FieldArg("cssclass", ""),
                        'button2_style':FieldArg("cssstyle", ""),
                        'link_ident2':FieldArg("url", ''),
                        'get_field2_1':FieldArg("text", "", valdt=True, jsonset=True),
                        'get_field2_2':FieldArg("text","", valdt=True, jsonset=True),
                        'get_field2_3':FieldArg("text","", valdt=True, jsonset=True),
                        'button_text2':FieldArg("text", "Confirm")
            }


    def __init__(self, name=None, brief='', **field_args):
        """
        hide: If True, sets display: none; on the widget, can be set/unset via JSON file
              If False, or error sets display:block
        boxdiv_class: class of the box holding paragraph and buttons
        paradiv_class: The class of the div containing the paragraph
        para_class: The class of the text paragraph
        buttondiv_class: The class of the div holding the buttons
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div")
        # The location 0,0 is the div containing the paragraph
        self[0][0] = tag.Part(tag_name="div")
        self[0][0][0] = tag.Part(tag_name="p")
        self[0][0][0][0] = ''
        # div holding buttons
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = tag.Part(tag_name="a", attribs={"role":"button"})
        self[0][1][1] = tag.Part(tag_name="a", attribs={"role":"button"})

    def _build(self, page, ident_list, environ, call_data, lang):
        "build the box"
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if self.get_field_value("boxdiv_class"):
            self[0].update_attribs({"class":self.get_field_value('boxdiv_class')})
        if self.get_field_value("buttondiv_class"):
            self[0][1].update_attribs({"class":self.get_field_value('buttondiv_class')})
        if self.get_field_value("paradiv_class"):
            self[0][0].update_attribs({"class":self.get_field_value('paradiv_class')})
        if self.get_field_value("para_class"):
            self[0][0][0].update_attribs({"class":self.get_field_value('para_class')})
        if self.get_field_value("para_text"):
            self[0][0][0][0] = self.get_field_value('para_text')
        # button1
        if self.get_field_value('button1_class'):
            self[0][1][0].update_attribs({"class":self.get_field_value('button1_class')})
        if self.get_field_value('button1_style'):
            self[0][1][0].update_attribs({"style":self.get_field_value('button1_style')})
        if not self.get_field_value("link_ident1"):
            self[0][1][0][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident1"), proj_ident=page.proj_ident)
            if not url:
                self[0][1][0][0] = "Warning: broken link"
            else:
                if self.get_field_value("button_text1"):
                    self[0][1][0][0] = self.get_field_value("button_text1")
                else:
                    self[0][1][0][0] = url
                # create a url for the href
                get_fields = {self.get_formname("get_field1_1"):self.get_field_value("get_field1_1"),
                                            self.get_formname("get_field1_2"):self.get_field_value("get_field1_2"),
                                            self.get_formname("get_field1_3"):self.get_field_value("get_field1_3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][1][0].update_attribs({"href": url})
        # button2
        if self.get_field_value('button2_class'):
            self[0][1][1].update_attribs({"class":self.get_field_value('button2_class')})
        if self.get_field_value('button2_style'):
            self[0][1][1].update_attribs({"style":self.get_field_value('button2_style')})
        if not self.get_field_value("link_ident2"):
            self[0][1][1][0] = "Warning: broken link"
        else:
            url = skiboot.get_url(self.get_field_value("link_ident2"), proj_ident=page.proj_ident)
            if not url:
                self[0][1][1][0] = "Warning: broken link"
            else:
                if self.get_field_value("button_text2"):
                    self[0][1][1][0] = self.get_field_value("button_text2")
                else:
                    self[0][1][1][0] = url
                # create a url for the href
                get_fields = {self.get_formname("get_field2_1"):self.get_field_value("get_field2_1"),
                                            self.get_formname("get_field2_2"):self.get_field_value("get_field2_2"),
                                            self.get_formname("get_field2_3"):self.get_field_value("get_field2_3")}
                url = self.make_get_url(page, url, get_fields, True)
                self[0][1][1].update_attribs({"href": url})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a click event handler on the a buttons"""
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
    <div> <!-- With paradiv_class -->
      <p> <!-- With class set by para_class -->
        <!-- para_text shown here -->
      </p>
    </div>
    <div>    <!-- with class set by buttondiv_class -->
      <a role="button" href="#">
        <!-- With class set by button1_class, and the href link will be the url of the link_ident1 with the three get_fields -->
        <!-- the button will show the button_text1 -->
      </a>
      <a role="button" href="#">
        <!-- With class set by button2_class, and the href link will be the url of the link_ident2 with the three get_fields -->
        <!-- the button will show the button_text2 -->
      </a>
    </div>
  </div>
</div>"""


class AlertClear1(Widget):
    """A div - normally used for modal background containing a div with a paragraph
         of text or error message and an X button with three optional get fields.
         The 'clear' button hides the widget without making a call if javascript is available
         if not, then the link is called."""

    error_location = (0,1,0,0)

    arg_descriptions = {'hide':FieldArg("boolean", True, jsonset=True),
                        'para_text':FieldArg("text", "", jsonset=True),
                        'pre_line':FieldArg("boolean", True),
                        'boxdiv_class':FieldArg("cssclass", ""),
                        'error_class':FieldArg("cssclass", ""),
                        'inner_class':FieldArg("cssclass", ""),
                        'inner_style':FieldArg("cssstyle", ""),
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
        para_text: The text appearing in the paragraph, replaced on error by error message
        pre_line: If True, sets style="white-space: pre-line;" into the paragraph which preserves
                  new line breaks
        boxdiv_class: class of the box holding paragraph and button
        inner_class: The CSS class of the div holding the paragraph, replaced by error_class on error
        error_class: The CSS class of the div holding the paragraph when error raised
        buttondiv_class: The class of the div holding the button
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="div")
        # div holding X button
        self[0][0] = tag.Part(tag_name="div")
        self[0][0][0] = tag.Part(tag_name="a", attribs={"role":"button"})
        self[0][0][0][0] = tag.HTMLSymbol("&times;")
        # The location 0,1 is the div holding the text paragraph
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
        if self.error_status and self.get_field_value("error_class"):
            self[0][1].update_attribs({"class":self.get_field_value('error_class')})
        elif self.get_field_value("inner_class"):
            self[0][1].update_attribs({"class":self.get_field_value('inner_class')})
        if self.get_field_value("inner_style"):
            self[0][1].update_attribs({'style':self.get_field_value("inner_style")})
        # insert an id for setting the error class
        self[0][1].insert_id()
        # paragraph
        if self.get_field_value("pre_line"):
            self[0][1][0].attribs={"style":"white-space: pre-line;"}
        if not self.error_status:
            self[0][1][0][0] = self.get_field_value("para_text")
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
        # return this javascript and the inner class and id
        return jscript + self._make_fieldvalues('inner_class', 'error_class', inner_id=self[0][1].get_id())


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
    <div> <!-- With class set by inner_class, replaced by error_class on error-->
      <p style = "white-space: pre-line;"> <!-- style set if pre_line is True -->
        <!-- para_text or error message appears in this paragraph -->
      </p>
    </div>
  </div>
</div>"""


