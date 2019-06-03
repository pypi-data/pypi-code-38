


"""Contains widgets for inputting text"""

from string import Template
import json

from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class TextInput1(ClosedWidget):
    """Defines an input field only (no form, label or submit button)
       does not display errors"""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'disabled':FieldArg("boolean", False),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", '')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        input_text: The default text in the text input field, field name used as name attribute
        size: The number of characters appearing in the text input field
        maxlength: The maximum number of characters accepted in the text input field
        disabled: Set True if the field is to be disabled
        required: Set True to put the 'required' attribute into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        """
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)
        self.update_attribs({"type":"text"})


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        self.update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if self.get_field_value('widget_class'):
                new_class = self.get_field_value('widget_class') + " " + self.get_field_value('input_accepted_class')
            else:
                new_class = self.get_field_value('input_accepted_class')
            self.update_attribs({"class":new_class})
        if self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if self.get_field_value('widget_class'):
                new_class = self.get_field_value('widget_class') + " " + self.get_field_value('input_errored_class')
            else:
                new_class = self.get_field_value('input_errored_class')
            self.update_attribs({"class":new_class})
        if self.get_field_value('size'):
            self.update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self.update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('disabled'):
            self.update_attribs({"disabled":"disabled"})
        if self.get_field_value('required'):
            self.update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self.update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self.update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self.update_attribs({"title":self.get_field_value('title')})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input_accepted_class, input_errored_class into fieldvalues"""
        return self._make_fieldvalues('input_accepted_class', 'input_errored_class')

 
    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
  <input type='text' />
  <!-- with widget id and class widget_class and input_accepted_class added if
       set_input_accepted is set to True, and input_errored_class added if
       set_input_errored is set to True, (which will remove input_accepted_class) -->
"""


class Password1(ClosedWidget):
    """Defines a password input field only (no form, label or submit button)
       does not display errors"""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'disabled':FieldArg("boolean", False),
                        'required':FieldArg("boolean", False)
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        input_text: The default text in the text input field, field name used as name attribute
        size: The number of characters appearing in the text input field
        maxlength: The maximum number of characters accepted in the text input field
        disabled: Set True if the field is to be disabled
        required: Set True to put the 'required' attribute into the input field
        """
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)
        self.update_attribs({"type":"password"})


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        self.update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if self.get_field_value('widget_class'):
                new_class = self.get_field_value('widget_class') + " " + self.get_field_value('input_accepted_class')
            else:
                new_class = self.get_field_value('input_accepted_class')
            self.update_attribs({"class":new_class})
        if self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if self.get_field_value('widget_class'):
                new_class = self.get_field_value('widget_class') + " " + self.get_field_value('input_errored_class')
            else:
                new_class = self.get_field_value('input_errored_class')
            self.update_attribs({"class":new_class})
        if self.get_field_value('size'):
            self.update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self.update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('disabled'):
            self.update_attribs({"disabled":"disabled"})
        if self.get_field_value('required'):
            self.update_attribs({"required":"required"})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input_accepted_class, input_errored_class into fieldvalues"""
        return self._make_fieldvalues('input_accepted_class', 'input_errored_class')

 
    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
  <input type='password' />
  <!-- with widget id and class widget_class and input_accepted_class added if
       set_input_accepted is set to True, and input_errored_class added if
       set_input_errored is set to True, (which will remove input_accepted_class) -->
"""


class TextInput2(Widget):
    """Defines a div containing a hidden error paragraph
       with a text input field (no form or submit button)
       A label to the left of the text can have a class and text set"""

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    error_location = (0,0,0)

    arg_descriptions = {
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'input_class':FieldArg("cssclass", ''),
                        'input_disabled_class':FieldArg("cssclass", ''),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'redstar':FieldArg("boolean", False),
                        'disabled':FieldArg("boolean", False, jsonset=True),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", '')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        label: The text appearing in a label tag to the left of the input field
        label_class: The css class of the label to the left of the input field
        error_class: The class applied to the hidden paragraph on error.
        inputdiv_class: The css class of the div containing the label and input field
        input_text: The default text in the text input field, field name used as name attribute
        input_class: The css class of the input field
        input_disabled_class: css class of the input field which replaces input_class if disabled is True
        size: The number of characters appearing in the text input area
        maxlength: The maximum number of characters accepted in the text area
        redstar: If True a red asterix is shown by the side of the input field
        disabled: Set True if the field is to be disabled
        required: Set True to put the 'required' flag into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # inputdiv
        self[1] = tag.Part(tag_name="div")
        # the label
        self[1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the text input field
        self[1][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('inputdiv_class'):
            self[1].update_attribs({"class": self.get_field_value('inputdiv_class')})
        if self.get_field_value('label_class'):
            self[1][0].update_attribs({"class": self.get_field_value('label_class')})
        if self.get_field_value("label"):
            self[1][0][0] = self.get_field_value("label")
        # set an id in the input field for the 'label for' tag
        self[1][1].insert_id()
        self[1][0].update_attribs({'for':self[1][1].get_id()})
        self[1][1].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('size'):
            self[1][1].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[1][1].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('required'):
            self[1][1].update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self[1][1].update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self[1][1].update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self[1][1].update_attribs({"title":self.get_field_value('title')})
        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''
        if self.get_field_value('disabled'):
            self[1][1].update_attribs({"disabled":"disabled"})
            if self.get_field_value('input_disabled_class'):
                input_class = self.get_field_value('input_disabled_class')
        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')
        if input_class:
            self[1][1].update_attribs({"class":input_class})
        if self.get_field_value('redstar'):
            self[1][2] = tag.Part(tag_name="span",  attribs ={"style":"color:red;"})
            self[1][2][0] = tag.HTMLSymbol(text="&nbsp;")
            self[1][2][1] = '*'

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input classes into fieldvalues"""
        fieldlist = []
        if self.get_field_value('input_accepted_class'):
            fieldlist.append('input_accepted_class')
        if self.get_field_value('input_errored_class'):
            fieldlist.append('input_errored_class')
        if self.get_field_value('input_class'):
            fieldlist.append('input_class')
        if self.get_field_value('input_disabled_class'):
            fieldlist.append('input_disabled_class')
        if fieldlist:
            return self._make_fieldvalues(*fieldlist)
        return ''

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <div>  <!-- class attribute set to inputdiv_class -->
    <label> <!-- with class set to label_class -->
            <!-- content set to label -->
    </label>
    <input type='text' /> <!-- with attributes set appropriately -->
    <span style="color:red;">&nbsp;*</span> <!-- shown if redstar is True -->
  </div>
</div>"""


class Password2(Widget):
    """Defines a div containing a hidden error paragraph
       with a password input field (no form or submit button)
       A label to the left of the text can have a class and text set"""

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    error_location = (0,0,0)

    arg_descriptions = {
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'input_disabled_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'input_class':FieldArg("cssclass", ''),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'disabled':FieldArg("boolean", False, jsonset=True),
                        'redstar':FieldArg("boolean", False),
                        'required':FieldArg("boolean", False)
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        input_disabled_class: css class of the input field which replaces input_class if disabled is True
        inputdiv_class: The css class of the div containing the label and input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        label: The text appearing in a label tag to the left of the input field
        label_class: The css class of the label to the left of the input field
        error_class: The class applied to the hidden paragraph on error.
        input_text: The default text in the text input field, field name used as name attribute
        input_class: The css class of the input field
        size: The number of characters appearing in the text input area
        maxlength: The maximum number of characters accepted in the text area
        disabled: Set True if the field is to be disabled
        redstar: If True a red asterix is shown by the side of the input field
        required: Set True to put the 'required' flag into the input field
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # inputdiv
        self[1] = tag.Part(tag_name="div")
        # the label
        self[1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the text input field
        self[1][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"password"})


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('inputdiv_class'):
            self[1].update_attribs({"class": self.get_field_value('inputdiv_class')})
        if self.get_field_value('label_class'):
            self[1][0].update_attribs({"class": self.get_field_value('label_class')})
        if self.get_field_value("label"):
            self[1][0][0] = self.get_field_value("label")
        # set an id in the input field for the 'label for' tag
        self[1][1].insert_id()
        self[1][0].update_attribs({'for':self[1][1].get_id()})
        self[1][1].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('size'):
            self[1][1].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[1][1].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('required'):
            self[1][1].update_attribs({"required":"required"})
        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''
        if self.get_field_value('disabled'):
            self[1][1].update_attribs({"disabled":"disabled"})
            if self.get_field_value('input_disabled_class'):
                input_class = self.get_field_value('input_disabled_class')
        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')
        if input_class:
            self[1][1].update_attribs({"class":input_class})
        if self.get_field_value('redstar'):
            self[1][2] = tag.Part(tag_name="span",  attribs ={"style":"color:red;"})
            self[1][2][0] = tag.HTMLSymbol(text="&nbsp;")
            self[1][2][1] = '*'

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input classes into fieldvalues"""
        fieldlist = []
        if self.get_field_value('input_accepted_class'):
            fieldlist.append('input_accepted_class')
        if self.get_field_value('input_errored_class'):
            fieldlist.append('input_errored_class')
        if self.get_field_value('input_class'):
            fieldlist.append('input_class')
        if self.get_field_value('input_disabled_class'):
            fieldlist.append('input_disabled_class')
        if fieldlist:
            return self._make_fieldvalues(*fieldlist)
        return ''


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden paragraph, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <div>  <!-- class attribute set to inputdiv_class -->
    <label> <!-- with class set to label_class -->
            <!-- content set to label -->
    </label>
    <input type='password' /> <!-- with attributes set appropriately -->
    <span style="color:red;">&nbsp;*</span> <!-- shown if redstar is True -->
  </div>
</div>"""


class TextInput3(Widget):
    """Defines a div containing a text input field (no form or submit button)
       with a left and right label, does not display errors"""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'input_class':FieldArg("cssclass", ''),
                        'input_style':FieldArg("cssclass", ''),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'left_label':FieldArg("text", ''),
                        'left_class':FieldArg("cssclass", ''),
                        'right_label':FieldArg("text", ''),
                        'right_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'disabled':FieldArg("boolean", False),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", '')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_class: The css class of the input field
        input_style: The css style of the input field
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        left_label: The text displayed to the left of the input field
        left_class: The css class of the label to the left of the input field
        right_label: The text displayed to the right of the input field
        right_class: The css class of the label to the right of the input field
        input_text: The default text in the text input field, field name used as name attribute
        size: The number of characters appearing in the text input field
        maxlength: The maximum number of characters accepted in the text input field
        disabled: Set True if the field is to be disabled
        required: Set True to put the 'required' attribute into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name="label", hide_if_empty=True)
        self[1] = tag.ClosedPart(tag_name="input", attribs = {"type":"text"})
        self[2] = tag.Part(tag_name="label", hide_if_empty=True)


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        if self.get_field_value('left_label'):
            self[0][0] = self.get_field_value('left_label')
        if self.get_field_value('left_class'):
            self[0].attribs = {"class": self.get_field_value('left_class')}
        self[1].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})

        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''

        if self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')
        if input_class:
            self[1].update_attribs({"class":input_class})

        if self.get_field_value('input_style'):
            self[1].update_attribs({"style":self.get_field_value('input_style')})
        if self.get_field_value('size'):
            self[1].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[1].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('disabled'):
            self[1].update_attribs({"disabled":"disabled"})
        if self.get_field_value('required'):
            self[1].update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self[1].update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self[1].update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self[1].update_attribs({"title":self.get_field_value('title')})
        if self.get_field_value('right_label'):
            self[2][0] = self.get_field_value('right_label')
        if self.get_field_value('right_class'):
            self[2].attribs = {"class": self.get_field_value('right_class')}
        # set an id in the text input field for the 'label for' tag
        self[1].insert_id()
        # set the label 'for' attribute
        self[0].update_attribs({'for':self[1].get_id()})
        self[2].update_attribs({'for':self[1].get_id()})


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input_accepted_class, input_errored_class into fieldvalues"""
        return self._make_fieldvalues('input_accepted_class', 'input_errored_class')
 
    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <label> <!-- with class set to left_class and content to left_label -->
  </label>
  <input type='text' /> <!-- with attributes set appropriately -->
  <label> <!-- with class set to right_class and content to right_label -->
  </label>
</div>"""


class TextInput4(Widget):
    """Defines a div containing a div with label
       and a div with a text input field (no form or submit button)
       All divs, label and input field can have class set
       No error display"""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True   

    arg_descriptions = {
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'labeldiv_class':FieldArg("cssclass", ''),
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'input_class':FieldArg("cssclass", ''),
                        'input_disabled_class':FieldArg("cssclass", ''),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'redstar':FieldArg("boolean", False),
                        'disabled':FieldArg("boolean", False, jsonset=True),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", '')
                       }
    def __init__(self, name=None, brief='', **field_args):
        """
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        labeldiv_class: The css class of the div containing the label
        label: The text appearing in a label tag to the left of the input field
        label_class: The css class of the label to the left of the input field
        inputdiv_class: The css class of the div containing the input field
        input_text: The default text in the text input field, field name used as name attribute
        input_class: The css class of the input field
        input_disabled_class: css class of the input field which replaces input_class if disabled is True
        size: The number of characters appearing in the text input area
        maxlength: The maximum number of characters accepted in the text area
        redstar: If True a red asterix is shown by the side of the input field
        disabled: Set True if the field is to be disabled
        required: Set True to put the 'required' flag into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # label div at 0
        self[0] = tag.Part(tag_name="div")
        # the label
        self[0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # input div at 1
        self[1] = tag.Part(tag_name="div")
        # the text input field
        self[1][0] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the input field"
        # label
        if self.get_field_value('labeldiv_class'):
            self[0].update_attribs({"class": self.get_field_value('labeldiv_class')})
        if self.get_field_value('label_class'):
            self[0][0].update_attribs({"class": self.get_field_value('label_class')})
        if self.get_field_value("label"):
            self[0][0][0] = self.get_field_value("label")
        # input div
        if self.get_field_value('inputdiv_class'):
            self[1].update_attribs({"class": self.get_field_value('inputdiv_class')})
        # set an id in the input field for the 'label for' tag
        self[1][0].insert_id()
        self[0][0].update_attribs({'for':self[1][0].get_id()})
        # input field
        self[1][0].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('size'):
            self[1][0].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[1][0].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('required'):
            self[1][0].update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self[1][0].update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self[1][0].update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self[1][0].update_attribs({"title":self.get_field_value('title')})
        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''
        if self.get_field_value('disabled'):
            self[1][0].update_attribs({"disabled":"disabled"})
            if self.get_field_value('input_disabled_class'):
                input_class = self.get_field_value('input_disabled_class')
        if self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')
        if input_class:
            self[1][0].update_attribs({"class":input_class})
        # redstar
        if self.get_field_value('redstar'):
            self[1][1] = tag.Part(tag_name="span",  attribs ={"style":"color:red;"})
            self[1][1][0] = tag.HTMLSymbol(text="&nbsp;")
            self[1][1][1] = '*'

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets input classes into fieldvalues"""
        fieldlist = []
        if self.get_field_value('input_accepted_class'):
            fieldlist.append('input_accepted_class')
        if self.get_field_value('input_errored_class'):
            fieldlist.append('input_errored_class')
        if self.get_field_value('input_class'):
            fieldlist.append('input_class')
        if self.get_field_value('input_disabled_class'):
            fieldlist.append('input_disabled_class')
        if fieldlist:
            return self._make_fieldvalues(*fieldlist)
        return ''

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div> <!-- with class set to labeldiv_class -->
    <label> <!-- with class set to label_class -->
            <!-- content set to label -->
    </label>
  </div>
  <div> <!-- with class set to inputdiv_class -->
    <input type='text' /> <!-- with attributes set appropriately -->
    <span style="color:red;">&nbsp;*</span> <!-- shown if redstar is True -->
  </div>
</div>"""



class SubmitTextInput1(Widget):
    """Defines a form with a text input field, and four hidden fields"""

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    error_location = (0,0,0)

    arg_descriptions = {'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'action_json':FieldArg("url", ''),
                        'action':FieldArg("url", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'target':FieldArg("text",''),
                        'button_text':FieldArg("text",'Submit'),
                        'button_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'inputandbutton_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", ''),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'input_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'hide':FieldArg("boolean", False, jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        label: The text displayed to the left of the text input field
        label_class: The css class of the label
        action_json:  if a value set, and client has jscript enabled, this is the page ident, label, url this button links to, expects a json page back
        action: The page ident, label, url this button links to, overridden if action_json is set.
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        target: if given, the target attribute will be set
        button_text: The text on the button
        button_class: The class given to the button tag
        inputdiv_class: the class attribute of the div which contains the label, input text and button
        inputandbutton_class: the class attribute of the span which contains the input text and button
        error_class: The class applied to the paragraph containing the error message on error.
        input_text: The default text in the text input field, field name used as the name attribute
        size: The number of characters appearing in the text input area
        maxlength: The maximum number of characters accepted in the text area
        required: Set True to put the 'required' flag into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        input_class: Class set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        hide: If True, widget is hidden
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})

        # div containing label, input text and button
        self[1][0] = tag.Part(tag_name='div')
        # the label
        self[1][0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # span containing input text and button
        self[1][0][1] = tag.Part(tag_name='span')
        # the text input field
        self[1][0][1][0] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})
        # the submit button
        self[1][0][1][1] = tag.Part(tag_name="button", attribs ={"type":"submit"})
        self[1][0][1][1][0] = "Submit"
        self._jsonurl = ''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        if self.get_field_value("target"):
            self[1].update_attribs({"target":self.get_field_value("target")})
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        self._jsonurl = skiboot.get_url(self.get_field_value("action_json"), proj_ident=page.proj_ident)
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
        # the div holding label, input text and button
        if self.get_field_value('inputdiv_class'):
            self[1][0].attribs = {"class": self.get_field_value('inputdiv_class')}

        if self.get_field_value('label_class'):
            self[1][0][0].attribs = {"class": self.get_field_value('label_class')}
        if self.get_field_value('label'):
            self[1][0][0][0] = self.get_field_value('label')

        # the span holding input text and button
        if self.get_field_value('inputandbutton_class'):
            self[1][0][1].attribs = {"class": self.get_field_value('inputandbutton_class')}

        # set an id in the input field for the 'label for' tag
        self[1][0][1][0].insert_id()

        self[1][0][1][0].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('size'):
            self[1][0][1][0].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[1][0][1][0].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('required'):
            self[1][0][1][0].update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self[1][0][1][0].update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self[1][0][1][0].update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self[1][0][1][0].update_attribs({"title":self.get_field_value('title')})
        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''

        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')

        if input_class:
            self[1][0][1][0].update_attribs({"class":input_class})

        # set the label 'for' attribute
        self[1][0][0].update_attribs({'for':self[1][0][1][0].get_id()})

        # submit button
        if self.get_field_value('button_class'):
            self[1][0][1][1].update_attribs({"class": self.get_field_value('button_class')})
        if self.get_field_value('button_text'):
            self[1][0][1][1][0] = self.get_field_value('button_text')


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
  <div>  <!-- div hidden when no error is displayed, with class set to error_class on error -->
    <p> <!-- error message appears in this paragraph --> </p>
  </div>
  <form role="form" method="post"> <!-- action attribute set to action field -->
    <div> <!-- class attribute set to inputdiv_class -->
      <label> <!-- with class set to label_class and content to label, for set to input text id -->
      </label>
      <span>  <!-- class attribute set to inputandbutton_class -->
          <input type="text" />  <!-- class set to input_class -->
            <!-- input text value set to input_text -->
          <button type="submit"> <!-- with class set to button_class -->
            <!-- button_text -->
          </button>
      </span>
    </div>
    <!-- hidden input fields -->                              
  </form>
</div>"""



class SubmitTextInput3(Widget):
    """Defines paragraphs followed by a form with a text input field"""

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    error_location = (0,0,0)

    arg_descriptions = {
                        'show_para1':FieldArg("boolean", True, jsonset=True),
                        'para_text':FieldArg("text", '', jsonset=True),
                        'show_para2':FieldArg("boolean", True, jsonset=True),
                        'textblock_ref':FieldArg("textblock_ref", ""),
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'button_label':FieldArg("text", ''),
                        'button_label_class':FieldArg("cssclass", ''),
                        'action':FieldArg("url", ''),
                        'action_json':FieldArg("url", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'target':FieldArg("text",''),
                        'button_text':FieldArg("text",'Submit'),
                        'button_class':FieldArg("cssclass", ''),
                        'buttondiv_class':FieldArg("cssclass", ''),
                        'outer_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ""),
                        'input_text':FieldArg("text", '', valdt=True, jsonset=True),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'required':FieldArg("boolean", False),
                        'type':FieldArg("text", 'text'),
                        'pattern':FieldArg("text", ''),
                        'title':FieldArg("text", ''),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'input_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored':FieldArg("boolean", False, jsonset=True),
                        'hide':FieldArg("boolean", False, jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        show_para1: True if the paragraph is to be visible, False if not
        para_text: The text appearing in the paragraph
        show_para2: True if the paragraph is to be visible, False if not
        textblock_ref: The reference of the TextBlock appearing in the second paragraph
        label: The text displayed to the left of the text input field
        label_class: The css class of the label
        button_label: The text displayed to the left of the button
        button_label_class: The css class of the label to the left of the button
        action_json:  if a value set, and client has jscript enabled, this is the page ident, label, url this button links to, expects a json page back
        action: The page ident, label, url this button links to
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        target: if given, the target attribute will be set
        button_text: The text on the button
        buttondiv_class: the class attribute of the div which contains the button
        button_class: the class attribute of the button
        outer_class: the class attribute of the outside div
        inputdiv_class: the class attribute of the tag which contains the label and input text
        error_class: The class applied to the paragraph containing the error message on error.
        input_text: The default text in the text input field, field name used as the name attribute
        size: The number of characters appearing in the text input area
        maxlength: The maximum number of characters accepted in the text area
        required: Set True to put the 'required' flag into the input field
        type: the type set on the input field, such as text or email
        pattern: regular expression pattern
        title: helps describe the pattern
        input_accepted_class: A class which can be set on the input field
        input_errored_class: A class which can be set on the input field
        input_class: Class set on the input field
        set_input_accepted: If True, input_accepted_class will be set on the input field
        set_errored_accepted: If True, input_errored_class will be set on the input field
        hide: If True, widget is hidden
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)

        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # div containing paragraphs
        self[1] = tag.Part(tag_name='div')
        # paragraph one and two
        self[1][0] = tag.Part(tag_name='p')
        self[1][0][0] =''
        self[1][1] = tag.Part(tag_name='p')
        self[1][1][0] = ''

        # The form
        self[2] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})

        # div containing label and input text
        self[2][0] = tag.Part(tag_name='div')
        # the label
        self[2][0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the text input field
        self[2][0][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})


        # div containing button
        self[2][1] = tag.Part(tag_name='div')
        # the label on the left of the button
        self[2][1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the submit button
        self[2][1][1] = tag.ClosedPart(tag_name="input", attribs={"type":"submit"})
        self._jsonurl = ''


    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        if self.get_field_value("target"):
            self[2].update_attribs({"target":self.get_field_value("target")})
        # Hides widget if no error and hide is True
        self.widget_hide(self.get_field_value("hide"))
        self._jsonurl = skiboot.get_url(self.get_field_value("action_json"), proj_ident=page.proj_ident)
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
        self[2].update_attribs({"action": actionurl})
        # the class of the outer div
        if self.get_field_value('outer_class'):
            self[1].attribs = {"class": self.get_field_value('outer_class')}

        # set paragraphs
        if not self.get_field_value("show_para1"):
            self[1][0].attribs={"style":"display:none;"}
        self[1][0][0] = self.get_field_value("para_text")
        if not self.get_field_value("show_para2"):
            self[1][1].attribs={"style":"display:none;"}
        # define the textblock
        tblock = self.get_field_value("textblock_ref")
        if tblock:
            tblock.proj_ident = page.proj_ident
            self[1][1][0] = tblock

        # the div holding label and input text
        if self.get_field_value('inputdiv_class'):
            self[2][0].attribs = {"class": self.get_field_value('inputdiv_class')}

        if self.get_field_value('label'):
            self[2][0][0][0] = self.get_field_value('label')
        if self.get_field_value('label_class'):
            self[2][0][0].attribs = {"class": self.get_field_value('label_class')}

        # set an id in the input field for the 'label for' tag
        self[2][0][1].insert_id()
        self[2][0][1].update_attribs({"name":self.get_formname('input_text'), "value":self.get_field_value('input_text')})
        if self.get_field_value('size'):
            self[2][0][1].update_attribs({"size":self.get_field_value('size')})
        if self.get_field_value('maxlength'):
            self[2][0][1].update_attribs({"maxlength":self.get_field_value('maxlength')})
        if self.get_field_value('required'):
            self[2][0][1].update_attribs({"required":"required"})
        if self.get_field_value('type'):
            self[2][0][1].update_attribs({"type":self.get_field_value('type')})
        if self.get_field_value('pattern'):
            self[2][0][1].update_attribs({"pattern":self.get_field_value('pattern')})
        if self.get_field_value('title'):
            self[2][0][1].update_attribs({"title":self.get_field_value('title')})

        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''

        if self.error_status and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_errored') and self.get_field_value('input_errored_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_errored_class')
            else:
                input_class = self.get_field_value('input_errored_class')
        elif self.get_field_value('set_input_accepted') and self.get_field_value('input_accepted_class'):
            if input_class:
                input_class = input_class + ' ' + self.get_field_value('input_accepted_class')
            else:
                input_class = self.get_field_value('input_accepted_class')

        if input_class:
            self[2][0][1].update_attribs({"class":input_class})

        # set the label 'for' attribute
        self[2][0][0].update_attribs({'for':self[2][0][1].get_id()})

        # the div holding button
        if self.get_field_value('buttondiv_class'):
            self[2][1].attribs = {"class": self.get_field_value('buttondiv_class')}

        if self.get_field_value('button_label'):
            self[2][1][0][0] = self.get_field_value('button_label')
        if self.get_field_value('button_label_class'):
            self[2][1][0].attribs = {"class": self.get_field_value('button_label_class')}

        # submit button
        self[2][1][1].update_attribs({"value":self.get_field_value('button_text')})
        # set an id in the submit button for the 'label for' tag
        self[2][1][1].insert_id()
        # the button class
        if self.get_field_value('button_class'):
            self[2][1][1].update_attribs({"class": self.get_field_value('button_class')})


        # set the label 'for' attribute
        self[2][1][0].update_attribs({'for':self[2][1][1].get_id()})

        # add ident and four hidden fields
        self.add_hiddens(self[2], page)



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
  <div> <!-- class attribute set to outer_class -->
    <p><!-- Paragraph 1, hidden if show_para1 is False -->
      <!-- Containing para_text -->
    </p>
    <p><!-- Paragraph 2, hidden if show_para2 is False -->
      <!-- Contains TextBlock -->
    </p>
  <div>
  <form method="post"> <!-- action attribute set to action field -->
    <div> <!-- class attribute set to inputdiv_class -->
      <label> <!-- with class set to label_class and content to label -->
      </label>
      <input type=\"text\" /> <!-- input text value set to input_text -->
    </div>
    <div> <!-- class attribute set to buttondiv_class -->
      <label> <!-- with class set to button_label_class and content to button_label -->
      </label>
      <input type=\"submit\" /> <!-- button value set to button_text and class to button_class -->
    </div>
    <!-- hidden input fields -->
  </form>    
</div>"""


class TwoInputsSubmit1(Widget):
    """Defines a form containing two text input fields."""

    error_location = (0,0,0)

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {'action':FieldArg("url", ''),
                        'action_json':FieldArg("url", ''),
                        'error_class':FieldArg("cssclass", ""),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'label':FieldArg("text", ''),
                        'label_class':FieldArg("cssclass", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'button_text':FieldArg("text", 'Submit'),
                        'button_class':FieldArg("cssclass", ''),
                        'input_text1':FieldArg("text", '', valdt=True, jsonset=True),
                        'size1':FieldArg("text", ''),
                        'maxlength1':FieldArg("text", ''),
                        'disabled1':FieldArg("boolean", False),
                        'required1':FieldArg("boolean", False),
                        'type1':FieldArg("text", 'text'),
                        'pattern1':FieldArg("text", ''),
                        'title1':FieldArg("text", ''),
                        'set_input_accepted1':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored1':FieldArg("boolean", False, jsonset=True),
                        'input_text2':FieldArg("text", '', valdt=True, jsonset=True),
                        'size2':FieldArg("text", ''),
                        'maxlength2':FieldArg("text", ''),
                        'disabled2':FieldArg("boolean", False),
                        'required2':FieldArg("boolean", False),
                        'type2':FieldArg("text", 'text'),
                        'pattern2':FieldArg("text", ''),
                        'title2':FieldArg("text", ''),
                        'set_input_accepted2':FieldArg("boolean", False, jsonset=True),
                        'set_input_errored2':FieldArg("boolean", False, jsonset=True),
                        'input_class1':FieldArg("cssclass", ''),
                        'input_class2':FieldArg("cssclass", ''),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", '')
                       }


    def __init__(self, name=None, brief='', **field_args):
        """
        action: The page ident this button links to
        action_json:  if a value set, and client has jscript enabled, this is the page ident, label, url this button links to, expects a json page back
        error_class: The class applied to the paragraph containing the error message on error.
        inputdiv_class: the class attribute of the tag which contains the label and inputs
        label: The text displayed to the left of the text input field
        label_class: The css class of the label
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
        type1: the type set on the first input field, such as text or email
        pattern1: regular expression pattern for first input field
        title1: helps describe the pattern of the first input field
        input_text2: The default text in the second text input field, field name used as the name attribute
        input_class2: Class set on the second input field
        size2: The number of characters appearing in the second text input area
        maxlength2: The maximum number of characters accepted in the second text area
        disabled2: Set True if the second field is to be disabled
        required2: Set True to put the 'required' flag into the second input field
        type2: the type set on the second input field, such as text or email
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
        # div containing label, input text and button
        self[1][0] = tag.Part(tag_name='div')

        # the label
        self[1][0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the first text input field
        self[1][0][1] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})
        # the second text input field
        self[1][0][2] = tag.ClosedPart(tag_name="input", attribs ={"type":"text"})
        # the submit button
        self[1][0][3] = tag.ClosedPart(tag_name="input", attribs={"type":"submit"})
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

        # the div holding label, input text and button
        if self.get_field_value('inputdiv_class'):
            self[1][0].attribs = {"class": self.get_field_value('inputdiv_class')}

        # set up label
        if self.get_field_value('label'):
            self[1][0][0][0] = self.get_field_value('label')
        if self.get_field_value('label_class'):
            self[1][0][0].attribs = {"class": self.get_field_value('label_class')}
        # first input field
        self[1][0][1].update_attribs({"name":self.get_formname('input_text1'), "value":self.get_field_value('input_text1')})
        if self.get_field_value('size1'):
            self[1][0][1].update_attribs({"size":self.get_field_value('size1')})
        if self.get_field_value('maxlength1'):
            self[1][0][1].update_attribs({"maxlength":self.get_field_value('maxlength1')})
        if self.get_field_value('disabled1'):
            self[1][0][1].update_attribs({"disabled":"disabled"})
        if self.get_field_value('required1'):
            self[1][0][1].update_attribs({"required":"required"})
        if self.get_field_value('type1'):
            self[1][0][1].update_attribs({"type":self.get_field_value('type1')})
        if self.get_field_value('pattern1'):
            self[1][0][1].update_attribs({"pattern":self.get_field_value('pattern1')})
        if self.get_field_value('title1'):
            self[1][0][1].update_attribs({"title":self.get_field_value('title1')})

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
            self[1][0][1].update_attribs({"class":input_class1})


        # second input field
        self[1][0][2].update_attribs({"name":self.get_formname('input_text2'), "value":self.get_field_value('input_text2')})
        if self.get_field_value('size2'):
            self[1][0][2].update_attribs({"size":self.get_field_value('size2')})
        if self.get_field_value('maxlength2'):
            self[1][0][2].update_attribs({"maxlength":self.get_field_value('maxlength2')})
        if self.get_field_value('disabled2'):
            self[1][0][2].update_attribs({"disabled":"disabled"})
        if self.get_field_value('required2'):
            self[1][0][2].update_attribs({"required":"required"})
        if self.get_field_value('type2'):
            self[1][0][2].update_attribs({"type":self.get_field_value('type2')})
        if self.get_field_value('pattern2'):
            self[1][0][2].update_attribs({"pattern":self.get_field_value('pattern2')})
        if self.get_field_value('title2'):
            self[1][0][2].update_attribs({"title":self.get_field_value('title2')})

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
            self[1][0][2].update_attribs({"class":input_class2})

        # the submit button
        self[1][0][3].update_attribs({"value":self.get_field_value('button_text')})
        # the button class
        if self.get_field_value('button_class'):
            self[1][0][3].update_attribs({"class": self.get_field_value('button_class')})

        # set an id in the first input field for the 'label for' tag
        self[1][0][1].insert_id()
        # set the label 'for' attribute
        self[1][0][0].update_attribs({'for':self[1][0][1].get_id()})

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
      <label> <!-- with class set to label_class and content to label -->
      </label>
      <input type=\"text\" /> <!-- input text value set to input_text1, class to input_class1 -->
      <input type=\"text\" /> <!-- input text value set to input_text2, class to input_class2 -->
      <input type=\"submit\" /> <!-- button value set to button_text and class to button_class -->
    </div>
    <!-- hidden input fields -->    
  </form>
</div>"""


class SubmitDict1(Widget):
    """Defines a form with a list of input fields followed by a single submit button
       to allow a client to input a dictionary"""

    display_errors = False

    arg_descriptions = {'action':FieldArg("url", ''),
                        'button_text':FieldArg("text", "Submit"),
                        'button_class':FieldArg("cssclass", ''),
                        'input_dict':FieldArgDict('text', valdt=False, senddict=True),
                        'input_class':FieldArg("cssclass", ''),
                        'inputdiv_class':FieldArg("cssclass", ''),
                        'inputdiv_style':FieldArg("cssstyle", ''),
                        'ul_class':FieldArg("cssclass", ""),
                        'ul_style':FieldArg("cssstyle", ""),
                        'li_class':FieldArg("cssclass", ""),
                        'li_style':FieldArg("cssstyle", ""),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        action: The label or ident of the action page
        button_text: text appearing on the button
        button_class: The css class of the button
        input_dict: an ordered dictionary, keys used in the field name, values are the text input
        input_class: Class set on each input field
        ul_class: Unordered list class
        ul_style: Style applied to ul element
        li_class: list element class
        li_style: Style applied to li element
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # The form
        self[0] = tag.Part(tag_name='form', attribs={"method":"post"})
        self[0][0] = tag.Part(tag_name='ul')
        # the submit button in a div
        self[0][1] = tag.Part(tag_name="div")
        self[0][1][0] = tag.ClosedPart(tag_name="input")

    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the form and list"

        input_dict = self.get_field_value("input_dict")
        if not input_dict:
            self.show = False
            return

        # get the form action url
        if not self.get_field_value("action"):
            # setting self._error replaces the entire tag
            self._error = "Warning: No form action"
            return
        action_url = skiboot.get_url(self.get_field_value("action"), proj_ident=page.proj_ident)
        if not action_url:
            # setting self._error replaces the entire tag by the self._error message
            self._error = "Warning: broken link"
            return
        self[0].update_attribs({"action": action_url})


        if self.get_field_value("ul_class"):
            self[0][0].update_attribs({"class": self.get_field_value("ul_class")})
        if self.get_field_value("ul_style"):
            self[0][0].update_attribs({"style": self.get_field_value("ul_style")})

        li_class =  self.get_field_value("li_class")

        input_name = self.get_formname("input_dict") + '-'

        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''

        linumber = -1
        for key, value in input_dict.items():
            keyed_name = input_name + key
            if input_class:
                li_input = tag.ClosedPart(tag_name="input",
                                          attribs ={"name":keyed_name,
                                                    "value":value,
                                                    "type":"text",
                                                    "class":input_class})
            else:
                li_input = tag.ClosedPart(tag_name="input",
                                          attribs ={"name":keyed_name,
                                                    "value":value,
                                                    "type":"text"})
            linumber += 1
            if li_class:
                self[0][0][linumber] = tag.Part(tag_name="li", attribs ={"class":li_class})
            else:
                self[0][0][linumber] = tag.Part(tag_name="li")
            if self.get_field_value("li_style"):
                self[0][0][linumber].update_attribs({"style": self.get_field_value("li_style")})


            self[0][0][linumber][0] = li_input

        # list done, now for submit button

        # the div holding button
        if self.get_field_value('inputdiv_class') and self.get_field_value('inputdiv_style'):
            self[0][1].attribs = {"class" : self.get_field_value('inputdiv_class'), "style": self.get_field_value('inputdiv_style')}
        elif self.get_field_value('inputdiv_class'):
            self[0][1].attribs = {"class" : self.get_field_value('inputdiv_class')}
        elif self.get_field_value('inputdiv_style'):
            self[0][1].attribs = {"style" : self.get_field_value('inputdiv_style')}

        if self.get_field_value('button_class'):
            self[0][1][0].attribs = {"value":self.get_field_value('button_text'), "type":"submit", "class": self.get_field_value('button_class')}
        else:
            self[0][1][0].attribs = {"value":self.get_field_value('button_text'), "type":"submit"}

        # add ident and four hidden fields
        self.add_hiddens(self[0], page)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <form method=\"post\"> <!-- action attribute set to action field -->
    <ul> <!-- with class set to ul_class and style to ul_style -->
      <!-- a li is created for each value in the input_dict dictionary -->
      <li>  <!-- with class set to li_class and style to li_style -->
        <input type="text" /> <!-- with CSS class input_class -->
             <!-- and with input name 'widgetname:input_dict-keyname' -->
      </li>
    </ul>
    <div> <!-- class attribute set to inputdiv_class, style to inputdiv_style -->
      <input type="submit" /> <!-- with value button_text, and CSS class button_class -->
    </div>
    <!-- hidden fields -->                              
  </form>
</div>"""


