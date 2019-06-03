


"""Contains widgets for textarea forms"""


from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict

class SubmitTextArea(Widget):
    """Defines a form containing a div with a text area input field"""

    error_location = (0,0,0)

    arg_descriptions = {'error_class':FieldArg("cssclass", ""),
                        'action':FieldArg("url", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'button_text':FieldArg("text", 'Submit'),
                        'button_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'textarea_class':FieldArg("cssclass", ''),
                        'textarea_style':FieldArg("cssstyle", ''),
                        'rows':FieldArg("text", '4'),
                        'cols':FieldArg("text", '40')
                       }


    def __init__(self, name=None, brief='', **field_args):
        """
        action: The page ident, label, url this button links to
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        button_text: The text on the button
        button_class: class set on the buttons
        inputdiv_class: the class attribute of the div which contains the input text area and button
        error_class: The class applied to the paragraph containing the error message on error.
        input_text: The default text in the text area, field name used as the name attribute
        textarea_class: The class applied to the textarea
        textarea_style: The style applied to the textarea
        rows:  The number of rows of the text area
        cols: The number of columns of the text area
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error at div 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})
        # div containing textarea and button
        self[1][0] = tag.Part(tag_name='div')
        # the text input field
        self[1][0][0] = tag.Part(tag_name="textarea")
        # the submit button
        self[1][0][1] = tag.ClosedPart(tag_name="input")


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
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
        # the class of the div holding textarea and button
        if self.get_field_value('inputdiv_class'):
            self[1][0].attribs = {"class": self.get_field_value('inputdiv_class')}

        # set up the text area
        self[1][0][0].attribs = {"name":self.get_formname('input_text')}

        if self.get_field_value('rows'):
            self[1][0][0].update_attribs({"rows": self.get_field_value('rows')})

        if self.get_field_value('cols'):
            self[1][0][0].update_attribs({"cols": self.get_field_value('cols')})

        if self.get_field_value('textarea_class'):
            self[1][0][0].update_attribs({"class": self.get_field_value('textarea_class')})

        if self.get_field_value("textarea_style"):
            self[1][0][0].update_attribs({"style":self.get_field_value("textarea_style")})

        if self.get_field_value('input_text'):
            self[1][0][0][0] = self.get_field_value('input_text')

        # set up the submit button
        if self.get_field_value('button_text'):
            submit = self.get_field_value('button_text')
        else:
            submit = "Submit"

        if self.get_field_value('button_class'):
            self[1][0][1].attribs = {"value":submit, "type":"submit", "class":self.get_field_value('button_class')}
        else:
            self[1][0][1].attribs = {"value":submit, "type":"submit"}

        # add ident and four hidden fields
        self.add_hiddens(self[1], page)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden paragraph, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <form method="post">  <!-- with action given by action field -->
    <div> <!-- the class attribute set to inputdiv_class -->
      <textarea> <!-- class attribute set to textarea_class. Rows, cols set to the given rows and columns -->
        <!-- textarea content set to input_text -->
      </textarea>
      <input type="submit" /> <!-- button value set to button_text -->
    </div>
    <!-- hidden input fields -->                              
  </form>
</div>"""



class TextArea1(Widget):
    """Defines an input field only (no form, label or submit button)
       does not display errors"""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'rows':FieldArg("text", '4'),
                        'cols':FieldArg("text", '40')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_text: The default text in the text input field, field name used as name attribute
        rows:  The number of rows of the text area
        cols: The number of columns of the text area
        """
        Widget.__init__(self, name=name, tag_name="textarea", brief=brief, **field_args)
        self[0] = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        self.update_attribs({"name":self.get_formname('input_text')})
        if self.get_field_value('input_text'):
            self[0] = self.get_field_value('input_text')
        if self.get_field_value('rows'):
            self.update_attribs({"rows": self.get_field_value('rows')})
        if self.get_field_value('cols'):
            self.update_attribs({"cols": self.get_field_value('cols')})
 
    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
    <textarea> <!-- with widget id and class widget_class. Rows, cols set to the given rows and columns -->
      <!-- textarea content set to input_text -->
    </textarea>
"""



class TextArea2(Widget):
    """Defines a div containing a hidden error paragraph
       with a textarea input field (no form or submit button)
       A label to the left of the textarea can have a class and text set"""

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    error_location = (0,0,0)

    arg_descriptions = {
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'textarea_class':FieldArg("cssclass", ''),
                        'textarea_style':FieldArg("cssstyle", ''),
                        'redstar':FieldArg("boolean", False),
                        'rows':FieldArg("text", '4'),
                        'cols':FieldArg("text", '40')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        label: The text appearing in a label tag to the left of the input field
        label_class: The css class of the label to the left of the input field
        error_class: The class applied to the hidden paragraph on error.
        input_text: The default text in the text input field, field name used as name attribute
        redstar: If True a red asterisk is shown by the side of the input field
        textarea_class: The class applied to the textarea
        textarea_style: The style applied to the textarea
        rows:  The number of rows of the text area
        cols: The number of columns of the text area
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # the label
        self[1] = tag.Part(tag_name="label", hide_if_empty=True)
        # the textarea input field
        self[2] = tag.Part(tag_name="textarea")
        self[2][0] =''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('label_class'):
            self[1].update_attribs({"class": self.get_field_value('label_class')})
        if self.get_field_value("label"):
            self[1][0] = self.get_field_value("label")
        # set an id in the textarea for the 'label for' tag
        self[2].insert_id()
        self[1].update_attribs({'for':self[2].get_id()})
        self[2].update_attribs({"name":self.get_formname('input_text')})
        if self.get_field_value('textarea_class'):
            self[2].update_attribs({"class": self.get_field_value('textarea_class')})
        if self.get_field_value("textarea_style"):
            self[2].update_attribs({"style":self.get_field_value("textarea_style")})

        if self.get_field_value('rows'):
            self[2].update_attribs({"rows": self.get_field_value('rows')})
        if self.get_field_value('cols'):
            self[2].update_attribs({"cols": self.get_field_value('cols')})
        if self.get_field_value('input_text'):
            self[2][0] = self.get_field_value('input_text')
        if self.get_field_value('redstar'):
            self[3] = tag.Part(tag_name="span",  attribs ={"style":"color:red;"})
            self[3][0] = tag.HTMLSymbol(text="&nbsp;")
            self[3][1] = '*'


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden paragraph, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <label> <!-- with class set to label_class -->
          <!-- content set to label -->
  </label>
  <textarea> <!-- class attribute set to textarea_class. Rows, cols set to the given rows and columns -->
    <!-- textarea content set to input_text -->
  </textarea>
  <span style="color:red;">&nbsp;*</span> <!-- shown if redstar is True -->
</div>"""
