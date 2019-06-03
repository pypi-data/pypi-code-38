

"""Contains widgets for logging in to a service"""


from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class Pin4(Widget):
    """Defines a form containing four single character input fields."""


    _container = ((0,1),)

    error_location = (0,0,0,0)

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'hide':FieldArg("boolean", False, jsonset=True),
                        'autofocus':FieldArg("boolean", True),
                        'action':FieldArg("url", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'button_text':FieldArg("text", 'Submit'),
                        'pin1':FieldArg("boolean", True, valdt=True),
                        'pin2':FieldArg("boolean", True, valdt=True),
                        'pin3':FieldArg("boolean", True, valdt=True),
                        'pin4':FieldArg("boolean", True, valdt=True),
                        'inner_div_class':FieldArg("cssclass", ''),
                        'char_div_class':FieldArg("cssclass", ''),
                        'char_div_style':FieldArg("cssstyle", ''),
                        'butt_div_class':FieldArg("cssclass", ''),
                        'button_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ""),
                        'left_label':FieldArg("text", ''),
                        'left_class':FieldArg("cssclass", ''),
                        'right_label':FieldArg("text", ''),
                        'right_class':FieldArg("cssclass", ''),
                       }


    def __init__(self, name=None, brief='', **field_args):
        """
        action: The page ident this button links to
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        button_text: The text on the button
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # inner div
        self[0] = tag.Part(tag_name="div")
        # error div
        self[0][0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0][0] = tag.Part(tag_name="p")
        self[0][0][0][0] = ''
        # container at 0,1
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = ""
        # form containing input text fields and button
        self[0][2] = tag.Part(tag_name="form", attribs={"role":"form", "method":"post"})
        # div containing text character fields
        self[0][2][0] = tag.Part(tag_name='div')
        # the first text input field
        self[0][2][0][0] = tag.ClosedPart(tag_name="input", attribs ={"type":"password",
                                                                      "size":"1",
                                                                      "maxlength":"1",
                                                                      "required":"required",
                                                                      "style":"width:2em;"})
        self[0][2][0][1] = "-"
        # the second text input field
        self[0][2][0][2] = tag.ClosedPart(tag_name="input", attribs ={"type":"password",
                                                                      "size":"1",
                                                                      "maxlength":"1",
                                                                      "required":"required",
                                                                      "style":"width:2em;"})
        self[0][2][0][3] = "-"
        # the third text input field
        self[0][2][0][4] = tag.ClosedPart(tag_name="input", attribs ={"type":"password",
                                                                      "size":"1",
                                                                      "maxlength":"1",
                                                                      "required":"required",
                                                                      "style":"width:2em;"})
        self[0][2][0][5] = "-"
        # the fourth text input field
        self[0][2][0][6] = tag.ClosedPart(tag_name="input", attribs ={"type":"password",
                                                                      "size":"1",
                                                                      "maxlength":"1",
                                                                      "required":"required",
                                                                      "style":"width:2em;"})
        # div containing submit button
        self[0][2][1] = tag.Part(tag_name='div')
        # the left label
        self[0][2][1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the submit button
        self[0][2][1][1] = tag.ClosedPart(tag_name="input", attribs = {"type":"submit"})
        # the right label
        self[0][2][1][2] = tag.Part(tag_name="label", hide_if_empty=True)



    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        if not self.get_field_value("action"):
            # setting self._error replaces the entire tag
            self._error = "Warning: No form action"
            return
        actionurl = skiboot.get_url(self.get_field_value("action"),  proj_ident=page.proj_ident)
        if not actionurl:
            # setting self._error replaces the entire tag
            self._error = "Warning: broken link"
            return

        if self.get_field_value('inner_div_class'):
            self[0].update_attribs({"class":self.get_field_value('inner_div_class')})

        if self.get_field_value('error_class'):
            self[0][0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0][0].del_one_attrib("style")

        # update the action of the form
        self[0][2].update_attribs({"action": actionurl})

        if self.get_field_value('char_div_class'):
            self[0][2][0].update_attribs({"class":self.get_field_value('char_div_class')})
        if self.get_field_value('char_div_style'):
            self[0][2][0].update_attribs({"style":self.get_field_value('char_div_style')})

        # enable disable the pin number fields

        # first input field
        self[0][2][0][0].update_attribs({"name":self.get_formname('pin1')})
        if not self.get_field_value('pin1'):
            self[0][2][0][0].update_attribs({"disabled":"disabled", "value":"X"})

        # second input field
        self[0][2][0][2].update_attribs({"name":self.get_formname('pin2')})
        if not self.get_field_value('pin2'):
            self[0][2][0][2].update_attribs({"disabled":"disabled", "value":"X"})

        # third input field
        self[0][2][0][4].update_attribs({"name":self.get_formname('pin3')})
        if not self.get_field_value('pin3'):
            self[0][2][0][4].update_attribs({"disabled":"disabled", "value":"X"})

        # fourth input field
        self[0][2][0][6].update_attribs({"name":self.get_formname('pin4')})
        if not self.get_field_value('pin4'):
            self[0][2][0][6].update_attribs({"disabled":"disabled", "value":"X"})

        if self.get_field_value("autofocus"):
            # set autofocus on first non-disabled input field
            if self.get_field_value('pin1'):
                self[0][2][0][0].update_attribs({"autofocus":"autofocus"})
            elif self.get_field_value('pin2'):
                self[0][2][0][2].update_attribs({"autofocus":"autofocus"})
            elif self.get_field_value('pin3'):
                self[0][2][0][4].update_attribs({"autofocus":"autofocus"})
            elif self.get_field_value('pin4'):
                self[0][2][0][6].update_attribs({"autofocus":"autofocus"})

        # div containing the button
        if self.get_field_value('butt_div_class'):
            self[0][2][1].update_attribs({"class":self.get_field_value('butt_div_class')})

        if self.get_field_value('left_label'):
            self[0][2][1][0][0] = self.get_field_value('left_label')
        if self.get_field_value('left_class'):
            self[0][2][1][0].attribs = {"class": self.get_field_value('left_class')}
 
        # the submit button
        if self.get_field_value('button_class'):
            self[0][2][1][1].update_attribs({"class":self.get_field_value('button_class'),
                                                                                   "value":self.get_field_value('button_text')})
        else:
            self[0][2][1][1].update_attribs({"value":self.get_field_value('button_text')})

        # set an id in the submit button for the 'label for' tag
        self[0][2][1][1].insert_id()

        if self.get_field_value('right_label'):
            self[0][2][1][2][0] = self.get_field_value('right_label')
        if self.get_field_value('right_class'):
            self[0][2][1][2].attribs = {"class": self.get_field_value('right_class')}

        # set the label 'for' attribute
        self[0][2][1][0].update_attribs({'for':self[0][2][1][1].get_id()})
        self[0][2][1][2].update_attribs({'for':self[0][2][1][1].get_id()})

        # add ident and four hidden fields
        self.add_hiddens(self[0][2], page)



    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a keypress event handler"""
        jscript = """  $("#{ident} input").keypress(function (e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident = self.get_id())
        #if self._jsonurl:
        #    return jscript + self._make_fieldvalues('button_wait_text', url=self._jsonurl)
        #else:
        #    return jscript + self._make_fieldvalues('button_wait_text')
        return jscript


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div>  <!-- with class attribute set to inner_div_class if a class is set -->
    <div> <!-- normally hidden div, with class error_class -->
      <p> <!-- Any error text appears here --> </p>
    </div>
    <div>
     <!- A container of further code goes here ->
    </div>
    <form method="post"> <!-- action attribute set to action field -->
      <div>  <!-- with class attribute set to char_div_class and style to char_div_style -->
       <!-- each input field has maxlength set to one character -->
        <input type=\"password\" />-<input type=\"password\" />-<input type=\"password\" />-<input type=\"password\" />
      </div>
      <div>  <!-- with class attribute set to butt_div_class if a class is set -->
        <label> <!-- with class set to left_class and content to left_label -->
        </label>
        <input type=\"submit\" /> <!-- button value set to button_text -->
                                       <!-- and class attribute set to button_class if a class is set -->
        <label> <!-- with class set to right_class and content to right_label -->
        </label>
      </div>
      <!-- hidden input fields -->    
    </form>
  </div>
</div>"""



class NamePasswd1(Widget):
    """Defines a form containing text input and password fields."""

    error_location = (0,0,0)

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {'action':FieldArg("url", ''),
                        'action_json':FieldArg("url", ''),
                        'error_class':FieldArg("cssclass", ""),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'div1_class':FieldArg("cssclass", ''),
                        'label1':FieldArg("text", 'Username:'),
                        'label_class1':FieldArg("cssclass", ''),
                        'input_text1':FieldArg("text", '', valdt=True, jsonset=True),
                        'size1':FieldArg("text", ''),
                        'maxlength1':FieldArg("text", ''),
                        'disabled1':FieldArg("boolean", False),
                        'required1':FieldArg("boolean", True),
                        'pattern1':FieldArg("text", ''),
                        'title1':FieldArg("text", ''),
                        'set_input_accepted1':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored1':FieldArg("boolean", False, jsonset=True),
                        'div2_class':FieldArg("cssclass", ''),
                        'label2':FieldArg("text", 'Password:'),
                        'label_class2':FieldArg("cssclass", ''),
                        'input_text2':FieldArg("text", '', valdt=True, jsonset=True),
                        'size2':FieldArg("text", ''),
                        'maxlength2':FieldArg("text", ''),
                        'disabled2':FieldArg("boolean", False),
                        'required2':FieldArg("boolean", True),
                        'pattern2':FieldArg("text", ''),
                        'title2':FieldArg("text", ''),
                        'set_input_accepted2':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored2':FieldArg("boolean", False, jsonset=True),
                        'input_class1':FieldArg("cssclass", ''),
                        'input_class2':FieldArg("cssclass", ''),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'div3_class':FieldArg("cssclass", ''),
                        'button_text':FieldArg("text", 'Submit'),
                        'button_class':FieldArg("cssclass", ''),
                        'button_style':FieldArg("cssstyle", ''),
                       }


    def __init__(self, name=None, brief='', **field_args):
        """
        action: The page ident this button links to
        action_json:  if a value set, and client has jscript enabled, this is the page ident, label, url this button links to, expects a json page back
        error_class: The class applied to the paragraph containing the error message on error.
        inputdiv_class: the class attribute of the tag which contains the label and inputs
        label1: The text displayed to the left of the text input field
        label_class1: The css class of the label
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        button_text: The text on the button
        button_class: the class attribute of the button
        input_accepted_class: A class which can be set on each input field
        input_errored_class: A class which can be set on each input field
        input_text1: The default text in the first text input field, field name used as the name attribute
        input_class1: Class set on the first input field
        size1: The number of characters appearing in the first text input area
        maxlength1: The maximum number of characters accepted in the first text area
        disabled1: Set True if the first input field is to be disabled
        required1: Set True to put the 'required' flag into the first input field
        pattern1: regular expression pattern for first input field
        title1: helps describe the pattern of the first input field
        label2: The text displayed to the left of the password input field
        label_class2: The css class of the label
        input_text2: The default text in the second text input field, field name used as the name attribute
        input_class2: Class set on the second input field
        size2: The number of characters appearing in the second text input area
        maxlength2: The maximum number of characters accepted in the second text area
        disabled2: Set True if the second field is to be disabled
        required2: Set True to put the 'required' flag into the second input field
        pattern2: regular expression pattern for the second input field
        title2: helps describe the pattern of the second input field
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})
        # div containing inputs and button
        self[1][0] = tag.Part(tag_name='div')
        # div containing label and input 1
        self[1][0][0] = tag.Part(tag_name='div')
        # the label 1
        self[1][0][0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the first text input field
        self[1][0][0][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})
        # div containing label and password input
        self[1][0][1] = tag.Part(tag_name='div')
        # the label 2
        self[1][0][1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the password field
        self[1][0][1][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"password"})
        # div containing submit button
        self[1][0][2] = tag.Part(tag_name='div')
        # the submit button
        self[1][0][2][0] = tag.ClosedPart(tag_name="input", attribs={"type":"submit"})
        self._jsonurl = ''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        if not self.get_field_value("action"):
            # setting self._error replaces the entire tag
            self._error = "Warning: No form action"
            return
        actionurl = skiboot.get_url(self.get_field_value("action"),  proj_ident=page.proj_ident)
        if not actionurl:
            # setting self._error replaces the entire tag
            self._error = "Warning: broken link"
            return
        # update the action of the form
        self[1].update_attribs({"action": actionurl})
        self._jsonurl = skiboot.get_url(self.get_field_value("action_json"), proj_ident=page.proj_ident)
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")

        # the div holding labels, input fields and button
        if self.get_field_value('inputdiv_class'):
            self[1][0].attribs = {"class": self.get_field_value('inputdiv_class')}

        # div1
        if self.get_field_value('div1_class'):
            self[1][0][0].attribs = {"class": self.get_field_value('div1_class')}

        # set up label1
        if self.get_field_value('label1'):
            self[1][0][0][0][0] = self.get_field_value('label1')
        if self.get_field_value('label_class1'):
            self[1][0][0][0].attribs = {"class": self.get_field_value('label_class1')}

        # first input field
        self[1][0][0][1].update_attribs({"name":self.get_formname('input_text1'), "value":self.get_field_value('input_text1')})
        if self.get_field_value('size1'):
            self[1][0][0][1].update_attribs({"size":self.get_field_value('size1')})
        if self.get_field_value('maxlength1'):
            self[1][0][0][1].update_attribs({"maxlength":self.get_field_value('maxlength1')})
        if self.get_field_value('disabled1'):
            self[1][0][0][1].update_attribs({"disabled":"disabled"})
        if self.get_field_value('required1'):
            self[1][0][0][1].update_attribs({"required":"required"})
        if self.get_field_value('pattern1'):
            self[1][0][0][1].update_attribs({"pattern":self.get_field_value('pattern1')})
        if self.get_field_value('title1'):
            self[1][0][0][1].update_attribs({"title":self.get_field_value('title1')})

        if self.get_field_value('input_class1'):
            input_class1 = self.get_field_value('input_class1')
        else:
            input_class1 = ''

        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class1:
                input_class1 = input_class1 + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class1 = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored1') and self.get_field_value('input_errored_class'):
            if input_class1:
                input_class1 = input_class1 + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class1 = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted1') and self.get_field_value('input_accepted_class'):
            if input_class1:
                input_class1 = input_class1 + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class1 = self.get_field_value('input_accepted_class')

        if input_class1:
            self[1][0][0][1].update_attribs({"class":input_class1})

        # set up label2
        if self.get_field_value('label2'):
            self[1][0][1][0][0] = self.get_field_value('label2')
        if self.get_field_value('label_class2'):
            self[1][0][1][0].attribs = {"class": self.get_field_value('label_class2')}

        # password field
        self[1][0][1][1].update_attribs({"name":self.get_formname('input_text2'), "value":self.get_field_value('input_text2')})
        if self.get_field_value('size2'):
            self[1][0][1][1].update_attribs({"size":self.get_field_value('size2')})
        if self.get_field_value('maxlength2'):
            self[1][0][1][1].update_attribs({"maxlength":self.get_field_value('maxlength2')})
        if self.get_field_value('disabled2'):
            self[1][0][1][1].update_attribs({"disabled":"disabled"})
        if self.get_field_value('required2'):
            self[1][0][1][1].update_attribs({"required":"required"})
        if self.get_field_value('pattern2'):
            self[1][0][1][1].update_attribs({"pattern":self.get_field_value('pattern2')})
        if self.get_field_value('title2'):
            self[1][0][1][1].update_attribs({"title":self.get_field_value('title2')})

        if self.get_field_value('input_class2'):
            input_class2 = self.get_field_value('input_class2')
        else:
            input_class2 = ''

        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class2:
                input_class2 = input_class2 + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class2 = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored2') and self.get_field_value('input_errored_class'):
            if input_class2:
                input_class2 = input_class2 + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class2 = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted2') and self.get_field_value('input_accepted_class'):
            if input_class2:
                input_class2 = input_class2 + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class2 = self.get_field_value('input_accepted_class')

        if input_class2:
            self[1][0][1][1].update_attribs({"class":input_class2})

        # div3
        if self.get_field_value('div3_class'):
            self[1][0][2].attribs = {"class": self.get_field_value('div3_class')}
        # the submit button
        self[1][0][2][0].update_attribs({"value":self.get_field_value('button_text')})
        # the button class
        if self.get_field_value('button_class'):
            self[1][0][2][0].update_attribs({"class": self.get_field_value('button_class')})
        if self.get_field_value('button_style'):
            self[1][0][2][0].update_attribs({"style": self.get_field_value('button_style')})


        # set an id in the first input field for the 'label for' tag
        self[1][0][0][1].insert_id()
        # set the label 'for' attribute
        self[1][0][0][0].update_attribs({'for':self[1][0][0][1].get_id()})

        # set an id in the password field for the 'label for' tag
        self[1][0][1][1].insert_id()
        # set the label 'for' attribute
        self[1][0][1][0].update_attribs({'for':self[1][0][1][1].get_id()})

        # add ident and four hidden fields
        self.add_hiddens(self[1], page)


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a submit event handler"""
        jscript = """  $("#{ident} form").on("submit input", function(e) {{
    SKIPOLE.widgets["{ident}"].eventfunc(e);
    }});
""".format(ident=self.get_id())
        if self._jsonurl:
            return jscript + self._make_fieldvalues('input_accepted_class', 'input_errored_class', url=self._jsonurl)
        return jscript + self._make_fieldvalues('input_accepted_class', 'input_errored_class')


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <form method="post"> <!-- action attribute set to action field -->
    <div> <!-- class attribute set to inputdiv_class -->
      <div> <!-- class attribute set to div1_class -->
        <label> <!-- with class set to label_class1 and content to label1 -->
        </label>
        <input type=\"text\" /> <!-- input text value set to input_text1, class to input_class1 -->
      </div>
      <div> <!-- class attribute set to div2_class -->
        <label> <!-- with class set to label_class2 and content to label2 -->
        </label>
        <input type=\"password\" /> <!-- input text value set to input_text2, class to input_class2 -->
      </div>
      <div> <!-- class attribute set to div3_class -->
        <input type=\"submit\" /> <!-- button value set to button_text and class to button_class -->
      </div>
    </div>
    <!-- hidden input fields -->    
  </form>
</div>"""






